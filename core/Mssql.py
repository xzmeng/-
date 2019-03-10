import datetime

from sqlalchemy import create_engine, MetaData, Table, Column, select, and_, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.types import Integer, Float, String, Boolean
from sqlalchemy.exc import NoSuchTableError

type_map_mssql = {
    'int': Integer,
    'string': String,
    'float': Float,
    'bool': Boolean,
    'datetime': DateTime
}


# Mssql 是 MssqlTarget 和 MssqlSource 的超类
# 使用Mssql.connect_db()建立自己的数据库连接
# 使用Mssql.list_table()查看当前数据库的表的列表
# 使用Mssql.set_table(table_name)设置数据源/目标使用哪张表
#     并且初始化Mssql.table (类型为sqlalchemy.Table)


class Mssql:
    def __init__(self, username, password, dsn):
        self.engine = None
        self.conn = None
        self.username = username
        self.password = password
        self.dsn = dsn
        self.metadata = MetaData()
        self.table = None

    def __str__(self):
        if self.table is not None:
            return self.table.name
        else:
            return 'Myssql'

    def is_connected(self):
        return self.conn is not None

    def connect_db(self):
        try:
            self.engine = create_engine(
                'mssql+pyodbc://{}:{}@{}'.format(
                    self.username, self.password, self.dsn
                )
            )
            Session = sessionmaker(self.engine)
            self.session = Session()
            self.conn = self.engine.connect()
            print(self.session)
            print(self.engine)
            self.metadata.reflect(self.engine)

            return True, '成功连接到数据库'
        except Exception as e:
            self.engine = None
            self.conn = None
            return False, str(e)

    def list_table(self):
        return list(self.metadata.tables.keys())

    def set_table(self, table_name):
        try:
            self.table = Table(table_name,
                               self.metadata,
                               autoload=True,
                               autoload_with=self.engine)
            return True
        except NoSuchTableError:
            return False

    # fields: 含有 name:type 对的字典
    def create_table(self, table_name, fields):
        # 如果 指定名字的表已经存在 直接返回该表
        if table_name in self.list_table():
            return self.metadata.tables[table_name]
        columns = [Column('id', Integer, primary_key=True)]
        for field_name, field_type in fields.items():
            c = Column(field_name, type_map_mssql[field_type])
            columns.append(c)
        table = Table(table_name, self.metadata, *columns)
        table.create(self.engine)
        return table

    def drop_table(self, table_name):
        if table_name in self.list_table():
            try:
                self.metadata.tables[table_name].drop(self.engine)
                return True
            except Exception as e:
                print(e)
                return False

    def get_table_detail(self, table_name):
        fields = {}
        table = self.metadata.tables.get(table_name)
        if table is not None:
            for c in table.c:
                fields[str(c.name)] = str(c.type)
        return fields

    def get_current_table_detail(self):
        if self.table is not None:
            return self.get_table_detail(self.table.name)
        return {}


class MssqlTarget(Mssql):
    pass


class MssqlSource(Mssql):
    def __init__(self, username, password, dsn, target, incremental=False):
        super().__init__(username, password, dsn)
        self.target = target

        # 是否开启增量抽取
        self.incremental = incremental
        # 保存历史抽取记录
        self.incremental_record = None

        self.fields_map = {}
        self.filters = []
        self.filters_tuple = []

        # 抽取数目和去重丢弃数目统计
        self.merge_count = 0
        self.drop_count = 0

    def add_map(self, source_name, target_name):
        if source_name not in self.get_current_table_detail():
            return False
        if target_name not in self.target.get_current_table_detail():
            return False
        if target_name in self.fields_map:
            return False
        self.fields_map[target_name] = source_name
        return True

    # 调用该函数时应能保证输入是有效的，该函数不负责检查输入的正确性
    def add_filter(self, source_name, filter_type, value):
        # int, float > = < !=
        # string  like '%filter%' not like
        # date before after equal not equal
        # bool True False

        # float, int, date
        if filter_type == 'gt':
            self.filters.append(self.table.c[source_name] > value)
        # float, int, date
        elif filter_type == 'ge':
            self.filters.append(self.table.c[source_name] >= value)
        # float, int, date
        elif filter_type == 'lt':
            self.filters.append(self.table.c[source_name] < value)
        # float, int, date
        elif filter_type == 'le':
            self.filters.append(self.table.c[source_name] <= value)
        # float, int, bool, string, date
        elif filter_type == 'eq':
            self.filters.append(self.table.c[source_name] == value)
        # string
        elif filter_type == 'contain':
            self.filters.append(self.table.c[source_name].like('%{}%'.format(value)))
        # string
        elif filter_type == 'notcontain':
            self.filters.append(~(self.table.c[source_name].like('%{}%'.format(value))))

    def merge_to_target(self):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        if self.incremental:
            incremental_record_name = '{}_to_{}'.format(
                self.table.name, self.target.table.name
            )
            if incremental_record_name not in self.list_table():

                self.incremental_record = Table(
                    incremental_record_name,
                    self.metadata,
                    Column('id', Integer, primary_key=True),
                )
                self.incremental_record.create(self.engine)
            else:
                self.incremental_record = \
                    self.metadata.tables[incremental_record_name]

        s = select([self.table]).where(and_(*self.filters))

        merge_count = 0
        drop_count = 0
        for row in self.conn.execute(s):
            row_dict = dict(row)
            if self.incremental:
                if session.query(self.incremental_record).filter(
                    self.incremental_record.c.id == row_dict['id']
                ).count() != 0:
                    drop_count += 1
                    continue
                else:
                    ins = self.incremental_record.insert()
                    self.engine.execute(ins, id=row_dict['id'])

            data = [(target_field, row_dict[source_field])
                    for target_field, source_field in self.fields_map.items()]
            if not data:
                continue
            ins = self.target.table.insert()
            self.target.conn.execute(ins, dict(data))
            merge_count += 1
        # 将抽取到的,增量丢弃掉的数据条数保存
        self.merge_count = merge_count
        self.drop_count = drop_count

    def merge_completed(self):
        pass


class Migration:
    def __init__(self):
        self.sources = []

    def handle_mssql(self):
        pass


if __name__ == '__main__':
    username = 'sa'
    password = '132132qq'
    dsn = 'a'
    target = MssqlTarget(username, password, dsn)
    source = MssqlSource(username, password, dsn, target, incremental=True)
    target.connect_db()
    source.connect_db()
    target.set_table('fake_data01')
    source.set_table('fake_data02')

    source.add_map('name2', 'name1')
    source.add_map('salary2', 'salary1')
    source.add_map('birthday2', 'birthday1')

    source.add_filter('birthday2', 'gt', datetime.datetime(2000, 1, 1))
    print(source.fields_map)
    source.merge_to_target()
    print(source.merge_count)
    print(source.drop_count)

