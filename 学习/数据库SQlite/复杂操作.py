'''
Author: 李晓乐
Date: 2025-07-25 19:20:50
LastEditors: enjoylearning96 148044540+enjoylearning96@users.noreply.github.com
LastEditTime: 2025-07-25 20:07:07
FilePath: \QT\报表生成\test\数据库SQlite\复杂操作.py
Description: 

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''
#1.创建多层次数据
# 1.1 多表关联
import sqlite3

# 连接数据库
conn = sqlite3.connect('nested_data.db')
cursor = conn.cursor()

# 创建部门表
cursor.execute('''
CREATE TABLE IF NOT EXISTS departments (
    dept_id INTEGER PRIMARY KEY,
    dept_name TEXT NOT NULL,
    location TEXT
)
''')

# 创建员工表（关联部门）
cursor.execute('''
CREATE TABLE IF NOT EXISTS employees (
    emp_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    age INTEGER,
    salary REAL,
    dept_id INTEGER,
    FOREIGN KEY (dept_id) REFERENCES departments(dept_id)
)
''')

# 创建项目表（多对多关系，通过关联表实现）
cursor.execute('''
CREATE TABLE IF NOT EXISTS projects (
    project_id INTEGER PRIMARY KEY,
    project_name TEXT,
    budget REAL
)
''')

# 创建员工-项目关联表
cursor.execute('''
CREATE TABLE IF NOT EXISTS emp_projects (
    emp_id INTEGER,
    project_id INTEGER,
    role TEXT,
    PRIMARY KEY (emp_id, project_id),
    FOREIGN KEY (emp_id) REFERENCES employees(emp_id),
    FOREIGN KEY (project_id) REFERENCES projects(project_id)
)
''')
'''
PRIMARY KEY (emp_id, project_id) 表示：
这是一个由两个字段组成的复合主键
组合 (emp_id, project_id) 必须是唯一的
一个员工可以参与多个项目（emp_id可以重复）
一个项目可以有多个员工参与（project_id可以重复）
但同一个员工不能重复参与同一个项目（emp_id + project_id组合必须唯一）
'''
'''
外键约束 (FOREIGN KEY)
两个外键约束确保：
emp_id 必须存在于 employees(emp_id) 表中
project_id 必须存在于 projects(project_id) 表中
'''

conn.commit()

#1.2 插入层次化数据

# 插入部门数据
departments = [
    (1, '研发部', '北京'),
    (2, '市场部', '上海'),
    (3, '财务部', '广州')
]
cursor.executemany('INSERT INTO departments VALUES (?, ?, ?)', departments)

# 插入员工数据
employees = [
    (101, '张三', 28, 15000, 1),
    (102, '李四', 35, 25000, 1),
    (103, '王五', 40, 30000, 2),
    (104, '赵六', 32, 22000, 3)
]
cursor.executemany('INSERT INTO employees VALUES (?, ?, ?, ?, ?)', employees)

# 插入项目数据
projects = [
    (1001, '项目A', 500000),
    (1002, '项目B', 1000000),
    (1003, '项目C', 750000)
]
cursor.executemany('INSERT INTO projects VALUES (?, ?, ?)', projects)

# 插入员工-项目关联数据
emp_projects = [
    (101, 1001, '开发工程师'),
    (101, 1002, '测试工程师'),
    (102, 1001, '项目经理'),
    (103, 1002, '市场顾问'),
    (104, 1003, '财务主管')
]
cursor.executemany('INSERT INTO emp_projects VALUES (?, ?, ?)', emp_projects)

conn.commit()

#2 多条件查询

#2.1 基本多条件查询
# AND 条件查询：研发部且年龄>30的员工
cursor.execute('''
SELECT * FROM employees 
WHERE dept_id = ? AND age > ?
''', (1, 30))
print("研发部且年龄>30的员工:")
for row in cursor.fetchall():
    print(row)

# OR 条件查询：薪资>20000或年龄<30的员工
cursor.execute('''
SELECT emp_id, name FROM employees 
WHERE salary > 20000 OR age < 30
''')
print("\n高薪或年轻员工:")
for row in cursor.fetchall():
    print(row)
    
#2.2 复杂多条件查询
# 组合条件：研发部或市场部，薪资在20000-30000之间，按年龄降序
cursor.execute('''
SELECT e.name, e.age, e.salary, d.dept_name 
FROM employees e
JOIN departments d ON e.dept_id = d.dept_id
WHERE (d.dept_name = '研发部' OR d.dept_name = '市场部')
AND e.salary BETWEEN 20000 AND 30000
ORDER BY e.age DESC
''')
# 指定了employees表(别名为e)和departments表(别名为d)
# 通过JOIN将两个表关联起来
print("\n复合条件查询结果:")
for row in cursor.fetchall():
    print(row)
    
#2.3 聚合查询与分组
# 各部门平均薪资和人数
cursor.execute('''
SELECT d.dept_name, AVG(e.salary), COUNT(e.emp_id)
FROM departments d
LEFT JOIN employees e ON d.dept_id = e.dept_id

GROUP BY d.dept_name
HAVING COUNT(e.emp_id) > 0  -- 只显示有员工的部门
''')
# LEFT JOIN 确保即使部门没有员工也会显示
print("\n部门薪资统计:")
for row in cursor.fetchall():
    print(f"{row[0]}: 平均薪资{row[1]:.2f}, 人数{row[2]}")

# 查询技巧
# 3.1 使用子查询
# 查询薪资高于平均薪资的员工
cursor.execute('''
SELECT * FROM employees
WHERE salary > (SELECT AVG(salary) FROM employees)
# 这里的子查询计算了所有员工的平均薪资
# 并将其作为条件
# 以筛选出薪资高于平均水平的员工
''')
print("\n薪资高于平均薪资的员工:")
for row in cursor.fetchall():
    print(row)
# 3.2 使用窗口函数
