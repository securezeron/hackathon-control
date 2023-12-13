from fastapi import APIRouter, Request, HTTPException, Depends, Header

from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from database.session import get_db
from sqlalchemy.orm import Session

from database.model import Flags, ScoreBoard, User, Levels

from utils import jwt_utils
from fastapi.security import OAuth2PasswordBearer

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

from fastapi.encoders import jsonable_encoder

import jwt

router = APIRouter()

templates = Jinja2Templates(directory="templates")

# Configure static files for the router
# router.mount("/static", StaticFiles(directory='/zeron/static'), name="static")

@router.get("/index", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/forget-password", response_class=HTMLResponse)
async def forget_password(request: Request):
    return templates.TemplateResponse("forget_password.html", {"request": request})

@router.get("/dashboard", response_class=HTMLResponse)
async def forget_password(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

class VerifyOTPRequest(BaseModel):
    username: str
    otp: str

@router.post("/verify-otp")
async def verify_otp(request_data: VerifyOTPRequest):
    raise HTTPException(status_code=401, detail="Unauthorized")


@router.get("/zero-login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("zero_login.html", {"request": request})

@router.get("/zero-registration", response_class=HTMLResponse)
async def register(request: Request):
    return templates.TemplateResponse("zero_registration.html", {"request": request})


@router.get("/zeron_dashboard", response_class=HTMLResponse)
async def zeron_dashboard(request: Request):
    return templates.TemplateResponse("zeron_dashboard.html", {"request": request})



# FastAPI endpoint
@router.get("/get-level/{user_id}")
async def get_level(user_id: int, db: Session = Depends(get_db)):

    # SQLAlchemy query to retrieve levels ordered by priority
    levels = (
        db.query(Levels)
        .order_by(Levels.priority)
        .all()
    )

    # SQLAlchemy query to retrieve flags for the specific user
    user_flags = (
        db.query(Flags)
        .filter(Flags.user_id == user_id)
        .all()
    )

    # Create a set of level IDs that are submitted by the user
    submitted_level_ids = {flag.level_id for flag in user_flags if flag.is_submitted}

    # Filter the levels based on whether the corresponding flag is not submitted
    filtered_levels = [
        {"id": level.id, "name": level.name, "score": level.score, "flag": level.flag, "priority": level.priority, "endpoint": level.endpoint}
        for level in levels
        if level.id not in submitted_level_ids
    ]

    print(filtered_levels)

    if len(filtered_levels) == 0:
        return {"message": "All level submitted"}
    else:
        return filtered_levels[0]

class FlagDetails(BaseModel):
    level: int
    flag: str

@router.post("/submit-flag")
async def submit_flag(flag_data: FlagDetails, authorization: str = Header(None), db: Session = Depends(get_db)):

    try:
        # Check if authorization header is provided
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Bearer token not provided")

        # Retrieve the token from the headers
        token = authorization.split("Bearer ")[1]

        # Verify the token and get user details
        user_id = jwt_utils.fetch_user_jwt(token)

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")

    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Continue with the rest of your code
    level_details = db.query(Levels).filter(Levels.id == flag_data.level, Levels.flag == flag_data.flag).first()

    if level_details is None:
        return {"message": "Incorrect flag"}
    
    flag_obj = Flags(user_id = user_id, level_id = level_details.id, is_submitted = 1)
    db.add(flag_obj)
    db.commit()

    score = db.query(ScoreBoard).filter(ScoreBoard.user_id == user_id).first()

    if score is None:
        new_score = ScoreBoard(
            user_id=user_id,
            final_score=level_details.score
        )
        db.add(new_score)
        db.commit()
    else:
        score.final_score += level_details.score
        db.commit()

    return {"message": "Flag submitted"}
    

    
@router.get("/scoreboard")
async def scoreboard(db: Session = Depends(get_db)):

    scores = db.query(ScoreBoard).order_by(-ScoreBoard.final_score).all()
    
    data = []

    for score in scores:
        user_data = db.query(User).get(score.user_id)
        uu = jsonable_encoder(score)
        uu['username'] = user_data.username
        data.append(uu)


    return data
