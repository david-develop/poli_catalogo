import os
from datetime import UTC, datetime, timedelta
from functools import wraps
from typing import Optional

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import EmailStr
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.models.models import Admin, Shopper, User
from app.models.schemas.auth import LoginForm, RegisterForm

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={status.HTTP_401_UNAUTHORIZED: {"user": "Not authorized"}},
)

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")


def get_password_hash(password):
    return bcrypt_context.hash(password)


def verify_password(plain_password, hashed_password):
    return bcrypt_context.verify(plain_password, hashed_password)


def get_user(request: Request, username: EmailStr):
    query = request.app.db.query(User)
    if username:
        return query.filter(User.username == username).first()
    return None


def authenticate_user(request: Request, username: EmailStr | str, password: str):
    user = get_user(request, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(
    email: str, user_id: str, expires_delta: Optional[timedelta] = None
):
    encode = {"sub": email, "id": user_id}
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=15)
    encode.update({"exp": expire})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(request: Request, token: str):
    try:
        if token is None:
            return None
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        user_id: str = payload.get("id")
        if email is None or user_id is None:
            return None
        return get_user(request, email)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )


def admin_only():
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = kwargs.get("request")
            bearer = request.headers.get("Authorization")
            token = bearer.split(" ")[1]
            if not token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token"
                )
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                user_email = payload.get("sub")
                user = await get_user(request, user_email)
                if user.get("role") != "admin":
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Admin role required",
                    )
                return await func(*args, **kwargs)
            except JWTError:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
                )

        return wrapper

    return decorator


@router.post("/token")
def login_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    user = authenticate_user(request, form_data.username, form_data.password)
    if not user:
        return None
    token_expires = timedelta(minutes=60)
    access_token = create_access_token(
        user.username, str(user.id), expires_delta=token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login")
def login(request: Request, data: LoginForm):
    try:
        validate_user_token = login_access_token(request, form_data=data)
        user = get_user(request, data.username)
        print(validate_user_token)
        token = validate_user_token.get("access_token")
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )
        return JSONResponse(
            content={
                "message": "Logged in",
                "token": token,
                "role": user.role,
                "full_name": user.full_name,
            },
            status_code=status.HTTP_200_OK,
        )
    except Exception as e:
        print(e)
        msg = "Error in credentials"
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg)


@router.get("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    return response


@router.post("/register")
async def register(
    request: Request,
    data: RegisterForm,
):
    print(data.email, data.full_name)
    user = get_user(request, data.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )
    if data.password != data.password_2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords don't match"
        )
    try:
        hashed_password = get_password_hash(data.password)
        if not data.role or data.role in ["user", "shopper"]:
            user_model = Shopper(
                full_name=data.full_name,
                username=data.email,
                hashed_password=hashed_password,
            )
        else:
            user_model = Admin(
                full_name=data.full_name,
                username=data.email,
                hashed_password=hashed_password,
            )
        request.app.db.add(user_model)
        request.app.db.commit()
        return JSONResponse(
            content={"message": f"User created successfully {data.email}"},
            status_code=status.HTTP_201_CREATED,
        )
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
