import sqlite3
class DatabaseManager:
    def __init__(self, db_file):
        self.connection = self.create_connection("../data/unmannedDrivingOperationDatabase.db")
        self.cursor = self.connection.cursor()
        self.create_tables()

        

    def create_connection(self, db_file):
        conn = None
        try:
            conn = sqlite3.connect(db_file)
            print("Connection established")
        except Error as e:
            print(e)
        return conn

    def close_connection(self):
        if self.connection:
            self.connection.close()
            print("Connection closed")
    
    def create_tables(self):
        
        # 创建车辆数据表
        # 车辆数据表包含车辆编号,车辆类型,车辆IP,车辆载重
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS vehicle_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    vehicle_number INTEGER NOT NULL,
                    vehicle_type TEXT NOT NULL,
                    vehicle_ip TEXT NOT NULL,
                    vehicle_load_capacity INTEGER NOT NULL DEFAULT 0
                )
            ''')
            self.connection.commit()
            print("Table 'vehicle_data' created successfully")
        except sqlite3.Error as e:
            print(f"Error creating table: {e}")
            
        # 创建车辆记录表
        # 车辆记录表包含车辆编号、日期、铲斗ID、车辆状态、车辆工作时长车辆产量和班次
        # 日期格式为YYYY-MM-DD，默认值为当前日期
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS vehicle_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    vehicle_number INTEGER NOT NULL,
                    date TEXT NOT NULL DEFAULT (strftime('%Y-%m-%d', 'now', 'localtime')),
                    shovel_id TEXT,
                    vehicle_status TEXT NOT NULL DEFAULT '待令',
                    vehicle_operating_hours REAL NOT NULL DEFAULT 0.0,
                    vehicle_production REAL NOT NULL DEFAULT 0.0,
                    shift TEXT NOT NULL DEFAULT CHECKED('一班', '二班', '三班'),
                )
            ''')
            self.connection.commit()
            print("Table 'vehicle_records' created successfully")
        except sqlite3.Error as e:
            print(f"Error creating table: {e}")
               
    # 插入车辆数据
    # 车辆数据包含车辆编号、车辆类型、车辆IP和载重
    def insert_vehicle_data(self, vehicle_number, vehicle_type, vehicle_ip, load_capacity):
        try:
            self.cursor.execute('''
                INSERT INTO vehicle_data (vehicle_number, vehicle_type, vehicle_ip, vehicle_load_capacity)
                VALUES (?, ?, ?, ?)
            ''', (vehicle_number, vehicle_type, vehicle_ip, load_capacity))
            self.connection.commit()
            print("Vehicle data inserted successfully")
        except sqlite3.Error as e:
            print(f"Error inserting vehicle data: {e}")
    
    # 插入车辆记录
    # 车辆记录包含车辆编号、日期、铲斗ID、车辆状态、车辆工作时长、车辆产量和班次
    def insert_vehicle_record(self, vehicle_number, date, shovel_id, vehicle_status, vehicle_operating_hours, vehicle_production, shift):
        try:
            self.cursor.execute('''
                INSERT INTO vehicle_records (vehicle_number, shovel_id, date, vehicle_status, vehicle_operating_hours, vehicle_production, shift)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (vehicle_number, shovel_id, vehicle_status, vehicle_operating_hours, vehicle_production, shift))
            self.connection.commit()
            print("Vehicle record inserted successfully")
        except sqlite3.Error as e:
            print(f"Error inserting vehicle record: {e}")
    
    # 更新车辆记录
    # 允许更新车辆状态、铲斗id，车辆工作时长、车辆产量和班次
    def update_vehicle_record(self, record_id, vehicle_status=None, shovel_id=None, vehicle_operating_hours=None, vehicle_production=None):
        """
        Args:
        record_id (int): 要更新的记录ID
        vehicle_status (str, optional): 车辆状态. Defaults to None.
        shovel_id (str): 铲斗ID
        vehicle_operating_hours (float, optional): 运行时长. Defaults to None.
        vehicle_production (float, optional): 产量. Defaults to None.
        
        Returns:
            bool: 更新是否成功
        """
        # 检查是否有任何字段需要更新
        update_fields = {
            'status': vehicle_status,
            'shovel_id': shovel_id,
            'operating_hours': vehicle_operating_hours,
            'production': vehicle_production,
        }
        
        # 过滤掉None值
        update_data = {k: v for k, v in update_fields.items() if v is not None}
        
        if not update_data:
            print("警告: 没有提供任何更新字段")
            return False

        try:
            # 构建SET子句
            # 例如，如果更新了status和production, set_clause 会是 "status = ?, production = ?"
            # 这将用于SQL UPDATE语句
            set_clause = ', '.join([f"{field} = ?" for field in update_data.keys()])
            # 构建参数列表
            # 例如，如果更新了status和production, params 会是 [new_status, new_production]
            # 还需要添加记录ID作为WHERE条件
            params = list(update_data.values())
            # 将记录ID添加到参数列表中
            params.append(record_id)  # 添加记录ID作为WHERE条件
            # 构建完整的UPDATE语句
            # 例如: UPDATE vehicle_records SET status = ?, production = ? WHERE id = ?
            query = f"UPDATE vehicle_records SET {set_clause} WHERE id = ?"
            
            self.cursor.execute(query, tuple(params))
            self.connection.commit()
            
            if self.cursor.rowcount == 0:
                print(f"警告: 没有找到ID为{record_id}的记录")
                return False
                
            print(f"成功更新ID为{record_id}的记录")
            return True
            
        except sqlite3.Error as e:
            print(f"数据库错误: {e}")
            self.connection.rollback()
            return False
        
    # 更新车辆数据
    # 允许更新车辆类型、车辆IP和载重
    def update_vehicle_data(self, vehicle_number, vehicle_type=None, vehicle_ip=None, load_capacity=None):
        """
        Args:
        vehicle_number (int): 车辆编号
        vehicle_type (str, optional): 车辆类型. Defaults to None.
        vehicle_ip (str, optional): 车辆IP. Defaults to None.
        load_capacity (int, optional): 载重. Defaults to None.
        
        Returns:
            bool: 更新是否成功
        """
        update_fields = {
            'vehicle_type': vehicle_type,
            'vehicle_ip': vehicle_ip,
            'vehicle_load_capacity': load_capacity,
        }
        
        update_data = {k: v for k, v in update_fields.items() if v is not None}
        
        if not update_data:
            print("警告: 没有提供任何更新字段")
            return False

        try:
            set_clause = ', '.join([f"{field} = ?" for field in update_data.keys()])
            params = list(update_data.values())
            params.append(vehicle_number)  # 添加车辆编号作为WHERE条件
            query = f"UPDATE vehicle_data SET {set_clause} WHERE vehicle_number = ?"
            
            self.cursor.execute(query, tuple(params))
            self.connection.commit()
            
            if self.cursor.rowcount == 0:
                print(f"警告: 没有找到车辆编号为{vehicle_number}的记录")
                return False
                
            print(f"成功更新车辆编号为{vehicle_number}的记录")
            return True
            
        except sqlite3.Error as e:
            print(f"数据库错误: {e}")
            self.connection.rollback()
            return False