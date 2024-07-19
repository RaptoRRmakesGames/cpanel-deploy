# Import the Flask class from the flask module
from flask import (
    Flask,
    render_template,
    get_flashed_messages,
    flash,
    session,
    request,
    redirect,
    url_for,
    jsonify,
)
from datetime import timedelta, datetime

import db

import json 

# Create an instance of the Flask class
app = Flask(__name__)

app.config["SECRET_KEY"] = "very_secret_key_12351232"

app.config.update(
    SESSION_PERMANENT=True,
    SESSION_TYPE='filesystem'
)

@app.before_request
def before():
    
    if 'user_id' in session:
        db.USER_ID = session['parent_id']

# Define a route and a view function
@app.route("/")
def index():
    if not auth() : return redirect(url_for('login_page'))
    
    return render_template("index.html", session=session,)

def auth():
    if 'auth' in session: return session['auth']
    else: return False

def admin():
    if auth(): return session['user_admin']
    else: return False

def get_next_seven_days(start_date_str):
    start_date = datetime.strptime(start_date_str, "%d/%m/%Y")
    next_seven_days = [
        (start_date + timedelta(days=i)).strftime("%d/%m/%Y") for i in range(8)
    ][0:7]
    return next_seven_days

@app.route("/add_kitchen", methods=["GET", "POST"])
def add_kitchen():

    if not auth() : return redirect(url_for('login_page'))
    
    match request.method:
        case "GET":
            return render_template(
                "add_kitchen.html", session=session, departments=db.get_all_departments()
            )

        case "POST":

            name, deps = request.form.get("name"), []
            for key in request.form:
                if key == "name" or key == "submit":
                    continue
                deps.append(request.form.get(key))

            db.Kitchen.create_kitchen(name, deps)

            flash("Created Kitchen Successfully!")

            return redirect(url_for("edit_objects"))

@app.route("/add_department", methods=["GET", "POST"])
def add_dep():

    if not auth() : return redirect(url_for('login_page'))
    match request.method:
        case "GET":
            return render_template("add_deps.html", session=session,)

        case "POST":

            db.create_dept(request.form.get("name"))

            flash("Created Department Successfully!")

            return redirect(url_for("edit_objects"))

@app.route("/add_title", methods=["GET", "POST"])
def add_title():
    if not auth() : return redirect(url_for('login_page'))
    match request.method:
        case "GET":
            return render_template("add_title.html", session=session,)

        case "POST":

            db.create_title(request.form.get("name"))

            flash("Created Title Successfully!")

            return redirect(url_for("edit_objects"))

@app.route("/save_schedule", methods=["POST"])
def save_schedule():
    if not auth() : return redirect(url_for('login_page'))
    data = request.json

    schedule = db.KitchenGroup(data["week"])

    schedule.load_schedule(data)

    schedule.save_schedule()

    return jsonify(
        {
            "status": "success",
        }
    )

@app.route("/add_employee", methods=["GET", "POST"])
def add_employee():
    if not auth() : return redirect(url_for('login_page'))
    match request.method:

        case "GET":

            all_departments = db.Department.get_all_departments()
            all_programs = db.get_all_programs()
            all_titles = db.get_all_titles()

            print(all_titles)

            return render_template(
                "add_employee.html", session=session,
                departments=all_departments,
                programs=all_programs,
                titles=all_titles,
            )

        case "POST":

            name, title, def_dep = (
                request.form.get("name"),
                request.form.get("title"),
                request.form.get("def_dep"),
            )

            db.Employee.create_employee(name, title, def_dep)

            flash("Added Employee Successfully!")
            return redirect(url_for("edit_objects"))

@app.route("/add_program", methods=["GET", "POST"])
def create_program():
    if not auth() : return redirect(url_for('login_page'))
    match request.method:
        case "GET":

            return render_template("add_program.html", session=session,)

        case "POST":

            name = request.form.get("name")

            db.add_program(name)

            flash("Program Created")

            return redirect(url_for("edit_objects"))

