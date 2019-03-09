from datetime import date

from sqlalchemy import create_engine, MetaData, Table, Column, select, and_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.types import Integer, Float, String, Boolean, Date
from sqlalchemy.exc import NoSuchTableError

from core.Mssql import MssqlTarget

type_map_mysql = {
    'int': Integer,
    'string': String(100),
    'float': Float,
    'bool': Boolean,
    'date': Date
}


class Mysql:
    def __init__(self, username, password, host, db):
        self.engine = None
        self.conn = None
        self.username = username
        self.password = password
        self.host = host
        self.db = db
        self.metadata = MetaData()
        self.table = None

    def is_connected(self):
        return self.conn is not None

    def connect_db(self):
        try:
            self.engine = create_engine(
               'mysql+mysqlconnector://{}:{}@{}/{}'.format(
                   self.username, self.password, self.host, self.db
               )
            )
            self.conn = self.engine.connect()
            self.metadata.reflect(bind=self.engine)

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
            c = Column(field_name, type_map_mysql[field_type])
            columns.append(c)
        table = Table(table_name, self.metadata, *columns)
        print(self.engine)
        table.create(self.engine)
        return table

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


class MysqlTarget(Mysql):
    pass


class MysqlSource(Mysql):
    def __init__(self, username, password, host, db, target, incremental=False):
        super().__init__(username, password, host, db)
        self.target = target

        # 是否开启增量抽取
        self.incremental = incremental
        # 保存历史抽取记录
        self.incremental_record = None

        self.fields_map = {}
        self.filters = []

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
            ins = self.target.table.insert()
            self.target.conn.execute(ins, dict(data))
            merge_count += 1
        # 将抽取到的,增量丢弃掉的数据条数保存
        self.merge_count = merge_count
        self.drop_count = drop_count

    def merge_completed(self):
        pass


if __name__ == '__main__':
    pass


