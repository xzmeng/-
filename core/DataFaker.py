import datetime
import random

from core.Mssql import Mssql
from faker import Faker

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


if __name__ == '__main__':
    fields = {
        'name': 'string',
        'age': 'int',
        'salary': 'float',
        'birthday': 'date',
        'is_human': 'bool'
    }

    my_faker = MssqlFaker('sa', '132132qq', 'a')
    # my_faker.gen_fake_data('fake_data01', 1)
    my_faker.gen_fake_data('fake_data02', 2)
