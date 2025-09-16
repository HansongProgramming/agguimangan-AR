from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from .. import models, auth
from ..database import get_db

router = APIRouter(prefix="/auth")


class UserCreate(BaseModel):
    name: str
    phone_number: str
    email: EmailStr
    password: str

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


# -------------------------
# Signup with Auto-Login
# -------------------------
@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(
    name: str = Form(...),
    phone_number: str = Form(...),
    email: EmailStr = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    # Check if email already registered
    result = await db.execute(select(models.User).where(models.User.email == email))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create new user
    new_user = models.User(
        name=name,
        phone_number=phone_number,
        email=email,
        password_hash=auth.hash_password(password)
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # Create token (store email as subject for consistency with auth.get_current_user)
    token = auth.create_access_token({"sub": new_user.email})

    # Redirect & set HttpOnly cookie
    response = RedirectResponse(url="/main", status_code=303)
    response.set_cookie(
        key="access_token",
        value=token,  # no "Bearer " prefix here, auth.py handles it
        httponly=True,
        max_age=60 * 60 * 24,  # 1 day
        secure=False,  # change to True in production with HTTPS
        samesite="lax",
    )
    return response


# -------------------------
# Login with Cookie
# -------------------------
@router.post("/login")
async def login(
    email: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(models.User).where(models.User.email == email))
    db_user = result.scalars().first()

    if not db_user or not auth.verify_password(password, db_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Create token
    token = auth.create_access_token({"sub": db_user.email})

    # Redirect & set HttpOnly cookie
    response = RedirectResponse(url="/booking", status_code=303)
    response.set_cookie(
        key="access_token",
        value=token,  # again, no Bearer prefix
        httponly=True,
        max_age=60 * 60 * 24,
        secure=False,  # True if HTTPS
        samesite="lax",
    )
    return response
