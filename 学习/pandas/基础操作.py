import pandas as pd
import numpy as np
from datetime import datetime

# ==============================================
# 1. 创建示例数据
# ==============================================

# 创建员工数据
employees = {
    '员工ID': ['E1001', 'E1002', 'E1003', 'E1004', 'E1005', 'E1006', 'E1007'],
    '姓名': ['张三', '李四', '王五', '赵六', '钱七', '孙八', '周九'],
    '部门': ['技术部', '市场部', '技术部', '人事部', '市场部', '技术部', '财务部'],
    '入职日期': ['2020-01-15', '2019-05-22', '2021-03-10', '2018-11-05', '2022-02-18', '2020-07-30', '2021-09-12'],
    '基本工资': [8500, 7800, 9200, 7500, 8100, 8800, 7900],
    '绩效奖金': [1200, 1500, 1800, 1000, 1300, 1600, 1100],
    '年龄': [28, 32, 25, 35, 29, 31, 27]
}

# 创建销售数据
sales = {
    '订单ID': ['S2023001', 'S2023002', 'S2023003', 'S2023004', 'S2023005'],
    '员工ID': ['E1001', 'E1002', 'E1001', 'E1003', 'E1004'],
    '销售金额': [4500, 6800, 3200, 5400, 2900],
    '订单日期': ['2023-01-05', '2023-01-12', '2023-02-03', '2023-02-15', '2023-03-02'],
    '产品类别': ['电子产品', '办公用品', '电子产品', '家具', '办公用品']
}

# 转换为DataFrame
df_employees = pd.DataFrame(employees)
df_sales = pd.DataFrame(sales)

# ==============================================
# 2. 数据预处理
# ==============================================

# 转换日期格式
df_employees['入职日期'] = pd.to_datetime(df_employees['入职日期'])
df_sales['订单日期'] = pd.to_datetime(df_sales['订单日期'])

# 计算总工资
df_employees['总工资'] = df_employees['基本工资'] + df_employees['绩效奖金']

# 计算工龄
current_date = datetime.now()
df_employees['工龄'] = (current_date - df_employees['入职日期']).dt.days // 365

# 添加季度信息
df_sales['季度'] = df_sales['订单日期'].dt.quarter

# ==============================================
# 3. 数据分析
# ==============================================

# 各部门平均工资
dept_avg_salary = df_employees.groupby('部门')['总工资'].mean().reset_index()
dept_avg_salary.columns = ['部门', '平均工资']

# 员工销售业绩汇总
sales_performance = df_sales.groupby('员工ID').agg(
    订单数量=('订单ID', 'count'),
    总销售额=('销售金额', 'sum'),
    平均订单金额=('销售金额', 'mean')
).reset_index()

# 合并员工信息和销售业绩
df_merged = pd.merge(df_employees, sales_performance, on='员工ID', how='left')

# 按季度统计销售额
quarterly_sales = df_sales.groupby('季度')['销售金额'].sum().reset_index()
quarterly_sales.columns = ['季度', '季度销售额']

# ==============================================
# 4. 数据可视化准备
# ==============================================

# 创建数据透视表
pivot_table = pd.pivot_table(df_sales, 
                            values='销售金额', 
                            index='产品类别', 
                            columns='季度', 
                            aggfunc='sum',
                            fill_value=0)

# ==============================================
# 5. 输出到Excel文件（带格式和图表）
# ==============================================

