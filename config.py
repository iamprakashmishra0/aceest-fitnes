"""Application configuration for ACEest Fitness & Gym."""

import atexit
import os
import tempfile

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def _temporary_database() -> str:
    """Return a unique throwaway SQLite path that is removed at exit."""

    descriptor, path = tempfile.mkstemp(prefix="aceest_test_", suffix=".db")
    os.close(descriptor)
    atexit.register(lambda: os.path.exists(path) and os.remove(path))
    return path


class Config:
    """Base configuration shared across environments."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "aceest-dev-secret-change-me")
    DATABASE = os.environ.get(
        "ACEEST_DATABASE", os.path.join(BASE_DIR, "aceest_fitness.db")
    )
    JSON_SORT_KEYS = False
    DEBUG = False
    TESTING = False


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    # A fresh temporary file per process keeps tests isolated and deterministic.
    DATABASE = os.environ.get("ACEEST_TEST_DATABASE") or _temporary_database()


class ProductionConfig(Config):
    DEBUG = False
