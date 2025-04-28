import mysql.connector, json, random
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask import flash, session
import mysql.connector.errors

USER_ID = None



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
    
    # print(ide)
    try:
        db,c = connect(); c.execute('SELECT * FROM sub_department WHERE id=%s', [ide]); return Department(c.fetchall()[0][0])
    except Exception as e:
        print('Error: ' , str(e))
    
def create_title(name):
    db,c = connect()
    
    try:
        c.execute("INSERT INTO titles (name,user_id) VALUES (%s,%s)", [name, USER_ID])
    except Exception as e:
        (f'Error: {e}')
    
    db.commit()

def get_all_titles(get_id=False):
    
    db,c = connect()
    
    c.execute("SELECT * FROM titles WHERE user_id=%s", [USER_ID])
    
    if get_id:
        return [(f[0],f[1]) for f in c.fetchall()]
        
    
    return [f[1] for f in c.fetchall()]

def create_dept(name):

    db,c = connect()
    
    try:
        c.execute("INSERT INTO sub_department (name, user_id) VALUES (%s,%s)", [name, USER_ID])
    except Exception as e:
        (f'Error: {e}')
    
    db.commit()

def get_random_date():
    
    db,c = connect()
    
    c.execute("SELECT name FROM programs WHERE user_id =%s", [USER_ID])
    
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
    
    c.execute('SELECT id, name FROM sub_department WHERE user_id=%s', [USER_ID])
    f = c.fetchall()
    if get_id:
        return [(fe[0], fe[1]) for fe in f]
    return [fe[1] for fe in f]

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

def week_passed(date_range_str):
    # Extract the start date from the range string
    start_date_str = date_range_str.split(' - ')[0][1:]
    
    # Parse the start date string
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    
    # Get the current date and time
    current_date = datetime.now()
    
    # Calculate the week number and year for both dates
    start_week = start_date.isocalendar()[1]
    start_year = start_date.isocalendar()[0]
    
    current_week = current_date.isocalendar()[1]
    current_year = current_date.isocalendar()[0]
    
    # Compare the week numbers along with the year to account for year boundaries
    if start_year < current_year:
        return True
    elif start_year == current_year:
        return start_week <= current_week
    else:
        return False

def add_program(name:str):
    
    db,c = connect()
    
    c.execute("INSERT INTO programs (name, user_id) VALUES (%s, %s)", [name, USER_ID])
    db.commit()

def get_all_programs(get_id = False):
    db,c = connect()
    
    c.execute("SELECT * FROM programs WHERE user_id=%s", [USER_ID])
    
    if get_id:
        return [[f[0],f[1]] for f in c.fetchall()]
        
    return [f[1] for f in c.fetchall()]

def remove_from_string(stre, to_remove='%20'):
    final_str = ''
    
    for stri in stre.split(to_remove):
    
        final_str += stri + ' '
        
    return final_str

# def get_random_program():
    
#     dbe,c =connect()
    
#     c.execute('SELECT * FROM programs WHERE user_id=%s', [USER_ID])
    
#     try:
#         return c.fetchall()[0][1]
#     except IndexError:
#         return None

