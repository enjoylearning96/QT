'''
Author: 李晓乐
Date: 2025-07-24 20:28:45
LastEditors: enjoylearning96 148044540+enjoylearning96@users.noreply.github.com
LastEditTime: 2025-07-25 18:55:22
FilePath: \QT\报表生成\test\数据库操作.py
Description: 

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''
import sqlite3

# 连接数据库（如果不存在会自动创建）
conn = sqlite3.connect('example.db')

# 创建游标对象
cursor = conn.cursor()

# 创建表
cursor.execute('''CREATE TABLE IF NOT EXISTS users
               (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)''')
#INTEGER: 整数类型
#PRIMARY KEY: 主键，唯一标识每一行，通常自增（在 SQLite 中会自动自增）

# 插入数据
# 插入单条数据（id 会自动递增）
cursor.execute("INSERT INTO users (name, age) VALUES (?, ?)", ('Alice', 25))

# 插入多条数据
users_data = [('Bob', 30), ('Charlie', 35), ('David', 40)]
cursor.executemany("INSERT INTO users (name, age) VALUES (?, ?)", users_data)

conn.commit()  # 提交更改

# 查询数据
# 查询所有数据
cursor.execute("SELECT * FROM users")
rows = cursor.fetchall()
for row in rows:
    print(row)  # 输出：(1, 'Alice', 25), (2, 'Bob', 30), ...

# 按条件查询（例如 age > 30）
cursor.execute("SELECT * FROM users WHERE age > ?", (30,))
older_users = cursor.fetchall()
print(older_users)  # 输出：(3, 'Charlie', 35), (4, 'David', 40)

# 更新数据
cursor.execute("UPDATE users SET age = ? WHERE name = ?", (26, 'Alice'))
conn.commit()

# 删除数据
cursor.execute("DELETE FROM users WHERE name = ?", ('Bob',))
conn.commit()

# 关闭连接
conn.close()