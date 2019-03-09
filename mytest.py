from datetime import date
from faker import Faker
from sqlalchemy import not_
from sqlalchemy.sql.elements import and_
from sqlalchemy.sql.expression import exists
from core.Mssql import MssqlSource
from sqlalchemy.sql import  select

mssql = MssqlSource('sa', '132132qq', 'a', None)
mssql.connect_db()

mssql.set_table('fake_data01')
table = mssql.table

# s = select([table]).where(
#     and_(
#         *[table.c['birthday1'] > date(2000, 1, 1),
#         table.c['birthday1'] < date(2002, 1, 1)]
#     )
# )
# for row in mssql.conn.execute(s):
#     print(row['birthday1'], type('birthday1'))
#     print(dict(row))
#
# filter = table.c['name1'].like('%Pope')
# print(filter, type(filter))
s = exists(select([table.c.id]).where(table.c.id == 100))
print(s)
mssql.conn.execute(s)
