from fastapi import APIRouter, Request, HTTPException, Depends, Header
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from database.model import User, Levels, Flags

from database.session import get_db
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, constr, ValidationError, validator
import bcrypt

from utils import jwt_utils
from datetime import datetime, timedelta
import jwt

router = APIRouter()


class UserCreate(BaseModel):
    username: constr(min_length=3, max_length=50)
    email: EmailStr
    password: constr(min_length=6, max_length=50)
    confirm_password: constr(min_length=6, max_length=50)

    @validator("confirm_password")
    def passwords_match(cls, v, values, **kwargs):
        if "password" in values and v != values["password"]:
            raise ValueError("Passwords do not match")
        return v


# API endpoint for user registration (sign-up)
@router.post("/signup")
def sign_up(user_data: UserCreate, db: Session = Depends(get_db)):
    hashed_password=bcrypt.hashpw(user_data.password.encode('utf-8'), bcrypt.gensalt())
    user = User(username=user_data.username, email=user_data.email, hashed_password=hashed_password.decode('utf-8'))
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "User registered successfully"}

class UserLogin(BaseModel): 
    username:str
    password:str

import uuid
@router.post("/login")
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == user_data.username).first()

    if user and bcrypt.checkpw(user_data.password.encode('utf-8'), user.hashed_password.encode('utf-8')):
        # Implement your authentication logic here (e.g., generate JWT token)

        access_token = jwt_utils.create_access_token({"user_id": user.id}, expires_delta=timedelta(days=7))
        user.jwt_token = access_token
        user.first_login = 1
        db.commit()

        # if user.first_login == 1:
        #     levels = db.query(Levels).all()
        #     for level in levels:
        #         flag_data = Flags(
        #             user_id = user.id,
        #             level_id = level.id,
        #             flag_details = f"Zero-one-{str(uuid.uuid4())}"
        #         )

        #         db.add(flag_data)
        #         db.commit()

        #     user.first_login = 0
        #     db.commit()

        
        db.refresh(user)
        return {
            "username": user.username,
            "access_token": user.jwt_token
        }

    raise HTTPException(status_code=401, detail="Invalid credentials")


@router.get("/get-all-user")
def get_all_user(db:Session = Depends(get_db)):

    all_user = db.query(User).all()

    return all_user


@router.get("/user-details")
async def user_details(request: Request, authorization: str = Header(None), db: Session = Depends(get_db)):
    # Retrieve the token from the headers
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split("Bearer ")[1]
        
        # Verify the token and get user details
        user_id = jwt_utils.fetch_user_jwt(token)
        user = db.query(User).filter(User.id == user_id).first()

        if user is not None:
            return {"id":user.id,"username": user.username, "email": user.email}
        else:
            raise HTTPException(status_code=404, detail="User not found")

    raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/logout")
async def logout(authorization: str = Header(None), db: Session = Depends(get_db)):
    try:
        # Check if authorization header is provided
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Bearer token not provided")

        # Retrieve the token from the headers
        token = authorization.split("Bearer ")[1]

        user_id = jwt_utils.fetch_user_jwt(token)
        user = db.query(User).filter(User.id == user_id).first()

        user.first_login = 0

        db.commit()
        # Perform any necessary actions for logging out (e.g., revoke token, update user status)
        # In this example, we are not invalidating the token, but you may want to implement token revocation logic
        # ...

        return {"message": "Logout successful"}

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")

    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")