from fastapi import FastAPI
# Import both mail and calendar routes
from backend.routes import mail, calendar

# Create the main FastAPI app
app = FastAPI(title="ZenDrive Mail Digest MVP")

# Connect your service routers to the main app
app.include_router(mail.router, prefix="/api", tags=["emails"])
app.include_router(calendar.router, prefix="/api", tags=["calendar"])

@app.get("/")
def welcome():
    """Welcome message - like a restaurant's front door"""
    return {"message": "Welcome to ZenDrive Mail Digest API!"}

# Add to mock_data.py
def get_calendar_events():
    """Get mock calendar events"""
    return [
        # ... calendar events data
    ]

def generate_calendar_summary(events):
    """Generate calendar speech summary"""
    # ... summary logic