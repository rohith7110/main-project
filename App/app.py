from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
import uuid

app = Flask(__name__)
app.secret_key = 'Rohith'

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'course_resource_provider'

# Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'coursea204@gmail.com'
app.config['MAIL_PASSWORD'] = 'ikpe hgdk mxqh ytml'
mail = Mail(app)

mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('login.html')


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM Admin WHERE username = %s', (username,))
        admin = cursor.fetchone()
        if admin and check_password_hash(admin[2], password):
            session['admin'] = admin[0]  # Store admin id
            return redirect(url_for('admin_dashboard'))
        flash('Invalid credentials', 'danger')
    return render_template('login.html')


@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM Users')
    users = cursor.fetchall()
    cursor.execute('SELECT * FROM Resources')
    resources = cursor.fetchall()
    return render_template('admin_dashboard.html', users=users, resources=resources)


@app.route('/admin/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        email = request.form['email']
        name = request.form['name']
        cursor = mysql.connection.cursor()

        # Check if the user already exists
        cursor.execute('SELECT * FROM Users WHERE email = %s', (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash(f'User with email {email} already exists. Please use a different email.', 'danger')
            return redirect(url_for('add_user'))

        # Generate a registration token
        registration_token = str(uuid.uuid4())

        # Insert unregistered user with a null password and Unregistered status
        cursor.execute('INSERT INTO Users (email, name, password, status, registration_token) VALUES (%s, %s, NULL, %s, %s)', 
                       (email, name, 'Unregistered', registration_token))
        mysql.connection.commit()

        # Send email to the user with a registration link
        registration_link = url_for('register_user', token=registration_token, _external=True)
        msg = Message('Welcome to Course Resource Platform', sender='coursea204@gmail.com', recipients=[email])
        msg.body = f'Hello {name},\n\nYou have been added to the course resource platform as an unregistered user. Please complete your registration by setting up your password here: {registration_link}\n\nThank you.'
        mail.send(msg)

        flash('User added successfully and a registration link has been sent.', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('add_user.html')


@app.route('/register_user/<token>', methods=['GET', 'POST'])
def register_user(token):
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT email FROM Users WHERE registration_token = %s', (token,))
    user = cursor.fetchone()

    if not user:
        flash('Invalid or expired registration link.', 'danger')
        return redirect(url_for('index'))

    email = user[0]
    
    if request.method == 'POST':
        # Get the form data
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Check if the passwords match
        if password != confirm_password:
            flash('Passwords do not match. Please try again.', 'danger')
            return render_template('register.html', email=email)
        
        # Update the user's password and set status to Registered
        hashed_password = generate_password_hash(password)
        cursor.execute('UPDATE Users SET password = %s, status = %s, registration_token = NULL WHERE email = %s', 
                       (hashed_password, 'Registered', email))
        mysql.connection.commit()

        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('index'))
    
    return render_template('register.html', email=email)


@app.route('/admin/send_invite/<int:user_id>')
def send_invite(user_id):
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT email, name, registration_token FROM Users WHERE id = %s', (user_id,))
    user = cursor.fetchone()
    
    if user:
        email = user[0]
        name = user[1]
        registration_token = user[2]
        
        # Create a unique registration link with the existing token
        registration_link = url_for('register_user', token=registration_token, _external=True)
        
        # Send email with registration link
        msg = Message('Welcome to Course Resource Platform', sender='coursea204@gmail.com', recipients=[email])
        msg.body = f'Hello {name},\n\nYou have been added to the course resource platform as an unregistered user. Please complete your registration by setting up your password here: {registration_link}\n\nThank you.'
        mail.send(msg)
        
        flash(f'Invite sent to {email}!', 'success')
    else:
        flash('User not found!', 'danger')
    
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/resources', methods=['GET', 'POST'])
def crud_resources():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    
    cursor = mysql.connection.cursor()

    if request.method == 'POST':
        resource_name = request.form['resource_name']
        allocated_to = request.form['allocated_to']
        
        # Check if a file was uploaded
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                # Save the file to the server
                file_path = f'uploads/{file.filename}'
                file.save(file_path)
                
                # Insert resource into database
                cursor.execute('INSERT INTO Resources (name, file_path, allocated_to) VALUES (%s, %s, %s)', 
                                (resource_name, file_path, allocated_to))
                mysql.connection.commit()
                flash('Resource added successfully!', 'success')
            else:
                flash('No file selected!', 'danger')
        else:
            flash('File is missing in the request!', 'danger')
    
    # Fetch all users for the dropdown list
    cursor.execute('SELECT id, name FROM Users')
    users = cursor.fetchall()
     
    cursor.execute('SELECT * FROM Resources')
    resources = cursor.fetchall()

    return render_template('crud_resources.html', users=users, resources=resources)

@app.route('/user/login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM Users WHERE email = %s', (email,))
        user = cursor.fetchone()
        if user and check_password_hash(user[3], password):
            session['user'] = user[0]  # Store user id
            return redirect(url_for('user_dashboard'))
        flash('Invalid credentials', 'danger')
    return render_template('user_login.html')

@app.route('/user/dashboard')
def user_dashboard():
    if 'user' not in session:
        return redirect(url_for('user_login'))
    
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM Resources WHERE allocated_to = %s', (session['user'],))
    resources = cursor.fetchall()
    return render_template('user_dashboard.html', resources=resources)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
