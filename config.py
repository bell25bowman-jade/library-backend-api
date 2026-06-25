import os

from dotenv import load_dotenv
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError


load_dotenv()


def _get_database_uri(default: str | None = None) -> str | None:
    database_uri = (
        os.getenv("SQLALCHEMY_DATABASE_URI")
        or os.getenv("SQLALCHEMY_DATABASE_URL")
        or os.getenv("DATABASE_URL")
        or default
    )

    if not database_uri:
        return None

    database_uri = database_uri.strip().strip('"').strip("'")

    if database_uri.startswith("postgres://"):
        database_uri = f"postgresql://{database_uri[len('postgres://') :]}"

    try:
        make_url(database_uri)
    except ArgumentError as exc:
        raise RuntimeError(
            "Invalid database URL in environment. Check Render DATABASE_URL or SQLALCHEMY_DATABASE_URL."
        ) from exc

    return database_uri


class ProductionConfig:
    SQLALCHEMY_DATABASE_URI = _get_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    CACHE_TYPE = "SimpleCache"
    

class developmentConfig:
    SQLALCHEMY_DATABASE_URI = _get_database_uri("sqlite:///library.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
