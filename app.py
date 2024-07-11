# Import the Flask class from the flask module
from flask import Flask, render_template, get_flashed_messages, flash, session, request, redirect, url_for, jsonify
from datetime import timedelta, datetime

from db import get_subdept, create_dept, Employee, Department, Kitchen, KitchenGroup, add_program, get_all_programs, get_next_weeks, get_current_week

# Create an instance of the Flask class
app = Flask(__name__)

app.config['SECRET_KEY'] = "very_secret_key_12351232"

# Define a route and a view function
@app.route('/')
def hello():
    return render_template("index.html")

def get_next_seven_days(start_date_str):
    start_date = datetime.strptime(start_date_str, "%d/%m/%Y")
    next_seven_days = [(start_date + timedelta(days=i)).strftime("%d/%m/%Y") for i in range(8)][0:7]
    return next_seven_days

@app.route('/table')
@app.route('/table/<week>')
def table(week=None):
    
    match request.method:
        
        case 'GET':
            
            if week == None:
            
                group = KitchenGroup(get_current_week())
                
                day_start = group.week.split('-')[2].strip()
                month_start = group.week.split('-')[1].strip()
                year_start = group.week.split('-')[0].split('(')[1].strip()
            
            else:
                
                year_start = week.split('_')[2]
                month_start = week.split('_')[1]
                day_start = week.split('_')[0]
                
                year_end = week.split('_')[5]
                month_end = week.split('_')[4]
                day_end = week.split('_')[3]
                
                formated_week = f"({year_start}-{month_start}-{day_start} - {year_end}-{month_end}-{day_end})"
                
                print(formated_week)
                
                group = KitchenGroup(formated_week)
                
            dates = get_next_seven_days(f"{day_start}/{month_start}/{year_start}")
            
            all_employees = group.get_unplaced_employees()
            
            all_programs = get_all_programs()
            
            all_departments = Department.get_all_departments()
            
            weeks = get_next_weeks(4)
            selected_week = get_current_week() if week == None else formated_week
            
            all_weeks_saved = KitchenGroup.get_saved_weeks()
            
            todays_week = get_current_week()
            
            split_days = group.get_split_days()
            
            new_week_message = '' if week == None else 'Week Successfully Created. Make Sure to Save!' if not group.saved else ''
            
            print(split_days)
            
            return render_template(
                'table.html',
                group=group,
                all_employees=all_employees,
                all_programs = all_programs,
                all_departments = all_departments,
                weeks = weeks,
                selected_week = selected_week,
                all_weeks_saved = all_weeks_saved,
                new_week_message=new_week_message,
                todays_week = todays_week,
                dates=dates,
                split_days = split_days
            )
            
@app.route('/see_week/<d_start>_<m_start>_<y_start>_<d_end>_<m_end>_<y_end>')
def see_week(d_start, m_start, y_start, d_end, m_end, y_end):
    
    return f"{d_start}/{m_start}/{y_start} - {d_end}/{m_end}/{y_end}"
    
    
            
@app.route('/save_schedule', methods=['POST'])
def save_schedule():
    data = request.json 
    
    schedule = KitchenGroup(data['week'])
    
    schedule.load_schedule(data)
    
    # print(schedule.sub_kitchens[0].sub_departments[0].employees[0])
    
    schedule.save_schedule()
    
    # print('sigma: \n', data['Main Kitchen']['Hot Kitchen'], '\n carti')

    
    return jsonify({'status':'success', })
        
@app.route('/add_employee', methods=['GET', 'POST'])
def add_employee():
    
    match request.method:
        
        case 'GET':
            
            all_departments = Department.get_all_departments()
            all_programs = get_all_programs()
            
            return render_template('add_employee.html', departments = all_departments, programs=all_programs)
        
        case 'POST':
            
            name, title, def_dep = request.form.get('name'), request.form.get('title'), request.form.get('def_dep')
            
            Employee.create_employee(name, title, def_dep)
            
            flash('Added Employee Successfully!')
            return redirect(url_for('add_employee'))
            
@app.route('/add_program', methods=['GET', 'POST'])
def create_program():
    
    match request.method:
        case 'GET':
            
            return render_template('add_program.html')
    
        case 'POST':
            
            name = request.form.get('name')
            
            add_program(name)
            
            flash('Program Created')
            
            return redirect(url_for('create_program'))

    
# Run the application
if __name__ == '__main__':
    app.run()