@app.route("/edit_objects")
def edit_objects():
    if not auth() : return redirect(url_for('login_page'))
    all_kitchens = db.Kitchen.get_all_kitchens()
    all_departments = db.get_all_departments(False)
    all_employees = db.Employee.get_all_employees()
    all_programs = db.get_all_programs()
    all_titles = db.get_all_titles()

    return render_template(
        "edit_objects.html", session=session,
        kitchens=all_kitchens,
        departments=all_departments,
        employees=all_employees,
        programs=all_programs,
        titles=all_titles,
    )
    
@app.route('/edit/kitchen/<kitchen>', methods=['GET', 'POST'])
def edit_kitchen(kitchen):
    if not auth() : return redirect(url_for('login_page'))
    match request.method:
        case "GET":
            print(kitchen)
            return render_template(
                "add_kitchen.html", session=session, departments = db.get_all_departments(),
                edit=True, kitchen = db.Kitchen(db.Kitchen.get_id_from_name(kitchen))
            )

        case "POST":

            name, deps = request.form.get("name"), []
            for key in request.form:
                if key == "name" or key == "submit" or key == 'id':
                    continue
                deps.append(request.form.get(key))

            k = db.Kitchen(db.Kitchen.get_id_from_name(kitchen))
            
            if k.name != name:
                
                db_obj, c = db.connect()
                
                c.execute('SELECT id, default_dep, name FROM employees')
                
                emps = c.fetchall()
                
                for emp in emps:
                    
                    empid = emp[0]
                    emp_def_kitch, emp_def_dep = emp[1].split(" - ")
                    empname = emp[2]
                    
                    if emp_def_kitch == k.name:
                        c.execute('UPDATE employees SET default_dep=%s WHERE id=%s', [f'{name} - {emp_def_dep}', empid])
                        db_obj.commit()
                        
                        flash(f'Updated Employee `{empname}`')
                        
            c.execute('SELECT id, week, schedule_json FROM schedules WHERE user_id=%s ', [session['parent_id']])
            
            f = c.fetchall()
            
            for sched in f:
                
                week_id = sched[0]
                week_name = sched[1]
                sched_json = json.loads(sched[2].replace("'", '"'))
                new_js = {}
                for kitchen_key in sched_json:
                    
                    if kitchen_key == k.name:
                        new_js[name] = sched_json[kitchen_key]
                    else:
                        
                        new_js[kitchen_key] = sched_json[kitchen_key]

                
                print(new_js)
                            
                c.execute('UPDATE schedules SET schedule_json=%s WHERE id=%s', [str(new_js), week_id])   
                db_obj.commit()       
                
                flash(f'Week `{week_name}` updated for Kitchen name change')
            
            k.update(name, deps)

            flash("Updated Kitchen Successfully!")

            return redirect(url_for("edit_objects"))
    
@app.route('/edit/department/<dep>', methods=['GET', 'POST'])
def edit_department(dep):
    if not auth() : return redirect(url_for('login_page'))
    match request.method:
        case "GET":
            return render_template(
                "add_deps.html", session=session, departments=db.get_all_departments(),
                edit=True, department = db.Department(db.Department.get_id_from_name(dep))
            )

        case "POST":

            name = request.form.get("name")

            old_dep  = db.Department(db.Department.get_id_from_name(dep))
            
            db_obj,c = db.connect()
            
            c.execute("SELECT id, default_dep,name FROM employees")
            
            emps = c.fetchall()
            
            for emp in emps:
                
                empid = emp[0]
                
                empname=emp[2]
                
                def_dep_kitch,def_dep = emp[1].split(' - ')
                
                if old_dep.name == def_dep:
                    c.execute('UPDATE employees SET default_dep=%s WHERE id=%s', [f"{def_dep_kitch} - {name}", empid])
                    
                    db_obj.commit()
                    flash(f"Updated Department in Employee `{empname}`")
            
            c.execute('SELECT id, week, schedule_json FROM schedules WHERE user_id=%s ', [session['parent_id']])
            
            f = c.fetchall()
            
            for sched in f:
                
                week_id = sched[0]
                week_name = sched[1]
                sched_json = json.loads(sched[2].replace("'", '"'))
                new_js = {}
                for kitchen_key in sched_json:
                    new_js[kitchen_key] = {}
                    for dep_key in sched_json[kitchen_key]:
                        if dep_key == old_dep.name:
                            
                            print(dep_key, 'new')
                            
                            new_js[kitchen_key][name] = []
                            
                            for ls in sched_json[kitchen_key][dep_key]:
                                new_js[kitchen_key][name].append(ls)        
                            
                        else:
                            print(dep_key, 'old')
                            new_js[kitchen_key][dep_key] = sched_json[kitchen_key][dep_key]
                
                print(new_js)
                            
                c.execute('UPDATE schedules SET schedule_json=%s WHERE id=%s', [str(new_js), week_id])   
                db_obj.commit()       
                
                flash(f'Week `{week_name}` updated for department name change')
                
            
            old_dep.update(name)

            flash("Updated Department Successfully!")

            return redirect(url_for("edit_objects"))
        
