<<<<<<< HEAD
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
    make_response,
    send_file,
)
from datetime import timedelta, datetime

import db

import json

import time

import pandas as pd

from io import BytesIO

# Create an instance of the Flask class
app = Flask(__name__)

app.config["SECRET_KEY"] = "very_secret_key_12351232"
app.config['debug'] = True

app.config.update(SESSION_PERMANENT=True, SESSION_TYPE="filesystem")


def auth():
    if "auth" in session:
        return session["auth"]
    else:
        return False


def admin():

    if auth():
        return session["user_admin"]
    else:
        return False


def get_next_seven_days(start_date_str):
    start_date = datetime.strptime(start_date_str, "%d/%m/%Y")
    next_seven_days = [
        (start_date + timedelta(days=i)).strftime("%d/%m/%Y") for i in range(8)
    ][0:7]
    return next_seven_days


@app.before_request
def before_request_func():

    session["start"] = time.time()

    if "user_id" in session:
        db.USER_ID = session["parent_id"]

    if "auth" in session and session["auth"]:

        dbe, c = db.connect()
        stuff = []
        c.execute("SELECT * FROM employees WHERE user_id = %s", [session["parent_id"]])
        stuff.append(c.fetchall())
        c.execute("SELECT * FROM titles WHERE user_id = %s", [session["parent_id"]])
        stuff.append(c.fetchall())
        c.execute(
            "SELECT * FROM sub_department WHERE user_id = %s", [session["parent_id"]]
        )
        stuff.append(c.fetchall())
        c.execute(
            "SELECT * FROM big_kitchens WHERE user_id = %s", [session["parent_id"]]
        )
        stuff.append(c.fetchall())
        c.execute(
            "SELECT * FROM large_department WHERE user_id = %s", [session["parent_id"]]
        )
        stuff.append(c.fetchall())
        c.execute("SELECT * FROM programs WHERE user_id = %s", [session["parent_id"]])
        stuff.append(c.fetchall())



        session["hide_edit"] = False
        for thing in stuff:
            if len(thing) > 0:
                break

        else:
            session["hide_edit"] = True


@app.after_request
def after_request_func(response):

    if __name__ == "__main__":
        print(time.time() - session["start"])
    return response


@app.route("/")
def index():
    if not auth():
        return redirect(url_for("login_page"))

    return render_template(
        "index.html",
        session=session,
    )


