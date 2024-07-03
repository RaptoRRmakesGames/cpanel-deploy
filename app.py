# Import the Flask class from the flask module
from flask import Flask, render_template, get_flashed_messages, flash, session, request, redirect, url_for

from db import get_subdept, create_dept, Employee, Department, Kitchen, KitchenGroup, add_program, get_all_programs

# Create an instance of the Flask class
app = Flask(__name__)

app.config['SECRET_KEY'] = "very_secret_key_12351232"

# Define a route and a view function
@app.route('/')
def hello():
    return render_template("index.html")

@app.route('/table')
def table():
    
    match request.method:
        
        case 'GET':
            
            group = KitchenGroup('2/7/2024')
            
            print(group.sub_kitchens[0].sub_departments[2].employees)
            
            all_employees = group.get_unplaced_employees()
            
            all_programs = get_all_programs()
            
            # print(group)
            
            return render_template('table.html', group=group, all_employees=all_employees, all_programs = all_programs)
        
@app.route('/add_employee', methods=['GET', 'POST'])
def add_employee():
    
    match request.method:
        
        case 'GET':
            
            all_departments = Department.get_all_departments()
            
            return render_template('add_employee.html', departments = all_departments)
        
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
