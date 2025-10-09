import sqlite3
from pathlib import Path

class DatabaseManager:
    def __init__(self):
        self.path = (Path(__file__).parent.parent / "data" / "unmannedDrivingOperationDatabase.db")
        self.connection = self.create_connection()
        self.cursor = self.connection.cursor()
        self.create_tables()

        

    def create_connection(self):
        conn = None
        try:
            conn = sqlite3.connect(self.path)
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
        # 车辆数据表包含车辆编号,车辆类型,车辆IP,车辆载重,teamviewer密码，VNC密码，是否可用
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS vehicle_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    vehicle_number INTEGER NOT NULL,
                    vehicle_type TEXT NOT NULL,
                    vehicle_ip TEXT NOT NULL,
                    vehicle_load_capacity TEXT NOT NULL DEFAULT '0',
                    vehicle_teamviewer_password TEXT NOT NULL DEFAULT '',
                    vehicle_vnc_password TEXT NOT NULL DEFAULT '',
                    vehicle_available BOOLEAN NOT NULL DEFAULT 1
                )
            ''')
            self.connection.commit()
            print("Table 'vehicle_data' created successfully")
        except sqlite3.Error as e:
            print(f"Error creating table: {e}")
            
        # 创建车辆记录表
        # 车辆记录表包含车辆编号、日期、铲斗ID、车辆状态、故障类型，车辆工作时长,车辆产量,车辆停放位置和班次
        # 日期格式为YYYY-MM-DD，默认值为当前日期
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS vehicle_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    vehicle_number INTEGER NOT NULL,
                    date TEXT NOT NULL DEFAULT CURRENT_DATE,
                    shovel_id TEXT NOT NULL DEFAULT '待令',
                    vehicle_status TEXT NOT NULL DEFAULT '正常',
                    vehicle_fault_type TEXT DEFAULT '待确认',
                    vehicle_fault_description TEXT DEFAULT '无',
                    vehicle_fault_solution TEXT DEFAULT '无',
                    vehicle_fault_duration REAL DEFAULT 0.0,
                    vehicle_operating_hours REAL NOT NULL DEFAULT 0.0,
                    vehicle_production REAL NOT NULL DEFAULT 0.0,
                    vehicle_parking_location TEXT DEFAULT '待确认',
                    shift TEXT NOT NULL DEFAULT '一班' CHECK(shift IN ('一班', '二班', '三班'))
                )
            ''')
            self.connection.commit()
            print("Table 'vehicle_records' created successfully")
        except sqlite3.Error as e:
            print(f"Error creating table: {e}")
        
        # 创建班次记录表
        # 班次记录表包含日期，班次，使用电铲，车数，产量，月累计产量，月计划，年度累计运行时间，年度累计拉运车数，
        # 年度累计产量,工长,装载区情况，运输区情况，卸载区情况，备停区情况，车辆情况，其他事项        
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS shift_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL DEFAULT CURRENT_DATE,
                    shift TEXT NOT NULL CHECK(shift IN ('一班', '二班', '三班')),
                    shovel_id TEXT,
                    vehicle_count INTEGER NOT NULL DEFAULT 0,
                    production REAL NOT NULL DEFAULT 0.0,
                    monthly_accumulated_production REAL NOT NULL DEFAULT 0.0,
                    monthly_plan REAL NOT NULL DEFAULT 0.0,
                    yearly_accumulated_operating_time REAL NOT NULL DEFAULT 0.0,
                    yearly_accumulated_vehicle_count INTEGER NOT NULL DEFAULT 0,
                    yearly_accumulated_production REAL NOT NULL DEFAULT 0.0,
                    foreman TEXT NOT NULL DEFAULT '无',
                    loading_area_status TEXT DEFAULT '无',
                    transportation_area_status TEXT DEFAULT '无',
                    unloading_area_status TEXT DEFAULT '无',
                    standby_area_status TEXT DEFAULT '无',
                    vehicle_status TEXT DEFAULT '无',
                    other_matters TEXT DEFAULT '无'
                )
            ''')
            self.connection.commit()
            print("Table 'shift_records' created successfully")
        except sqlite3.Error as e:
            print(f"Error creating table: {e}")

    # 插入车辆数据
    # 车辆数据包含车辆编号、车辆类型、车辆IP,teamviewer密码，VNC密码和载重
    def insert_vehicle_data(self, vehicle_number, vehicle_type="unkonwn", vehicle_ip="unkonwn", vehicle_load_capacity=0, 
                            vehicle_teamviewer_password="unkonwn", vehicle_vnc_password="unkonwn", vehicle_available=True):
        existing_vehicle = self.get_vehicle_data(vehicle_number=vehicle_number)
        if existing_vehicle:
            print(f"Vehicle {vehicle_number} already exists.")
            return
        try:
            self.cursor.execute('''
                INSERT INTO vehicle_data (vehicle_number, vehicle_type, vehicle_ip, vehicle_load_capacity, vehicle_teamviewer_password, vehicle_vnc_password, vehicle_available)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (vehicle_number, vehicle_type, vehicle_ip, vehicle_load_capacity, vehicle_teamviewer_password, vehicle_vnc_password, vehicle_available))
            self.connection.commit()
            print("Vehicle data inserted successfully")
        except sqlite3.Error as e:
            print(f"Error inserting vehicle data: {e}")
    
    # 插入车辆记录
    # 车辆记录包含车辆编号、日期、铲斗ID、车辆状态、车辆工作时长、车辆产量和班次
    def insert_vehicle_record(self, vehicle_number, date, shovel_id=None, vehicle_status=None, vehicle_fault_type=None, vehicle_fault_description=None, 
                              vehicle_fault_solution=None, vehicle_fault_duration=0, vehicle_operating_hours=0, vehicle_production=0, vehicle_parking_location=None, shift="一班"):
        existing_record = self.get_vehicle_records(vehicle_number=vehicle_number, date=date, shift=shift)
        if existing_record:
            print(f"Record for vehicle {vehicle_number} on {date} for shift {shift} already exists.")
            self.update_vehicle_record(vehicle_number=vehicle_number, date=date, shift=shift, vehicle_status=vehicle_status, shovel_id=shovel_id, vehicle_fault_type=vehicle_fault_type, vehicle_fault_description=vehicle_fault_description,
                                        vehicle_fault_duration=vehicle_fault_duration, vehicle_operating_hours=vehicle_operating_hours, vehicle_production=vehicle_production)
            return
        try:
            #先判断内容是否为空，为空则不插入对应项
            insert_fields = {         
                "vehicle_number": vehicle_number,
                "shovel_id": shovel_id,
                "date": date,
                "vehicle_status": vehicle_status,
                "vehicle_fault_type": vehicle_fault_type,
                "vehicle_fault_description": vehicle_fault_description,
                "vehicle_fault_solution": vehicle_fault_solution,
                "vehicle_fault_duration": vehicle_fault_duration,
                "vehicle_operating_hours": vehicle_operating_hours,
                "vehicle_production": vehicle_production,
                "vehicle_parking_location": vehicle_parking_location,
                "shift": shift
            }
            # 过滤掉None值
            insert_data = {k: v for k, v in insert_fields.items() if v is not None}
            columns = ', '.join(insert_data.keys())
            placeholders = ', '.join(['?'] * len(insert_data))
            self.cursor.execute(f'''
                INSERT INTO vehicle_records ({columns})
                VALUES ({placeholders})
                ''', tuple(insert_data.values()))
            self.connection.commit()
            print("Vehicle record inserted successfully")
        except sqlite3.Error as e:
            print(f"Error inserting vehicle record: {e}")
    
    # 插入班次记录
    def insert_shift_record(self, date, shift, shovel_id, vehicle_count = 0, production = 0.0, 
                            monthly_accumulated_production = 0.0, monthly_plan = 0.0, yearly_accumulated_operating_time = 0.0, 
                            yearly_accumulated_vehicle_count = 0, yearly_accumulated_production = 0.0, foreman="无",
                            loading_area_status="无", transportation_area_status="无", unloading_area_status="无", 
                            standby_area_status="无", vehicle_status="无", other_matters="无"):
        existing_record = self.get_shift_records(date=date, shift=shift, shovel_id=shovel_id)
        if existing_record:
            print(f"Shift record for {date} {shift}  {shovel_id} already exists.")
            self.update_shift_record(date=date, shift=shift, shovel_id=shovel_id,
                                     vehicle_count=vehicle_count, production=production, 
                                     monthly_accumulated_production=monthly_accumulated_production,
                                     monthly_plan=monthly_plan,
                                     yearly_accumulated_production=yearly_accumulated_production,
                                     yearly_accumulated_operating_time=yearly_accumulated_operating_time,
                                     yearly_accumulated_vehicle_count=yearly_accumulated_vehicle_count,
                                     foreman=foreman,
                                     loading_area_status=loading_area_status,
                                     transportation_area_status=transportation_area_status,
                                     unloading_area_status=unloading_area_status,
                                     standby_area_status=standby_area_status,
                                     vehicle_status=vehicle_status,
                                     other_matters=other_matters)
            return
        try:
            self.cursor.execute('''
                INSERT INTO shift_records (date, shift, shovel_id, vehicle_count, production, 
                monthly_accumulated_production, monthly_plan, yearly_accumulated_operating_time,
                yearly_accumulated_vehicle_count, yearly_accumulated_production, foreman,
                loading_area_status, transportation_area_status, unloading_area_status, standby_area_status,
                vehicle_status, other_matters)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (date, shift, shovel_id, vehicle_count, production, monthly_accumulated_production, monthly_plan, yearly_accumulated_operating_time, yearly_accumulated_vehicle_count, yearly_accumulated_production, foreman, loading_area_status, transportation_area_status, unloading_area_status, standby_area_status, vehicle_status, other_matters))
            self.connection.commit()
            print("Shift record inserted successfully")
        except sqlite3.Error as e:
            print(f"Error inserting shift record: {e}")
    
    #获取车辆数据
    # 返回指定指定条件的的车辆数据，可选条件有车辆编号、车辆类型、是否可用
    def get_vehicle_data(self, vehicle_number=None, vehicle_type=None, vehicle_available=None):
        query = "SELECT * FROM vehicle_data WHERE 1=1"
        params = []
        
        if vehicle_number is not None:
            query += " AND vehicle_number = ?"
            params.append(vehicle_number)
        
        if vehicle_type is not None:
            query += " AND vehicle_type = ?"
            params.append(vehicle_type)
        if vehicle_available is not None:
            query += " AND vehicle_available = ?"
            params.append(vehicle_available)
        try:
            self.cursor.execute(query, tuple(params))
            rows = self.cursor.fetchall()
            # 转换为字典列表（更易处理）
            vehicles = []
            for row in rows:
                vehicle = {
                    'id': row[0],
                    'vehicle_number': row[1],
                    'vehicle_type': row[2],
                    'vehicle_ip': row[3],
                    'vehicle_load_capacity': row[4],
                    'vehicle_teamviewer_password':row[5],
                    'vehicle_vnc_password':row[6],
                    'vehicle_available': row[7]
                }
                vehicles.append(vehicle)
            return vehicles
        except sqlite3.Error as e:
            print(f"Error fetching vehicle data: {e}")
            return None
        
    #获取车辆记录
    # 返回指定条件的车辆记录，可选条件有车辆编号、日期、铲斗ID、车辆状态
    def get_vehicle_records(self, vehicle_number=None, date=None, shovel_id=None, vehicle_status=None, 
                            vehicle_fault_type=None, vehicle_fault_description=None, shift=None):
        query = "SELECT * FROM vehicle_records WHERE 1=1"
        params = []
        
        if vehicle_number is not None:
            query += " AND vehicle_number = ?"
            params.append(vehicle_number)
        
        if date is not None:
            query += " AND date = ?"
            params.append(date)
        
        if shovel_id is not None:
            query += " AND shovel_id = ?"
            params.append(shovel_id)
        
        if vehicle_status is not None:
            query += " AND vehicle_status = ?"
            params.append(vehicle_status)

        if vehicle_fault_type is not None:
            query += " AND vehicle_fault_type = ?"
            params.append(vehicle_fault_type)

        if vehicle_fault_description is not None:
            query += " AND vehicle_fault_description = ?"
            params.append(vehicle_fault_description)

        if shift is not None:
            query += " AND shift = ?"
            params.append(shift)

        try:
            self.cursor.execute(query, tuple(params))
            rows = self.cursor.fetchall()
            # 转换为字典列表（更易处理）
            vehicles = []
            for row in rows:
                vehicle = {
                    'id': row[0],
                    'vehicle_number': row[1],
                    'shovel_id': row[2],
                    'date': row[3],
                    'vehicle_status': row[4],
                    'vehicle_fault_type': row[5],
                    'vehicle_fault_description': row[6],
                    'vehicle_fault_solution': row[7],
                    'vehicle_fault_duration': row[8],
                    'vehicle_operating_hours': row[9],
                    'vehicle_production': row[10],
                    'vehicle_parking_location': row[11],
                    'shift': row[12]
                }
                vehicles.append(vehicle)
            return vehicles
        except sqlite3.Error as e:
            print(f"Error fetching vehicle records: {e}")
            return []


    # 获取最新车辆记录,查询可用条件为车辆编号，电铲id，停放位置
    def get_vehicle_lastestrecord(self, type=None, vehicle_number=None, shovel_id=None, vehicle_parking_location=None):
        query = "SELECT * FROM vehicle_records WHERE 1=1"
        params = []
        if type is not None:
            query += " AND vehicle_status = ?"
            params.append(type)
        if vehicle_number is not None:
            query += " AND vehicle_number = ?"
            params.append(vehicle_number)
        if shovel_id is not None:
            query += " AND shovel_id = ?"
            params.append(shovel_id)
        if vehicle_parking_location is not None:
            query += " AND vehicle_parking_location = ?"
            params.append(vehicle_parking_location)
        query += " ORDER BY id DESC LIMIT 1"
        try:
            self.cursor.execute(query, tuple(params))
            row = self.cursor.fetchone()
            if row:
                vehicle = {
                    'id': row[0],
                    'vehicle_number': row[1],
                    'shovel_id': row[2],
                    'date': row[3],
                    'vehicle_status': row[4],
                    'vehicle_fault_type': row[5],
                    'vehicle_fault_description': row[6],
                    'vehicle_fault_solution': row[7],
                    'vehicle_fault_duration': row[8],
                    'vehicle_operating_hours': row[9],
                    'vehicle_production': row[10],
                    'vehicle_parking_location': row[11],
                    'shift': row[12]
                }
                return vehicle
        except sqlite3.Error as e:
            print(f"Error fetching vehicle records: {e}")
            return []

    #获取班次记录
    # 返回指定条件的班次记录，可选条件有日期、班次、铲斗ID,工长
    def get_shift_records(self, date=None, shift=None, shovel_id=None, foreman=None):
        query = "SELECT * FROM shift_records WHERE 1=1"
        params = []
        
        if date is not None:
            query += " AND date = ?"
            params.append(date)
        
        if shift is not None:
            query += " AND shift = ?"
            params.append(shift)
        
        if shovel_id is not None:
            query += " AND shovel_id = ?"
            params.append(shovel_id)
            
        if foreman is not None:
            query += " AND foreman = ?"
            params.append(foreman)
        
        try:
            self.cursor.execute(query, tuple(params))
            rows = self.cursor.fetchall()
            # 转换为字典列表（更易处理）
            shifts = []
            for row in rows:
                shift_record = {
                    'id': row[0],
                    'date': row[1],
                    'shift': row[2],
                    'shovel_id': row[3],
                    'vehicle_count': row[4],
                    'production': row[5],
                    'monthly_accumulated_production': row[6],
                    'monthly_plan': row[7],
                    'yearly_accumulated_operating_time': row[8],
                    'yearly_accumulated_vehicle_count': row[9],
                    'yearly_accumulated_production': row[10],
                    'foreman': row[11]
                }
                shifts.append(shift_record)
            return shifts
        except sqlite3.Error as e:
            print(f"Error fetching shift records: {e}")
            return []
    
    # 更新车辆记录
    def update_vehicle_record(self, vehicle_number, date, shift, vehicle_status=None, shovel_id=None, vehicle_fault_type=None, vehicle_fault_description=None, 
                              vehicle_fault_duration=None, vehicle_operating_hours=None, vehicle_production=None):
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
        existing_record = self.get_vehicle_records(vehicle_number=vehicle_number, date=date, shift=shift)
        if not existing_record:
            print(f"没有找到车辆 {vehicle_number} 在 {shift} 班次的记录")
            return False
        update_fields = {
            'vehicle_fault_type': vehicle_fault_type,
            'vehicle_fault_description': vehicle_fault_description,
            'vehicle_fault_duration': vehicle_fault_duration,
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
           
            params = list(update_data.values())
            # 将记录ID添加到参数列表中
            params.append(vehicle_number)  # 添加车辆编号作为WHERE条件
            params.append(shift)  # 添加班次作为WHERE条件
            # 构建完整的UPDATE语句
            # 例如: UPDATE vehicle_records SET status = ?, production = ? WHERE vehicle_number = ? AND date = ? AND shift = ?
            query = f"UPDATE vehicle_records SET {set_clause} WHERE vehicle_number = ? AND date = ? AND shift = ?"

            self.cursor.execute(query, tuple(params))
            self.connection.commit()
            
            if self.cursor.rowcount == 0:
                print("警告: 没有找到记录")
                return False

            print("成功更新记录")
            return True
            
        except sqlite3.Error as e:
            print(f"数据库错误: {e}")
            self.connection.rollback()
            return False
        
    # 更新车辆数据
    def update_vehicle_data(self, vehicle_number, vehicle_type=None, vehicle_ip=None, vehicle_load_capacity=None, vehicle_teamviewer_password=None, vehicle_vnc_password=None, vehicle_available=None):
        """
        Args:
        vehicle_number (int): 车辆编号
        vehicle_type (str, optional): 车辆类型. Defaults to None.
        vehicle_ip (str, optional): 车辆IP. Defaults to None.
        load_capacity (int, optional): 载重. Defaults to None.
        
        Returns:
            bool: 更新是否成功
        """
        existing_vehicle = self.get_vehicle_data(vehicle_number=vehicle_number)
        if not existing_vehicle:
            print(f"没有找到车辆 {vehicle_number} 的记录")
            return False

        update_fields = {
            'vehicle_type': vehicle_type,
            'vehicle_ip': vehicle_ip,
            'vehicle_load_capacity': vehicle_load_capacity,
            'vehicle_teamviewer_password': vehicle_teamviewer_password,
            'vehicle_vnc_password': vehicle_vnc_password,
            'vehicle_available': vehicle_available,
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
    
    # 更新班次记录
    def update_shift_record(self, date, shift, shovel_id, vehicle_count=None,
                            production=None, monthly_accumulated_production=None, monthly_plan=None,
                            yearly_accumulated_operating_time=None, yearly_accumulated_vehicle_count=None,
                            yearly_accumulated_production=None, foreman=None,
                            loading_area_status=None, transportation_area_status=None, unloading_area_status=None,
                            standby_area_status=None, vehicle_status=None, other_matters=None):
        """
        更新班次记录
        """
        existing_record = self.get_shift_records(date=date, shift=shift, shovel_id=shovel_id)
        if not existing_record:
            print(f"没有找到 {date} {shift} {shovel_id} 的班次记录")
            return False

        update_fields = {
            'vehicle_count': vehicle_count,
            'production': production,
            'monthly_accumulated_production': monthly_accumulated_production,
            'monthly_plan': monthly_plan,
            'yearly_accumulated_operating_time': yearly_accumulated_operating_time,
            'yearly_accumulated_vehicle_count': yearly_accumulated_vehicle_count,
            'yearly_accumulated_production': yearly_accumulated_production,
            'foreman': foreman,
            'loading_area_status': loading_area_status,
            'transportation_area_status': transportation_area_status,
            'unloading_area_status': unloading_area_status,
            'standby_area_status': standby_area_status,
            'vehicle_status': vehicle_status,
            'other_matters': other_matters
        }
        
        update_data = {k: v for k, v in update_fields.items() if v is not None}
        
        if not update_data:
            print("警告: 没有提供任何更新字段")
            return False

        try: 
            set_clause = ', '.join([f"{field} = ?" for field in update_data.keys()])
            params = list(update_data.values())
            params.append(date)  # 添加日期作为WHERE条件
            params.append(shift)  # 添加班次作为WHERE条件
            params.append(shovel_id)  # 添加铲斗ID作为WHERE条件
            query = f"UPDATE shift_records SET {set_clause} WHERE date = ? AND shift = ? AND shovel_id = ?"
            
            self.cursor.execute(query, tuple(params))
            self.connection.commit()
            
            if self.cursor.rowcount == 0:
                print(f"警告: 没有找到 {date} {shift} {shovel_id} 的班次记录")
                return False
                
            print(f"成功更新 {date} {shift} {shovel_id} 的班次记录")
            return True
            
        except sqlite3.Error as e:
            print(f"数据库错误: {e}")
            self.connection.rollback()
            return False
    
    # 移除车辆数据
    def delete_vehicle_data(self, vehicle_number):
        existing_vehicle = self.get_vehicle_data(vehicle_number=vehicle_number)
        if not existing_vehicle:
            print(f"没有找到车辆 {vehicle_number} 的记录")
            return False

        try:
            self.cursor.execute("DELETE FROM vehicle_data WHERE vehicle_number = ?", (vehicle_number,))
            self.connection.commit()
        except sqlite3.Error as e:
            print(f"Error delete vehicle data: {e}")
            return False
        
    # 移除车辆记录
    def delete_vehicle_record(self, vehicle_number, date, shift):
        existing_record = self.get_vehicle_records(vehicle_number=vehicle_number, date=date, shift=shift)
        if not existing_record:
            print(f"没有找到车辆 {vehicle_number} 在 {shift} 班次的记录")
            return False
        try:
            self.cursor.execute("DELETE FROM vehicle_records WHERE vehicle_number = ? AND date = ? AND shift = ?", (vehicle_number, date, shift))
            self.connection.commit()
        except sqlite3.Error as e:
            print(f"Error delete vehicle record: {e}")
            return False
     
    # 移除班次记录
    def delete_shift_record(self, date, shift, shovel_id):
        existing_record = self.get_shift_records(date=date, shift=shift, shovel_id=shovel_id)
        if not existing_record:
            print(f"没有找到 {date} {shift} {shovel_id} 的班次记录")
            return False
        try:
            self.cursor.execute("DELETE FROM shift_records WHERE date = ? AND shift = ? AND shovel_id = ?", (date, shift, shovel_id))
            self.connection.commit()
        except sqlite3.Error as e:
            print(f"Error delete shift record: {e}")
            return False   