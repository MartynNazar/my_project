import uvicorn
import os
from fastapi import FastAPI, Form, Depends, HTTPException, status, Response
from starlette.requests import Request
from starlette.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Annotated, Optional
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from services.ORM import ORM
from services.models import Song, User

if os.path.exists("songs.db"):
    try:
        os.remove("songs.db")
    except:
        pass

app = FastAPI(title="AudioServer")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

SECRET_KEY = "nazar_secret_key_2026"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
security = OAuth2PasswordBearer(tokenUrl="/token", auto_error=False)

ORM.create_tables()

s1 = Song(year=2023, name="Za Terykonamy", author="Myusli UA",
          audio="K1698732120_ua-ft_-misha-scorpion-za-terikonami-mega-mix.mp3", genre="Electronic")
s2 = Song(year=2004, name="Zoloto Karpat", author="Stepan Giga", audio="1766481336_giga-zoloto-karpat-maver-remix.mp3",
          genre="Pop")
s3 = Song(year=2023, name="Unochi", author="YAKTAK", audio="1694025342_yaktak-unoch.mp3", genre="Pop-Soul")

ORM.add_record(s1)
ORM.add_record(s2)
ORM.add_record(s3)

admin = User(username="admin", password="123")
ORM.add_user(admin)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token or not token.startswith("Bearer "):
        return None
    try:
        token = token.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None


@app.get("/")
async def main_page(request: Request):
    all_songs = ORM.get_all_users()
    return templates.TemplateResponse(
        request=request,
        name="audio_main_page.html",
        context={"songs": all_songs}
    )


@app.post("/token")
async def login_for_access_token(response: Response, form_data: OAuth2PasswordRequestForm = Depends()):
    user_name = ORM.get_correct_user(form_data.username, form_data.password)
    if not user_name:
        raise HTTPException(status_code=401, detail="Incorrect login or password")

    access_token = create_access_token(data={"sub": user_name})
    redirect_response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    redirect_response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return redirect_response


@app.get("/song/{song_id}")
async def p_song(request: Request, song_id: int):
    song_correct = ORM.get_song_by_id(song_id)
    return templates.TemplateResponse(
        request=request,
        name="song.html",
        context={"song_correct": song_correct}
    )


@app.get("/add_page")
async def p_adding(request: Request):
    return templates.TemplateResponse(request=request, name="page-add-song.html", context={})


@app.post("/add_song")
async def add_song(
        request: Request,
        name: Annotated[str, Form()],
        author: Annotated[str, Form()],
        year: Annotated[int, Form()],
        audio: Annotated[str, Form()],
        genre: Annotated[str, Form()]
):
    new_song = Song(year=year, name=name, author=author, audio=audio, genre=genre)
    ORM.add_record(new_song)
    songs = ORM.get_all_users()
    return templates.TemplateResponse(request=request, name="audio_main_page.html", context={"songs": songs})


@app.get("/delete_song/{song_id}")
async def deleting_song(request: Request, song_id: int):
    ORM.delete_record(song_id)
    songs = ORM.get_all_users()
    return templates.TemplateResponse(request=request, name="audio_main_page.html", context={"songs": songs})


@app.get("/registration")
async def reg_page(request: Request):
    return templates.TemplateResponse(request=request, name="registration.html", context={})


@app.get("/sign_page")
async def sig_page(request: Request):
    return templates.TemplateResponse(request=request, name="signing.html", context={})


@app.post("/added_user")
async def add_user(request: Request, username_of: Annotated[str, Form()], password_of: Annotated[str, Form()]):
    new_user = User(username=username_of, password=password_of)
    ORM.add_user(new_user)
    return templates.TemplateResponse(request=request, name="registration.html", context={})


@app.post("/search_song")
async def searching(request: Request, author_name: Annotated[str, Form()]):
    all_songs = ORM.get_all_users()
    filtered = [s for s in all_songs if author_name.lower() in s.author.lower()]
    return templates.TemplateResponse(request=request, name="audio_main_page.html", context={"songs": filtered})


@app.get("/change_page/{song_id}")
async def page_change(request: Request, song_id: int):
    song = ORM.get_song_by_id(song_id)
    return templates.TemplateResponse(request=request, name="p_change.html", context={"song_correct": song})


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8005)