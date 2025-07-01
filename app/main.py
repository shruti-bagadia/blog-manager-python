import logging

from fastapi import FastAPI

from app.models import Author, Post
from .database import Base, SessionLocal, engine
from .api.posts import router as post_router
from .auth import router as auth_router
from .api.websocket import router as ws_router
from .constants import SHREYA_UUID, ADITI_UUID

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Blog API",
    version="0.1.0",
    description="A simple FastAPI blog with UUIDs, auth, CRUD & filtering"
)

@app.on_event("startup")
def populate_sample_data():
    db = SessionLocal()
    try:
        if not db.query(Author).first():
            # create two authors with fixed UUIDs
            s = Author(author_uuid=SHREYA_UUID, name="Shreya", email="shreya@example.com")
            a = Author(author_uuid=ADITI_UUID,  name="Aditi",  email="aditi@example.com")
            db.add_all([s, a]); db.commit()
            db.refresh(s); db.refresh(a)

            # 5 posts for Shreya
            posts = [
                Post(
                    title=f"Shreya post #{i}",
                    content="Sample content",
                    author_uuid=SHREYA_UUID
                ) for i in range(1, 6)
            ]
            # 8 posts for Aditi
            posts += [
                Post(
                    title=f"Aditi post #{j}",
                    content="Sample content",
                    author_uuid=ADITI_UUID
                ) for j in range(1, 9)
            ]
            db.add_all(posts); db.commit()
            logger.info("Entered sample authors & posts")
    finally:
        db.close()
        
# app.include_router(authors.router)
app.include_router(post_router)
app.include_router(auth_router)
app.include_router(ws_router)