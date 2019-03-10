from config import *
from core.Excel import Excel
from core.Mongodb import Mongodb
from core.Mssql import MssqlTarget, MssqlSource
from core.Mysql import MysqlSource
from core.DataFaker import drop, create


class Task:
    def __init__(self):
        self.sources = []

    def add_source(self, source):
        self.sources.append(source)

    def add_sources(self, sources):
        print(sources)
        if isinstance(sources, list):
            self.sources.extend(sources)

    def merge(self):
        print(self.sources)
        for source in self.sources:
            print('merging {}...'.format(str(source)))
            source.merge_to_target()


def test_task():
    task = Task()

    # configure target
    target = MssqlTarget(
        config_mssql['username'],
        config_mssql['password'],
        config_mssql['dsn']
    )
    target.connect_db()
    target.set_table(config_mssql['fake_target_name'])

    # configure mssql
    source_mssql = MssqlSource(
        config_mssql['username'],
        config_mssql['password'],
        config_mssql['dsn'],
        target, incremental=True
    )
    source_mssql.connect_db()
    source_mssql.set_table(config_mssql['fake_table_name'])
    source_mssql.add_map('name_mssql', 'name_mssql')
    source_mssql.add_map('age_mssql', 'age_mssql')
    source_mssql.add_map('salary_mssql', 'salary_mssql')
    source_mssql.add_map('birthday_mssql', 'birthday_mssql')
    source_mssql.add_map('is_human_mssql', 'is_human_mssql')

    # configure mysql
    source_mysql = MysqlSource(config_mysql['username'],
                               config_mysql['password'],
                               config_mysql['host'],
                               config_mysql['db'],
                               target, incremental=True)
    source_mysql.connect_db()
    source_mysql.set_table(config_mysql['fake_table_name'])
    source_mysql.add_map('name_mysql', 'name_mssql')
    source_mysql.add_map('age_mysql', 'age_mssql')
    source_mysql.add_map('salary_mysql', 'salary_mssql')
    source_mysql.add_map('birthday_mysql', 'birthday_mssql')
    source_mysql.add_map('is_human_mysql', 'is_human_mssql')

    # configure mongo
    source_mongo = Mongodb(config_mongodb['fake_db'],
                           config_mongodb['fake_collection'],
                           target, incremental=True)
    source_mongo.add_map('name_mongo', 'name_mssql')
    source_mongo.add_map('age_mongo', 'age_mssql')
    source_mongo.add_map('salary_mongo', 'salary_mssql')
    source_mongo.add_map('birthday_mongo', 'birthday_mssql')
    source_mongo.add_map('is_human_mongo', 'is_human_mssql')

    # configure excel
    source_excel = Excel(config_excel['file_path'],
                         target, incremental=True)
    source_excel.add_map('name_excel', 'name_mssql')
    source_excel.add_map('age_excel', 'age_mssql')
    source_excel.add_map('salary_excel', 'salary_mssql')
    source_excel.add_map('birthday_excel', 'birthday_mssql')
    source_excel.add_map('is_human_excel', 'is_human_mssql')

    task.add_sources([source_mssql,
                      source_mysql,
                      source_excel,
                      source_mongo])
    task.merge()
    print('ok')


if __name__ == '__main__':
    test_task()


