import sqlite3
import os
import config


class SpiderDB:
    """用于管理SQLite数据库的类"""

    def __init__(self, save_path):
        self.save_path = save_path
        # 判断数据库文件是否存在
        if not os.path.exists(self.save_path):
            print(f"Database file '{self.save_path}' does not exist. create a new DATABASE...")

        try:
            # 创建一个SQLite数据库连接
            self.conn = sqlite3.connect(self.save_path)

            # 创建一个表格存储成功请求的请求数据
            self.conn.execute('''CREATE TABLE IF NOT EXISTS request_data
                                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                 url TEXT NOT NULL,
                                 method TEXT NOT NULL,
                                 headers TEXT NOT NULL,
                                 params TEXT NOT NULL,
                                 data TEXT NOT NULL,
                                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);''')

            # 创建一个表格存储返回数据
            self.conn.execute('''CREATE TABLE IF NOT EXISTS response_data
                                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                 request_id INTEGER NOT NULL,
                                 status_code INTEGER NOT NULL,
                                 title TEXT NOT NULL,
                                 url TEXT NOT NULL,
                                 headers TEXT NOT NULL,
                                 content TEXT NOT NULL,
                                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                 FOREIGN KEY(request_id) REFERENCES request_data(id));''')

        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            self.conn.rollback()
            raise e

    def insert_request_data(self, url, method, headers, params, data):
        try:
            self.conn.execute("INSERT INTO request_data (url, method, headers, params, data) VALUES (?, ?, ?, ?, ?)",
                              (url, method, headers, params, data))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred while inserting request data: {e}")
            self.conn.rollback()
            raise e

    def insert_response_data(self, request_id, status_code, headers, title, content, url):
        try:
            self.conn.execute(
                "INSERT INTO response_data (request_id, status_code,  title, url, headers, content) VALUES (?, ?, ?, ?,"
                " ?, ?)",
                (request_id, status_code, title, url, headers, content))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred while inserting response data: {e}")
            self.conn.rollback()
            raise e

    def close(self):
        # 关闭数据库连接
        self.conn.close()