@app.route('/edit/employee/<emp>', methods=['GET', 'POST'])
def edit_demployee(emp):
    if not auth() : return redirect(url_for('login_page'))
    match request.method:
        case "GET":
            
            return render_template(
                "add_employee.html", session=session, departments=db.Department.get_all_departments(),
                edit=True, employee = db.Employee(db.Employee.get_id_by_name(emp)), titles=db.get_all_titles(), programs=db.get_all_programs()
            )

        case "POST":

            name = request.form.get("name")
            title = request.form.get('title')
            pref_dep = request.form.get('def_dep')

            db.Employee(db.Employee.get_id_by_name(emp)).update(name, title, pref_dep)

            flash("Updated Department Successfully!")

            return redirect(url_for("edit_objects"))
        
@app.route('/delete/program/<program>')
def delete_program(program):
    if not auth() : return redirect(url_for('login_page'))
    
    db_obj,c =db.connect()
    
    program = db.remove_from_string(program)
    flash(f"`{program}` Deleted Successfully")
    
    c.execute("DELETE FROM programs WHERE name=%s ", [program])
    db_obj.commit()
    
    return redirect(url_for('edit_objects'))

@app.route('/delete/title/<title>')
def delete_title(title):
    if not auth() : return redirect(url_for('login_page'))
    
    db_obj,c =db.connect()
    title = db.remove_from_string(title)
    flash(f"`{title}` Deleted Successfully")
    c.execute("DELETE FROM titles WHERE name=%s ", [title])
    db_obj.commit()
    
    return redirect(url_for('edit_objects'))

@app.route('/delete/kitchen/<kitchen>')
def delete_kitchen(kitchen):
    if not auth() : return redirect(url_for('login_page'))
    
    db_obj,c =db.connect()
    kitchen = db.remove_from_string(kitchen)
    flash(f"`{kitchen}` Deleted Successfully. Make sure to edit Employees that were assigned to that kitchen!")
    c.execute("DELETE FROM big_kitchens WHERE name=%s ", [kitchen])
    db_obj.commit()
    
    return redirect(url_for('edit_objects'))

@app.route('/delete/department/<department>')
def delete_department(department):
    if not auth() : return redirect(url_for('login_page'))
    
    db_obj,c =db.connect()
    department = db.remove_from_string(department)
    flash(f"`{department}` Deleted Successfully. Make sure to edit Employees that were assigned to that department!")
    c.execute("DELETE FROM sub_department WHERE name=%s ", [department])
    db_obj.commit()
    
    return redirect(url_for('edit_objects'))

@app.route('/delete/employee/<employee>')
def delete_employee(employee):
    if not auth() : return redirect(url_for('login_page'))
    
    db_obj,c =db.connect()
    flash(f"`{db.remove_from_string(employee)}` Deleted Successfully")
    c.execute("DELETE FROM employees WHERE name=%s ", [db.remove_from_string(employee)])
    db_obj.commit()
    
    return redirect(url_for('edit_objects'))

