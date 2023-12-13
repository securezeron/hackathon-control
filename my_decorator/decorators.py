
from fastapi import APIRouter, Request, HTTPException, Depends, Header
from database.model import User
from utils import jwt_utils
from database.session import get_db
from sqlalchemy.orm import Session
import jwt

def jwt_authorization(authorization: str = Header(None), db: Session = Depends(get_db)):
    if not authorization or not authorization.startswith("Bearer "):
            
            raise HTTPException(status_code=401, detail="Bearer token not provided")

    token = authorization.split("Bearer ")[1]
    try:

        login_detail = db.query(User).filter(User.jwt_token == token).first()
        if login_detail is None:
             raise HTTPException(status_code=401, detail="Invalid token")

        user_id = jwt_utils.fetch_user_jwt(token)

        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
             raise HTTPException(status_code=404, detail="User not found")

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    return {"user_id": user_id}