import mysql.connector, json, random
from datetime import datetime, timedelta

def connect():
    
    with open("db_creds.json") as f:
        db_cr = json.load(f)

    db = mysql.connector.connect(
        host=db_cr["host"],
        user=db_cr["username"],
        passwd=db_cr["password"],
        database=db_cr["dbname"],
        port=db_cr["port"],
    )

    return db, db.cursor()

def create_database():
    
    db,c = connect()
    
    with open('create_db.sql') as f:
        query = f.read()
        
    (query.split('\n'))
        
    c.execute(query, multi=True)

    db.commit()

def get_subdept(ide):
    
    db,c = connect(); c.execute('SELECT * FROM sub_department WHERE id=%s', [ide]); return Department(c.fetchall()[0][0])
    
def create_title(name):
    db,c = connect()
    
    try:
        c.execute("INSERT INTO titles (name) VALUES (%s)", [name])
    except Exception as e:
        (f'Error: {e}')
    
    db.commit()

def get_all_titles():
    
    db,c = connect()
    
    c.execute("SELECT * FROM titles")
    
    return [f[1] for f in c.fetchall()]

def create_dept(name):

    db,c = connect()
    
    try:
        c.execute("INSERT INTO sub_department (name) VALUES (%s)", [name])
    except Exception as e:
        (f'Error: {e}')
    
    db.commit()

def get_random_date():
    
    db,c = connect()
    
    c.execute("SELECT name FROM programs")
    
    return c.fetchall()[0][0]

def get_random_program():
    
    return [
        {
            'monday': (get_random_date(), ''),
            'tuesday': (get_random_date(), ''),
            'wednesday': (get_random_date(), ''),
            'thursday': (get_random_date(), ''),
            'friday': (get_random_date(), ''),
            'saturday': (get_random_date(), ''),
            'sunday': (get_random_date(), ''),
        }
    ]
    
def get_current_week():
    today = datetime.today()

    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    
    monday_date = start_of_week.strftime('%Y-%m-%d')
    sunday_date = end_of_week.strftime('%Y-%m-%d')

    return f'({monday_date} - {sunday_date})'    

def get_all_departments(get_id=True):
    db,c = connect()
    
    c.execute('SELECT id, name FROM sub_department')
    
    if get_id:
        return [(f[0], f[1]) for f in c.fetchall()]
    return [f[1] for f in c.fetchall()]

def get_next_weeks(n=4):
    # Get today's date
    today = datetime.today()
    
    # Initialize a list to store week ranges
    week_ranges = []
    
    for i in range(n):
        # Calculate the start (Monday) and end (Sunday) of each week
        start_of_week = today - timedelta(days=today.weekday()) + timedelta(weeks=i)
        end_of_week = start_of_week + timedelta(days=6)
        
        # Format the dates as strings
        monday_date = start_of_week.strftime('%Y-%m-%d')
        sunday_date = end_of_week.strftime('%Y-%m-%d')
        
        # Add the formatted string to the list
        week_ranges.append(f'({monday_date} - {sunday_date})')
    
    return week_ranges

def add_program(name:str):
    
    db,c = connect()
    
    c.execute("INSERT INTO programs (name) VALUES (%s)", [name])
    db.commit()

def get_all_programs():
    db,c = connect()
    
    c.execute("SELECT * FROM programs")
    
    return [f[1] for f in c.fetchall()]

