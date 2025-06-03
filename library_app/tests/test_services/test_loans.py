import pytest
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from src.models.loans import Loan as LoanModel
from src.models.books import Book as BookModel
from src.models.users import User as UserModel
from src.repositories.loans import LoanRepository
from src.services.loans import LoanService
from src.api.schemas.loans import LoanCreate, LoanUpdate


def test_create_loan(db_session: Session):
    """
    Test de création d'un emprunt.
    """
    # Arrange
    repository = LoanRepository(LoanModel, db_session)
    service = LoanService(repository)

    # Créer un utilisateur et un livre pour le test
    user = UserModel(
        email="loan_test@example.com",
        hashed_password="hashed_password",
        full_name="Loan Test User",
        is_active=True
    )
    db_session.add(user)

    book = BookModel(
        title="Loan Test Book",
        author="Loan Test Author",
        isbn="9876543210123",
        publication_year=2023,
        quantity=5
    )
    db_session.add(book)

    db_session.commit()
    db_session.refresh(user)
    db_session.refresh(book)

    loan_data = {
        "user_id": user.id,
        "book_id": book.id,
        "loan_date": datetime.utcnow(),
        "due_date": datetime.utcnow() + timedelta(days=14)
    }
    loan_in = LoanCreate(**loan_data)

    # Act
    loan = service.create(obj_in=loan_in)

    # Assert
    assert loan.user_id == loan_data["user_id"]
    assert loan.book_id == loan_data["book_id"]
    assert loan.return_date is None
    assert loan.extended is False


def test_get_active_loans_by_user(db_session: Session):
    """
    Test de récupération des emprunts actifs d'un utilisateur.
    """
    # Arrange
    repository = LoanRepository(LoanModel, db_session)
    service = LoanService(repository)

    # Créer un utilisateur et des livres pour le test
    user = UserModel(
        email="active_loans@example.com",
        hashed_password="hashed_password",
        full_name="Active Loans User",
        is_active=True
    )
    db_session.add(user)

    book1 = BookModel(
        title="Active Loan Book 1",
        author="Active Loan Author",
        isbn="1111222233334",
        publication_year=2023,
        quantity=5
    )
    db_session.add(book1)

    book2 = BookModel(
        title="Active Loan Book 2",
        author="Active Loan Author",
        isbn="4444333322221",
        publication_year=2023,
        quantity=3
    )
    db_session.add(book2)

    db_session.commit()
    db_session.refresh(user)
    db_session.refresh(book1)
    db_session.refresh(book2)

    # Créer un emprunt actif
    active_loan = LoanModel(
        user_id=user.id,
        book_id=book1.id,
        loan_date=datetime.utcnow() - timedelta(days=7),
        due_date=datetime.utcnow() + timedelta(days=7),
        return_date=None,
        extended=False
    )
    db_session.add(active_loan)

    # Créer un emprunt retourné
    returned_loan = LoanModel(
        user_id=user.id,
        book_id=book2.id,
        loan_date=datetime.utcnow() - timedelta(days=14),
        due_date=datetime.utcnow() - timedelta(days=7),
        return_date=datetime.utcnow() - timedelta(days=2),
        extended=False
    )
    db_session.add(returned_loan)

    db_session.commit()

    # Act
    active_loans = service.get_active_loans_by_user(user_id=user.id)

    # Assert
    assert len(active_loans) == 1
    assert active_loans[0].user_id == user.id
    assert active_loans[0].book_id == book1.id
    assert active_loans[0].return_date is None


def test_return_loan(db_session: Session):
    """
    Test de retour d'un emprunt.
    """
    # Arrange
    repository = LoanRepository(LoanModel, db_session)
    service = LoanService(repository)

    # Créer un utilisateur et un livre pour le test
    user = UserModel(
        email="return_loan@example.com",
        hashed_password="hashed_password",
        full_name="Return Loan User",
        is_active=True
    )
    db_session.add(user)

    book = BookModel(
        title="Return Loan Book",
        author="Return Loan Author",
        isbn="5555666677778",
        publication_year=2023,
        quantity=2
    )
    db_session.add(book)

    db_session.commit()
    db_session.refresh(user)
    db_session.refresh(book)

    # Créer un emprunt actif
    loan = LoanModel(
        user_id=user.id,
        book_id=book.id,
        loan_date=datetime.utcnow() - timedelta(days=7),
        due_date=datetime.utcnow() + timedelta(days=7),
        return_date=None,
        extended=False
    )
    db_session.add(loan)
    db_session.commit()
    db_session.refresh(loan)

    # Act
    returned_loan = service.return_loan(loan_id=loan.id)

    # Assert
    assert returned_loan.id == loan.id
    assert returned_loan.return_date is not None

    # Vérifier que l'emprunt est bien marqué comme retourné dans la base de données
    db_loan = db_session.query(LoanModel).filter(LoanModel.id == loan.id).first()
    assert db_loan.return_date is not None


