from sqlalchemy.orm import Session

import models
import schemas


def create_user(db: Session, username: str, hashed_password: str):
    db_user = models.User(username=username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)


def create_user_bookmark(db: Session, new_bookmark: schemas.BookmarkBase, user_id: int):
    db_bookmark = models.Bookmark(**new_bookmark.dict(), owner_id=user_id)
    db.add(db_bookmark)
    db.commit()
    db.refresh(db_bookmark)


def read_user(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def update_user(db: Session, db_user: schemas.UserInDb, new_hashed_password: str):
    db_user.hashed_password = new_hashed_password
    db.add(db_user)
    db.commit()
    db.refresh(db_user)


def delete_user(db: Session, user: schemas.User):
    db.query(models.User).filter(models.User.username == user.username).delete()
    db.commit()


def delete_user_bookmark(
    db: Session, user: schemas.User, bookmark: schemas.BookmarkBase
):
    db.query(models.Bookmark).filter(
        models.Bookmark.title == bookmark.title, models.Bookmark.owner_id == user.id
    ).delete()
    db.commit()
