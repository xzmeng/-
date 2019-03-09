from datetime import date
from faker import Faker
from sqlalchemy import not_

from core.Mssql import MssqlSource
from sqlalchemy.sql import  select

mssql = MssqlSource('sa', '132132qq', 'a', None)
mssql.connect_db()

mssql.set_table('fake_data01')
table = mssql.table

s = select([table]).where(~(table.c['name1'].like('%Pope%')))
for row in mssql.conn.execute(s):
    print(row)

filter = table.c['name1'].like('%Pope')
print(filter, type(filter))