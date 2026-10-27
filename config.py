import os

from dotenv import load_dotenv

# Read variables from a local .env file (if present) into os.environ.
# Real environment variables win, so production can override the file.
load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///todos.db")
