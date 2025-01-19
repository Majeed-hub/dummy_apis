import requests

# This is the main URL that you need to replace local host URL with!
API_URI = "https://dummy-apis-backend.onrender.com"

def add_driver(name, phone, vehicle, license_plate):
    try:
        payload = {
            "name": name,
            "phone": phone,
            "vehicle": vehicle,
            "license_plate": license_plate,
        }
        response = requests.post(f"{API_URI}/drivers", json=payload)
        response.raise_for_status()
        print("Driver added:", response.json())
    except requests.RequestException as e:
        print("Error adding driver:", e)


def get_all_drivers():
    try:
        response = requests.get(f"{API_URI}/drivers")
        response.raise_for_status()
        print("Drivers:", response.json())
    except requests.RequestException as e:
        print("Error fetching drivers:", e)


def get_driver(driver_id):
    try:
        response = requests.get(f"{API_URI}/drivers/{driver_id}")
        response.raise_for_status()
        print("Driver details:", response.json())
    except requests.RequestException as e:
        print(f"Error fetching driver with ID {driver_id}:", e)


def update_driver(driver_id, name, phone, vehicle, license_plate):
    try:
        payload = {
            "name": name,
            "phone": phone,
            "vehicle": vehicle,
            "license_plate": license_plate,
        }
        response = requests.put(f"{API_URI}/drivers/{driver_id}", json=payload)
        response.raise_for_status()
        print("Driver updated:", response.json())
    except requests.RequestException as e:
        print(f"Error updating driver with ID {driver_id}:", e)


def delete_driver(driver_id):
    try:
        response = requests.delete(f"{API_URI}/drivers/{driver_id}")
        response.raise_for_status()
        print("Driver deleted:", response.json())
    except requests.RequestException as e:
        print(f"Error deleting driver with ID {driver_id}:", e)


def calculate_ride_cost(distance):
    try:
        payload = {"distance": distance}
        response = requests.post(f"{API_URI}/ride-cost", json=payload)
        response.raise_for_status()
        print("Ride cost:", response.json())
    except requests.RequestException as e:
        print("Error calculating ride cost:", e)



if __name__ == "__main__":

    # This how the api can be accessed via dedicated functions!
  
    add_driver("Abdul Majeed", "1234567890", "Toyota Landcruiser", "KA 47 R 9737")

    get_all_drivers()

    get_driver(1)

    update_driver(1, "Abdul Majeed", "7022277060",
                  "Toyota Landcruiser", "KA 47 R 9737")

    # delete_driver(1)

    calculate_ride_cost(12)