def test_extend_loan(db_session: Session):
    """
    Test de prolongation d'un emprunt.
    """
    # Arrange
    repository = LoanRepository(LoanModel, db_session)
    service = LoanService(repository)

    # Créer un utilisateur et un livre pour le test
    user = UserModel(
        email="extend_loan@example.com",
        hashed_password="hashed_password",
        full_name="Extend Loan User",
        is_active=True
    )
    db_session.add(user)

    book = BookModel(
        title="Extend Loan Book",
        author="Extend Loan Author",
        isbn="8888999900001",
        publication_year=2023,
        quantity=1
    )
    db_session.add(book)

    db_session.commit()
    db_session.refresh(user)
    db_session.refresh(book)

    # Créer un emprunt actif
    original_due_date = datetime.utcnow() + timedelta(days=3)
    loan = LoanModel(
        user_id=user.id,
        book_id=book.id,
        loan_date=datetime.utcnow() - timedelta(days=11),
        due_date=original_due_date,
        return_date=None,
        extended=False
    )
    db_session.add(loan)
    db_session.commit()
    db_session.refresh(loan)

    # Act
    extended_loan = service.extend_loan(loan_id=loan.id, days=7)

    # Assert
    assert extended_loan.id == loan.id
    assert extended_loan.extended is True
    assert extended_loan.due_date > original_due_date

    # Vérifier que la date d'échéance a bien été prolongée de 7 jours
    expected_due_date = original_due_date + timedelta(days=7)
    assert abs((extended_loan.due_date - expected_due_date).total_seconds()) < 60  # Tolérance d'une minute


def test_get_overdue_loans(db_session: Session):
    """
    Test de récupération des emprunts en retard.
    """
    # Arrange
    repository = LoanRepository(LoanModel, db_session)
    service = LoanService(repository)

    # Créer un utilisateur et des livres pour le test
    user = UserModel(
        email="overdue_loans@example.com",
        hashed_password="hashed_password",
        full_name="Overdue Loans User",
        is_active=True
    )
    db_session.add(user)

    book1 = BookModel(
        title="Overdue Loan Book 1",
        author="Overdue Loan Author",
        isbn="1212121212121",
        publication_year=2023,
        quantity=1
    )
    db_session.add(book1)

    book2 = BookModel(
        title="Overdue Loan Book 2",
        author="Overdue Loan Author",
        isbn="2323232323232",
        publication_year=2023,
        quantity=1
    )
    db_session.add(book2)

    book3 = BookModel(
        title="Overdue Loan Book 3",
        author="Overdue Loan Author",
        isbn="3434343434343",
        publication_year=2023,
        quantity=1
    )
    db_session.add(book3)

    db_session.commit()
    db_session.refresh(user)
    db_session.refresh(book1)
    db_session.refresh(book2)
    db_session.refresh(book3)

    # Créer un emprunt en retard
    overdue_loan = LoanModel(
        user_id=user.id,
        book_id=book1.id,
        loan_date=datetime.utcnow() - timedelta(days=21),
        due_date=datetime.utcnow() - timedelta(days=7),
        return_date=None,
        extended=False
    )
    db_session.add(overdue_loan)

    # Créer un emprunt actif mais pas en retard
    active_loan = LoanModel(
        user_id=user.id,
        book_id=book2.id,
        loan_date=datetime.utcnow() - timedelta(days=7),
        due_date=datetime.utcnow() + timedelta(days=7),
        return_date=None,
        extended=False
    )
    db_session.add(active_loan)

    # Créer un emprunt retourné qui était en retard
    returned_overdue_loan = LoanModel(
        user_id=user.id,
        book_id=book3.id,
        loan_date=datetime.utcnow() - timedelta(days=21),
        due_date=datetime.utcnow() - timedelta(days=7),
        return_date=datetime.utcnow() - timedelta(days=1),
        extended=False
    )
    db_session.add(returned_overdue_loan)

    db_session.commit()

    # Act
    overdue_loans = service.get_overdue_loans()

    # Assert
    assert len(overdue_loans) == 1
    assert overdue_loans[0].id == overdue_loan.id
    assert overdue_loans[0].user_id == user.id
    assert overdue_loans[0].book_id == book1.id
    assert overdue_loans[0].due_date < datetime.utcnow()
    assert overdue_loans[0].return_date is None