# Import the Flask class from the flask module
from flask import Flask, render_template

# Create an instance of the Flask class
app = Flask(__name__)

# Define a route and a view function
@app.route('/')
def hello():
    return render_template("index.html")

@app.route("/about_as")
def about():
    
    return render_template("about_as.html")

    
# Run the application
if __name__ == '__main__':
    app.run(debug=True)
