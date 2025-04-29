from flask import render_template
from owner_panel import app 

@app.route('/chemistry')
def chemistry_project():
    return render_template('chem_project.html')


if __name__ == '__main__':
    
    app.run()