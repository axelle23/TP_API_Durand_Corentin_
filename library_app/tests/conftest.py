import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models.base import Base
from src.db.session import get_db
from src.main import app


# Créer une base de données SQLite en mémoire pour les tests
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    # Créer les tables dans la base de données de test
    Base.metadata.create_all(bind=engine)

    # Créer une session de base de données pour les tests
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

    # Supprimer les tables après les tests
    Base.metadata.drop_all(bind=engine)


# Remplacer la dépendance get_db par get_test_db pour les tests
@pytest.fixture(scope="function")
def client(db_session):
    def get_test_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = get_test_db

    from fastapi.testclient import TestClient
    with TestClient(app) as client:
        yield client

    app.dependency_overrides = {}