class Employee:
    
    @staticmethod
    def create_employee(name, title, def_dep):
        
        db,c = connect()
        
        c.execute("INSERT INTO employees (name, title, default_dep) VALUES (%s,%s,%s)", [name, title, def_dep])
        db.commit()
        
        c.execute('SELECT * FROM employees WHERE name=%s', [name])
        
        return Employee(c.fetchall()[0][0])
    
    @staticmethod 
    def get_id_by_name(name):
        
        db,c = connect()
        
        c.execute("SELECT id FROM employees WHERE name =%s", [name])
        
        return c.fetchall()[0][0]
    
    @staticmethod
    def get_all_employees():
        
        db,c = connect()
        
        c.execute("SELECT id FROM employees")
        
        return [Employee(id[0]) for id in c.fetchall()]
    
    def __init__(self, idd) -> None:
        db,c = connect()
        
        self.id = idd
        
        c.execute("SELECT * FROM employees WHERE id=%s", [self.id])
        # (f"SELECT * FROM employee WHERE id={self.id}")
        f = c.fetchall()[0]
        self.raw = {
            'id' : self.id,
            'name' : f[1],
            'title' : f[2],
            'default_dep' : f[3]
        }
        
        
        self.title = self.raw['title']
        self.name = self.raw['name']
        
        
        self.prefered_dep = self.raw['default_dep'].split(' - ')
        self.prefered_dep_str = self.raw['default_dep']
        print(self.prefered_dep_str)
    
    def update(self, name, title, def_dep):
        
        db,c = connect()
        
        c.execute("UPDATE employees SET name=%s, title=%s, default_dep=%s WHERE id=%s", [name, title, def_dep, self.id])
        
        db.commit()
        
    def get_last_program(self, dic: dict):
        
        for kitchen in dic:
            for department in dic[kitchen]:
                for employee_id in department:
                    if str(employee_id)==str(self.id):
                        return department[employee_id][1]
        
        return get_random_program()
        
    def pass_to_department(self, department, program:dict):
        
        
        if program == '':
            program = get_random_program()
        if program== 'last_program':
            
            db,c = connect()
            
            c.execute("SELECT schedule_json FROM schedules ORDER BY id ASC")
            
            try:
                dic = json.loads(c.fetchall()[0][0].replace("'", '"'))
                program = self.get_last_program(dic)
                
                # print(program)
                
                
            except IndexError as e:
                program = get_random_program()
                # print(e)
            
            
        
        department.receive_employee(self, program)
        
    def __repr__(self) -> str:
        return f"{self.name}"
        
    def __eq__(self, other):
        if isinstance(other, Employee):
            return self.id == other.id
        return False

    def __hash__(self):
        return hash(self.id)
        
class Department:
    
    @staticmethod
    def get_all_departments():
        
        db,c = connect()
        
        c.execute("SELECT name, dep_ids FROM big_kitchens")
        
        departments = []
        
        kitchens = c.fetchall()
        
        for tup in kitchens:
            kitchen, department_ids = tup 
            
            department_ids = json.loads(department_ids.replace("'", '"'))
            
            for id in department_ids:
                dep = get_subdept(id)
                
                departments.append(f'{kitchen} - {dep.name}')
        
        return departments
               
    @staticmethod
    def get_id_from_name(name):
        db,c = connect()
        
        c.execute("SELECT id FROM sub_department WHERE name=%s", [name])
        
        try:
            
            return c.fetchall()[0][0]
        except IndexError:
            strings = name.split('%20')
            final_string = ''
            for stri in strings:
                final_string += stri + ' '
            final_string.strip()
            
            c.execute("SELECT id FROM sub_department WHERE name=%s", [final_string])
            f = c.fetchall()
            return f[0][0]
    
    def __init__(self, id):
        
        db,c = connect()
        
        self.id = id 
        
        c.execute("SELECT * FROM sub_department WHERE id=%s", [self.id])
        f = c.fetchall()[0]
        self.raw = {
            'id' : self.id,
            'name' : f[1]
        }
        
        self.name = self.raw['name']
        
        self.employees = []
        
    def receive_employee(self, employee, program):
        
        self.employees.append((employee, program))

    def remove_duplicates(self):
        unique_employees = {}
        for employee_tuple in self.employees:
            employee, dict_list = employee_tuple
            unique_employees[employee] = dict_list  # This will overwrite any previous entries with the same employee
        
        # Convert back to the required format
        self.employees = [(employee, dict_list) for employee, dict_list in unique_employees.items()]
    
    def update(self, name):
        
        db,c = connect()
        
        c.execute("UPDATE sub_department SET name=%s WHERE id = %s", [name, self.id])
        
        db.commit()

