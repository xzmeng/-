import datetime
import re

import pymongo

from core.Mssql import Mssql


# 操作MongoDB使用到了pymongo，应该先浏览一下官方的教程

class Mongodb:
    def __init__(self, db, collection, target, incremental=False):
        # 创建数据库连接，采取默认安装时没有用户名密码，所以可以不传参数
        self.client = pymongo.MongoClient()
        self.db = self.client[db]
        self.collection = self.db[collection]

        self.target = target
        self.incremental = incremental

        if target:
            target_table_name = target.table.name
        else:
            target_table_name = ''

        # 增量抽取的原理是在文档(表)中添加一个字段来标记是否导入过目标表
        self.incremental_record_name = '{}_to_{}'.format(self.collection,
                                                         target_table_name)
        self.fields_map = {}
        self.filters = {}
        self.filters_tuple = []

        # 统计信息
        self.drop_count = 0
        self.merge_count = 0

        # 标签
        self.tag = None

    # 返回字符串表示
    def __str__(self):
        if self.db and self.collection:
            return 'Mongo:{}.{}'.format(self.db.name, self.collection.name)
        else:
            return 'Mongo'

    def add_map(self, source_name, target_name):
        if target_name not in self.target.get_current_table_detail():
            return False
        if target_name in self.fields_map:
            return False
        self.fields_map[target_name] = source_name
        return True

    # 请简单看一下mongodb/pymongo的查询语法
    def add_filter(self, source_name, filter_type, value):
        # float, int, date
        if filter_type == 'gt':
            self.filters[source_name] = {
                '$gt': value
            }
        # float, int, date
        elif filter_type == 'ge':
            self.filters[source_name] = {
                '$gte': value
            }
        # float, int, date
        elif filter_type == 'lt':
            self.filters[source_name] = {
                '$lt': value
            }
        # float, int, date
        elif filter_type == 'le':
            self.filters[source_name] = {
                '$lte': value
            }
        # float, int, bool, string, date
        elif filter_type == 'eq':
            self.filters[source_name] = {
                '$eq': value
            }
        # string
        elif filter_type == 'contain':
            self.filters[source_name] = re.compile(value)
        # string
        elif filter_type == 'notcontain':
            self.filters[source_name] = {
                '$not': re.compile(value)
            }

    # 提取到数据库
    def merge_to_target(self):
        merge_count = 0
        drop_count = 0
        for row in self.collection.find(self.filters):
            if self.incremental:
                # 如果id已经存在增量信息表中，丢弃
                if row.get(self.incremental_record_name):
                    drop_count += 1
                    continue
                # 更新增量信息表
                else:
                    self.collection.update_one(
                        {"_id": row["_id"]},
                        {"$set": {self.incremental_record_name: True}}
                    )

            data = [(target_name, row.get(self.fields_map[target_name]))
                    for target_name in self.fields_map]
            print(data)
            if not data:
                continue
            ins = self.target.table.insert()
            self.target.conn.execute(ins, dict(data))
            merge_count += 1
        self.merge_count = merge_count
        self.drop_count = drop_count


if __name__ == '__main__':
    target = Mssql('sa', '132132qq', 'a')
    target.connect_db()
    target.set_table('studenta')
    mongo = Mongodb('fake', 'fake', target, incremental=True)
    mongo.add_map('name_mongo', 'name1')
    mongo.add_map('age_mongo', 'age1')
    mongo.add_map('salary_mongo', 'salary1')
    mongo.add_map('birthday_mongo', 'birthday1')
    mongo.add_filter('birthday_mongo', 'gt', datetime.datetime(2000, 1, 1))
    mongo.merge_to_target()
