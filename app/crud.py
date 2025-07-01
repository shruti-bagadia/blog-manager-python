# app/crud.py

from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session
from . import models
from .schema import author , post

def get_author_by_uuid(db: Session, author_uuid: str) -> Optional[models.Author]:
    return (
        db.query(models.Author)
          .filter(models.Author.author_uuid == author_uuid)
          .first()
    )

def create_author(db: Session, author_in: author.AuthorCreate) -> models.Author:
    author = models.Author(**author_in.dict())
    db.add(author); db.commit(); db.refresh(author)
    return author

def get_post_by_uuid(db: Session, post_uuid: str) -> Optional[models.Post]:
    return (
        db.query(models.Post)
          .filter(models.Post.post_uuid == post_uuid)
          .first()
    )

def get_posts(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    author_uuid: Optional[str] = None,
    date_from: Optional[date] = None,
) -> List[models.Post]:
    q = db.query(models.Post)
    if author_uuid:
        q = q.filter(models.Post.author_uuid == author_uuid)
    if date_from:
        q = q.filter(models.Post.created_at >= date_from)
    return (
        q.order_by(models.Post.created_at.desc())
         .offset(skip)
         .limit(limit)
         .all()
    )

def create_post(db: Session, post_in: post.PostCreate) -> models.Post:
    post = models.Post(**post_in.dict())
    db.add(post); db.commit(); db.refresh(post)
    return post

def update_post(
    db: Session,
    post: models.Post,
    update_in: post.PostUpdate
) -> models.Post:
    for k, v in update_in.dict(exclude_unset=True).items():
        setattr(post, k, v)
    db.commit(); db.refresh(post)
    return post

def delete_post(db: Session, post: models.Post) -> None:
    db.delete(post); db.commit()
