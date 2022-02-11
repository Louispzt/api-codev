import os
import json
from time import time

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from functools import lru_cache
from sqlalchemy.orm import Session
import requests
import uvicorn

import authentification
import constants
import crud
from database import SessionLocal, engine
import models
import schemas
import utils

load_dotenv()

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(
    token: str = Depends(authentification.oauth2_scheme),
    db: SessionLocal = Depends(get_db),
):
    return await authentification.get_current_user(token, db)


async def get_current_active_user(
    current_user: schemas.User = Depends(get_current_user),
):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = authentification.authenticate_user(
        db, form_data.username, form_data.password
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = authentification.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/me", response_model=schemas.UserRead)
async def read_users_me(current_user: schemas.User = Depends(get_current_active_user)):
    return schemas.UserRead(
        username=current_user.username, bookmarks=current_user.bookmarks
    )


@app.post("/me/add_bookmark", response_model=schemas.Bookmark)
def create_bookmark_for_user(
    new_bookmark: schemas.BookmarkCreate,
    current_user: schemas.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    try:
        crud.create_user_bookmark(
            db, new_bookmark=new_bookmark, user_id=current_user.id
        )
    except:
        raise HTTPException(status_code=400, detail="bookmark already exists")


@app.post("/me/delete_bookmark", response_model=dict)
def delete_bookmark_for_user(
    bookmark: schemas.BookmarkBase,
    current_user: schemas.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    crud.delete_user_bookmark(db, current_user, bookmark)


@app.post("/signup")
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.read_user(db, user.username)
    if db_user is None:
        return crud.create_user(
            db, user.username, authentification.get_password_hash(user.password)
        )


@app.post("/delete")
def delete_user(
    current_user: schemas.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    crud.delete_user(db, current_user)


@app.post("/update")
def update_user(
    new_password: str,
    new_password_2,
    current_user: schemas.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    if new_password == new_password_2:
        return crud.update_user(
            db, current_user, authentification.get_password_hash(new_password)
        )
    raise HTTPException(status_code=400, detail="passwords don't match")


@app.get("/")
async def read_root():
    return {"API is working properly"}


@app.get("/eco2/sum/summary")
async def eCO2_energy_info_per_region_per_capita_daily(
    token: str = Depends(authentification.oauth2_scheme),
):
    """Return the consumption and the procution mix of electricity during the last 24h"""
    df_eco2 = get_eCO2_data(get_ttl_hash(900))

    df = utils.get_energy_mix_detail_per_region_per_capita_daily(df_eco2)

    return json.loads(df.to_json(orient="index"))


@app.get("/eco2/sum/{region}")
async def eCO2_energy_info_per_region_daily(
    region: str, token: str = Depends(authentification.oauth2_scheme)
):
    """Return the sum of energy, renewable and non renewable ones consumption during the last 24h"""
    df_eco2 = get_eCO2_data(get_ttl_hash(900))

    df = utils.get_energy_mix_detail_per_region_daily(df_eco2)

    if region == "all":
        df = df.drop(columns=["region"]).sum()
    else:
        try:
            df = df[df["region"] == region].drop(columns=["region"]).iloc[0]
        except:
            raise HTTPException(status_code=400, detail="region doesn't exist")

    return json.loads(df.to_json(orient="index"))


@app.get("/eco2/{region}")
async def eCO2_energy_info_per_region_every_15_minutes(
    region: str, token: str = Depends(authentification.oauth2_scheme)
):
    """Return the sum of the details of electricity consumption / production per region per 15 minutes, or in the whole country, in the last 24 hours"""
    df_eco2 = get_eCO2_data(get_ttl_hash(900))

    if region == "all":
        df = utils.get_sum(df_eco2)
    else:
        df = df_eco2[df_eco2["region"] == region].drop(columns=["region"])
    return json.loads(df.to_json(orient="records"))


@lru_cache(maxsize=1)
def get_eCO2_data(ttl_hash=None):
    """Return the last 24 hours data from eCO2 data. Updated every 15 minutes"""
    del ttl_hash

    response = requests.get(constants.ECO2_URL, params=utils.eCO2_24h_params())
    response.raise_for_status()
    return utils.get_dataframe_region(response.json())


def get_ttl_hash(seconds: int):
    """Return the same value withing `seconds` time period"""
    return time() // seconds * seconds


if __name__ == "__main__":
    uvicorn.run("main:app", port=int(os.environ["API_PORT"]), reload=True)