class User:
    
    @staticmethod 
    def register_user(username,role, email, password, admin,is_hotel_admin, owner, parent_id):
        
        db,c = connect()
        
        password = generate_password_hash(password)
        
        if parent_id == '' or parent_id == None:
            parent_id = -1
        
        c.execute(
        "INSERT INTO users (name, role, admin, owner, parent_id, password, email, hotel_owner) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
        [username,role, admin, owner, parent_id, password, email, is_hotel_admin,]
        )
        
        if parent_id == -1:
            c.execute('UPDATE users SET parent_id=id WHERE name=%s', [username])
        
        db.commit()
        
    @staticmethod
    def check_email_valid(email):
        
        db,c = connect()
        
        c.execute('SELECT * FROM users WHERE email=%s', [email])
        
        return len(c.fetchall()) == 0
        
    @staticmethod
    def login(email, password):
        
        db,c = connect()
        
        c.execute("SELECT * FROM users WHERE email=%s", [email])
        
        f = c.fetchall()
        
        
        if len(f) == 0:
            return 'No user With this Email!'

        f = f[0]    
        print(f[6])    
        if not check_password_hash(f[6], password):
            return 'Wrong Password'
        
        return User(f[0])
    def __init__(self, ide) -> None:
        self.id = ide
        
        db,c = connect()
        c.execute('SELECT * FROM users WHERE id=%s', [self.id])
        try:
            f = c.fetchall()[0]
        except IndexError:
            return None
        
        self.name = f[1]
        self.role = f[2]
        self.admin = bool(f[3])
        self.owner = bool(f[4])
        self.parent_id = f[5]
        self.email = f[6]
        self.hotel_owner = bool(f[8])
        
    def get_all_departments(self):
        
        kitchens = execute('SELECT name, dep_ids FROM big_kitchens WHERE user_id=%s', [self.id, ])
        import ast 
        deps = []
        for kitchen in kitchens:
            name = kitchen[0]
            ids = ast.literal_eval(kitchen[1])
            
            for n in ids:
                nme = execute('SELECT name FROM sub_department WHERE id=%s', [n])[0][0]
                deps.append(f'{name} - {nme}')
        print('deps: ', deps)
        return deps
            
            
        
        

