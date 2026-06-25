import os

from dotenv import load_dotenv


load_dotenv()


class ProductionConfig:
    SQLALCHEMY_DATABASE_URI = (
        os.getenv("SQLALCHEMY_DATABASE_URI")
        or os.getenv("SQLALCHEMY_DATABASE_URL")
        or os.getenv("DATABASE_URL")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    CACHE_TYPE = "SimpleCache"
    

class developmentConfig:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///library.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
