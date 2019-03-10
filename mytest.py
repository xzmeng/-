import datetime
import random
import re

import datetime
import pandas as pd
import numpy as np
from faker import Faker

from openpyxl import Workbook
from openpyxl import load_workbook

import pymongo

from core.Mssql import MssqlTarget

# mssql = MssqlTarget('sa', '132132qq', 'a')
# mssql.connect_db()
# table = mssql.metadata.tables.get('studenta')

# info = []
# title = '{:<20}{:<20}'.format('名称', '类型')
# print(title)
# info = '{:<20}{:<20}'.format('aaa', 'bbb')
# print(info)
# for c in table.c:
#     field_name = str(c.name)
#     field_type = str(c.type).split(' ')[0]
#     text = '%-20s%-20s' % (field_name, field_type)
#     print(text)
#
# x = ['a', 'b', 'c']
# print('x'.join(x))
x = []
y = []
for i in range(10):
    x.append(lambda i=i: func(i))
    y.append(lambda i=i: func(i))

import pymongo

mongo = pymongo.MongoClient()
db = mongo['d']
