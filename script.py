from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)


def init_db():
    """Initialize the SQLite database."""
    with sqlite3.connect('drivers.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS drivers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                vehicle TEXT NOT NULL,
                license_plate TEXT NOT NULL
            )
        ''')
        conn.commit()


@app.route('/drivers', methods=['POST'])
def add_driver():
    """Add a new driver."""
    data = request.get_json()
    name = data.get('name')
    phone = data.get('phone')
    vehicle = data.get('vehicle')
    license_plate = data.get('license_plate')

    if not all([name, phone, vehicle, license_plate]):
        return jsonify({'error': 'Missing required fields'}), 400

    with sqlite3.connect('drivers.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO drivers (name, phone, vehicle, license_plate)
            VALUES (?, ?, ?, ?)
        ''', (name, phone, vehicle, license_plate))
        conn.commit()
        driver_id = cursor.lastrowid

    return jsonify({'id': driver_id, 'message': 'Driver added successfully'}), 201


@app.route('/drivers', methods=['GET'])
def get_all_drivers():
    """Retrieve all drivers."""
    with sqlite3.connect('drivers.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM drivers')
        drivers = [
            {'id': row[0], 'name': row[1], 'phone': row[2],
                'vehicle': row[3], 'license_plate': row[4]}
            for row in cursor.fetchall()
        ]
    return jsonify(drivers), 200


@app.route('/drivers/<int:driver_id>', methods=['GET'])
def get_driver(driver_id):
    """Retrieve a specific driver by ID."""
    with sqlite3.connect('drivers.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM drivers WHERE id = ?', (driver_id,))
        row = cursor.fetchone()
        if row:
            driver = {'id': row[0], 'name': row[1], 'phone': row[2],
                      'vehicle': row[3], 'license_plate': row[4]}
            return jsonify(driver), 200
        else:
            return jsonify({'error': 'Driver not found'}), 404


@app.route('/drivers/<int:driver_id>', methods=['PUT'])
def update_driver(driver_id):
    """Update driver information."""
    data = request.get_json()
    name = data.get('name')
    phone = data.get('phone')
    vehicle = data.get('vehicle')
    license_plate = data.get('license_plate')

    with sqlite3.connect('drivers.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM drivers WHERE id = ?', (driver_id,))
        if not cursor.fetchone():
            return jsonify({'error': 'Driver not found'}), 404

        cursor.execute('''
            UPDATE drivers
            SET name = ?, phone = ?, vehicle = ?, license_plate = ?
            WHERE id = ?
        ''', (name, phone, vehicle, license_plate, driver_id))
        conn.commit()

    return jsonify({'message': 'Driver updated successfully'}), 200


@app.route('/drivers/<int:driver_id>', methods=['DELETE'])
def delete_driver(driver_id):
    """Delete a driver."""
    with sqlite3.connect('drivers.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM drivers WHERE id = ?', (driver_id,))
        if not cursor.fetchone():
            return jsonify({'error': 'Driver not found'}), 404

        cursor.execute('DELETE FROM drivers WHERE id = ?', (driver_id,))
        conn.commit()

    return jsonify({'message': 'Driver deleted successfully'}), 200


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
        total_cost = base_fare + \
            (extra_distance * additional_rate) + pickup_charge

    return jsonify({'distance': distance, 'total_cost': round(total_cost, 2)}), 200


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