class Employee:
    
    @staticmethod
    def create_employee(name, title, def_dep, salary, working_days, salary13, salary14, gesy, provident_fund, guild, leave, time):
        
        db,c = connect()
        
        c.execute('SELECT id FROM employees WHERE name=%s and user_id=%s', [name, USER_ID])
        if len(f:=c.fetchall()) > 0:
            print('yeah', f)
            return False
        print(salary13, salary14, leave)
        c.execute("INSERT INTO employees (name, title, default_dep, user_id, salary, working_days, 13_salary, 14_salary,ann_leave, gesy, provident_fund, guild, pref_time) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            [name, title, def_dep, USER_ID, salary, working_days, salary13, salary14,leave,  gesy,provident_fund, guild, time  ])
        db.commit()
        
        c.execute('SELECT * FROM employees WHERE name=%s', [name])
        
        return Employee(c.fetchall()[0][0])
    
    @staticmethod 
    def get_id_by_name(name):
        
        db,c = connect()
        
        c.execute("SELECT id FROM employees WHERE name =%s AND user_id=%s", [name, USER_ID])
        
        try:
            
            return c.fetchall()[0][0]
        except IndexError:
            c.execute("SELECT id FROM employees WHERE name =%s AND user_id=%s", [remove_from_string(name), USER_ID])
            
            return c.fetchall()[0][0]
        
    @staticmethod 
    def get_id_by_name_archive(name):
        
        db,c = connect()
        
        c.execute("SELECT id FROM employee_archive WHERE name =%s AND user_id=%s", [name, USER_ID])
        
        try:
            
            return c.fetchall()[0][0]
        except IndexError:
            c.execute("SELECT id FROM employee_archive WHERE name =%s AND user_id=%s", [remove_from_string(name), USER_ID])
            
            return c.fetchall()[0][0]
            
    @staticmethod
    def get_all_employees():
        
        db,c = connect()
        
        c.execute("SELECT id FROM employees WHERE user_id=%s ORDER BY default_dep", [USER_ID])
        
        employees = [Employee(ide[0]) for ide in c.fetchall()]
        while True:
            try:
                employees.remove(None)
            except ValueError:
                break 
        return employees
    
    @staticmethod
    def from_archive(idd:str):
        
        if idd.isnumeric():
            final_id = idd
        else:
            final_id = Employee.get_id_by_name_archive(idd)
        
        return Employee(final_id, True)
        
    
    def __init__(self, idd, check_archive=False) -> None:
        db,c = connect()
        
        self.id = idd
        
        c.execute("SELECT * FROM employees WHERE id=%s AND user_id=%s", [self.id, USER_ID])
        # (f"SELECT * FROM employee WHERE id={self.id}")
        try:
            f = c.fetchall()[0]
        except IndexError:
            
            if check_archive:
                print(self.id)
                c.execute('SELECT * FROM employee_archive WHERE id=%s AND user_id=%s', [self.id, USER_ID])
                f = c.fetchall()
                if len(f) == 0:
                    print("Employee Doesnt Exist (check_archive = True)")
                    return None
                f = f[0]
                
            else:
                    
                print("Employee Doesnt Exist (check_archive = False)")
                return None
            
        self.raw = {
            'id' : self.id,
            'name' : f[1],
            'title' : f[2],
            'default_dep' : f[3],
            'salary' : f[5],
            'working_days' : f[6],
            'salary13' : f[7],
            'salary14' : f[8],
            'ann_leave' : f[9],
            'gesy' : f[10],
            'prov_fund' : f[11],
            'guild' : f[12],
            'time' : f[13]
        }
        
        
        self.title = self.raw['title']
        self.name = self.raw['name']
        self.user_id = f[4]
        
        self.prefered_dep = self.raw['default_dep'].split(' - ')
        self.prefered_dep_str = self.raw['default_dep']
        
        self.salary = self.raw['salary']
        self.working_days = self.raw['working_days']
        self.salary13 = self.raw['salary13']
        self.salary14 = self.raw['salary14']
        self.ann_leave = self.raw['ann_leave']
        self.gesy = self.raw['gesy']
        self.prov_fund = self.raw['prov_fund']
        self.guild = self.raw['guild']
        self.time = self.raw['time']
        
    def copy_to_archive(self):
        
        dbe,c = connect()
        
        c.execute('SELECT * FROM employee_archive WHERE id=%s', [self.id])
        if len(c.fetchall()) != 0:
            return False
        
        c.execute('INSERT INTO employee_archive (id,name,title,default_dep,user_id) VALUES (%s,%s,%s,%s,%s)', [self.id, self.name, self.title, self.prefered_dep_str, self.user_id])
    
        dbe.commit()
        
        return True
    
    def update(self, name, title, def_dep, salary, working_days, salary13, salary14, gesy, provident_fund, guild, leave, time):
        
        db,c = connect()
        
        c.execute("UPDATE employees SET name=%s, title=%s, default_dep=%s, salary=%s, working_days=%s, 13_salary=%s, 14_salary=%s, ann_leave=%s, gesy=%s, provident_fund=%s, guild=%s, pref_time=%s WHERE id=%s",
                  [name, title, def_dep,salary, working_days, salary13, salary14, gesy, provident_fund, guild, leave,time ,self.id])
        
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
            
            c.execute("SELECT schedule_json FROM schedules WHERE user_id=%s ORDER BY id ASC", [USER_ID])
            
            try:
                dic = json.loads(c.fetchall()[0][0].replace("'", '"'))
                program = self.get_last_program(dic)
                
            except IndexError as e:
                
                print(e)
                program = [{
                    'monday' : [self.time if self.time is not None else get_random_program(), ''],
                    'tuesday' : [self.time if self.time is not None else get_random_program(), ''],
                    'wednesday' : [self.time if self.time is not None else get_random_program(), ''],
                    'thursday' : [self.time if self.time is not None else get_random_program(), ''],
                    'friday' : [self.time if self.time is not None else get_random_program(), ''],
                    'saturday' : [self.time if self.time is not None else get_random_program(), ''],
                    'sunday' : [self.time if self.time is not None else get_random_program(), ''],
                }]

            
        print(program)
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
        
        c.execute("SELECT name, dep_ids FROM big_kitchens WHERE user_id=%s", [USER_ID])
        
        departments = []
        
        kitchens = c.fetchall()
        
        
        for tup in kitchens:
            kitchen, department_ids = tup 
            
            department_ids = json.loads(department_ids.replace("'", '"'))
            
            for ide in department_ids:
                try:
                    dep = get_subdept(ide)
                    
                    departments.append(f'{kitchen} - {dep.name}')
                except Exception as e:
                    print('Error: ', e)
        
        return departments
               
    @staticmethod
    def get_id_from_name(name):
        db,c = connect()
        
        c.execute("SELECT id FROM sub_department WHERE name=%s AND user_id=%s", [name,USER_ID])
        
        try:
            
            return c.fetchall()[0][0]
        except IndexError:
            strings = name.split('%20')
            final_string = ''
            for stri in strings:
                final_string += stri + ' '
            final_string.strip()
            
            c.execute("SELECT id FROM sub_department WHERE name=%s AND user_id=%s", [final_string,USER_ID])
            f = c.fetchall()
            return f[0][0]
    
    def __init__(self, ide):
        
        db,c = connect()
        
        self.id = ide
        
        c.execute("SELECT * FROM sub_department WHERE id=%s AND user_id=%s", [self.id, USER_ID])
        try:
            f = c.fetchall()[0]
        except IndexError:
            print('Department Doesnt Exist')
            return
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
        
        c.execute('INSERT INTO big_kitchens (name, dep_ids, user_id, row) VALUES (%s,%s, %s, %s)', [name, str(dept_ids), USER_ID, -1])
        
        
        
        db.commit()
        
        c.execute('UPDATE big_kitchens SET row=id WHERE row=-1')
        db.commit()
        
        c.execute('SELECT id FROM big_kitchens WHERE name=%s AND user_id=%s', [name, USER_ID])
        
        return Kitchen(c.fetchall()[0][0])
    
    @staticmethod
    def get_all_kitchens(get_id = False):
        
        db,c = connect()
        
        
        c.execute("SELECT id, name FROM big_kitchens WHERE user_id=%s ORDER BY row ASC", [USER_ID])
        
        
        
        if get_id:
            return [(f[0], f[1]) for f in c.fetchall()]
            
        return [f[1] for f in c.fetchall()]
    
    @staticmethod
    def get_id_from_name(name):
        
        db,c =connect()
        
        c.execute("SELECT id FROM big_kitchens WHERE name=%s AND user_id=%s", [name, USER_ID])
        
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
    
    def __init__(self, ide) -> None:
        db,c = connect()
        
        c.execute("SELECT * FROM big_kitchens WHERE id=%s AND user_id=%s", [ide, USER_ID])
        f = c.fetchall()[0]
        self._raw = {
            'id' : id,
            'name' : f[1],
            'dep_ids': json.loads(f[2].replace("'", '"'))
        }
        
        self.id = ide
        
        self.sub_departments = []
        
        self.name = self._raw['name']

        
        for ide in self._raw['dep_ids']:
            if get_subdept(ide) != None:
                self.sub_departments.append(get_subdept(ide))
            
    def update(self, new_name, departments):
        
        db,c = connect()
        
        c.execute("UPDATE big_kitchens SET name=%s, dep_ids=%s WHERE id=%s", [new_name, str(departments), self.id])
        
        db.commit()

class KitchenGroup:
    
    @staticmethod
    def get_all_weeks(week):
        
        db,c = connect()
        
        c.execute("SELECT week FROM schedules WHERE week=%s  AND user_id=%s", [week, USER_ID])
        
        return c.fetchall()
    
    @staticmethod
    def get_saved_weeks():
        
        db,c = connect()
        
        c.execute("SELECT week FROM schedules WHERE user_id=%s", [USER_ID])
        
        return c.fetchall()
    
    def __init__(self,week='') -> None:
        db,c = connect()
        
        self.week = week 
        
        c.execute('SELECT id FROM big_kitchens WHERE user_id=%s ORDER BY row ASC', [USER_ID])
        self.sub_kitchens = [Kitchen(id[0]) for id in c.fetchall()]
        
        
        # print('week : ',self.week)
        
        if self.week != '':
            
            self.week_passed = week_passed(self.week)
            
            # print(self.week_passed)
            
            c.execute('SELECT * FROM schedules WHERE week=%s AND user_id=%s', [week, USER_ID])
            
            
            
            if len((f := c.fetchall() )) > 0:
                # print('sched load')
                self.load_schedule(f[0][2].replace("'", '"'))
                self.saved = True
            else:
                # self.set_employees_to_default()
                # print('load_last_sched')
                self.load_last_schedule()
                self.saved = False
            try:
                self.id = f[0][0]
            except IndexError:
                pass
            
            # ('empty')
            
    def get_all_employees(self):
        
        db,c = connect()
        
        c.execute('SELECT name FROM employees WHERE user_id=%s', [USER_ID])
        
        return [f[0] for f in c.fetchall()]
            
    def load_last_schedule(self):
        db,c = connect()
        
        c.execute("SELECT schedule_json FROM schedules WHERE user_id=%s ORDER BY id DESC", [USER_ID])
        
        f = c.fetchall()
        
        # print(f)
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
                    
                    if dep == None:
                        continue
                
                    if emp in dep.employees:
                        all_emps.remove(emp)
        
        return all_emps
        
    def set_employees_to_default(self):
        employees = Employee.get_all_employees()
        
        for employee in employees:
            # print(employee)
            self.set_def_employee(employee)
        
    def set_def_employee(self,emp:Employee):
        
        pref_dep_kitch,pref_dep = emp.prefered_dep
        
        dep = self.get_department_by_name(pref_dep.lower(), pref_dep_kitch.lower())
        
        if dep == None:
            flash(f'Error!: `{pref_dep}` department  in `{pref_dep_kitch}` doesnt exist!')
            return 
        
        emp.pass_to_department(dep, 'last_program')
            
    def set_week(self, week):
        
        self.week = week 
        
        dbe,c= connect()
        c.execute('SELECT * FROM schedules WHERE week=%s AND user_id=%s', [week, USER_ID])
        
        if len((f := c.fetchall() )) > 0:
            self.load_schedule(f[0][2].replace("'", '"'))
            
    def get_all_employees_programs(self):

        return [emp for kitchen in self.sub_kitchens for dep in kitchen.sub_departments for emp in dep.employees]
    
    def get_split_days(self):
        
        days = set()
        
        for emp, program in self.get_all_employees_programs():
            
            for prog in program:
                
                for key in prog: 
                    
                    if isinstance(prog, int):
                        continue

                    print(f"prog: {prog}, key: {key}")
                    try:
                        if prog[key][1] != '':
                            days.add(key.lower())
                    except TypeError as e:
                        print(f'TypeError: {e}')
                    
        # print('fwaeh',list(days))
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
                    
                    if emp[0] == None:
                        continue
                    
                    if str(emp[0]).isnumeric():
                        (emp[0], 'numeric')
                        em = Employee(emp[0])
                    else:
                        (emp[0], 'name')
                        em = Employee(Employee.get_id_by_name(emp[0]))
                        
                    try:
                        print(em.name)
                    except AttributeError:
                        if self.week_passed:
                            em = Employee.from_archive(str(emp[0]))
                            
                            if not hasattr(em, 'name'):
                                continue
                        else: continue
                        
                    emps_added.append(em.name)
                    self.remove_employee_from_current_department(em)
                    # em.pass_to_department(self.get_department_by_name(dept, kitchen), emp[1])
                    try:
                        self.get_department_by_name(dept, kitchen).employees.append((em, emp[1]))
                    except AttributeError:
                        print('sum weird sh happning')
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
                if dep == None:
                    continue


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
            c.execute("UPDATE schedules SET schedule_json=%s WHERE week=%s AND user_id=%s", [str(schedule_json),self.week, USER_ID])
        else: 
            c.execute("INSERT INTO schedules (week, schedule_json, user_id) VALUES (%s, %s, %s)", [self.week, str(schedule_json), USER_ID])
            
        self.saved = True
        
        db.commit()
        
def random_string(l=16) -> str:
    import random, string; return ''.join(random.choices(string.ascii_letters + string.digits, k=l))
     

def execute(query:str, params:list):
    
    params = [None if param is None else param for param in params]
    dbe,c = connect()
    
    print(query, params)
    
    c.execute(query, params)
    
    try:
        f = c.fetchall()
    except mysql.connector.errors.InterfaceError:
        pass
    
    dbe.commit()
    
    c.close()
    dbe.close()
    # print(f)
    try:
        return f
    except UnboundLocalError:
        return None
        
def get_dep_id(name):
    # print(name)
    return execute('SELECT id FROM sub_department WHERE name=%s', [name])[0][0]
    
    
        
if __name__ == '__main__':

    db,c = connect()
    
    print('Connection to Database Successful!')
    
    while True:
        
        match (f:=input('$ ')):
            
            case 'help':
                with open('help.txt') as file:
                    
                    print(file.read())
                
                
            case 'create_user':
                User.register_user(
                    input('Username: '),
                    input('Role: '),
                    input('Email: '),
                    input('Password: '),
                    input('Admin (0/1): '),
                    input('Owner (0/1): '),
                    input('Parent User Id (empty for same as id): '),
                )
            case 'edit_user':
                print('edit_user')
            case 'wipe_user_content':
                tables = ['big_kitchens', 'sub_department', 'employee_archive', 'programs', 'schedules', 'titles', 'employees']
                user_id = int(input('Enter User Id'))
                    
                execute('DELETE FROM big_kitchens WHERE user_id=%s', [user_id,])
                execute('DELETE FROM sub_department WHERE user_id=%s', [user_id,])
                execute('DELETE FROM employee_archive WHERE user_id=%s', [user_id,])
                execute('DELETE FROM programs WHERE user_id=%s', [user_id,])
                execute('DELETE FROM schedules WHERE user_id=%s', [user_id,])
                execute('DELETE FROM titles WHERE user_id=%s', [user_id,])
                execute('DELETE FROM employees WHERE user_id=%s', [user_id,])
                
            case 'delete_user':
                print('delete')
            case 'create_db':
                with open('create_db.sql') as f:
                    text = f.read()
                    
                db,c= connect()
                
                try:
                    
                    c.execute(text, multi=True)
                    
                    db.commit()
                    print('Successfully Created Database')
                except Exception as e:
                    print('Error Creating Database: \n'+str(e))
                
            case 'spam_db':
                
                user_id = str(input('User Id: '))
                names = []
            
                for i in range(K := int(input('Amount of Departments: '))):
                    rand =random_string(12)
                    names.append(rand)
                    execute('INSERT INTO sub_department (name, user_id) VALUES (%s,%s)', [rand, user_id])
                    print('Departments Done!')
                    
                names = [int(get_dep_id(name)) for name in names]
                
                
                for name in names: names.remove(name) if not str(name).isdigit() else 0
             
                for i in range(int(input('How Many Kitchens? '))):
                    
                    execute('INSERT INTO big_kitchens (name, dep_ids, user_id, row) VALUES (%s,%s,%s,%s)', [rand, str(random.choices(names, k=random.randint(1,K))), user_id, 0])
                    print('Kitchens Done!')
             
                for i in range(int(input('How Many Time Programs? '))):
                    
                    execute('INSERT INTO programs (name, user_id) VALUES (%s, %s)', [random_string(8), user_id])
                    print('Programs Done!')
                    
                titles = []
                for i in range(int(input('How Many Titles? '))):
                    f = random_string(6)
                    titles.append(f)
                    execute('INSERT INTO titles (name, user_id) VALUES (%s, %s)', [f, user_id])
                    print('Titles Done!')
                    
                all_deps = User(user_id).get_all_departments()
                    
                for i in range(int(input('How Many Employees? '))):
                    
                    execute('INSERT INTO employees (name,title,default_dep, user_id) VALUES (%s,%s,%s,%s)', [random_string(12),random.choice(titles),random.choice(User(user_id).get_all_departments()) ,user_id])
                    
                    print('Employees Done!')
                print('All Done!')
                
                    
                    
                
                
            case '':
                break
            
            case _:
                print(F'`{f}` is not a recognised command. `help` for command list')
                
        print('\n\n')