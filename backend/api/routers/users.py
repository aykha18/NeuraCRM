from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from api.db import get_db
from api.dependencies import get_current_user
from api.models import User

router = APIRouter(prefix="/api/users", tags=["users"])


class CreateUserRequest(BaseModel):
    name: str
    email: EmailStr
    password: str  # plaintext; in a real system we'd hash here or call existing auth util


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str | None = None
    organization_id: int

    class Config:
        from_attributes = True


@router.get("", response_model=list[UserOut])
def list_users(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Return all users in the current user's organization."""
    users = db.query(User).filter(User.organization_id == current_user.organization_id).all()
    return users


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(payload: CreateUserRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create a user in the current organization (simple fast path)."""
    # Basic duplicate email check within org
    existing = (
        db.query(User)
        .filter(User.organization_id == current_user.organization_id, User.email == payload.email)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="A user with this email already exists in the organization")

    # For fast fix, store password as-is in password_hash; in production, hash it
    new_user = User(
        name=payload.name,
        email=payload.email,
        password_hash=payload.password,
        role="member",
        organization_id=current_user.organization_id,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete a user in the same organization (cannot delete yourself)."""
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot delete yourself")

    user = (
        db.query(User)
        .filter(User.id == user_id, User.organization_id == current_user.organization_id)
        .first()
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return None