class Kitchen:
    
    @staticmethod
    def create_kitchen(name: str, dept_ids: list[str]):
        """"returns a Kitchen object"""
        
        db,c = connect()
        
        c.execute('INSERT INTO big_kitchens (name, dep_ids) VALUES (%s,%s)', [name, str(dept_ids)])
        
        db.commit()
        
        c.execute('SELECT id FROM big_kitchens WHERE name=%s', [name])
        
        return Kitchen(c.fetchall()[0][0])
    
    @staticmethod
    def get_all_kitchens():
        
        db,c = connect()
        
        c.execute("SELECT name FROM big_kitchens")
        
        return [f[0] for f in c.fetchall()]
    
    @staticmethod
    def get_id_from_name(name):
        
        db,c =connect()
        
        c.execute("SELECT id FROM big_kitchens WHERE name=%s", [name])
        
        f = c.fetchall()
        
        try:
            return f[0][0]
        except IndexError:
            strings = name.split('%20')
            final_string = ''
            for stri in strings:
                final_string += stri + ' '
            final_string.strip()
            
            c.execute("SELECT id FROM big_kitchens WHERE name=%s", [final_string])
            f = c.fetchall()
            return f[0][0]
            
    def __repr__(self) -> str:
        return f'Kitchen Object: {self.name}, #{self.id}'
    
    def __init__(self, id) -> None:
        db,c = connect()
        
        c.execute("SELECT * FROM big_kitchens WHERE id=%s", [id])
        f = c.fetchall()[0]
        self._raw = {
            'id' : id,
            'name' : f[1],
            'dep_ids': json.loads(f[2].replace("'", '"'))
        }
        
        self.id = id 
        
        self.sub_departments = []
        
        self.name = self._raw['name']

        
        for ide in self._raw['dep_ids']:
            self.sub_departments.append(get_subdept(ide))
            
    def update(self, new_name, departments):
        
        db,c = connect()
        
        c.execute("UPDATE big_kitchens SET name=%s, dep_ids=%s WHERE id=%s", [new_name, str(departments), self.id])
        
        db.commit()

