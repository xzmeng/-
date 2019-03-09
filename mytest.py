import datetime
import random

import pandas as pd
import numpy as np
from faker import Faker

from openpyxl import Workbook
from openpyxl import load_workbook


a = 'hello'
b = 'el'

def get_date(d):
    if isinstance(d, datetime.datetime):
        return d.date()
    else:
        return d

a = datetime.datetime(2000, 1, 1).date()
print(type(a), a)
print(b)



