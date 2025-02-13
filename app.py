# app.py

# Import the 'Flask' class from the 'flask' library.
import psycopg2, psycopg2.extras
from flask import Flask, request
from flask_cors import CORS
from dotenv import load_dotenv
load_dotenv()

import os
import datetime
# from datetime import datetime, time



# Initialize Flask
# We'll use the pre-defined global '__name__' variable to tell Flask where it is.
app = Flask(__name__)
CORS(app)


def get_db_connection():
    connection = psycopg2.connect(
        host='localhost',
        database='appointments_db',
        # user=os.environ['POSTGRES_USER'],
        # password=os.environ['POSTGRES_PASSWORD']
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
    for appointment in appointments:
         if isinstance(appointment['time'], datetime.time):
                appointment['time'] = appointment['time'].strftime('%H:%M:%S')
    connection.close()
    return appointments
  except:
    return "Application Error", 500  #Index Works for postman


# Create Route
@app.route('/appointments', methods=['POST'])
def create_appointment():
    try:
        new_appointment = request.json
        
        if not new_appointment.get('style') or not new_appointment.get('date') or not new_appointment.get('time'):
            return {"error": "Missing required fields"}, 400
        try:
            appointment_date = new_appointment['date']
            appointment_time = new_appointment['time']
        except ValueError:
            return {"error": "Invalid date or time format. Use 'YYYY-MM-DD' for date and 'HH:MM:SS' for time."}, 400
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("INSERT INTO appointments (style, date, time) VALUES (%s, %s, %s) RETURNING *",
                       (new_appointment['style'], appointment_date, appointment_time))
        
        created_appointment = cursor.fetchone()
        connection.commit()
        connection.close()
        if isinstance(created_appointment['time'], datetime.time):
            created_appointment['time'] = created_appointment['time'].strftime('%H:%M:%S')
        return created_appointment, 201

    except psycopg2.DatabaseError as db_error:
        return {"error": f"Database error: {str(db_error)}"}, 500
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"},   #This Works on postman


# Show Route
@app.route('/appointments/<appointment_id>', methods=['GET'])
def show_appointment(appointment_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT * FROM appointments WHERE id = %s", (appointment_id,))
        appointment = cursor.fetchone()
        if appointment is not None:
            if isinstance(appointment['time'], datetime.time):
                appointment['time'] = appointment['time'].strftime('%H:%M:%S')
        if appointment is None:
            connection.close()
            return "Appointment Not Found", 404
        connection.close()
        return appointment, 200

    except Exception as e:
        return str(e), 500    # This works for postman I believe 



# Delete Route

@app.route('/appointments/<appointment_id>', methods=['DELETE'])
def delete_appointment(appointment_id):
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Delete the appointment
        cursor.execute("DELETE FROM appointments WHERE id = %s", (appointment_id,))
        
        # Check if the appointment was deleted
        if cursor.rowcount == 0:
            return {"error": "Appointment not found"}, 404
        
        # Commit the transaction
        connection.commit()
        
        # Return a success message
        return {"message": "Appointment deleted successfully"}, 200  # 200 or 202 is more appropriate here

    except psycopg2.DatabaseError as db_error:
        return {"error": f"Database error: {str(db_error)}"}, 500
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}, 500
    finally:
        # Ensure that the cursor and connection are always closed, even if an exception occurs
        if cursor:
            cursor.close()
        if connection:
            connection.close()


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