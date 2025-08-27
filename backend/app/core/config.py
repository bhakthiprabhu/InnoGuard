import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    JWT_SECRET = os.getenv("JWT_SECRET")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
    JWT_EXP_MINUTES = int(os.getenv("JWT_EXP_MINUTES"))

    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")

settings = Settings()
