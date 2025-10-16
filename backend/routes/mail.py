from fastapi import APIRouter

# Create a "router" - think of it as a section of service counters
router = APIRouter()

@router.get("/mail-digest")
def get_mail_digest():
    """
    This is like a service window where clients can request email summaries
    When someone makes a GET request to /mail-digest, this function runs
    """
    return {"message": "Hello! This will return email digest soon."}