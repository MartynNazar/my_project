import os
import sys
from datetime import datetime, timedelta
import uvicorn
from typing import Annotated
from fastapi import FastAPI, Query, Form, Depends, HTTPException, status
from starlette.requests import Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from starlette.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from ..services.ORM import ORM
from jose import JWTError, jwt
from passlib.context import CryptContext

app = FastAPI(title="AudioServer")

@app.post("/song/{{song_name}}")
def p_car(request: Request, car_id):
    all_songs = ORM.get_all_cars()
    song = all_songs[int(car_id) - 1]
    return templates.TemplateResponse("song.html", {"request": request, "song": song})




app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


class Song(BaseModel):
    year: int
    name: Annotated[str, Query] = Query(description="Name of song", min_length=2, max_length=40)
    author: Annotated[str, Query] = Query(description="Author of song", max_length=100)
    audio: str
    genre: Annotated[str, Query] = Query(min_length=2, max_length=100, default="None")

class User(BaseModel):
    username: str
    password: str

songs = []
songs.append(Song(year = 2021,name = "Tighter", author = "KRBK", audio = "Krbk_-_Krepche.mp3", genre="Rap"))
songs.append(Song(year = 2022, name = "Knife", author = "KRBK", audio = "Krbk Нож.mp3", genre="Rap-pop"))
songs.append(Song(year = 2023, name = "Gentle", author = "Zink Urodov", audio = "cink-urodov-nezhnaya-mp3.mp3", genre="Rap-pop"))


@app.get("/")
async def main_page(request: Request):
    return templates.TemplateResponse("audio_main_page.html", {"request": request, "songs": songs})


@app.post("/add_song")
async def add_song(request: Request, name: Annotated[str, Form()], author: Annotated[str, Form()], year: Annotated[int, Form()], audio: Annotated[str, Form()], genre: Annotated[str, Form()]):
    new_song = Song(year=year, name=name, author=author, audio=audio, genre=genre)
    songs.append(new_song)
    return templates.TemplateResponse("audio_main_page.html", {"request": request, "songs": songs})

@app.get("/add_page")
async def p_adding(request: Request):
    return templates.TemplateResponse("page-add-song.html", {"request": request})

@app.get("/change-song/{song_name}")
async def page_change(request: Request, song_name:str):
    index = next((i for i, obj in enumerate(songs) if obj.name == song_name), None)
    song_correct = songs[index]
    return templates.TemplateResponse("p_change.html", {"request": request, "song_correct": song_correct})

@app.get("/song/{song_name}")
async def p_song(request: Request, song_name: str):
    index = next((i for i, obj in enumerate(songs) if obj.name == song_name), None)
    song_correct = songs[index]
    if index is not None:
        return templates.TemplateResponse("song.html", {"request": request, "song_correct": song_correct})

@app.get("/delete_song/{song_name}", name="deleting_song")
async def deleting_song(request: Request, song_name: str):
    index = next((i for i, obj in enumerate(songs) if obj.name == song_name), None)
    song_correct = songs[index]
    if index is not None:
        songs.remove(song_correct)
        return templates.TemplateResponse("audio_main_page.html", {"request": request, "songs": songs})

@app.get("/song/{song_name}/change_song")
async def p_change(request: Request, song_name, name_new: Annotated[str, Query()], author_new: Annotated[str, Query()], year_new: Annotated[int, Query()], genre_new: Annotated[str, Query()]):
    index = next((i for i, obj in enumerate(songs) if obj.name == song_name), None)
    song_correct = songs[index]
    if index is not None:
        song_correct.name = name_new
        song_correct.author = author_new
        song_correct.year = year_new
        song_correct.genre = genre_new
        return templates.TemplateResponse("song.html", {"request": request, "song_correct": song_correct})

@app.post("/search_song")
async def searching(request: Request, author_name: Annotated[str, Form()]):
    songs_of_author = []
    for song in songs:
        if song.author == author_name:
            songs_of_author.append(song)
    return templates.TemplateResponse("audio_main_page.html", {"request": request, "songs": songs_of_author})


@app.post("/delete-all-songs")
def delete_all(request: Request):
    songs.clear()
    return templates.TemplateResponse("audio_main_page.html", {"request": request, "songs": songs})







song1 = Song(
    year=2021,
    name="Tighter",
    author="KRBK",
    audio="Krbk_-_Krepche.mp3",
    genre="Rap"
)

# Створюємо другу пісню
song2 = Song(
    year=2022,
    name="Knife",
    author="KRBK",
    audio="Krbk Нож.mp3",
    genre="Rap-pop"
)

# Створюємо третю пісню
song3 = Song(
    year=2023,
    name="Gentle",
    author="Zink Urodov",
    audio="cink-urodov-nezhnaya-mp3.mp3",
    genre="Rap-pop"
)

# Тепер ці команди спрацюють без помилок
ORM.add_record(song1)
ORM.add_record(song2)
ORM.add_record(song3)

# І користувач (теж дані в дужках)
user1 = User(username="admin", password="1234")
ORM.add_user(user1)





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
    if username == "admin" and password == "secret":
        return username
    return None


@app.post("/regis", response_model=Token)
def reg_token(name_user: Annotated[str, Form()], password_user: Annotated[str, Form()], request: Request):
    user = authenticate_user(name_user, password_user)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user})
    return templates.TemplateResponse("registration.html", {"access_token": access_token, "token_type": "bearer", "request": request})

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
            headers={"WWW-Authenticate": "Bearer"})


uvicorn.run(app, port=8005)