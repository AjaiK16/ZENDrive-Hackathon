from fastapi import APIRouter
from datetime import datetime

# Create calendar router
router = APIRouter()

@router.get("/calendar-digest")
async def get_calendar_digest():
    """Get today's calendar summary for voice output"""
    
    # Mock calendar data - replace with real calendar API
    calendar_events = [
        {
            "time": "9:00 AM",
            "title": "Team Standup",
            "duration": "30 minutes",
            "location": "Conference Room A",
            "priority": "medium"
        },
        {
            "time": "11:00 AM", 
            "title": "Client Demo - ZenDrive Presentation",
            "duration": "1 hour",
            "location": "Zoom Meeting",
            "priority": "high"
        },
        {
            "time": "2:00 PM",
            "title": "Code Review Session", 
            "duration": "45 minutes",
            "location": "Dev Room",
            "priority": "medium"
        },
        {
            "time": "4:00 PM",
            "title": "Project Planning",
            "duration": "1 hour",
            "location": "Conference Room B", 
            "priority": "low"
        }
    ]
    
    # Create voice-optimized summary
    total_meetings = len(calendar_events)
    high_priority = [e for e in calendar_events if e["priority"] == "high"]
    
    # Build speech summary
    speech_summary = f"Good morning! You have {total_meetings} meetings today. "
    
    if high_priority:
        speech_summary += f"Your priority meeting is at {high_priority[0]['time']}: {high_priority[0]['title']}. "
    
    speech_summary += f"Your day starts with {calendar_events[0]['title']} at {calendar_events[0]['time']}. "
    speech_summary += f"You'll be free after {calendar_events[-1]['time']}."
    
    return {
        "total_events": total_meetings,
        "events": calendar_events,
        "high_priority_count": len(high_priority),
        "summary": f"You have {total_meetings} meetings today, including {len(high_priority)} high priority.",
        "speech": speech_summary
    }