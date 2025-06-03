import pytest
from sqlalchemy.orm import Session

from src.models.users import User as UserModel
from src.repositories.users import UserRepository
from src.services.users import UserService
from src.api.schemas.users import UserCreate, UserUpdate


def test_create_user(db_session: Session):
    """
    Test de création d'un utilisateur.
    """
    # Arrange
    repository = UserRepository(UserModel, db_session)
    service = UserService(repository)

    user_data = {
        "email": "test@example.com",
        "password": "password123",
        "full_name": "Test User"
    }
    user_in = UserCreate(**user_data)

    # Act
    user = service.create(obj_in=user_in)

    # Assert
    assert user.email == user_data["email"]
    assert user.full_name == user_data["full_name"]
    assert user.hashed_password != user_data["password"]  # Le mot de passe doit être hashé
    assert service.verify_password(user_data["password"], user.hashed_password)
    assert user.is_active is True
    assert user.is_admin is False


def test_authenticate_user(db_session: Session):
    """
    Test d'authentification d'un utilisateur.
    """
    # Arrange
    repository = UserRepository(UserModel, db_session)
    service = UserService(repository)

    email = "auth_test@example.com"
    password = "securepassword"

    user_data = {
        "email": email,
        "password": password,
        "full_name": "Auth Test User"
    }
    user_in = UserCreate(**user_data)
    service.create(obj_in=user_in)

    # Act
    authenticated_user = service.authenticate(email=email, password=password)

    # Assert
    assert authenticated_user is not None
    assert authenticated_user.email == email


def test_authenticate_user_invalid_password(db_session: Session):
    """
    Test d'authentification avec un mot de passe invalide.
    """
    # Arrange
    repository = UserRepository(UserModel, db_session)
    service = UserService(repository)

    email = "auth_test2@example.com"
    password = "securepassword"

    user_data = {
        "email": email,
        "password": password,
        "full_name": "Auth Test User 2"
    }
    user_in = UserCreate(**user_data)
    service.create(obj_in=user_in)

    # Act
    authenticated_user = service.authenticate(email=email, password="wrongpassword")

    # Assert
    assert authenticated_user is None


def test_authenticate_user_nonexistent(db_session: Session):
    """
    Test d'authentification avec un utilisateur inexistant.
    """
    # Arrange
    repository = UserRepository(UserModel, db_session)
    service = UserService(repository)

    # Act
    authenticated_user = service.authenticate(email="nonexistent@example.com", password="anypassword")

    # Assert
    assert authenticated_user is None


def test_get_user_by_email(db_session: Session):
    """
    Test de récupération d'un utilisateur par email.
    """
    # Arrange
    repository = UserRepository(UserModel, db_session)
    service = UserService(repository)

    email = "email_test@example.com"
    user_data = {
        "email": email,
        "password": "password123",
        "full_name": "Email Test User"
    }
    user_in = UserCreate(**user_data)
    created_user = service.create(obj_in=user_in)

    # Act
    user = service.get_by_email(email=email)

    # Assert
    assert user is not None
    assert user.id == created_user.id
    assert user.email == email


def test_update_user(db_session: Session):
    """
    Test de mise à jour d'un utilisateur.
    """
    # Arrange
    repository = UserRepository(UserModel, db_session)
    service = UserService(repository)

    # Créer un utilisateur pour le test
    user_data = {
        "email": "update_test@example.com",
        "password": "password123",
        "full_name": "Original Name"
    }
    user_in = UserCreate(**user_data)
    user = service.create(obj_in=user_in)

    # Données de mise à jour
    update_data = {
        "full_name": "Updated Name",
        "is_active": False
    }
    user_update = UserUpdate(**update_data)

    # Act
    updated_user = service.update(db_obj=user, obj_in=user_update)

    # Assert
    assert updated_user.id == user.id
    assert updated_user.email == user_data["email"]  # Non modifié
    assert updated_user.full_name == update_data["full_name"]
    assert updated_user.is_active == update_data["is_active"]


def test_update_user_password(db_session: Session):
    """
    Test de mise à jour du mot de passe d'un utilisateur.
    """
    # Arrange
    repository = UserRepository(UserModel, db_session)
    service = UserService(repository)

    # Créer un utilisateur pour le test
    old_password = "oldpassword"
    new_password = "newpassword"

    user_data = {
        "email": "password_update@example.com",
        "password": old_password,
        "full_name": "Password Update User"
    }
    user_in = UserCreate(**user_data)
    user = service.create(obj_in=user_in)

    # Vérifier que l'ancien mot de passe fonctionne
    assert service.authenticate(email=user.email, password=old_password) is not None

    # Données de mise à jour
    update_data = {
        "password": new_password
    }
    user_update = UserUpdate(**update_data)

    # Act
    updated_user = service.update(db_obj=user, obj_in=user_update)

    # Assert
    assert updated_user.id == user.id
    assert service.verify_password(new_password, updated_user.hashed_password)
    assert not service.verify_password(old_password, updated_user.hashed_password)

    # Vérifier que l'authentification fonctionne avec le nouveau mot de passe
    assert service.authenticate(email=user.email, password=new_password) is not None
    assert service.authenticate(email=user.email, password=old_password) is None


def test_is_active(db_session: Session):
    """
    Test de la méthode is_active.
    """
    # Arrange
    repository = UserRepository(UserModel, db_session)
    service = UserService(repository)

    # Créer un utilisateur actif
    active_user_data = {
        "email": "active@example.com",
        "password": "password123",
        "full_name": "Active User",
        "is_active": True
    }
    active_user = UserModel(**active_user_data)
    db_session.add(active_user)

    # Créer un utilisateur inactif
    inactive_user_data = {
        "email": "inactive@example.com",
        "password": "password123",
        "full_name": "Inactive User",
        "is_active": False
    }
    inactive_user = UserModel(**inactive_user_data)
    db_session.add(inactive_user)

    db_session.commit()

    # Act & Assert
    assert service.is_active(active_user) is True
    assert service.is_active(inactive_user) is False


def test_is_admin(db_session: Session):
    """
    Test de la méthode is_admin.
    """
    # Arrange
    repository = UserRepository(UserModel, db_session)
    service = UserService(repository)

    # Créer un utilisateur admin
    admin_user_data = {
        "email": "admin@example.com",
        "password": "password123",
        "full_name": "Admin User",
        "is_admin": True
    }
    admin_user = UserModel(**admin_user_data)
    db_session.add(admin_user)

    # Créer un utilisateur non-admin
    regular_user_data = {
        "email": "regular@example.com",
        "password": "password123",
        "full_name": "Regular User",
        "is_admin": False
    }
    regular_user = UserModel(**regular_user_data)
    db_session.add(regular_user)

    db_session.commit()

    # Act & Assert
    assert service.is_admin(admin_user) is True
    assert service.is_admin(regular_user) is False