class KitchenGroup:
    
    @staticmethod
    def get_all_weeks(week):
        
        db,c = connect()
        
        c.execute("SELECT week FROM schedules WHERE week=%s", [week])
        
        return c.fetchall()
    
    @staticmethod
    def get_saved_weeks():
        
        db,c = connect()
        
        c.execute("SELECT week FROM schedules")
        
        return c.fetchall()
    
    
    def __init__(self,week='') -> None:
        db,c = connect()
        
        self.week = week 
        
        c.execute('SELECT id FROM big_kitchens')
        self.sub_kitchens = [Kitchen(id[0]) for id in c.fetchall()]
        
        if self.week != '':
            
            c.execute('SELECT * FROM schedules WHERE week=%s', [week])
            
            if len((f := c.fetchall() )) > 0:
                self.load_schedule(f[0][2].replace("'", '"'))
                self.saved = True
            else:
                # self.set_employees_to_default()
                self.load_last_schedule()
                self.saved = False
            
            # ('empty')
            
    def get_all_employees(self):
        
        db,c = connect()
        
        c.execute('SELECT name FROM employees')
        
        return [f[0] for f in c.fetchall()]
            
    def load_last_schedule(self):
        db,c = connect()
        
        c.execute("SELECT schedule_json FROM schedules ORDER BY id DESC")
        
        f = c.fetchall()
        if len(f) < 1:
            self.set_employees_to_default()
            return 
        employees_added = self.load_schedule(f[0][0].replace("'", '"'))
        all_employees = self.get_all_employees()
        
        if len(employees_added) == all_employees:
            return
        else:
            not_added_employees = list(set(all_employees) - set(employees_added))
            
            for emp in not_added_employees:
                self.set_def_employee(Employee(Employee.get_id_by_name(emp)))
                 
    def get_unplaced_employees(self,):
        
        all_emps = Employee.get_all_employees()
        
        for kitchen in self.sub_kitchens:
            
            for dep in kitchen.sub_departments:
                
                for emp in all_emps:
                
                    if emp in dep.employees:
                        all_emps.remove(emp)
        
        return all_emps
        
    def set_employees_to_default(self):
        employees = Employee.get_all_employees()
        
        for employee in employees:
            self.set_def_employee(employee)
        
    def set_def_employee(self,emp:Employee):
        
        pref_dep_kitch,pref_dep = emp.prefered_dep
        
        dep = self.get_department_by_name(pref_dep.lower(), pref_dep_kitch.lower())
        
        emp.pass_to_department(dep, 'last_program')
            
    def set_week(self, week):
        
        self.week = week 
        c.execute('SELECT * FROM schedules WHERE week=%s', [week])
        
        if len((f := c.fetchall() )) > 0:
            self.load_schedule(f[0][2].replace("'", '"'))
            
    def get_all_employees_programs(self):

        return [emp for kitchen in self.sub_kitchens for dep in kitchen.sub_departments for emp in dep.employees]
    
    def get_split_days(self):
        
        days = set()
        
        for emp, program in self.get_all_employees_programs():
            
            for prog in program:
                
                for key in prog: 
                    
                    if prog[key][1] != '':
                        days.add(key.lower())
                        print(prog[key][1])
                    
                    
                        
        return list(days)
          
    def load_schedule(self, schedule_json):
        
        if self.week == '' == None:
            raise Exception('This Schedule doesnt have a week set to it. Please use `KitchenGroup.set_week()`')
        
        schedule_dict = schedule_json
        if not isinstance(schedule_json, dict):
        
            schedule_dict = json.loads(schedule_json)
        # (schedule_dict)
        
        emps_added = []
        
        for kitchen in schedule_dict:
            
            if kitchen=='week':
                continue
            
            for dept in schedule_dict[kitchen]:
                
                for emp in schedule_dict[kitchen][dept]:
                    
                    # print(emp[1])
                    if emp[0] == None:
                        continue
                    
                    if str(emp[0]).isnumeric():
                        (emp[0], 'numeric')
                        em = Employee(emp[0])
                    else:
                        (emp[0], 'name')
                        em = Employee(Employee.get_id_by_name(emp[0]))
                        
                    emps_added.append(em.name)
                    self.remove_employee_from_current_department(em)
                    # em.pass_to_department(self.get_department_by_name(dept, kitchen), emp[1])
                    self.get_department_by_name(dept, kitchen).employees.append((em, emp[1]))
        return emps_added

    def __repr__(self) -> str:
        txt = ''
        for kitchen in self.sub_kitchens:
            
            txt += f"{kitchen}, departments:" + '\n'
            
            for dep in kitchen.sub_departments:
                txt += f"{dep.name}, {dep.employees}" + '\n'
        return txt
    
    def get_department_by_name(self, name, kitch_hint=''):
        
        if kitch_hint == '':
            for kitch in self.sub_kitchens:
                
                
                for dep in kitch.sub_departments:
                    if dep.name.lower() == name.lower():
                        return dep
                
        for kitch in self.sub_kitchens:
            
            if kitch.name.lower() == kitch_hint.lower():
                
                for dep in kitch.sub_departments:
                    
                    if dep.name.lower() == name.lower():
                        return dep
                    
    def remove_employee_from_current_department(self, employee):
        
        for kitch in self.sub_kitchens:
            for dep in kitch.sub_departments:
                if employee in dep.employees:
                    dep.employees.remove(employee)
                    
    def remove_duplicates(self):
        
        for kitch in self.sub_kitchens:
            
            for dep in kitch.sub_departments:
                
                dep.remove_duplicates()
                    
    def save_schedule(self):
        
        schedule_json = {}
        
        self.remove_duplicates()
        
        for kitchen in self.sub_kitchens:
            
            schedule_json[kitchen.name] = {}
            
            for department in kitchen.sub_departments:
                
                schedule_json[kitchen.name][department.name] = []
                
                for employee, program in department.employees:
                    schedule_json[kitchen.name][department.name].append([employee.id, program])
                    
                    
        # (schedule_json)
                    
        db,c = connect()
        
        # (schedule_json)
        # 
        
        if len(KitchenGroup.get_all_weeks(self.week)) > 0:
            c.execute("UPDATE schedules SET schedule_json=%s WHERE week=%s", [str(schedule_json),self.week])
        else: 
            c.execute("INSERT INTO schedules (week, schedule_json) VALUES (%s, %s)", [self.week, str(schedule_json)])
            
        self.saved = True
        
        db.commit()
        
if __name__ == '__main__':
    
    db,c = connect()
    
    ('Connected to db')
    
    # while True:
    
    #     text = input('Enter Dept Name (empty to stop): ')
    #     create_dept(text) if text != '' else 0
        
    #     if text=='':
    #         break
    
    # dep_ids_list = []
    # while True:
    #     text = input('Enter Dept Id (empty to stop): ')
        
    #     dep_ids_list.append(text) if text != '' else 0
        
    #     if text == '':
    #         break
        
    # new_k = Kitchen.create_kitchen(input("Enter Kitchen Name: "), dep_ids_list)

    # (new_k) 
    
    k = KitchenGroup('2/7/2024')
        
    
    # employee = Employee(1)
    # employee.pass_to_department(k.get_department_by_name('Breakfast', 'Main Kitchen'), '6-12')
    
    # # employee2 = Employee.create_employee('Giorgos Kafantaris Junior', 'A Cook')
    # employee2 = Employee(2)
    # employee2.pass_to_department(k.get_department_by_name('Kitchen', 'Glass House Kitchen'), '6-12')
    
    # k.save_schedule()
    
    (k)