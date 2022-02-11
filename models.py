from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    PrimaryKeyConstraint,
    String,
)
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    bookmarks = relationship("Bookmark", back_populates="owner", cascade="all, delete")


class Bookmark(Base):
    __tablename__ = "bookmark"

    title = Column(String, index=True)
    description = Column(String, index=True)
    owner_id = Column(
        Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )

    __table_args__ = (PrimaryKeyConstraint(title, owner_id),)

    owner = relationship("User", back_populates="bookmarks")
