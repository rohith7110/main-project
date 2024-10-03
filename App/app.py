from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'  # Replace with your MySQL username
app.config['MYSQL_PASSWORD'] = 'root9876'  # Replace with your MySQL password
app.config['MYSQL_DB'] = 'course_resource_provider'
mysql = MySQL(app)

# Function to get a database cursor
def get_cursor():
    return mysql.connection.cursor(MySQLdb.cursors.DictCursor)

# Admin login route
@app.route('/', methods=['GET', 'POST'])
def admin_login():
    cursor = get_cursor()

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cursor.execute("SELECT * FROM admin WHERE email=%s AND password=%s", (email, password))
        admin = cursor.fetchone()

        if admin:
            print("Logged In")
            return redirect(url_for('admin_dashboard'))  # Redirect to admin dashboard
        else:
            flash("Invalid email or password")
            return render_template('login.html')

    return render_template('login.html')

@app.route('/admin_dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    return render_template('admin_dashboard.html')

# User signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Handle user signup logic here
        pass  # Replace with your logic for handling user signup

    return render_template('signup.html')

if __name__ == '__main__':
    app.run(debug=True)
