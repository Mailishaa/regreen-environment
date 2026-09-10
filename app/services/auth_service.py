from fastapi import HTTPException, status

from app.core.security import verify_password, hash_password, create_access_token
from app.repositories.user_repository import UserRepository


def authenticate(db, email, password):
    user = UserRepository(db).get_by_email(email)

    if (
        not user
        or not user.is_active
        or not verify_password(password, user.password_hash)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    return user, create_access_token(str(user.id))


def register(db, data):
    repo = UserRepository(db)

    if repo.get_by_email(data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    return repo.create(
        email=data.email,
        password_hash=hash_password(data.password),
        full_name=data.full_name,
        role="institution",
    )
