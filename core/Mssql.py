from sqlalchemy import create_engine, MetaData, Table, Column
from sqlalchemy.types import Integer, Float, String, Boolean, Date
from sqlalchemy.exc import NoSuchTableError

type_map_mssql = {
    'int': Integer,
    'string': String,
    'float': Float,
    'bool': Boolean,
    'date': Date
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

    def is_connected(self):
        return self.conn is not None

    def connect_db(self):
        try:
            self.engine = create_engine(
                'mssql+pyodbc://{}:{}@{}'.format(
                    self.username, self.password, self.dsn
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
        columns = [Column('id', Integer, primary_key=True)]
        for field_name, field_type in fields.items():
            c = Column(field_name, type_map_mssql[field_type])
            columns.append(c)
        table = Table(table_name, self.metadata, *columns)
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


class MssqlTarget(Mssql):
    pass


class MssqlSource(Mssql):
    def __init__(self, username, password, dsn, target):
        super().__init__(username, password, dsn)
        self.target = target
        self.fields_map = {}
        self.filters = {}

    def add_map(self, source_name, target_name):
        if source_name not in self.get_current_table_detail():
            return False
        if target_name not in self.target.get_current_table_detail():
            return False
        if target_name not in self.fields_map:
            self.fields_map[target_name] = source_name
            return True
        return False

    # 调用该函数时应能保证输入是有效的，该函数不负责检查输入的正确性
    def add_filter(self, source_name, fitler):
        self.filters[source_name] = 'filter'
        # int, float > = < !=
        # string  like '%filter%' not like
        # date before after equal not equal
        # bool True False


class Filter:
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
    source = MssqlSource(username, password, dsn, target)
    target.connect_db()
    source.connect_db()
    target.set_table('fake_data01')
    source.set_table('fake_data02')

    source.add_map('name2', 'name1')
    source.add_map('age2', 'age1')
    source.add_map('salary2', 'salary1')
    source.add_map('birthday2', 'birthday1')
    source.add_map('is_human2', 'is_human1')

    print(source.fields_map)

