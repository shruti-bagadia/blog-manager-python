from datetime import date
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import UUID4

from ..database import get_db
from ..schema.post import PostCreate, PostRead, PostUpdate
from ..crud import (
    get_post_by_uuid,
    get_posts,
    create_post as crud_create_post,
    update_post as crud_update_post,
    delete_post as crud_delete_post,
)
from ..auth import get_current_user
from .websocket import manager

router = APIRouter(prefix="/posts", tags=["posts"])
logger = logging.getLogger("app")


@router.post("/", response_model=PostRead)
def create_post(
    post_in: PostCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    logger.info(f"[CREATE] user={user['author_uuid']}")
    if str(post_in.author_uuid) != str(user["author_uuid"]):
        logger.warning("[CREATE] forbidden author_uuid mismatch")
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not allowed")
    try:
        post = crud_create_post(db, post_in)
        logger.info(f"[CREATED] post={post.post_uuid}")
        background_tasks.add_task(
        manager.broadcast,
        {
            "event": "new_post",
            "post": PostRead.from_orm(post).dict()
        }
    )
        return post
    except Exception as e:
        logger.error(f"[CREATE] error: {e}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal error")


@router.get("/", response_model=List[PostRead])
def list_posts(
    skip: int = 0,
    limit: int = Query(10, le=100),
    author_uuid: Optional[UUID4] = None,
    date_from: Optional[date] = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    logger.info(f"[LIST] user={user['author_uuid']} skip={skip} limit={limit}")
    try:
        return get_posts(
            db,
            skip=skip,
            limit=limit,
            author_uuid=author_uuid,
            date_from=date_from,
        )
    except Exception as e:
        logger.error(f"[LIST] error: {e}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal error")


@router.get("/{post_uuid}", response_model=PostRead)
def read_post(
    post_uuid: UUID4,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    logger.info(f"[READ] post={post_uuid} user={user['author_uuid']}")
    post = get_post_by_uuid(db, str(post_uuid))
    if not post:
        logger.warning(f"[READ] not found post={post_uuid}")
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Post not found")
    return post


@router.put("/{post_uuid}", response_model=PostRead)
def update_post(
    post_uuid: UUID4,
    updates: PostUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    logger.info(f"[UPDATE] post={post_uuid} user={user['author_uuid']}")
    post = get_post_by_uuid(db, str(post_uuid))
    if not post or str(post.author_uuid) != user["author_uuid"]:
        logger.warning(f"[UPDATE] forbidden or missing post={post_uuid}")
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not found or forbidden")
    try:
        updated = crud_update_post(db, post, updates)
        logger.info(f"[UPDATED] post={post_uuid}")
        return updated
    except Exception as e:
        logger.error(f"[UPDATE] error: {e}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal error")


@router.delete("/{post_uuid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_uuid: UUID4,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    logger.info(f"[DELETE] post={post_uuid} user={user['author_uuid']}")
    post = get_post_by_uuid(db, str(post_uuid))
    if not post or str(post.author_uuid) != user["author_uuid"]:
        logger.warning(f"[DELETE] forbidden or missing post={post_uuid}")
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not found or forbidden")
    try:
        crud_delete_post(db, post)
        logger.info(f"[DELETED] post={post_uuid}")
    except Exception as e:
        logger.error(f"[DELETE] error: {e}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal error")
