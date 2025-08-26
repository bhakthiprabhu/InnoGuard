import psycopg2
import random
from faker import Faker
from dotenv import load_dotenv
import os
from datetime import date, timedelta

# Load environment variables
load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

fake = Faker("en_IN")

# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)
cur = conn.cursor()

diseases = ["Diabetes", "Hypertension", "Asthma", "Cancer", "Heart Disease"]

for _ in range(1000):
    name = fake.name()
    phone = "+91-" + str(fake.random_int(min=7000000000, max=9999999999))
    email = fake.email()
    address = fake.address().replace("\n", ", ")
    age = random.randint(20, 80)
    disease = random.choice(diseases)
    purchase_amount = round(random.uniform(200, 5000), 2)

    # Derive date_of_birth from age
    today = date.today()
    dob_year = today.year - age
    # random day in that year
    dob = date(dob_year, random.randint(1, 12), random.randint(1, 28))

    cur.execute("""
        INSERT INTO privacy_gateway.patients
        (name, phone, email, address, date_of_birth, age, disease, purchase_amount)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (name, phone, email, address, dob, age, disease, purchase_amount))

conn.commit()
cur.close()
conn.close()
print("✅ Inserted 1000 patients with DOB filled in!")
