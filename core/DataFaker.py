import datetime
import random

from openpyxl import Workbook, load_workbook

from core.Mssql import Mssql
from faker import Faker

from core.Mysql import Mysql

fake = Faker()


class MssqlFaker:
    def __init__(self, username, password, dsn):
        self.mssql = Mssql(username, password, dsn)
        self.mssql.connect_db()

    def gen_fake_data(self, table_name, table_id, insert_count=100):
        self.mssql.connect_db()
        fields_pair = [['name', 'string'],
                       ['age', 'int'],
                       ['salary', 'float'],
                       ['birthday', 'date'],
                       ['is_human', 'bool']]
        for pair in fields_pair:
            pair[0] += str(table_id)
        print(fields_pair)
        fields = dict(fields_pair)

        table = self.mssql.create_table(table_name, fields)
        ins = table.insert()

        self.mssql.conn.execute(
            ins, [{
                fields_pair[0][0]: fake.name(),
                fields_pair[1][0]: random.randint(1, 89),
                fields_pair[2][0]: random.randint(10000, 20000) / 100,
                fields_pair[3][0]: datetime.date(random.randint(1980, 2010, ),
                                                 random.randint(1, 12),
                                                 random.randint(1, 28)),
                fields_pair[4][0]: True if random.randint(0, 1) == 1 else False
            } for i in range(insert_count)]
        )


class ExcelFaker:
    def __init__(self):
        pass

    def gen_fake_data(self, file_name='data.xlsx', insert_count=100):
        wb = Workbook()
        ws = wb.active
        ws.title = '学生信息表'
        ws['A1'] = 'id'
        ws['B1'] = 'name_excel'
        ws['C1'] = 'age_excel'
        ws['D1'] = 'salary_excel'
        ws['E1'] = 'birthday_excel'
        ws['F1'] = 'is_human_excel'
        count = 1
        fake = Faker()
        for row in ws.iter_rows(min_row=2,
                                max_col=6,
                                max_row=2 + insert_count - 1):
            row[0].value = count
            count += 1
            row[1].value = fake.name()
            row[2].value = random.randint(1, 55)
            row[3].value = random.randint(10000, 99999) / 100
            row[4].value = datetime.date(
                random.randint(1970, 2019),
                random.randint(1, 12),
                random.randint(1, 28)
            )
            row[5].value = True if random.randint(0, 1) > 0 else False
        wb.save(file_name)

    def append_fake_data(self, file_name='data.xlsx', insert_count=100):
        wb = load_workbook(file_name)
        ws = wb.active
        row_num = 2
        last_id = 0
        while True:
            value = ws.cell(row_num, 1).value
            if value is not None:
                last_id = value
                row_num += 1
            else:
                break
        current_id = last_id + 1
        fake = Faker()
        for row in ws.iter_rows(min_row=row_num,
                                max_col=6,
                                max_row=row_num + insert_count - 1):
            row[0].value = current_id
            current_id += 1
            row[1].value = fake.name()
            row[2].value = random.randint(1, 55)
            row[3].value = random.randint(10000, 99999) / 100
            row[4].value = datetime.date(
                random.randint(1970, 2019),
                random.randint(1, 12),
                random.randint(1, 28)
            )
            row[5].value = True if random.randint(0, 1) > 0 else False
        wb.save(file_name)


class MysqlFaker:
    def __init__(self, username, password, host, db):
        self.mysql = Mysql(username, password, host, db)
        self.mysql.connect_db()

    def gen_fake_data(self, table_name, table_id, insert_count=100):
        self.mysql.connect_db()
        fields_pair = [['name', 'string'],
                       ['age', 'int'],
                       ['salary', 'float'],
                       ['birthday', 'date'],
                       ['is_human', 'bool']]
        for pair in fields_pair:
            pair[0] += str(table_id)
        print(fields_pair)
        fields = dict(fields_pair)

        table = self.mysql.create_table(table_name, fields)
        ins = table.insert()

        self.mysql.conn.execute(
            ins, [{
                fields_pair[0][0]: fake.name(),
                fields_pair[1][0]: random.randint(1, 89),
                fields_pair[2][0]: random.randint(10000, 20000) / 100,
                fields_pair[3][0]: datetime.date(random.randint(1980, 2010, ),
                                                 random.randint(1, 12),
                                                 random.randint(1, 28)),
                fields_pair[4][0]: True if random.randint(0, 1) == 1 else False
            } for i in range(insert_count)])


def run():
    # fields = {
    #     'name': 'string',
    #     'age': 'int',
    #     'salary': 'float',
    #     'birthday': 'date',
    #     'is_human': 'bool'
    # }
    my_faker = MssqlFaker('sa', '132132qq', 'a')
    my_faker.gen_fake_data('studenta', 1)
    my_faker.gen_fake_data('studentb', 2)



def run2():
    # fields = {
    #     'name': 'string',
    #     'age': 'int',
    #     'salary': 'float',
    #     'birthday': 'date',
    #     'is_human': 'bool'
    # }
    my_faker = MysqlFaker('root', '132132qq', 'localhost', 'flask')
    my_faker.gen_fake_data('fake_data01', 1)
    my_faker.gen_fake_data('fake_data02', 2)


if __name__ == '__main__':
    run()

