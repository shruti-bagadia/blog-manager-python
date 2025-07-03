import logging
from typing import List
from fastapi import (
    APIRouter, Depends, HTTPException, Query, status, BackgroundTasks
)
from sqlalchemy.orm import Session
from pydantic import UUID4

from ..database import get_db
from ..schema.author import (
    AuthorCreate, AuthorRead, AuthorUpdate
)
from ..crud import (
    get_author_by_uuid,
    get_authors,
    create_author as crud_create_author,
    update_author as crud_update_author,
    delete_author as crud_delete_author,
)
from ..auth import get_current_user

router = APIRouter(prefix="/authors", tags=["Authors"])
logger = logging.getLogger("api.authors")


@router.post(
    "/",
    response_model=AuthorRead,
    status_code=status.HTTP_201_CREATED
)
def create_author(
    author_in: AuthorCreate,
    db: Session = Depends(get_db),
):
    logger.info("[CREATE] author")
    try:
        return crud_create_author(db, author_in)
    except Exception as e:
        logger.error(f"[CREATE] error: {e}")
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Could not create author"
        )


@router.get(
    "/",
    response_model=List[AuthorRead]
)
def list_authors(
    skip: int = 0,
    limit: int = Query(10, le=100),
    db: Session = Depends(get_db),
):
    logger.info(f"[LIST] skip={skip} limit={limit}")
    return get_authors(db, skip=skip, limit=limit)


@router.get(
    "/{author_uuid}",
    response_model=AuthorRead
)
def read_author(
    author_uuid: UUID4,
    db: Session = Depends(get_db),
):
    logger.info(f"[READ] author={author_uuid}")
    author = get_author_by_uuid(db, str(author_uuid))
    if not author:
        logger.warning(f"[READ] not found author={author_uuid}")
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            "Author not found"
        )
    return author


@router.put(
    "/{author_uuid}",
    response_model=AuthorRead
)
def update_author_endpoint(
    author_uuid: UUID4,
    update_in: AuthorUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    logger.info(f"[UPDATE] author={author_uuid} user={user['author_uuid']}")
    author = get_author_by_uuid(db, str(author_uuid))
    if not author or str(author.author_uuid) != user["author_uuid"]:
        logger.warning(f"[UPDATE] forbidden or missing author={author_uuid}")
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            "Not found or forbidden"
        )
    try:
        return crud_update_author(db, author, update_in)
    except Exception as e:
        logger.error(f"[UPDATE] error: {e}")
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Could not update author"
        )


@router.delete(
    "/{author_uuid}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_author_endpoint(
    author_uuid: UUID4,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    logger.info(f"[DELETE] author={author_uuid} user={user['author_uuid']}")
    author = get_author_by_uuid(db, str(author_uuid))
    if not author or str(author.author_uuid) != user["author_uuid"]:
        logger.warning(f"[DELETE] forbidden or missing author={author_uuid}")
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            "Not found or forbidden"
        )
    try:
        crud_delete_author(db, author)
    except Exception as e:
        logger.error(f"[DELETE] error: {e}")
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Could not delete author"
        )
