# app.py

# Import the 'Flask' class from the 'flask' library.
import psycopg2, psycopg2.extras
from flask import Flask, request
from flask_cors import CORS
from dotenv import load_dotenv
load_dotenv()

import os


# Initialize Flask
# We'll use the pre-defined global '__name__' variable to tell Flask where it is.
app = Flask(__name__)
CORS(app)

# # def get_db_connection():
# #     connection = psycopg2.connect(
# #         host='localhost',
# #         database='hairsalon_db',
# #         #user=os.environ['POSTGRES_USER'],
# #         #password=os.environ['POSTGRES_PASSWORD']
# #     )
# #     return connection


# # Route To View All Users
# @app.route('/users')
# def get_useres():
#   try:
#     connection = get_db_connection()
#     cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
#     cursor.execute("SELECT * FROM users;")
#     users = cursor.fetchall()
#     connection.close()
#     return users
#   except Exception as err:
#         return ({"err": str(err)}), 500

     
# # Route to sign-up a new user
# @app.route('/auth/sign-up', methods=['POST'])
# def sign_up():
#     try:
#         new_user_data = request.get_json()
#         username = new_user_data.get("username")
#         password = new_user_data.get("password")
#         email = new_user_data.get("email")

#         if not username or not password or not email:
#             return ({"err": "Missing fields"}), 400
#         connection = get_db_connection()
#         cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
#         cursor.execute("SELECT * FROM users WHERE username = %s;", (username,))
#         existing_user = cursor.fetchone()

#         if existing_user:
#             cursor.close()
#             return ({"err": "Username already taken"}), 400
#         hashed_password = bcrypt.hashpw(bytes(password, 'utf-8'), bcrypt.gensalt())
#         cursor.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s) RETURNING id, username",
#                        (username, hashed_password.decode('utf-8'), email))
#         created_user = cursor.fetchone()
#         connection.commit()
#         connection.close()
#         payload = {"username": created_user["username"], "id": created_user["id"]}
#         token = jwt.encode({"payload": payload}, os.getenv('JWT_SECRET'), algorithm="HS256")

#         return ({"token": token}), 201
#     except Exception as err:
#         return ({"err": str(err)}), 500


# # Route For User Sign-in 
# @app.route('/signin', methods=['POST'])
# def sign_in():
#     try:
#         user_credentials = request.json
#         username = user_credentials.get('username')
#         password = user_credentials.get('password')
#         email =    user_credentials.get("email")

        
#         connection = get_db_connection()
#         cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
#         cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
#         user = cursor.fetchone()
#         connection.close()

#         if user:
#             return user  
#         else:
#             return "Invalid credentials", 401
#     except Exception as e:
#         return str(e), 500


# #Route To Create New User 
# @app.route('/users', methods=['POST'])
# def create_user():
#     try:
#         new_user = request.json
#         connection = get_db_connection()
#         cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
#         cursor.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s) RETURNING *",
#                        (new_user['username'], new_user['password'], new_user['email']))
#         created_user = cursor.fetchone()
#         connection.commit()
#         connection.close()
#         return created_user, 201  
#     except Exception as e:
#         return str(e), 500


# # Route To User ID
# @app.route('/users/<user_id>', methods=['GET'])
# def get_user(user_id):
#    try:
#       connection = get_db_connection()
#       cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
#       cursor.execute("SELECT * FROM user WHERE id = %s", (user_id,))
#       user = cursor.fetchone()
#       connection.close()
#       if user:
#          return user
#       else:
#          return 404
#     except Exception as e:
#       return str(e), 500


def get_db_connection():
    connection = psycopg2.connect(
        host='localhost',
        database='appointments_db',
        user=os.environ['POSTGRES_USER'],
        password=os.environ['POSTGRES_PASSWORD']
    )
    return connection

# Index

@app.route("/appointments")
def index():
  try:
    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM appointments;")
    appointments = cursor.fetchall()
    connection.close()
    return appointments
  except Exception as e: 
    print(f"Error: {e}")
    return "Application Error", 500


# Create Route

app.route('/appointments', methods=['POST'])
def create_appointment():
  try:
    new_appointment = request.json
    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("INSERT INTO appointment (style, date, time) VALUES (%s, %s, %s) RETURNING *",
                   (new_appointment['style'], new_appointment['date'], new_appointment['time']))
    created_appointment = cursor.fetchone()
    connection.commit()
    connection.close()
    return created_appointment, 201
  except Exception as e:
     return str(e), 500


# Show Route

@app.route('/appointments/<appointment_id>', methods=['GET'])
def show_appointment(appointment_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT * FROM appointments WHERE id = %s", (appointment_id,))
        appointment = cursor.fetchone()
        if appointment is None:
            connection.close()
            return "Appointment Not Found", 404
        connection.close()
        return appointment, 200
    except Exception as e:
        return str(e), 500


# Delete Route

@app.route('/appointments/<appointment_id>', methods=['DELETE'])
def delete_appointment(appointment_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("DELETE FROM appointments WHERE id = %s", (appointment_id,))
        if cursor.rowcount == 0:
            return "Appointment not found", 404
        connection.commit()
        cursor.close()
        return "Appointment deleted successfully", 204
    except Exception as e:
        return str(e), 500

# Update Route

@app.route('/appointments/<appointment_id>', methods=['PUT'])
def update_appointment(appointment_id):
    try:
      appointment = request.json
      connection = get_db_connection()
      cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
      cursor.execute("UPDATE appointments SET style = %s, date = %s, time = %s WHERE id = %s RETURNING *", (appointment['style'], appointment['date'], appointment['time'], appointment_id))
      updated_appointment = cursor.fetchone()
      if updated_appointment is None:
        return "Appointment Not Found", 404
      connection.commit()
      connection.close()
      return updated_appointment, 202
    except Exception as e:
      return str(e), 500


app.run()