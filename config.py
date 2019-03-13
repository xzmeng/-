# 请把数据库的配置信息全部填在这里
# DataFaker.py会自动生成测试数据

config_mssql = {
    'username': 'sa',
    'password': '132132qq',
    'dsn': 'a',
    'fake_table_name': 'fake_mssql',
    'fake_target_name': 'fake_target',
}

config_mysql = {
    'username': 'root',
    'password': '132132qq',
    'host': 'localhost',
    'db': 'flask',
    'fake_table_name': 'fake_mysql',
}

config_mongodb = {
    'fake_db': 'fake',
    'fake_collection': 'fake_mongo',
}

config_excel = {
    'file_path': 'data.xlsx'
}