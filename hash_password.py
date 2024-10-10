from werkzeug.security import generate_password_hash

# Replace 'your_password_here' with the actual admin password
hashed_password = generate_password_hash('cadmin@123')
print(hashed_password)
