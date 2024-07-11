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

from db import (
    get_subdept,
    create_dept,
    Employee,
    Department,
    Kitchen,
    KitchenGroup,
    add_program,
    get_all_programs,
    get_next_weeks,
    get_current_week,
    get_all_departments,
    create_title,
    get_all_titles,
    connect
)

# Create an instance of the Flask class
app = Flask(__name__)

app.config["SECRET_KEY"] = "very_secret_key_12351232"


# Define a route and a view function
@app.route("/")
def hello():
    return render_template("index.html")


def get_next_seven_days(start_date_str):
    start_date = datetime.strptime(start_date_str, "%d/%m/%Y")
    next_seven_days = [
        (start_date + timedelta(days=i)).strftime("%d/%m/%Y") for i in range(8)
    ][0:7]
    return next_seven_days

@app.route("/add_kitchen", methods=["GET", "POST"])
def add_kitchen():

    match request.method:
        case "GET":
            return render_template(
                "add_kitchen.html", departments=get_all_departments()
            )

        case "POST":

            name, deps = request.form.get("name"), []
            for key in request.form:
                if key == "name" or key == "submit":
                    continue
                deps.append(request.form.get(key))

            Kitchen.create_kitchen(name, deps)

            flash("Created Kitchen Successfully!")

            return redirect(url_for("add_kitchen"))


@app.route("/add_department", methods=["GET", "POST"])
def add_dep():

    match request.method:
        case "GET":
            return render_template("add_deps.html")

        case "POST":

            create_dept(request.form.get("name"))

            flash("Created Department Successfully!")

            return redirect(url_for("add_dep"))


@app.route("/add_title", methods=["GET", "POST"])
def add_title():

    match request.method:
        case "GET":
            return render_template("add_title.html")

        case "POST":

            create_title(request.form.get("name"))

            flash("Created Title Successfully!")

            return redirect(url_for("add_title"))


@app.route("/save_schedule", methods=["POST"])
def save_schedule():
    data = request.json

    schedule = KitchenGroup(data["week"])

    schedule.load_schedule(data)

    schedule.save_schedule()

    return jsonify(
        {
            "status": "success",
        }
    )


@app.route("/add_employee", methods=["GET", "POST"])
def add_employee():

    match request.method:

        case "GET":

            all_departments = Department.get_all_departments()
            all_programs = get_all_programs()
            all_titles = get_all_titles()

            print(all_titles)

            return render_template(
                "add_employee.html",
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

            Employee.create_employee(name, title, def_dep)

            flash("Added Employee Successfully!")
            return redirect(url_for("add_employee"))


@app.route("/add_program", methods=["GET", "POST"])
def create_program():

    match request.method:
        case "GET":

            return render_template("add_program.html")

        case "POST":

            name = request.form.get("name")

            add_program(name)

            flash("Program Created")

            return redirect(url_for("create_program"))


@app.route("/edit_objects")
def edit_objects():

    all_kitchens = Kitchen.get_all_kitchens()
    all_departments = get_all_departments(False)
    all_employees = Employee.get_all_employees()
    all_programs = get_all_programs()
    all_titles = get_all_titles()

    return render_template(
        "edit_objects.html",
        kitchens=all_kitchens,
        departments=all_departments,
        employees=all_employees,
        programs=all_programs,
        titles=all_titles,
    )
    
@app.route('/edit/kitchen/<kitchen>', methods=['GET', 'POST'])
def edit_kitchen(kitchen):
    match request.method:
        case "GET":
            return render_template(
                "add_kitchen.html", departments=get_all_departments(),
                edit=True, kitchen = Kitchen(Kitchen.get_id_from_name(kitchen))
            )

        case "POST":

            name, deps = request.form.get("name"), []
            for key in request.form:
                if key == "name" or key == "submit" or key == 'id':
                    continue
                deps.append(request.form.get(key))

            Kitchen(Kitchen.get_id_from_name(kitchen)).update(name, deps)

            flash("Updated Kitchen Successfully!")

            return redirect(url_for("edit_objects"))
    
@app.route('/edit/department/<dep>', methods=['GET', 'POST'])
def edit_department(dep):
    match request.method:
        case "GET":
            return render_template(
                "add_deps.html", departments=get_all_departments(),
                edit=True, department = Department(Department.get_id_from_name(dep))
            )

        case "POST":

            name = request.form.get("name")

            Department(Department.get_id_from_name(dep)).update(name)

            flash("Updated Department Successfully!")

            return redirect(url_for("edit_objects"))
        
@app.route('/edit/employee/<emp>', methods=['GET', 'POST'])
def edit_demployee(emp):
    match request.method:
        case "GET":
            print(emp)
            
            return render_template(
                "add_employee.html", departments=Department.get_all_departments(),
                edit=True, employee = Employee(Employee.get_id_by_name(emp)), titles=get_all_titles(), programs=get_all_programs()
            )

        case "POST":

            name = request.form.get("name")
            title = request.form.get('title')
            pref_dep = request.form.get('def_dep')

            Employee(Employee.get_id_by_name(emp)).update(name, title, pref_dep)

            flash("Updated Department Successfully!")

            return redirect(url_for("edit_objects"))
        
@app.route('/delete/program/<program>')
def delete_program(program):
    
    db,c =connect()
    
    flash(f"`{program}` Deleted Successfully")
    
    c.execute("DELETE FROM programs WHERE name=%s ", [program])
    db.commit()
    
    return redirect(url_for('edit_objects'))

@app.route('/delete/title/<title>')
def delete_title(title):
    
    db,c =connect()
    flash(f"`{title}` Deleted Successfully")
    c.execute("DELETE FROM titles WHERE name=%s ", [title])
    db.commit()
    
    return redirect(url_for('edit_objects'))


@app.route('/delete/kitchen/<kitchen>')
def delete_kitchen(kitchen):
    
    db,c =connect()
    flash(f"`{kitchen}` Deleted Successfully")
    c.execute("DELETE FROM big_kitchens WHERE name=%s ", [kitchen])
    db.commit()
    
    return redirect(url_for('edit_objects'))

@app.route('/delete/department/<department>')
def delete_department(department):
    
    db,c =connect()
    flash(f"`{department}` Deleted Successfully")
    c.execute("DELETE FROM sub_department WHERE name=%s ", [department])
    db.commit()
    
    return redirect(url_for('edit_objects'))

@app.route('/delete/employee/<employee>')
def delete_employee(employee):
    
    db,c =connect()
    flash(f"`{employee}` Deleted Successfully")
    c.execute("DELETE FROM employees WHERE name=%s ", [employee])
    db.commit()
    
    return redirect(url_for('edit_objects'))

@app.route("/table")
@app.route("/table/<week>")
def table(week=None):

    match request.method:

        case "GET":

            if week == None:

                group = KitchenGroup(get_current_week())

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

    return f"{d_start}/{m_start}/{y_start} - {d_end}/{m_end}/{y_end}"


# Run the application
if __name__ == "__main__":
    app.run()
