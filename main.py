from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware


from router import event, auth

from database.session import engine
from database import model

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from fastapi.responses import HTMLResponse

model.Base.metadata.create_all(bind=engine)

app = FastAPI()


templates = Jinja2Templates(directory="templates")



app.mount("/static", StaticFiles(directory="static"), name="static")
# app.mount("/assets", StaticFiles(directory="assets"), name="assets")

#-----------------------------------------CORS----------------------------------------
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#-----------------------------------------CORS----------------------------------------

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(event.router, prefix="/event", tags=["Event"])


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("zero_index.html", {"request": request})

if __name__ == "__main__":
    import uvicorn

    uvicorn_params = {
        "app": "main:app",
        "host": "0.0.0.0",
        "port": 8000,
        "reload": True,
    }

    uvicorn.run(**uvicorn_params)