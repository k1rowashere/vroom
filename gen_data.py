import csv
import random
from datetime import datetime, timedelta


# Helper functions
def random_date(start, end):
    """Generate a random datetime between `start` and `end`."""
    delta = end - start
    random_seconds = random.randint(0, int(delta.total_seconds()))
    return start + timedelta(seconds=random_seconds)


def random_string(length):
    """Generate a random alphanumeric string."""
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    return ''.join(random.choices(chars, k=length))


# File paths
office_file = 'offices.csv'
vehicle_models_file = 'vehicle_models.csv'
vehicles_file = 'vehicles.csv'
auth_user_file = 'auth_users.csv'
customer_info_file = 'customer_info.csv'
reservations_file = 'reservations.csv'

# Office data
offices = [
    ['Downtown Office', '123 Main Street, Cityville'],
    ['Uptown Office', '456 High Street, Townsville'],
    ['Suburban Office', '789 Elm Street, Suburbia'],
]

# Generate CSVs

# Offices
with open(office_file, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['id', 'name', 'address'])
    for i, office in enumerate(offices, start=1):
        writer.writerow([i, office[0], office[1]])

# Vehicle Models
makes = ['Toyota', 'Ford', 'Honda', 'Tesla', 'Chevrolet']
models = ['Corolla', 'Fiesta', 'Civic', 'Model 3', 'Malibu']
with open(vehicle_models_file, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['id', 'make', 'model', 'year', 'price_per_day', 'price_per_hour', 'rating'])
    for i in range(1, 101):
        make = random.choice(makes)
        model = random.choice(models)
        year = random.randint(2015, 2023)
        price_per_day = round(random.uniform(30, 150), 2)
        price_per_hour = round(price_per_day / 10, 2)
        rating = round(random.uniform(3.0, 5.0), 1)
        writer.writerow([i, make, model, year, price_per_day, price_per_hour, rating])

# Vehicles
with open(vehicles_file, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['plate_no', 'model_id', 'color', 'office_id', 'mileage', 'status'])
    colors = ['Red', 'Blue', 'Black', 'White', 'Silver']
    statuses = ['available', 'rented', 'maintenance']
    for i in range(1, 201):
        plate_no = random_string(6)
        model_id = random.randint(1, 100)
        color = random.choice(colors)
        office_id = random.randint(1, len(offices))
        mileage = random.randint(5000, 50000)
        status = random.choice(statuses)
        writer.writerow([plate_no, model_id, color, office_id, mileage, status])

# Auth Users
with open(auth_user_file, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined'])
    for i in range(1, 51):
        username = f'user{i}'
        email = f'user{i}@example.com'
        first_name = f'First{i}'
        last_name = f'Last{i}'
        is_staff = random.choice([True, False])
        is_active = True
        date_joined = random_date(datetime(2020, 1, 1), datetime(2023, 12, 31)).isoformat()
        writer.writerow([i, username, email, first_name, last_name, is_staff, is_active, date_joined])

# Customer Info
with open(customer_info_file, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['user_id', 'name', 'phone', 'address', 'license_no', 'license_expiry'])
    for i in range(1, 31):
        name = f'Customer{i}'
        phone = f'555-{random.randint(1000, 9999)}'
        address = f'{random.randint(1, 999)} Elm Street'
        license_no = random_string(8)
        license_expiry = random_date(datetime(2024, 1, 1), datetime(2030, 12, 31)).date().isoformat()
        writer.writerow([i, name, phone, address, license_no, license_expiry])

# Reservations
with open(reservations_file, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['id', 'user_id', 'vehicle_plate', 'owed_amount', 'pickup', 'dropoff', 'approved_at'])
    for i in range(1, 101):
        user_id = random.randint(1, 30)
        vehicle_plate = random_string(6)
        owed_amount = round(random.uniform(50, 500), 2)
        pickup = random_date(datetime(2024, 1, 1), datetime(2024, 6, 30))
        dropoff = pickup + timedelta(days=random.randint(1, 7))
        approved_at = pickup - timedelta(days=random.randint(1, 3))
        writer.writerow(
            [i, user_id, vehicle_plate, owed_amount, pickup.isoformat(), dropoff.isoformat(), approved_at.isoformat()])

print("CSV files generated successfully.")