@app.route("/table")
@app.route("/table/<week>")
def table(week=None):
    if not auth() : return redirect(url_for('login_page'))
    
    

    match request.method:

        case "GET":

            if week == None:

                group = db.KitchenGroup(db.get_current_week())

                day_start = group.week.split("-")[2].strip()
                month_start = group.week.split("-")[1].strip()
                year_start = group.week.split("-")[0].split("(")[1].strip()

            else:

                year_start = week.split("_")[2]
                month_start = week.split("_")[1]
                day_start = week.split("_")[0]

                year_end = week.split("_")[5]
                month_end = week.split("_")[4]
                day_end = week.split("_")[3]

                formated_week = f"({year_start}-{month_start}-{day_start} - {year_end}-{month_end}-{day_end})"

                print(formated_week)

                group = db.KitchenGroup(formated_week)

            dates = get_next_seven_days(f"{day_start}/{month_start}/{year_start}")

            all_employees = group.get_unplaced_employees()

            all_programs = db.get_all_programs()

            all_departments = db.Department.get_all_departments()

            weeks = db.get_next_weeks(4)
            selected_week = db.get_current_week() if week == None else formated_week

            all_weeks_saved = db.KitchenGroup.get_saved_weeks()

            todays_week = db.get_current_week()

            split_days = group.get_split_days()

            new_week_message = (
                ""
                if week == None
                else (
                    "Week Successfully Created. Make Sure to Save!"
                    if not group.saved
                    else ""
                )
            )

            return render_template(
                "table.html", session=session,
                group=group,
                all_employees=all_employees,
                all_programs=all_programs,
                all_departments=all_departments,
                weeks=weeks,
                selected_week=selected_week,
                all_weeks_saved=all_weeks_saved,
                new_week_message=new_week_message,
                todays_week=todays_week,
                dates=dates,
                split_days=split_days,
            )

@app.route("/see_week/<d_start>_<m_start>_<y_start>_<d_end>_<m_end>_<y_end>")
def see_week(d_start, m_start, y_start, d_end, m_end, y_end):
    if not auth() : return redirect(url_for('login_page'))

    return f"{d_start}/{m_start}/{y_start} - {d_end}/{m_end}/{y_end}"

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    
    match request.method:
        
        case 'POST':
            user = db.User.login(request.form.get('email'), request.form.get('pass'))
            print(user)
            if isinstance(user,  db.User):
                flash('Login Successful!')
                session['auth'] = True
                session['user_id'] = user.id
                session['user_name'] = user.name
                session['user_email'] = user.email
                session['user_role'] = user.role
                session['user_admin'] = user.admin
                session['user_owner'] = user.owner
                session['parent_id'] = user.parent_id
                            
                return redirect(url_for('index'))
            
            else: flash(user); return redirect(url_for('login_page'))
            
        case 'GET':
            
            return render_template('login.html')
        
@app.route('/register', methods=['GET', 'POST'])
def register_page():
    if not admin() : return redirect(url_for('login_page'))
    
    match request.method:
        
        case 'GET':
            
            return render_template('register.html', session=session)
    
        case 'POST':
            
            name = request.form.get('name')
            role = request.form.get('role')
            email = request.form.get('email')
            password = request.form.get('name')
            is_admin = {True: 1, False: 2}[request.form.get('is_admin') == 'on']
            
            if not db.User.check_email_valid(email):
                
                flash('Email is not Valid or already in Use!')
                return redirect(url_for('edit_objects'))
            
            db.User.register_user(name, role, email, password, is_admin, 0, session['user_id'])
            
            flash(f"User `{name}` Succesfully Created!")
            
            return redirect(url_for('edit_objects'))
    
        
@app.route('/logout')
def logout():
    
    session.clear()
    
    flash("Successfully Logged Out!")
    
    return redirect(url_for('login_page'))

# Run the application
if __name__ == "__main__":
    app.run()