@app.route("/add_kitchen", methods=["GET", "POST"])
def add_kitchen():

    if not auth():
        return redirect(url_for("login_page"))

    match request.method:
        case "GET":
            return render_template(
                "add_kitchen.html",
                session=session,
                departments=db.get_all_departments(),
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

    if not auth():
        return redirect(url_for("login_page"))
    match request.method:
        case "GET":
            return render_template(
                "add_deps.html",
                session=session,
            )

        case "POST":

            db.create_dept(request.form.get("name"))

            flash("Created Department Successfully!")

            return redirect(url_for("edit_objects"))


@app.route("/add_title", methods=["GET", "POST"])
def add_title():
    if not auth():
        return redirect(url_for("login_page"))
    match request.method:
        case "GET":
            return render_template(
                "add_title.html",
                session=session,
            )

        case "POST":

            db.create_title(request.form.get("name"))

            flash("Created Title Successfully!")

            return redirect(url_for("edit_objects"))


@app.route("/save_schedule", methods=["POST"])
def save_schedule():
    if not auth():
        return redirect(url_for("login_page"))
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
    if not auth():
        return redirect(url_for("login_page"))
    match request.method:

        case "GET":

            all_departments = db.Department.get_all_departments()
            all_programs = db.get_all_programs()
            all_titles = db.get_all_titles()

            return render_template(
                "add_employee.html",
                session=session,
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

            employee = db.Employee.create_employee(name, title, def_dep)

            dbe, c = db.connect()

            c.execute(
                "SELECT * FROM schedules WHERE user_id=%s", [session["parent_id"]]
            )
            kitch, dep = employee.prefered_dep
            for sched in c.fetchall():

                ide = sched[0]
                week = sched[1]
                js = json.loads(sched[2].replace("'", '"'))

                program = db.get_random_program()

                for kitchen in js:

                    if kitchen == kitch:

                        for department in js[kitchen]:

                            if department == dep:

                                js[kitchen][department].append(
                                    [
                                        employee.id,
                                        [
                                            {
                                                "monday": [program, ""],
                                                "tuesday": [program, ""],
                                                "wednesday": [program, ""],
                                                "thursday": [program, ""],
                                                "friday": [program, ""],
                                                "saturday": [program, ""],
                                                "sunday": [program, ""],
                                            }
                                        ],
                                    ]
                                )

                flash(f"Added into `{week}` Schedule")
                c.execute(
                    "UPDATE schedules SET schedule_json =%s WHERE id=%s", [str(js), ide]
                )

                dbe.commit()

            flash("Added Employee Successfully!")
            return redirect(url_for("edit_objects"))


@app.route("/add_program", methods=["GET", "POST"])
def create_program():
    if not auth():
        return redirect(url_for("login_page"))
    match request.method:
        case "GET":

            return render_template(
                "add_program.html",
                session=session,
            )

        case "POST":

            name = request.form.get("name")

            db.add_program(name)

            flash("Program Created")

            return redirect(url_for("edit_objects"))


@app.route("/edit_objects")
def edit_objects():
    if not auth():
        return redirect(url_for("login_page"))
    all_kitchens = db.Kitchen.get_all_kitchens(True)
    all_departments = db.get_all_departments(True)

    employee_departments = db.Department.get_all_departments()
    all_employees = db.Employee.get_all_employees()
    all_programs = db.get_all_programs(True)
    all_titles = db.get_all_titles(True)

    dbe, c = db.connect()

    c.execute("SELECT * FROM schedules WHERE user_id=%s", [session["parent_id"]])
    all_schedules = []

    for thing in c.fetchall():

        week_name = thing[1]

        day_start = week_name.split("-")[2].strip()
        day_end = week_name.split("-")[5].split(")")[0]

        month_start = week_name.split("-")[1]
        month_end = week_name.split("-")[4]

        year_start = week_name.split("-")[0].split("(")[1]
        year_end = week_name.split("-")[3].strip()

        url_time = (
            f"{day_start}_{month_start}_{year_start}_{day_end}_{month_end}_{year_end}"
        )

        all_schedules.append(
            [
                thing[0],
                thing[1],
                thing[2],
                url_time,
            ]
        )

    return render_template(
        "edit_objects.html",
        session=session,
        kitchens=all_kitchens,
        departments=all_departments,
        employees=all_employees,
        programs=all_programs,
        titles=all_titles,
        employee_departments=employee_departments,
        schedules=all_schedules,
    )


@app.route("/delete/table/<ide>")
def delete_table(ide):

    dbe, c = db.connect()

    c.execute("DELETE FROM schedules WHERE id=%s", [ide])

    dbe.commit()

    flash(f"Deleted Schedule ID-`{ide}`!")

    return redirect(url_for("edit_objects"))


@app.route("/edit/kitchen/<kitchen>", methods=["GET", "POST"])
def edit_kitchen(kitchen):
    if not auth():
        return redirect(url_for("login_page"))
    match request.method:
        case "GET":
            return render_template(
                "add_kitchen.html",
                session=session,
                departments=db.get_all_departments(),
                edit=True,
                kitchen=db.Kitchen(db.Kitchen.get_id_from_name(kitchen)),
            )

        case "POST":

            name, deps = request.form.get("name"), []
            for key in request.form:
                if key == "name" or key == "submit" or key == "id":
                    continue
                deps.append(request.form.get(key))

            k = db.Kitchen(db.Kitchen.get_id_from_name(kitchen))

            db_obj, c = db.connect()
            if k.name != name:

                c.execute("SELECT id, default_dep, name FROM employees")

                emps = c.fetchall()

                for emp in emps:

                    empid = emp[0]
                    emp_def_kitch, emp_def_dep = emp[1].split(" - ")
                    empname = emp[2]

                    if emp_def_kitch == k.name:
                        c.execute(
                            "UPDATE employees SET default_dep=%s WHERE id=%s",
                            [f"{name} - {emp_def_dep}", empid],
                        )
                        db_obj.commit()

                        flash(f"Updated Employee `{empname}`")

            c.execute(
                "SELECT id, week, schedule_json FROM schedules WHERE user_id=%s ",
                [session["parent_id"]],
            )

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

                c.execute(
                    "UPDATE schedules SET schedule_json=%s WHERE id=%s",
                    [str(new_js), week_id],
                )
                db_obj.commit()

                flash(f"Week `{week_name}` updated for Kitchen name change")

            k.update(name, deps)

            flash("Updated Kitchen Successfully!")

            return redirect(url_for("edit_objects"))


@app.route("/edit/department/<dep>", methods=["GET", "POST"])
def edit_department(dep):
    if not auth():
        return redirect(url_for("login_page"))
    match request.method:
        case "GET":
            return render_template(
                "add_deps.html",
                session=session,
                departments=db.get_all_departments(),
                edit=True,
                department=db.Department(db.Department.get_id_from_name(dep)),
            )

        case "POST":

            name = request.form.get("name")

            old_dep = db.Department(db.Department.get_id_from_name(dep))

            db_obj, c = db.connect()

            c.execute("SELECT id, default_dep,name FROM employees")

            emps = c.fetchall()

            for emp in emps:

                empid = emp[0]

                empname = emp[2]

                def_dep_kitch, def_dep = emp[1].split(" - ")

                if old_dep.name == def_dep:
                    c.execute(
                        "UPDATE employees SET default_dep=%s WHERE id=%s",
                        [f"{def_dep_kitch} - {name}", empid],
                    )

                    db_obj.commit()
                    flash(f"Updated Department in Employee `{empname}`")

            c.execute(
                "SELECT id, week, schedule_json FROM schedules WHERE user_id=%s ",
                [session["parent_id"]],
            )

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

                            new_js[kitchen_key][name] = []

                            for ls in sched_json[kitchen_key][dep_key]:
                                new_js[kitchen_key][name].append(ls)

                        else:

                            new_js[kitchen_key][dep_key] = sched_json[kitchen_key][
                                dep_key
                            ]

                c.execute(
                    "UPDATE schedules SET schedule_json=%s WHERE id=%s",
                    [str(new_js), week_id],
                )
                db_obj.commit()

                flash(f"Week `{week_name}` updated for department name change")

            old_dep.update(name)

            flash("Updated Department Successfully!")

            return redirect(url_for("edit_objects"))


@app.route("/edit/employee/<emp>", methods=["GET", "POST"])
def edit_demployee(emp):
    if not auth():
        return redirect(url_for("login_page"))
    match request.method:
        case "GET":

            return render_template(
                "add_employee.html",
                session=session,
                departments=db.Department.get_all_departments(),
                edit=True,
                employee=db.Employee(db.Employee.get_id_by_name(emp)),
                titles=db.get_all_titles(),
                programs=db.get_all_programs(),
            )

        case "POST":

            name = request.form.get("name")
            title = request.form.get("title")
            pref_dep = request.form.get("def_dep")

            db.Employee(db.Employee.get_id_by_name(emp)).update(name, title, pref_dep)

            flash("Updated Department Successfully!")

            return redirect(url_for("edit_objects"))


@app.route("/delete/program/<program>")
def delete_program(program):
    if not auth():
        return redirect(url_for("login_page"))

    db_obj, c = db.connect()

    program = db.remove_from_string(program)

    c.execute(
        "SELECT schedule_json FROM schedules WHERE user_id=%s", [session["parent_id"]]
    )
    remove = True
    for schedule in c.fetchall():

        if program.strip() in schedule[0]:
            remove = False
            break

    if remove:
        flash(f"`{program}` Deleted Successfully")

        c.execute("DELETE FROM programs WHERE name=%s ", [program])
        db_obj.commit()
    else:
        flash(f"`{program}` Could not be deleted because it is used in a Schedule!.")
    return redirect(url_for("edit_objects"))


@app.route("/delete/title/<title>")
def delete_title(title):
    if not auth():
        return redirect(url_for("login_page"))

    db_obj, c = db.connect()

    title = db.remove_from_string(title).strip()

    c.execute(
        "SELECT id, name, title FROM employees WHERE user_id=%s", [session["parent_id"]]
    )

    remove = True
    for emp in c.fetchall():

        if remove == False:
            break

        remove = not emp[2].strip() == db.remove_from_string(title).strip()

    if remove:
        title = db.remove_from_string(title)
        flash(f"`{title}` Deleted Successfully")
        c.execute("DELETE FROM titles WHERE name=%s ", [title])
        db_obj.commit()
    else:
        flash(f"`{title}` couldnt be deleted because its used in an Employee!")

    return redirect(url_for("edit_objects"))


@app.route("/delete/kitchen/<kitchen>")
def delete_kitchen(kitchen):
    if not auth():
        return redirect(url_for("login_page"))

    kitchen = db.remove_from_string(kitchen).strip()

    dbe, c = db.connect()

    c.execute("SELECT id FROM employees")
    remove = True
    for emp in c.fetchall():

        if not remove:
            break

        empl = db.Employee(emp[0])

        remove = not db.remove_from_string(kitchen).strip() in empl.prefered_dep_str

    if remove:
        db_obj, c = db.connect()
        kitchen = db.remove_from_string(kitchen)
        flash(f"`{kitchen}` Deleted Successfully")
        c.execute("DELETE FROM big_kitchens WHERE name=%s ", [kitchen])
        db_obj.commit()

    else:
        flash(f"`{kitchen}` could not be deleted because its used in an Employee!")

    return redirect(url_for("edit_objects"))


@app.route("/delete/department/<department>")
def delete_department(department):
    if not auth():
        return redirect(url_for("login_page"))
    dbe, c = db.connect()

    department = db.remove_from_string(department).strip()

    c.execute("SELECT id FROM employees")
    remove = True
    for emp in c.fetchall():

        if not remove:
            break

        empl = db.Employee(emp[0])

        remove = not department.strip() in empl.prefered_dep_str

    if remove:

        db_obj, c = db.connect()
        department = db.remove_from_string(department)
        flash(
            f"`{department}` Deleted Successfully. Make sure to edit Employees that were assigned to that department!"
        )
        c.execute("DELETE FROM sub_department WHERE name=%s ", [department])
        db_obj.commit()

    else:
        flash(f"`{department}` could not be deleted because its used in an Employee!")

    return redirect(url_for("edit_objects"))


@app.route("/delete/employee/<employee>")
def delete_employee(employee):
    if not auth():
        return redirect(url_for("login_page"))

    emp_name = db.remove_from_string(employee).strip()

    db_obj, c = db.connect()

    empl = db.Employee(db.Employee.get_id_by_name(emp_name))

    if empl == None:
        flash("Error Deleting Employee")
        return redirect(url_for("edit_objects"))

    empl.copy_to_archive()
    c.execute("DELETE FROM employees WHERE id=%s ", [empl.id])
    flash(f"`{emp_name}` Deleted Successfully")
    db_obj.commit()

    return redirect(url_for("edit_objects"))


@app.route("/table")
@app.route("/table/<week>")
def table(week=None):
    if not auth():
        return redirect(url_for("login_page"))

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
                "table.html",
                session=session,
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
    if not auth():
        return redirect(url_for("login_page"))

    return f"{d_start}/{m_start}/{y_start} - {d_end}/{m_end}/{y_end}"


@app.route("/login", methods=["GET", "POST"])
def login_page():

    match request.method:

        case "POST":
            user = db.User.login(request.form.get("email"), request.form.get("pass"))
            if isinstance(user, db.User):
                flash("Login Successful!")
                session["auth"] = True
                session["user_id"] = user.id
                session["user_name"] = user.name
                session["user_email"] = user.email
                session["user_role"] = user.role
                session["user_admin"] = user.admin
                session["user_owner"] = user.owner
                session["parent_id"] = user.parent_id

                return redirect(url_for("index"))

            else:
                flash(user)
                return redirect(url_for("login_page"))

        case "GET":

            return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register_page():
    if not admin():
        return redirect(url_for("login_page"))

    match request.method:

        case "GET":

            return render_template("register.html", session=session)

        case "POST":

            name = request.form.get("name")
            role = request.form.get("role")
            email = request.form.get("email")
            password = request.form.get("name")
            is_admin = {True: 1, False: 2}[request.form.get("is_admin") == "on"]

            if not db.User.check_email_valid(email):

                flash("Email is not Valid or already in Use!")
                return redirect(url_for("edit_objects"))

            db.User.register_user(
                name, role, email, password, is_admin, 0, session["user_id"]
            )

            flash(f"User `{name}` Succesfully Created!")

            return redirect(url_for("edit_objects"))


@app.route("/logout")
def logout():

    session.clear()

    session["start"] = time.time()

    flash("Successfully Logged Out!")

    return redirect(url_for("login_page"))


@app.route("/create_objects/<page>", methods=["GET", "POST"])
def object_startup(page):

    match request.method:

        case "GET":
            all_departments = db.get_all_departments()
            all_programs = db.get_all_programs()
            all_titles = db.get_all_titles()
            employee_departments = db.Department.get_all_departments()
            return render_template(
                "object_startup.html",
                session=session,
                title="Startup Objects",
                page=page,
                object_name={
                    "1": "department",
                    "2": "kitchen",
                    "3": "program",
                    "4": "title",
                    "5": "employee",
                },
                departments=all_departments,
                programs=all_programs,
                titles=all_titles,
                employee_departments=employee_departments,
                edit=False,
            )

        case "POST":

            match request.form.get("add_type"):

                case "department":

                    db.create_dept(request.form.get("name"))

                    flash("Department Created Successfully!")

                    return redirect(url_for("object_startup", page=page))

                case "kitchen":

                    name, deps = request.form.get("name"), []
                    for key in request.form:
                        if key == "name" or key == "submit" or key == "add_type":
                            continue
                        deps.append(request.form.get(key))

                    db.Kitchen.create_kitchen(name, deps)

                    flash("Created Kitchen Successfully!")
                    return redirect(url_for("object_startup", page=page))

                case "program":

                    db.add_program(request.form.get("name"))

                    flash("Program Created Successfully!")
                    return redirect(url_for("object_startup", page=page))

                case "title":

                    db.create_title(request.form.get("name"))

                    flash("Title Created Successfully!")
                    return redirect(url_for("object_startup", page=page))

                case "employee":

                    name, title, def_dep = (
                        request.form.get("name"),
                        request.form.get("title"),
                        request.form.get("def_dep"),
                    )

                    db.Employee.create_employee(name, title, def_dep)

                    flash("Employee Created Successfully!")
                    return redirect(url_for("object_startup", page=page))

                case _:

                    flash(f"Page #{page} is not valid!")

                    return redirect(url_for("object_startup", page=page))


@app.route("/save_department", methods=["POST"])
def save_department():
    if not auth():
        return redirect(url_for("login_page"))

    data = request.json
    print("Received data:", data)  # Debug statement to check received data

    try:
        dbe, c = db.connect()
        c.execute(
            "UPDATE sub_department SET name=%s WHERE id=%s",
            [data["new_name"], data["id"]],
        )

        old_dep = db.Department(data["id"])
        name = data["new_name"]

        c.execute("SELECT id, default_dep,name FROM employees")

        emps = c.fetchall()

        for emp in emps:

            empid = emp[0]

            empname = emp[2]

            def_dep_kitch, def_dep = emp[1].split(" - ")

            if old_dep.name == def_dep:
                c.execute(
                    "UPDATE employees SET default_dep=%s WHERE id=%s",
                    [f"{def_dep_kitch} - {name}", empid],
                )

                dbe.commit()
                flash(f"Updated Department in Employee `{empname}`")

        c.execute(
            "SELECT id, week, schedule_json FROM schedules WHERE user_id=%s ",
            [session["parent_id"]],
        )

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

                        new_js[kitchen_key][name] = []

                        for ls in sched_json[kitchen_key][dep_key]:
                            new_js[kitchen_key][name].append(ls)

                    else:
                        new_js[kitchen_key][dep_key] = sched_json[kitchen_key][dep_key]

            c.execute(
                "UPDATE schedules SET schedule_json=%s WHERE id=%s",
                [str(new_js), week_id],
            )
            dbe.commit()

            flash(f"Week `{week_name}` updated for department name change")

        dbe.commit()
        return jsonify({"status": "success"})
    except Exception as e:
        print("Error:", e)  # Debug statement to check the error
        return jsonify({"status": "error", "message": str(e)})
    finally:
        c.close()
        dbe.close()


@app.route("/save_kitchen", methods=["POST"])
def save_kitchen():
    if not auth():
        return redirect(url_for("login_page"))

    data = request.json
    print("Received data:", data)  # Debug statement to check received data

    try:
        dbe, c = db.connect()
        c.execute(
            "UPDATE big_kitchens SET name=%s WHERE id=%s",
            [data["new_name"], data["id"]],
        )

        name = data["new_name"]
        k = db.Kitchen(data["id"])

        db_obj, c = db.connect()
        if k.name != name:

            c.execute(
                "SELECT id, default_dep, name FROM employees WHERE user_id=%s",
                [session["parent_id"]],
            )

            emps = c.fetchall()

            for emp in emps:

                empid = emp[0]
                emp_def_kitch, emp_def_dep = emp[1].split(" - ")
                empname = emp[2]

                if emp_def_kitch == k.name:
                    c.execute(
                        "UPDATE employees SET default_dep=%s WHERE id=%s",
                        [f"{name} - {emp_def_dep}", empid],
                    )
                    db_obj.commit()

                    flash(f"Updated Employee `{empname}`")

        c.execute(
            "SELECT id, week, schedule_json FROM schedules WHERE user_id=%s ",
            [session["parent_id"]],
        )

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

            c.execute(
                "UPDATE schedules SET schedule_json=%s WHERE id=%s",
                [str(new_js), week_id],
            )
            db_obj.commit()

            flash(f"Week `{week_name}` updated for Kitchen name change")

        dbe.commit()

        return jsonify({"status": "success"})
    except Exception as e:
        print("Error:", e)  # Debug statement to check the error
        return jsonify({"status": "error", "message": str(e)})
    finally:
        c.close()
        dbe.close()


@app.route("/save_program", methods=["POST"])
def save_program():
    if not auth():
        return redirect(url_for("login_page"))

    data = request.json
    print("Received data:", data)  # Debug statement to check received data

    try:
        dbe, c = db.connect()
        c.execute(
            "UPDATE programs SET name=%s WHERE id=%s", [data["new_name"], data["id"]]
        )
        dbe.commit()
        return jsonify({"status": "success"})
    except Exception as e:
        print("Error:", e)  # Debug statement to check the error
        return jsonify({"status": "error", "message": str(e)})
    finally:
        c.close()
        dbe.close()


@app.route("/save_title", methods=["POST"])
def save_title():
    if not auth():
        return redirect(url_for("login_page"))

    data = request.json
    print("Received data:", data)  # Debug statement to check received data

    try:
        dbe, c = db.connect()
        c.execute(
            "UPDATE titles SET name=%s WHERE id=%s", [data["new_name"], data["id"]]
        )
        dbe.commit()
        return jsonify({"status": "success"})
    except Exception as e:
        print("Error:", e)  # Debug statement to check the error
        return jsonify({"status": "error", "message": str(e)})
    finally:
        c.close()
        dbe.close()


@app.route("/save_emp_name", methods=["POST"])
def save_emp_name():
    if not auth():
        return redirect(url_for("login_page"))

    data = request.json
    print("Received data:", data)  # Debug statement to check received data

    try:
        dbe, c = db.connect()
        c.execute(
            "UPDATE employees SET name=%s WHERE id=%s", [data["new_name"], data["id"]]
        )
        dbe.commit()
        return jsonify({"status": "success"})
    except Exception as e:
        print("Error:", e)  # Debug statement to check the error
        return jsonify({"status": "error", "message": str(e)})
    finally:
        c.close()
        dbe.close()


@app.route("/save_emp_title", methods=["POST"])
def save_emp_title():
    if not auth():
        return redirect(url_for("login_page"))

    data = request.json
    print("Received data:", data)  # Debug statement to check received data

    try:
        dbe, c = db.connect()
        c.execute(
            "UPDATE employees SET title=%s WHERE id=%s", [data["new_name"], data["id"]]
        )
        dbe.commit()
        return jsonify({"status": "success"})
    except Exception as e:
        print("Error:", e)  # Debug statement to check the error
        return jsonify({"status": "error", "message": str(e)})
    finally:
        c.close()
        dbe.close()


@app.route("/save_emp_pref_dep", methods=["POST"])
def save_emp_pref_dep():
    if not auth():
        return redirect(url_for("login_page"))

    data = request.json
    print("Received data:", data)  # Debug statement to check received data

    try:
        dbe, c = db.connect()
        c.execute(
            "UPDATE employees SET default_dep=%s WHERE id=%s",
            [data["new_name"], data["id"]],
        )
        dbe.commit()
        return jsonify({"status": "success"})
    except Exception as e:
        print("Error:", e)  # Debug statement to check the error
        return jsonify({"status": "error", "message": str(e)})
    finally:
        c.close()
        dbe.close()
        
@app.route('/save_table_excel', methods=['GET', 'POST'])
def save_table_excel():
    if not auth():
        return redirect(url_for("login_page"))
    
    data = dict(request.json)
    rows = []
    week_name= ''
    for location, events in data.items():
        if location == 'week':
            week_name = events.replace('(', '').replace(')', '')
            continue
        rows.append({'Name' : location})
        for event, details in events.items():
            rows.append({'Name' : event})
            if details:  # Check if the event has details
                
                for detail in details:
                
                    print(details)
                    employee_name = detail[0]

                    for i, days_info in enumerate(detail[1]):
                        row = {
                            "Name": f"{employee_name if i == 0 else f'Split {i}'}",
                            "Monday": days_info.get("monday", ["", ""])[0],
                            "Change M": days_info.get("monday", ["", ""])[1],
                            "Tuesday": days_info.get("tuesday", ["", ""])[0],
                            "Change T": days_info.get("tuesday", ["", ""])[1],
                            "Wednesday": days_info.get("wednesday", ["", ""])[0],
                            "Change W": days_info.get("wednesday", ["", ""])[1],
                            "Thursday": days_info.get("thursday", ["", ""])[0],
                            "Change Tu": days_info.get("thursday", ["", ""])[1],
                            "Friday": days_info.get("friday", ["", ""])[0],
                            "Change F": days_info.get("friday", ["", ""])[1],
                            "Saturday": days_info.get("saturday", ["", ""])[0],
                            "Change Sa": days_info.get("saturday", ["", ""])[1],
                            "Sunday": days_info.get("sunday", ["", ""])[0],
                            "Change Su": days_info.get("sunday", ["", ""])[1]
                    }
                        rows.append(row)

    # Create DataFrame
    df = pd.DataFrame(rows)
    
    excel_buffer = BytesIO()
    df.to_excel(excel_buffer, index=False)

    # Get the binary content of the file
    excel_buffer.seek(0)
    excel_data = excel_buffer.read()
    
    response = make_response(excel_data)
    response.headers['Content-Disposition'] = 'attachment; filename=report.xlsx'
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    
    return response
    
    
    
    
    # output = io.BytesIO()
    # with pd.ExcelWriter(output, engine='openpyxl') as writer:
    #     df.to_excel(writer, index=False)
    # output.seek(0)
    
    # df.to_excel('fwaeh.xlsx')
    
    # print(df.head(150))
    
    # return send_file(
    #     output,
    #     as_attachment=True,
    #     download_name  =f"{week_name}.xlsx",
    #     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    # )
    
@app.route('/change_kitchen_row', methods=['GET', 'POST'])
def save_kitchen_row():
    if not auth():
        return redirect(url_for("login_page"))
    
    match request.method:
        
        case 'GET':
            
            return render_template('kitchen_row.html', kitchens = db.Kitchen.get_all_kitchens(True))
        
        case 'POST':
            
            dbe,c = db.connect()
            
            for kitchen_id in request.form:
                
                row = request.form.get(kitchen_id)
                
                c.execute('UPDATE big_kitchens SET row=%s WHERE id=%s', [kitchen_id, row])
                
            dbe.commit()
            
            return redirect(url_for('save_kitchen_row'))


if __name__ == "__main__":
    app.run()
=======
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
    make_response,
    send_file,
)
from datetime import timedelta, datetime

import db

import json

import time

import pandas as pd

from io import BytesIO

# Create an instance of the Flask class
app = Flask(__name__)

app.config["SECRET_KEY"] = "very_secret_key_12351232"

app.config.update(SESSION_PERMANENT=True, SESSION_TYPE="filesystem")


def auth():
    if "auth" in session:
        return session["auth"]
    else:
        return False


def admin():

    if auth():
        return session["user_admin"]
    else:
        return False


def get_next_seven_days(start_date_str):
    start_date = datetime.strptime(start_date_str, "%d/%m/%Y")
    next_seven_days = [
        (start_date + timedelta(days=i)).strftime("%d/%m/%Y") for i in range(8)
    ][0:7]
    return next_seven_days


@app.before_request
def before_request_func():

    session["start"] = time.time()

    if "user_id" in session:
        db.USER_ID = session["parent_id"]

    if "auth" in session and session["auth"]:

        dbe, c = db.connect()
        stuff = []
        c.execute("SELECT * FROM employees WHERE user_id = %s", [session["parent_id"]])
        stuff.append(c.fetchall())
        c.execute("SELECT * FROM titles WHERE user_id = %s", [session["parent_id"]])
        stuff.append(c.fetchall())
        c.execute(
            "SELECT * FROM sub_department WHERE user_id = %s", [session["parent_id"]]
        )
        stuff.append(c.fetchall())
        c.execute(
            "SELECT * FROM big_kitchens WHERE user_id = %s", [session["parent_id"]]
        )
        stuff.append(c.fetchall())
        c.execute(
            "SELECT * FROM large_department WHERE user_id = %s", [session["parent_id"]]
        )
        stuff.append(c.fetchall())
        c.execute("SELECT * FROM programs WHERE user_id = %s", [session["parent_id"]])
        stuff.append(c.fetchall())



        session["hide_edit"] = False
        for thing in stuff:
            if len(thing) > 0:
                break

        else:
            session["hide_edit"] = True


@app.after_request
def after_request_func(response):

    if __name__ == "__main__":
        print(time.time() - session["start"])
    return response


@app.route("/")
def index():
    if not auth():
        return redirect(url_for("login_page"))

    return render_template(
        "index.html",
        session=session,
    )


@app.route("/add_kitchen", methods=["GET", "POST"])
def add_kitchen():

    if not auth():
        return redirect(url_for("login_page"))

    match request.method:
        case "GET":
            return render_template(
                "add_kitchen.html",
                session=session,
                departments=db.get_all_departments(),
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

    if not auth():
        return redirect(url_for("login_page"))
    match request.method:
        case "GET":
            return render_template(
                "add_deps.html",
                session=session,
            )

        case "POST":

            db.create_dept(request.form.get("name"))

            flash("Created Department Successfully!")

            return redirect(url_for("edit_objects"))


@app.route("/add_title", methods=["GET", "POST"])
def add_title():
    if not auth():
        return redirect(url_for("login_page"))
    match request.method:
        case "GET":
            return render_template(
                "add_title.html",
                session=session,
            )

        case "POST":

            db.create_title(request.form.get("name"))

            flash("Created Title Successfully!")

            return redirect(url_for("edit_objects"))


@app.route("/save_schedule", methods=["POST"])
def save_schedule():
    if not auth():
        return redirect(url_for("login_page"))
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
    if not auth():
        return redirect(url_for("login_page"))
    match request.method:

        case "GET":

            all_departments = db.Department.get_all_departments()
            all_programs = db.get_all_programs()
            all_titles = db.get_all_titles()

            return render_template(
                "add_employee.html",
                session=session,
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

            employee = db.Employee.create_employee(name, title, def_dep)

            dbe, c = db.connect()

            c.execute(
                "SELECT * FROM schedules WHERE user_id=%s", [session["parent_id"]]
            )
            kitch, dep = employee.prefered_dep
            for sched in c.fetchall():

                ide = sched[0]
                week = sched[1]
                js = json.loads(sched[2].replace("'", '"'))

                program = db.get_random_program()

                for kitchen in js:

                    if kitchen == kitch:

                        for department in js[kitchen]:

                            if department == dep:

                                js[kitchen][department].append(
                                    [
                                        employee.id,
                                        [
                                            {
                                                "monday": [program, ""],
                                                "tuesday": [program, ""],
                                                "wednesday": [program, ""],
                                                "thursday": [program, ""],
                                                "friday": [program, ""],
                                                "saturday": [program, ""],
                                                "sunday": [program, ""],
                                            }
                                        ],
                                    ]
                                )

                flash(f"Added into `{week}` Schedule")
                c.execute(
                    "UPDATE schedules SET schedule_json =%s WHERE id=%s", [str(js), ide]
                )

                dbe.commit()

            flash("Added Employee Successfully!")
            return redirect(url_for("edit_objects"))


@app.route("/add_program", methods=["GET", "POST"])
def create_program():
    if not auth():
        return redirect(url_for("login_page"))
    match request.method:
        case "GET":

            return render_template(
                "add_program.html",
                session=session,
            )

        case "POST":

            name = request.form.get("name")

            db.add_program(name)

            flash("Program Created")

            return redirect(url_for("edit_objects"))


@app.route("/edit_objects")
def edit_objects():
    if not auth():
        return redirect(url_for("login_page"))
    all_kitchens = db.Kitchen.get_all_kitchens(True)
    all_departments = db.get_all_departments(True)

    employee_departments = db.Department.get_all_departments()
    all_employees = db.Employee.get_all_employees()
    all_programs = db.get_all_programs(True)
    all_titles = db.get_all_titles(True)

    dbe, c = db.connect()

    c.execute("SELECT * FROM schedules WHERE user_id=%s", [session["parent_id"]])
    all_schedules = []

    for thing in c.fetchall():

        week_name = thing[1]

        day_start = week_name.split("-")[2].strip()
        day_end = week_name.split("-")[5].split(")")[0]

        month_start = week_name.split("-")[1]
        month_end = week_name.split("-")[4]

        year_start = week_name.split("-")[0].split("(")[1]
        year_end = week_name.split("-")[3].strip()

        url_time = (
            f"{day_start}_{month_start}_{year_start}_{day_end}_{month_end}_{year_end}"
        )

        all_schedules.append(
            [
                thing[0],
                thing[1],
                thing[2],
                url_time,
            ]
        )

    return render_template(
        "edit_objects.html",
        session=session,
        kitchens=all_kitchens,
        departments=all_departments,
        employees=all_employees,
        programs=all_programs,
        titles=all_titles,
        employee_departments=employee_departments,
        schedules=all_schedules,
    )


@app.route("/delete/table/<ide>")
def delete_table(ide):

    dbe, c = db.connect()

    c.execute("DELETE FROM schedules WHERE id=%s", [ide])

    dbe.commit()

    flash(f"Deleted Schedule ID-`{ide}`!")

    return redirect(url_for("edit_objects"))


@app.route("/edit/kitchen/<kitchen>", methods=["GET", "POST"])
def edit_kitchen(kitchen):
    if not auth():
        return redirect(url_for("login_page"))
    match request.method:
        case "GET":
            return render_template(
                "add_kitchen.html",
                session=session,
                departments=db.get_all_departments(),
                edit=True,
                kitchen=db.Kitchen(db.Kitchen.get_id_from_name(kitchen)),
            )

        case "POST":

            name, deps = request.form.get("name"), []
            for key in request.form:
                if key == "name" or key == "submit" or key == "id":
                    continue
                deps.append(request.form.get(key))

            k = db.Kitchen(db.Kitchen.get_id_from_name(kitchen))

            db_obj, c = db.connect()
            if k.name != name:

                c.execute("SELECT id, default_dep, name FROM employees")

                emps = c.fetchall()

                for emp in emps:

                    empid = emp[0]
                    emp_def_kitch, emp_def_dep = emp[1].split(" - ")
                    empname = emp[2]

                    if emp_def_kitch == k.name:
                        c.execute(
                            "UPDATE employees SET default_dep=%s WHERE id=%s",
                            [f"{name} - {emp_def_dep}", empid],
                        )
                        db_obj.commit()

                        flash(f"Updated Employee `{empname}`")

            c.execute(
                "SELECT id, week, schedule_json FROM schedules WHERE user_id=%s ",
                [session["parent_id"]],
            )

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

                c.execute(
                    "UPDATE schedules SET schedule_json=%s WHERE id=%s",
                    [str(new_js), week_id],
                )
                db_obj.commit()

                flash(f"Week `{week_name}` updated for Kitchen name change")

            k.update(name, deps)

            flash("Updated Kitchen Successfully!")

            return redirect(url_for("edit_objects"))


@app.route("/edit/department/<dep>", methods=["GET", "POST"])
def edit_department(dep):
    if not auth():
        return redirect(url_for("login_page"))
    match request.method:
        case "GET":
            return render_template(
                "add_deps.html",
                session=session,
                departments=db.get_all_departments(),
                edit=True,
                department=db.Department(db.Department.get_id_from_name(dep)),
            )

        case "POST":

            name = request.form.get("name")

            old_dep = db.Department(db.Department.get_id_from_name(dep))

            db_obj, c = db.connect()

            c.execute("SELECT id, default_dep,name FROM employees")

            emps = c.fetchall()

            for emp in emps:

                empid = emp[0]

                empname = emp[2]

                def_dep_kitch, def_dep = emp[1].split(" - ")

                if old_dep.name == def_dep:
                    c.execute(
                        "UPDATE employees SET default_dep=%s WHERE id=%s",
                        [f"{def_dep_kitch} - {name}", empid],
                    )

                    db_obj.commit()
                    flash(f"Updated Department in Employee `{empname}`")

            c.execute(
                "SELECT id, week, schedule_json FROM schedules WHERE user_id=%s ",
                [session["parent_id"]],
            )

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

                            new_js[kitchen_key][name] = []

                            for ls in sched_json[kitchen_key][dep_key]:
                                new_js[kitchen_key][name].append(ls)

                        else:

                            new_js[kitchen_key][dep_key] = sched_json[kitchen_key][
                                dep_key
                            ]

                c.execute(
                    "UPDATE schedules SET schedule_json=%s WHERE id=%s",
                    [str(new_js), week_id],
                )
                db_obj.commit()

                flash(f"Week `{week_name}` updated for department name change")

            old_dep.update(name)

            flash("Updated Department Successfully!")

            return redirect(url_for("edit_objects"))


@app.route("/edit/employee/<emp>", methods=["GET", "POST"])
def edit_demployee(emp):
    if not auth():
        return redirect(url_for("login_page"))
    match request.method:
        case "GET":

            return render_template(
                "add_employee.html",
                session=session,
                departments=db.Department.get_all_departments(),
                edit=True,
                employee=db.Employee(db.Employee.get_id_by_name(emp)),
                titles=db.get_all_titles(),
                programs=db.get_all_programs(),
            )

        case "POST":

            name = request.form.get("name")
            title = request.form.get("title")
            pref_dep = request.form.get("def_dep")

            db.Employee(db.Employee.get_id_by_name(emp)).update(name, title, pref_dep)

            flash("Updated Department Successfully!")

            return redirect(url_for("edit_objects"))


@app.route("/delete/program/<program>")
def delete_program(program):
    if not auth():
        return redirect(url_for("login_page"))

    db_obj, c = db.connect()

    program = db.remove_from_string(program)

    c.execute(
        "SELECT schedule_json FROM schedules WHERE user_id=%s", [session["parent_id"]]
    )
    remove = True
    for schedule in c.fetchall():

        if program.strip() in schedule[0]:
            remove = False
            break

    if remove:
        flash(f"`{program}` Deleted Successfully")

        c.execute("DELETE FROM programs WHERE name=%s ", [program])
        db_obj.commit()
    else:
        flash(f"`{program}` Could not be deleted because it is used in a Schedule!.")
    return redirect(url_for("edit_objects"))


@app.route("/delete/title/<title>")
def delete_title(title):
    if not auth():
        return redirect(url_for("login_page"))

    db_obj, c = db.connect()

    title = db.remove_from_string(title).strip()

    c.execute(
        "SELECT id, name, title FROM employees WHERE user_id=%s", [session["parent_id"]]
    )

    remove = True
    for emp in c.fetchall():

        if remove == False:
            break

        remove = not emp[2].strip() == db.remove_from_string(title).strip()

    if remove:
        title = db.remove_from_string(title)
        flash(f"`{title}` Deleted Successfully")
        c.execute("DELETE FROM titles WHERE name=%s ", [title])
        db_obj.commit()
    else:
        flash(f"`{title}` couldnt be deleted because its used in an Employee!")

    return redirect(url_for("edit_objects"))


@app.route("/delete/kitchen/<kitchen>")
def delete_kitchen(kitchen):
    if not auth():
        return redirect(url_for("login_page"))

    kitchen = db.remove_from_string(kitchen).strip()

    dbe, c = db.connect()

    c.execute("SELECT id FROM employees")
    remove = True
    for emp in c.fetchall():

        if not remove:
            break

        empl = db.Employee(emp[0])

        remove = not db.remove_from_string(kitchen).strip() in empl.prefered_dep_str

    if remove:
        db_obj, c = db.connect()
        kitchen = db.remove_from_string(kitchen)
        flash(f"`{kitchen}` Deleted Successfully")
        c.execute("DELETE FROM big_kitchens WHERE name=%s ", [kitchen])
        db_obj.commit()

    else:
        flash(f"`{kitchen}` could not be deleted because its used in an Employee!")

    return redirect(url_for("edit_objects"))


@app.route("/delete/department/<department>")
def delete_department(department):
    if not auth():
        return redirect(url_for("login_page"))
    dbe, c = db.connect()

    department = db.remove_from_string(department).strip()

    c.execute("SELECT id FROM employees")
    remove = True
    for emp in c.fetchall():

        if not remove:
            break

        empl = db.Employee(emp[0])

        remove = not department.strip() in empl.prefered_dep_str

    if remove:

        db_obj, c = db.connect()
        department = db.remove_from_string(department)
        flash(
            f"`{department}` Deleted Successfully. Make sure to edit Employees that were assigned to that department!"
        )
        c.execute("DELETE FROM sub_department WHERE name=%s ", [department])
        db_obj.commit()

    else:
        flash(f"`{department}` could not be deleted because its used in an Employee!")

    return redirect(url_for("edit_objects"))


@app.route("/delete/employee/<employee>")
def delete_employee(employee):
    if not auth():
        return redirect(url_for("login_page"))

    emp_name = db.remove_from_string(employee).strip()

    db_obj, c = db.connect()

    empl = db.Employee(db.Employee.get_id_by_name(emp_name))

    if empl == None:
        flash("Error Deleting Employee")
        return redirect(url_for("edit_objects"))

    empl.copy_to_archive()
    c.execute("DELETE FROM employees WHERE id=%s ", [empl.id])
    flash(f"`{emp_name}` Deleted Successfully")
    db_obj.commit()

    return redirect(url_for("edit_objects"))


@app.route("/table")
@app.route("/table/<week>")
def table(week=None):
    if not auth():
        return redirect(url_for("login_page"))

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
                "table.html",
                session=session,
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
    if not auth():
        return redirect(url_for("login_page"))

    return f"{d_start}/{m_start}/{y_start} - {d_end}/{m_end}/{y_end}"


@app.route("/login", methods=["GET", "POST"])
def login_page():

    match request.method:

        case "POST":
            user = db.User.login(request.form.get("email"), request.form.get("pass"))
            if isinstance(user, db.User):
                flash("Login Successful!")
                session["auth"] = True
                session["user_id"] = user.id
                session["user_name"] = user.name
                session["user_email"] = user.email
                session["user_role"] = user.role
                session["user_admin"] = user.admin
                session["user_owner"] = user.owner
                session["parent_id"] = user.parent_id

                return redirect(url_for("index"))

            else:
                flash(user)
                return redirect(url_for("login_page"))

        case "GET":

            return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register_page():
    if not admin():
        return redirect(url_for("login_page"))

    match request.method:

        case "GET":

            return render_template("register.html", session=session)

        case "POST":

            name = request.form.get("name")
            role = request.form.get("role")
            email = request.form.get("email")
            password = request.form.get("name")
            is_admin = {True: 1, False: 2}[request.form.get("is_admin") == "on"]

            if not db.User.check_email_valid(email):

                flash("Email is not Valid or already in Use!")
                return redirect(url_for("edit_objects"))

            db.User.register_user(
                name, role, email, password, is_admin, 0, session["user_id"]
            )

            flash(f"User `{name}` Succesfully Created!")

            return redirect(url_for("edit_objects"))


@app.route("/logout")
def logout():

    session.clear()

    session["start"] = time.time()

    flash("Successfully Logged Out!")

    return redirect(url_for("login_page"))


@app.route("/create_objects/<page>", methods=["GET", "POST"])
def object_startup(page):

    match request.method:

        case "GET":
            all_departments = db.get_all_departments()
            all_programs = db.get_all_programs()
            all_titles = db.get_all_titles()
            employee_departments = db.Department.get_all_departments()
            return render_template(
                "object_startup.html",
                session=session,
                title="Startup Objects",
                page=page,
                object_name={
                    "1": "department",
                    "2": "kitchen",
                    "3": "program",
                    "4": "title",
                    "5": "employee",
                },
                departments=all_departments,
                programs=all_programs,
                titles=all_titles,
                employee_departments=employee_departments,
                edit=False,
            )

        case "POST":

            match request.form.get("add_type"):

                case "department":

                    db.create_dept(request.form.get("name"))

                    flash("Department Created Successfully!")

                    return redirect(url_for("object_startup", page=page))

                case "kitchen":

                    name, deps = request.form.get("name"), []
                    for key in request.form:
                        if key == "name" or key == "submit" or key == "add_type":
                            continue
                        deps.append(request.form.get(key))

                    db.Kitchen.create_kitchen(name, deps)

                    flash("Created Kitchen Successfully!")
                    return redirect(url_for("object_startup", page=page))

                case "program":

                    db.add_program(request.form.get("name"))

                    flash("Program Created Successfully!")
                    return redirect(url_for("object_startup", page=page))

                case "title":

                    db.create_title(request.form.get("name"))

                    flash("Title Created Successfully!")
                    return redirect(url_for("object_startup", page=page))

                case "employee":

                    name, title, def_dep = (
                        request.form.get("name"),
                        request.form.get("title"),
                        request.form.get("def_dep"),
                    )

                    db.Employee.create_employee(name, title, def_dep)

                    flash("Employee Created Successfully!")
                    return redirect(url_for("object_startup", page=page))

                case _:

                    flash(f"Page #{page} is not valid!")

                    return redirect(url_for("object_startup", page=page))


@app.route("/save_department", methods=["POST"])
def save_department():
    if not auth():
        return redirect(url_for("login_page"))

    data = request.json
    print("Received data:", data)  # Debug statement to check received data

    try:
        dbe, c = db.connect()
        c.execute(
            "UPDATE sub_department SET name=%s WHERE id=%s",
            [data["new_name"], data["id"]],
        )

        old_dep = db.Department(data["id"])
        name = data["new_name"]

        c.execute("SELECT id, default_dep,name FROM employees")

        emps = c.fetchall()

        for emp in emps:

            empid = emp[0]

            empname = emp[2]

            def_dep_kitch, def_dep = emp[1].split(" - ")

            if old_dep.name == def_dep:
                c.execute(
                    "UPDATE employees SET default_dep=%s WHERE id=%s",
                    [f"{def_dep_kitch} - {name}", empid],
                )

                dbe.commit()
                flash(f"Updated Department in Employee `{empname}`")

        c.execute(
            "SELECT id, week, schedule_json FROM schedules WHERE user_id=%s ",
            [session["parent_id"]],
        )

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

                        new_js[kitchen_key][name] = []

                        for ls in sched_json[kitchen_key][dep_key]:
                            new_js[kitchen_key][name].append(ls)

                    else:
                        new_js[kitchen_key][dep_key] = sched_json[kitchen_key][dep_key]

            c.execute(
                "UPDATE schedules SET schedule_json=%s WHERE id=%s",
                [str(new_js), week_id],
            )
            dbe.commit()

            flash(f"Week `{week_name}` updated for department name change")

        dbe.commit()
        return jsonify({"status": "success"})
    except Exception as e:
        print("Error:", e)  # Debug statement to check the error
        return jsonify({"status": "error", "message": str(e)})
    finally:
        c.close()
        dbe.close()


@app.route("/save_kitchen", methods=["POST"])
def save_kitchen():
    if not auth():
        return redirect(url_for("login_page"))

    data = request.json
    print("Received data:", data)  # Debug statement to check received data

    try:
        dbe, c = db.connect()
        c.execute(
            "UPDATE big_kitchens SET name=%s WHERE id=%s",
            [data["new_name"], data["id"]],
        )

        name = data["new_name"]
        k = db.Kitchen(data["id"])

        db_obj, c = db.connect()
        if k.name != name:

            c.execute(
                "SELECT id, default_dep, name FROM employees WHERE user_id=%s",
                [session["parent_id"]],
            )

            emps = c.fetchall()

            for emp in emps:

                empid = emp[0]
                emp_def_kitch, emp_def_dep = emp[1].split(" - ")
                empname = emp[2]

                if emp_def_kitch == k.name:
                    c.execute(
                        "UPDATE employees SET default_dep=%s WHERE id=%s",
                        [f"{name} - {emp_def_dep}", empid],
                    )
                    db_obj.commit()

                    flash(f"Updated Employee `{empname}`")

        c.execute(
            "SELECT id, week, schedule_json FROM schedules WHERE user_id=%s ",
            [session["parent_id"]],
        )

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

            c.execute(
                "UPDATE schedules SET schedule_json=%s WHERE id=%s",
                [str(new_js), week_id],
            )
            db_obj.commit()

            flash(f"Week `{week_name}` updated for Kitchen name change")

        dbe.commit()

        return jsonify({"status": "success"})
    except Exception as e:
        print("Error:", e)  # Debug statement to check the error
        return jsonify({"status": "error", "message": str(e)})
    finally:
        c.close()
        dbe.close()


@app.route("/save_program", methods=["POST"])
def save_program():
    if not auth():
        return redirect(url_for("login_page"))

    data = request.json
    print("Received data:", data)  # Debug statement to check received data

    try:
        dbe, c = db.connect()
        c.execute(
            "UPDATE programs SET name=%s WHERE id=%s", [data["new_name"], data["id"]]
        )
        dbe.commit()
        return jsonify({"status": "success"})
    except Exception as e:
        print("Error:", e)  # Debug statement to check the error
        return jsonify({"status": "error", "message": str(e)})
    finally:
        c.close()
        dbe.close()


@app.route("/save_title", methods=["POST"])
def save_title():
    if not auth():
        return redirect(url_for("login_page"))

    data = request.json
    print("Received data:", data)  # Debug statement to check received data

    try:
        dbe, c = db.connect()
        c.execute(
            "UPDATE titles SET name=%s WHERE id=%s", [data["new_name"], data["id"]]
        )
        dbe.commit()
        return jsonify({"status": "success"})
    except Exception as e:
        print("Error:", e)  # Debug statement to check the error
        return jsonify({"status": "error", "message": str(e)})
    finally:
        c.close()
        dbe.close()


@app.route("/save_emp_name", methods=["POST"])
def save_emp_name():
    if not auth():
        return redirect(url_for("login_page"))

    data = request.json
    print("Received data:", data)  # Debug statement to check received data

    try:
        dbe, c = db.connect()
        c.execute(
            "UPDATE employees SET name=%s WHERE id=%s", [data["new_name"], data["id"]]
        )
        dbe.commit()
        return jsonify({"status": "success"})
    except Exception as e:
        print("Error:", e)  # Debug statement to check the error
        return jsonify({"status": "error", "message": str(e)})
    finally:
        c.close()
        dbe.close()


@app.route("/save_emp_title", methods=["POST"])
def save_emp_title():
    if not auth():
        return redirect(url_for("login_page"))

    data = request.json
    print("Received data:", data)  # Debug statement to check received data

    try:
        dbe, c = db.connect()
        c.execute(
            "UPDATE employees SET title=%s WHERE id=%s", [data["new_name"], data["id"]]
        )
        dbe.commit()
        return jsonify({"status": "success"})
    except Exception as e:
        print("Error:", e)  # Debug statement to check the error
        return jsonify({"status": "error", "message": str(e)})
    finally:
        c.close()
        dbe.close()


@app.route("/save_emp_pref_dep", methods=["POST"])
def save_emp_pref_dep():
    if not auth():
        return redirect(url_for("login_page"))

    data = request.json
    print("Received data:", data)  # Debug statement to check received data

    try:
        dbe, c = db.connect()
        c.execute(
            "UPDATE employees SET default_dep=%s WHERE id=%s",
            [data["new_name"], data["id"]],
        )
        dbe.commit()
        return jsonify({"status": "success"})
    except Exception as e:
        print("Error:", e)  # Debug statement to check the error
        return jsonify({"status": "error", "message": str(e)})
    finally:
        c.close()
        dbe.close()
        
@app.route('/save_table_excel', methods=['GET', 'POST'])
def save_table_excel():
    if not auth():
        return redirect(url_for("login_page"))
    
    data = dict(request.json)
    rows = []
    week_name= ''
    for location, events in data.items():
        if location == 'week':
            week_name = events.replace('(', '').replace(')', '')
            continue
        rows.append({'Name' : location})
        for event, details in events.items():
            rows.append({'Name' : event})
            if details:  # Check if the event has details
                
                for detail in details:
                
                    print(details)
                    employee_name = detail[0]

                    for i, days_info in enumerate(detail[1]):
                        row = {
                            "Name": f"{employee_name if i == 0 else f'Split {i}'}",
                            "Monday": days_info.get("monday", ["", ""])[0],
                            "Change M": days_info.get("monday", ["", ""])[1],
                            "Tuesday": days_info.get("tuesday", ["", ""])[0],
                            "Change T": days_info.get("tuesday", ["", ""])[1],
                            "Wednesday": days_info.get("wednesday", ["", ""])[0],
                            "Change W": days_info.get("wednesday", ["", ""])[1],
                            "Thursday": days_info.get("thursday", ["", ""])[0],
                            "Change Tu": days_info.get("thursday", ["", ""])[1],
                            "Friday": days_info.get("friday", ["", ""])[0],
                            "Change F": days_info.get("friday", ["", ""])[1],
                            "Saturday": days_info.get("saturday", ["", ""])[0],
                            "Change Sa": days_info.get("saturday", ["", ""])[1],
                            "Sunday": days_info.get("sunday", ["", ""])[0],
                            "Change Su": days_info.get("sunday", ["", ""])[1]
                    }
                        rows.append(row)

    # Create DataFrame
    df = pd.DataFrame(rows)
    
    excel_buffer = BytesIO()
    df.to_excel(excel_buffer, index=False)

    # Get the binary content of the file
    excel_buffer.seek(0)
    excel_data = excel_buffer.read()
    
    response = make_response(excel_data)
    response.headers['Content-Disposition'] = 'attachment; filename=report.xlsx'
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    
    return response
    
    
    
    
    # output = io.BytesIO()
    # with pd.ExcelWriter(output, engine='openpyxl') as writer:
    #     df.to_excel(writer, index=False)
    # output.seek(0)
    
    # df.to_excel('fwaeh.xlsx')
    
    # print(df.head(150))
    
    # return send_file(
    #     output,
    #     as_attachment=True,
    #     download_name  =f"{week_name}.xlsx",
    #     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    # )
    
@app.route('/change_kitchen_row', methods=['GET', 'POST'])
def save_kitchen_row():
    if not auth():
        return redirect(url_for("login_page"))
    
    match request.method:
        
        case 'GET':
            
            return render_template('kitchen_row.html', kitchens = db.Kitchen.get_all_kitchens(True))
        
        case 'POST':
            
            dbe,c = db.connect()
            
            for kitchen_id in request.form:
                
                row = request.form.get(kitchen_id)
                
                c.execute('UPDATE big_kitchens SET row=%s WHERE id=%s', [kitchen_id, row])
                
            dbe.commit()
            
            return redirect(url_for('save_kitchen_row'))

@app.errorhandler(500)
def internal_error(error):
    return "500 error: " + str(error), 500

@app.errorhandler(Exception)
def unhandled_exception(e):
    return "An error occurred: " + str(e), 500


if __name__ == "__main__":
    app.run()
>>>>>>> 3a464b48033fb6f78d78b539f380cf4828d78237
