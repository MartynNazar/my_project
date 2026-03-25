import uvicorn
import secrets
from typing import Annotated
from fastapi import FastAPI, Query, Form, Body, UploadFile, File, HTTPException, status, Depends
from starlette.requests import Request
from starlette.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from services.ORM import ORM
from jose import jwt, JWTError
from services.models import Song, User
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta






app = FastAPI(title="AudioServer")
app.mount("/static", StaticFiles(directory="static"), name="static")



templates = Jinja2Templates(directory="templates")

ORM.create_tables()



SECRET_KEY = "your_secret_key_here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
security = OAuth2PasswordBearer(tokenUrl="/token")




class Token(BaseModel):
    access_token: str
    token_type: str


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def authenticate_user(username: str, password: str):
    return ORM.get_correct_user(username, password)


@app.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user})
    return {"access_token": access_token, "token_type": "bearer"}


def get_current_user(token: str = Depends(security)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=404, detail="User not found")
        return username
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


@app.get("/")
async def main_page(request: Request):
    songs = ORM.get_all_users()
    return templates.TemplateResponse("audio_main_page.html", {"request": request, "songs": songs})

@app.get("/registration")
async def reg_page(request: Request):
    return templates.TemplateResponse("registration.html", {"request": request})

@app.get("/sign_page")
async def sig_page(request: Request):
    return templates.TemplateResponse("signing.html", {"request": request})


@app.get("/song/{song_id}")
async def p_song(request: Request, song_id: int):
    song_correct = ORM.get_song_by_id(song_id)
    return templates.TemplateResponse("song.html", {"request": request, "song_correct": song_correct})

@app.post("/add_song")
async def add_song(request: Request, name: Annotated[str, Form()], author: Annotated[str, Form()], year: Annotated[int, Form()], audio: Annotated[str, Form()], genre: Annotated[str, Form()], username: str = Depends(get_current_user)):
    new_song = Song()
    new_song.year = year
    new_song.name = name
    new_song.author = author
    new_song.audio = audio
    new_song.genre = genre
    ORM.add_record(new_song)
    songs = ORM.get_all_users()
    return templates.TemplateResponse("audio_main_page.html", {"request": request, "songs": songs})

@app.post("/added_user")
async def add_user(request: Request, username_of: Annotated[str, Form()], password_of: Annotated[str, Form()]):
    new_user = User()
    new_user.username = username_of
    new_user.password = password_of
    ORM.add_user(new_user)
    songs = ORM.get_all_users()
    return templates.TemplateResponse("registration.html", {"request": request, "songs": songs})

@app.get("/delete_song/{song_id}")
async def deleting_song(request: Request, song_id: int, username: str = Depends(get_current_user)):
    ORM.delete_record(song_id)
    songs = ORM.get_all_users()
    return templates.TemplateResponse("audio_main_page.html", {"request": request, "songs": songs})


@app.get("/add_page")
async def p_adding(request: Request):
    return templates.TemplateResponse("page-add-song.html", {"request": request})

@app.get("/change-song/{song_id}")
async def page_change(request: Request, song_id:int):
    song_correct = ORM.get_song_by_id(song_id)
    return templates.TemplateResponse("p_change.html", {"request": request, "song_correct": song_correct})

@app.get("/song/{song_id}/changed_song")
async def p_change(request: Request, name_new: Annotated[str, Query()], author_new: Annotated[str, Query()], year_new: Annotated[int, Query()], genre_new: Annotated[str, Query()], song_id: int, username: str = Depends(get_current_user)):
    song_correct = ORM.get_song_by_id(song_id)
    ORM.change_record(song_id, song_correct,year_new, name_new, author_new, genre_new)
    song_correct.name = name_new
    song_correct.author = author_new
    song_correct.year = year_new
    song_correct.genre = genre_new
    return templates.TemplateResponse("song.html", {"request": request, "song_correct": song_correct})

@app.post("/search_song")
async def searching(request: Request, author_name: Annotated[str, Form()]):
    songs_of_author = []
    songs = ORM.get_all_users()
    for song in songs:
        if song.author == author_name:
            songs_of_author.append(song)
    return templates.TemplateResponse("audio_main_page.html", {"request": request, "songs": songs_of_author})



#, username: str = Depends(get_current_user)

uvicorn.run(app, port=8005)