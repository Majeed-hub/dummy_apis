from flask import Flask, request, jsonify, abort
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing (CORS)

# Set the upload folder for images
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Environment variables
DATABASE_NAME = os.getenv('DATABASE_NAME', 'drivers.db')
DEBUG_MODE = os.getenv('DEBUG_MODE', 'true').lower() in ['true', '1']


def init_db():
    """Initialize the SQLite database."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS drivers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                vehicle TEXT NOT NULL,
                license_plate TEXT NOT NULL,
                profile_photo TEXT,  -- Path to the profile photo
                vehicle_logo TEXT    -- Path to the vehicle logo
            )
        ''')
        conn.commit()


def validate_driver_data(data):
    """Validate the required fields for drivers."""
    if not all(key in data for key in ['name', 'phone', 'vehicle', 'license_plate']):
        abort(400, 'Missing required fields')
    if not isinstance(data.get('phone'), str) or len(data.get('phone')) < 5:
        abort(400, 'Invalid phone number')


@app.route('/drivers', methods=['POST'])
def add_driver():
    """Add a new driver with file uploads."""
    name = request.form.get('name')
    phone = request.form.get('phone')
    vehicle = request.form.get('vehicle')
    license_plate = request.form.get('license_plate')

    # Handle file uploads
    profile_photo = request.files.get('profile_photo')
    vehicle_logo = request.files.get('vehicle_logo')

    # Validate required fields
    if not all([name, phone, vehicle, license_plate]):
        return jsonify({'error': 'Missing required fields'}), 400

    # Save the files if uploaded
    profile_photo_path = None
    vehicle_logo_path = None

    if profile_photo:
        profile_photo_path = os.path.join(app.config['UPLOAD_FOLDER'], profile_photo.filename)
        profile_photo.save(profile_photo_path)

    if vehicle_logo:
        vehicle_logo_path = os.path.join(app.config['UPLOAD_FOLDER'], vehicle_logo.filename)
        vehicle_logo.save(vehicle_logo_path)

    # Insert driver data into the database
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(''' 
            INSERT INTO drivers (name, phone, vehicle, license_plate, profile_photo, vehicle_logo)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, phone, vehicle, license_plate, profile_photo_path, vehicle_logo_path))
        conn.commit()
        driver_id = cursor.lastrowid

    return jsonify({'id': driver_id, 'message': 'Driver added successfully'}), 201


@app.route('/drivers', methods=['GET'])
def get_all_drivers():
    """Retrieve all drivers from the database."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM drivers')
        rows = cursor.fetchall()

    if not rows:
        return jsonify({'message': 'No drivers found'}), 404

    drivers = []
    for row in rows:
        driver = {
            'id': row[0],
            'name': row[1],
            'phone': row[2],
            'vehicle': row[3],
            'license_plate': row[4],
            'profile_photo': row[5],
            'vehicle_logo': row[6]
        }
        drivers.append(driver)

    return jsonify(drivers), 200


@app.route('/drivers/<int:driver_id>', methods=['GET'])
def get_driver(driver_id):
    """Retrieve a specific driver by ID."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM drivers WHERE id = ?', (driver_id,))
        row = cursor.fetchone()
        if row:
            driver = {
                'id': row[0],
                'name': row[1],
                'phone': row[2],
                'vehicle': row[3],
                'license_plate': row[4],
                'profile_photo': row[5],
                'vehicle_logo': row[6]
            }
            return jsonify(driver), 200
        else:
            return jsonify({'error': 'Driver not found'}), 404


@app.route('/drivers/<int:driver_id>', methods=['PUT'])
def update_driver(driver_id):
    """Update driver information."""
    data = request.get_json()
    validate_driver_data(data)

    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM drivers WHERE id = ?', (driver_id,))
        if not cursor.fetchone():
            return jsonify({'error': 'Driver not found'}), 404

        cursor.execute('''
            UPDATE drivers
            SET name = ?, phone = ?, vehicle = ?, license_plate = ?
            WHERE id = ?
        ''', (data['name'], data['phone'], data['vehicle'], data['license_plate'], driver_id))
        conn.commit()

    return jsonify({'message': 'Driver updated successfully'}), 200


@app.route('/drivers/<int:driver_id>', methods=['DELETE'])
def delete_driver(driver_id):
    """Delete a driver by ID."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM drivers WHERE id = ?', (driver_id,))
        row = cursor.fetchone()

        if row:
            cursor.execute('DELETE FROM drivers WHERE id = ?', (driver_id,))
            conn.commit()
            return jsonify({'message': 'Driver deleted successfully'}), 200
        else:
            return jsonify({'error': 'Driver not found'}), 404


@app.route('/ride-cost', methods=['POST'])
def calculate_ride_cost():
    """
    Calculate the cost of a ride based on distance.
    - Minimum fare: 10.25 SAR for up to 8 km.
    - Additional cost: 1.23 SAR per km after 8 km.
    - Pickup charge: 1 SAR.
    """
    data = request.get_json()
    distance = data.get('distance')

    if distance is None or distance < 0:
        return jsonify({'error': 'Invalid distance provided'}), 400

    base_fare = 10.25
    additional_rate = 1.23
    pickup_charge = 1.0

    if distance <= 8:
        total_cost = base_fare + pickup_charge
    else:
        extra_distance = distance - 8
        total_cost = base_fare + (extra_distance * additional_rate) + pickup_charge

    return jsonify({'distance': distance, 'total_cost': round(total_cost, 2)}), 200


@app.errorhandler(Exception)
def handle_exception(e):
    """Global error handler."""
    return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    init_db()
    port = int(os.getenv('PORT', 5000))
    app.run(debug=DEBUG_MODE, host='0.0.0.0', port=port)
