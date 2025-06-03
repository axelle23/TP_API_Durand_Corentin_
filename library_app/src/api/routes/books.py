from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any

from ...db.session import get_db
from ...models.books import Book as BookModel
from ..schemas.books import Book, BookCreate, BookUpdate
from ...repositories.books import BookRepository
from ...services.books import BookService
from ..dependencies import get_current_active_user, get_current_admin_user

router = APIRouter()


@router.get("/", response_model=List[Book])
def read_books(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_active_user)
) -> Any:
    """
    Récupère la liste des livres.
    """
    repository = BookRepository(BookModel, db)
    service = BookService(repository)
    books = service.get_multi(skip=skip, limit=limit)
    return books


@router.post("/", response_model=Book, status_code=status.HTTP_201_CREATED)
def create_book(
    *,
    db: Session = Depends(get_db),
    book_in: BookCreate,
    current_user = Depends(get_current_admin_user)
) -> Any:
    """
    Crée un nouveau livre.
    """
    repository = BookRepository(BookModel, db)
    service = BookService(repository)

    try:
        book = service.create(obj_in=book_in)
        return book
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{id}", response_model=Book)
def read_book(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user = Depends(get_current_active_user)
) -> Any:
    """
    Récupère un livre par son ID.
    """
    repository = BookRepository(BookModel, db)
    service = BookService(repository)
    book = service.get(id=id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Livre non trouvé"
        )
    return book


@router.put("/{id}", response_model=Book)
def update_book(
    *,
    db: Session = Depends(get_db),
    id: int,
    book_in: BookUpdate,
    current_user = Depends(get_current_admin_user)
) -> Any:
    """
    Met à jour un livre.
    """
    repository = BookRepository(BookModel, db)
    service = BookService(repository)
    book = service.get(id=id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Livre non trouvé"
        )

    try:
        book = service.update(db_obj=book, obj_in=book_in)
        return book
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{id}", response_model=Book)
def delete_book(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user = Depends(get_current_admin_user)
) -> Any:
    """
    Supprime un livre.
    """
    repository = BookRepository(BookModel, db)
    service = BookService(repository)
    book = service.get(id=id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Livre non trouvé"
        )
    book = service.remove(id=id)
    return book


@router.get("/search/title/{title}", response_model=List[Book])
def search_books_by_title(
    *,
    db: Session = Depends(get_db),
    title: str,
    current_user = Depends(get_current_active_user)
) -> Any:
    """
    Recherche des livres par titre.
    """
    repository = BookRepository(BookModel, db)
    service = BookService(repository)
    books = service.get_by_title(title=title)
    return books


@router.get("/search/author/{author}", response_model=List[Book])
def search_books_by_author(
    *,
    db: Session = Depends(get_db),
    author: str,
    current_user = Depends(get_current_active_user)
) -> Any:
    """
    Recherche des livres par auteur.
    """
    repository = BookRepository(BookModel, db)
    service = BookService(repository)
    books = service.get_by_author(author=author)
    return books


@router.get("/search/isbn/{isbn}", response_model=Book)
def search_book_by_isbn(
    *,
    db: Session = Depends(get_db),
    isbn: str,
    current_user = Depends(get_current_active_user)
) -> Any:
    """
    Recherche un livre par ISBN.
    """
    repository = BookRepository(BookModel, db)
    service = BookService(repository)
    book = service.get_by_isbn(isbn=isbn)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Livre non trouvé"
        )
    return book

    Mettez à jour le fichier src/api/routes/users.py de manière similaire, en utilisant le UserService.

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any

from ...db.session import get_db
from ...models.users import User as UserModel
from ..schemas.users import User, UserCreate, UserUpdate
from ...repositories.users import UserRepository
from ...services.users import UserService
from ..dependencies import get_current_active_user, get_current_admin_user

router = APIRouter()


@router.get("/", response_model=List[User])
def read_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_admin_user)
) -> Any:
    """
    Récupère la liste des utilisateurs.
    """
    repository = UserRepository(UserModel, db)
    service = UserService(repository)
    users = service.get_multi(skip=skip, limit=limit)
    return users


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
    current_user = Depends(get_current_admin_user)
) -> Any:
    """
    Crée un nouvel utilisateur.
    """
    repository = UserRepository(UserModel, db)
    service = UserService(repository)

    try:
        user = service.create(obj_in=user_in)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/me", response_model=User)
def read_user_me(
    current_user = Depends(get_current_active_user),
) -> Any:
    """
    Récupère l'utilisateur connecté.
    """
    return current_user


@router.put("/me", response_model=User)
def update_user_me(
    *,
    db: Session = Depends(get_db),
    user_in: UserUpdate,
    current_user = Depends(get_current_active_user)
) -> Any:
    """
    Met à jour l'utilisateur connecté.
    """
    repository = UserRepository(UserModel, db)
    service = UserService(repository)

    try:
        user = service.update(db_obj=current_user, obj_in=user_in)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{id}", response_model=User)
def read_user(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user = Depends(get_current_admin_user)
) -> Any:
    """
    Récupère un utilisateur par son ID.
    """
    repository = UserRepository(UserModel, db)
    service = UserService(repository)
    user = service.get(id=id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    return user


@router.put("/{id}", response_model=User)
def update_user(
    *,
    db: Session = Depends(get_db),
    id: int,
    user_in: UserUpdate,
    current_user = Depends(get_current_admin_user)
) -> Any:
    """
    Met à jour un utilisateur.
    """
    repository = UserRepository(UserModel, db)
    service = UserService(repository)
    user = service.get(id=id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )

    try:
        user = service.update(db_obj=user, obj_in=user_in)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{id}", response_model=User)
def delete_user(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user = Depends(get_current_admin_user)
) -> Any:
    """
    Supprime un utilisateur.
    """
    repository = UserRepository(UserModel, db)
    service = UserService(repository)
    user = service.get(id=id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )

    # Empêcher la suppression de l'utilisateur connecté
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Impossible de supprimer l'utilisateur connecté"
        )

    user = service.remove(id=id)
    return user


@router.get("/by-email/{email}", response_model=User)
def get_user_by_email(
    email: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
) -> Any:
    """
    Récupère un utilisateur par son email.
    """
    repository = UserRepository(UserModel, db)
    service = UserService(repository)
    user = service.get_by_email(email=email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    return user