with pd.ExcelWriter('公司数据分析报告.xlsx', engine='xlsxwriter') as writer:
    # 5.1 写入员工数据
    df_employees.to_excel(writer, sheet_name='员工信息', index=False)
    
    # 5.2 写入销售数据
    df_sales.to_excel(writer, sheet_name='销售记录', index=False)
    
    # 5.3 写入分析结果
    dept_avg_salary.to_excel(writer, sheet_name='部门分析', index=False)
    df_merged.to_excel(writer, sheet_name='员工绩效', index=False)
    quarterly_sales.to_excel(writer, sheet_name='季度销售', index=False)
    pivot_table.to_excel(writer, sheet_name='产品季度销售')
    
    # 获取工作簿和工作表对象
    workbook = writer.book
    
    # 5.4 设置格式
    ## 定义格式
    header_format = workbook.add_format({
        'bold': True,
        'text_wrap': True,
        'valign': 'top',
        'fg_color': '#4F81BD',
        'font_color': 'white',
        'border': 1
    })
    
    money_format = workbook.add_format({'num_format': '¥#,##0'})
    date_format = workbook.add_format({'num_format': 'yyyy-mm-dd'})
    
    ## 应用到员工信息表
    worksheet_emp = writer.sheets['员工信息']
    for col_num, value in enumerate(df_employees.columns.values):
        worksheet_emp.write(0, col_num, value, header_format)
    
    # 设置列宽和数字格式
    worksheet_emp.set_column('A:A', 10)
    worksheet_emp.set_column('B:B', 8)
    worksheet_emp.set_column('C:C', 12)
    worksheet_emp.set_column('D:D', 12, date_format)
    worksheet_emp.set_column('E:G', 10, money_format)
    worksheet_emp.set_column('H:H', 10, money_format)
    worksheet_emp.set_column('I:I', 8)
    
    # 5.5 添加图表
    ## 部门平均工资图表
    worksheet_dept = writer.sheets['部门分析']
    
    chart_dept = workbook.add_chart({'type': 'column'})
    chart_dept.add_series({
        'categories': '=部门分析!$A$2:$A$' + str(len(dept_avg_salary)+1),
        'values':     '=部门分析!$B$2:$B$' + str(len(dept_avg_salary)+1),
        'name':       '平均工资',
        'data_labels': {'value': True, 'num_format': '¥#,##0'}
    })
    chart_dept.set_title({'name': '各部门平均工资对比'})
    chart_dept.set_y_axis({'num_format': '¥#,##0'})
    worksheet_dept.insert_chart('D2', chart_dept)
    
    ## 季度销售趋势图
    worksheet_qsales = writer.sheets['季度销售']
    
    chart_sales = workbook.add_chart({'type': 'line'})
    chart_sales.add_series({
        'categories': '=季度销售!$A$2:$A$' + str(len(quarterly_sales)+1),
        'values':     '=季度销售!$B$2:$B$' + str(len(quarterly_sales)+1),
        'name':       '季度销售额',
        'data_labels': {'value': True, 'num_format': '¥#,##0'}
    })
    chart_sales.set_title({'name': '季度销售趋势'})
    chart_sales.set_y_axis({'num_format': '¥#,##0'})
    worksheet_qsales.insert_chart('D2', chart_sales)
    
    # 5.6 添加条件格式
    ## 在员工绩效表中高亮显示高销售额
    worksheet_perf = writer.sheets['员工绩效']
    
    # 设置条件格式 - 数据条
    worksheet_perf.conditional_format(
        'H3:H' + str(len(df_merged)+2),
        {
            'type': 'data_bar',
            'bar_color': '#63C384',
            'bar_solid': True
        }
    )
    
    # 设置条件格式 - 色阶
    worksheet_perf.conditional_format(
        'I3:I' + str(len(df_merged)+2),
        {
            'type': '2_color_scale',
            'min_color': '#F8696B',
            'max_color': '#63BE7B'
        }
    )

# ==============================================
# 6. 完成提示
# ==============================================

print("公司数据分析报告已生成: 公司数据分析报告.xlsx")
print("包含以下工作表:")
print("- 员工信息: 基础员工数据")
print("- 销售记录: 详细销售数据")
print("- 部门分析: 部门平均工资及图表")
print("- 员工绩效: 员工销售绩效分析")
print("- 季度销售: 按季度销售趋势及图表")
print("- 产品季度销售: 产品类别季度销售透视表")