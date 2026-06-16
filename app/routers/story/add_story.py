from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user_model import User
from app.models.story_model import Story
from app.schemas import StoryCreate

router = APIRouter(
    prefix="/stories",
    tags=["Stories"]
)


@router.post("/")
def create_story(
    data: StoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """A logged-in patient submits a story/testimonial."""
    story = Story(content=data.content, user_id=current_user.user_id)
    db.add(story)
    db.commit()
    db.refresh(story)

    return {
        "story_id": story.story_id,
        "name": current_user.name,
        "content": story.content,
        "created_at": story.created_at,
    }


@router.get("/")
def get_all_stories(db: Session = Depends(get_db)):
    """Public list of all patient stories (newest first) for the Testimonials page."""
    stories = db.query(Story).options(
        joinedload(Story.user)
    ).order_by(Story.created_at.desc()).all()

    return [
        {
            "story_id": s.story_id,
            "name": s.user.name if s.user else "Anonymous",
            "content": s.content,
            "created_at": s.created_at,
        }
        for s in stories
    ]
