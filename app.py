# Import the Flask class from the flask module
from flask import Flask, render_template, get_flashed_messages, flash, session

# Create an instance of the Flask class
app = Flask(__name__)

app.config['SECRET_KEY'] = "very_secret_key_12351232"

# Define a route and a view function
@app.route('/')
def hello():
    return render_template("index.html")

@app.route("/about_us")
def about():
    
    return render_template("about_Us.html")

@app.route('/table')
def table():
    
    return render_template('table.html')


    
# Run the application
if __name__ == '__main__':
    app.run(debug=True)
