from dotenv import load_dotenv
import os
load_dotenv()

# Import the 'Flask' class from the 'flask' library.
from auth_middleware import token_required

from flask import Flask, jsonify, request, g
import jwt
import bcrypt
import psycopg2, psycopg2.extras
# Initialize Flask
# We'll use the pre-defined global '__name__' variable to tell Flask where it is.
app = Flask(__name__)

def get_db_connection():
    connection = psycopg2.connect(host='localhost',
                            database='flask_auth_db',
                            user=os.getenv('POSTGRES_USERNAME'),
                            password=os.getenv('POSTGRES_PASSWORD')
                            )
    return connection


# Define our route
# This syntax is using a Python decorator, which is essentially a succinct way to wrap a function in another function.
@app.route('/')
def index():
  return "Hello, world!"

# AUTH ROUTES
@app.route('/sign-token', methods=['GET'])
def sign_token():
    user = {
        "id": 1,
        "username": "test",
        "password": "test"
    }

    token = jwt.encode(user, os.getenv('JWT_SECRET'), algorithm="HS256")

    return jsonify({"token": token})

@app.route('/auth/signup', methods=['POST'])
def signup():
    try:
        # Get data from form
        new_user_data = request.get_json()

        # Find user in DB
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT * FROM users WHERE username = %s;", (new_user_data["username"],))
        existing_user = cursor.fetchone()

        # Dont create a duplicate account
        if existing_user:
            cursor.close()
            return jsonify({"error": "Username already taken"}), 400

        # Encrypt the raw password
        hashed_password = bcrypt.hashpw(bytes(new_user_data["password"], 'utf-8'), bcrypt.gensalt())

        # Create the new user in DB
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s) RETURNING username, id", (new_user_data["username"], hashed_password.decode('utf-8')))
        created_user = cursor.fetchone()
        connection.commit()
        connection.close()

        # Sign the person in
        token = jwt.encode(created_user, os.getenv('JWT_SECRET'))
        return jsonify({"token": token, "user": created_user}), 201
    except Exception as error:
        return jsonify({"error": str(error)}), 401


@app.route('/auth/signin', methods=["POST"])
def signin():
    try:
        # get the info from the form
        sign_in_form_data = request.get_json()

        # Find user in DB
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT * FROM users WHERE username = %s;", (sign_in_form_data["username"],))
        existing_user = cursor.fetchone()

        # Check if the user exists
        if existing_user is None:
            return jsonify({"error": "Invalid credentials."}), 401

        # Check if the password matches
        password_is_valid = bcrypt.checkpw(bytes(sign_in_form_data["password"], 'utf-8'), bytes(existing_user["password"], 'utf-8'))
        if not password_is_valid:
            return jsonify({"error": "Invalid credentials."}), 401

        # Sign token
        token = jwt.encode({"username": existing_user["username"], "id": existing_user["id"]}, os.getenv('JWT_SECRET'))
        return jsonify({"token": token}), 201


    except Exception as error:
        return jsonify({"error": "Invalid credentials."}), 401
    finally:
        connection.close()


# PROTECTED ROUTES
@app.route('/verify-token', methods=['POST'])
def verify_token():
    try:
        token = request.headers.get('Authorization').split(' ')[1]
        decoded_token = jwt.decode(token, os.getenv('JWT_SECRET'), algorithms=["HS256"])
        return jsonify({"user": decoded_token})
    except Exception as error:
       return jsonify({"error": error.message})

@app.route('/vip-lounge')
@token_required
def vip_lounge():
    return f"Welcome to the party, {g.user['username']}"

# Run our application, by default on port 5000
app.run()
