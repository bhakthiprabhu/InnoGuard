# Privacy Gateway API

## Overview

The Privacy Gateway is a **role-aware Privacy-as-a-Service Gateway** for hospital data. It allows different user roles to access patient information safely:

* **doctor** → Full, original patient data.
* **Researchers** → De-identified patient data with pseudonymized IDs.
* **Developers** → Fake identities with realistic values for testing.

This ensures GDPR/HIPAA compliance while supporting research and development.

## Features

* **Role-based access control (RBAC)**
* **Audit & compliance logging**
* **Real-time pseudonymization & anonymization**
* **API-first approach**
* **Synthetic data generation for testing**

## Tech Stack

* Python 3.13+
* FastAPI
* PostgreSQL
* Psycopg2
* PyJWT
* Faker
* python-dotenv

## Folder Structure
```json

backend/
├── app
│   ├── app.py
│   ├── api
│   │   ├── auth.py
│   │   ├── patients.py
│   │   └── schemas.py
│   ├── core
│   │   ├── config.py
│   │   └── security.py
│   ├── db
│   │   └── connection.py
│   └── services
│       └── audit_service.py
├── database
│   ├── privacy_gateway-postgres-schema.sql
│   └── seed_patients.py
├── .env  
├── README.md
└── requirements.txt
```

## Setup Instructions

### 1. Clone Repository

```bash
git clone https://github.com/bhakthiprabhu/InnoGuard.git
cd backend
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the backend folder:

```env
DB_HOST=<your_db_host>
DB_PORT=<your_db_port>
DB_NAME=<your_db_name>
DB_USER=<your_db_user>
DB_PASSWORD=<your_db_password>

JWT_SECRET=<your_jwt_secret>
JWT_ALGORITHM=<your_jwt_algorithm>
JWT_EXP_MINUTES=<your_jwt_expiration_minutes>
```

### 4. Setup Database

* Create the PostgreSQL database.
* Run the schema script:

```bash
psql -d privacy_gateway -f privacy-gateway-postgres-schema.sql
```

### 5. Seed Sample Data (Optional)

```bash
python seed_patients.py
```

### 6. Run FastAPI Server

```bash
cd app
uvicorn app:app --reload
```

Server will be available at `http://127.0.0.1:8000`.

### 7. API Endpoints

#### Health Check

```http
GET /
```

#### Generate Token 

```http
POST /token
Content-Type: application/json

{
  "role": "researcher"   # clinician / developer
}
```

#### Fetch Patients (Role-based)

```http
GET /patients
Authorization: Bearer <your_token>
```

* Returns data according to your role:

  * Clinician → raw patients
  * Researcher → de-identified
  * Developer → fake identities


### 8. Audit Logging

All API accesses are logged with:

* `actor_id`
* `actor_role`
* `action`
* `patient_id` (real for doctor/devs)
* `meta` (pseudonymized IDs for researchers)
* `timestamp`


### 9. Notes

* Ensure sensitive data is never exported in plaintext to untrusted users.

## License

This project is licensed under the MIT License.

---