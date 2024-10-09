from dotenv import load_dotenv
import os
import mysql.connector
from flask import Flask, jsonify

app = Flask(__name__)

# Load the environment variables from p.env
load_dotenv('p.env')
db_config = {
    'host': os.environ.get('DB_HOST'),
    'user': os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PASSWORD'),
    'database': os.environ.get('DB_NAME'),
}

# Function to create a database connection
def get_db_connection():
    connection = mysql.connector.connect(**db_config)
    return connection

# Route for dynamic table access
@app.route('/table/<table_name>', methods=['GET'])
def get_table_data(table_name):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Validate if the table exists before executing the query
        cursor.execute(f"SHOW TABLES LIKE %s", (table_name,))
        result = cursor.fetchone()

        if not result:
            return jsonify({"error": f"Table '{table_name}' does not exist."}), 404

        # Fetch all records from the specified table
        cursor.execute(f"SELECT * FROM {table_name}")
        table_data = cursor.fetchall()

        cursor.close()
        connection.close()

        # Return the table data in JSON format
        return jsonify(table_data)
    
    except mysql.connector.Error as err:
        print(f"Error: {err}")  # Log the error to the console for debugging
        return jsonify({"error": str(err)}), 500

# Error handling route if table doesn't exist
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Resource not found"}), 404

if __name__ == '__main__':
    # Set host and port for deployment
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
