import mysql.connector

def get_db_connection():
  
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root9876",
        database="course_resource_provider"
    )

