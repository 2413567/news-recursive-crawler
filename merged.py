import os
import pandas as pd
import sqlite3

# 目录路径和新 SQLite 数据库文件名
dir_path = '数据'
output_file = 'merged.db'

# 创建新 SQLite 数据库连接
conn = sqlite3.connect(output_file)

# 循环遍历目录中的所有 SQLite 数据库文件
for file_name in os.listdir(dir_path):
    if file_name.endswith('.db'):
        file_path = os.path.join(dir_path, file_name)
        # 读取当前 SQLite 数据库文件中的 response_data 表数据
        df = pd.read_sql_query('SELECT * FROM response_data', sqlite3.connect(file_path))
        # 将当前 SQLite 数据库文件中的 response_data 表数据合并到新 SQLite 数据库文件中
        df.to_sql('response_data', conn, if_exists='append', index=False)

# 提交并关闭新 SQLite 数据库连接
conn.commit()
conn.close()
