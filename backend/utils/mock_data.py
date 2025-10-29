from datetime import datetime, timedelta
from typing import List, Dict, Any

# Realistic Mock Email Data for Mail Digest
MOCK_EMAILS: List[Dict[str, Any]] = [
    {
        "id": "email_001",
        "from_email": "sarah.chen@acmecorp.com",
        "from_name": "Sarah Chen",
        "subject": "URGENT: Client Meeting Moved to 3 PM Today",
        "received": (datetime.now() - timedelta(minutes=15)).isoformat(),
        "importance": "high",
        "preview": "Hi team, the client just requested to move our product demo from 4 PM to 3 PM today. Please confirm your availability. We need to be ready with the Q4 roadmap presentation.",
        "has_attachments": True
    },
    {
        "id": "email_002",
        "from_email": "ceo@company.com",
        "from_name": "Jennifer Martinez",
        "subject": "Q4 Strategic Priorities - Leadership Team",
        "received": (datetime.now() - timedelta(hours=1, minutes=30)).isoformat(),
        "importance": "high",
        "preview": "Leadership team, please review the attached Q4 strategic priorities document. Key focus areas include customer retention (target: 95%), new market expansion, and platform scalability improvements.",
        "has_attachments": True
    },
    {
        "id": "email_003",
        "from_email": "alice.johnson@company.com",  
        "from_name": "Alice Johnson",
        "subject": "Sprint Planning Tomorrow - Agenda Inside",
        "received": (datetime.now() - timedelta(hours=2, minutes=45)).isoformat(),
        "importance": "normal",
        "preview": "Hi everyone! Tomorrow's sprint planning agenda: 1) Review last sprint velocity 2) Prioritize Q4 features 3) Capacity planning. Please review user stories in backlog beforehand.",
        "has_attachments": False
    },
    {
        "id": "email_004",
        "from_email": "finance@company.com",        
        "from_name": "Finance Team",
        "subject": "Action Required: October Expense Reports Due Friday",
        "received": (datetime.now() - timedelta(hours=3, minutes=20)).isoformat(),
        "importance": "normal",
        "preview": "Reminder: October expense reports must be submitted by end of day Friday. Late submissions will be processed in November. Submit through the finance portal using your employee ID.",       
        "has_attachments": False
    },
    {
        "id": "email_005",
        "from_email": "devops@company.com",
        "from_name": "DevOps Team",
        "subject": "Platform Performance: 25% Improvement This Week!",
        "received": (datetime.now() - timedelta(hours=4, minutes=10)).isoformat(),
        "importance": "normal",
        "preview": "Great news! Our recent optimizations delivered significant improvements: API response time down 25%, database query performance up 30%, and 99.9% uptime maintained.",
        "has_attachments": True
    }
]

# Calendar Mock Data
MOCK_CALENDAR_EVENTS = [
    {
        "id": "meeting_001",
        "title": "Team Standup",
        "start_time": "09:00",
        "end_time": "09:30",
        "location": "Conference Room A",
        "attendees": ["team@company.com"],
        "priority": "medium",
        "type": "meeting"
    },
    {
        "id": "meeting_002", 
        "title": "Client Demo - ZenDrive Presentation",
        "start_time": "11:00",
        "end_time": "12:00",
        "location": "Zoom Meeting Room",
        "attendees": ["client@acmecorp.com", "sarah.chen@company.com"],
        "priority": "high",
        "type": "presentation"
    },
    {
        "id": "meeting_003",
        "title": "Code Review Session",
        "start_time": "14:00", 
        "end_time": "14:45",
        "location": "Dev Room",
        "attendees": ["dev-team@company.com"],
        "priority": "medium",
        "type": "review"
    },
    {
        "id": "meeting_004",
        "title": "Project Planning - Q4 Roadmap",
        "start_time": "16:00",
        "end_time": "17:00", 
        "location": "Conference Room B",
        "attendees": ["leadership@company.com"],
        "priority": "high",
        "type": "planning"
    }
]

# Utility Functions for Emails
def get_unread_emails(limit: int = 8) -> List[Dict[str, Any]]:
    """Get all unread emails (mock data)"""
    return [
        {
            "id": 1,
            "sender": "Sarah Johnson",
            "subject": "URGENT: Client Meeting Moved to 3 PM Today",
            "snippet": "Hi team, our client meeting has been moved from 2 PM to 3 PM today. Please update your calendars accordingly.",
            "timestamp": "2024-10-29T09:15:00Z",    
            "priority": "high",
            "unread": True
        },
        {
            "id": 2,
            "sender": "Jennifer Chen",
            "subject": "Q4 Strategic Priorities - Leadership Team",
            "snippet": "Please review the attached Q4 priorities document before our leadership meeting tomorrow at 10 AM.",
            "timestamp": "2024-10-29T08:30:00Z",    
            "priority": "high",
            "unread": True
        },
        {
            "id": 3,
            "sender": "Marketing Team",
            "subject": "Weekly Newsletter - October Edition",
            "snippet": "Check out this week's highlights including our product launch success metrics and upcoming campaigns.",
            "timestamp": "2024-10-29T07:45:00Z",    
            "priority": "low",
            "unread": True
        },
        {
            "id": 4,
            "sender": "HR Department",
            "subject": "Benefits Update - Open Enrollment",
            "snippet": "Open enrollment for health benefits starts next week. Please review your options in the HR portal.",
            "timestamp": "2024-10-28T16:20:00Z",    
            "priority": "medium",
            "unread": True
        },
        {
            "id": 5,
            "sender": "Alex Rodriguez",
            "subject": "Lunch Plans for Friday?",   
            "snippet": "Hey! Want to try that new sushi place downtown this Friday? Let me know if you're interested!",
            "timestamp": "2024-10-28T15:10:00Z",    
            "priority": "low",
            "unread": True
        }
    ]

def get_high_priority_emails() -> List[Dict[str, Any]]:
    """Get only high priority emails"""
    all_emails = get_unread_emails()
    return [email for email in all_emails if email.get("priority") == "high"]

def get_medium_priority_emails() -> List[Dict[str, Any]]:
    """Get medium priority emails"""
    all_emails = get_unread_emails()
    return [email for email in all_emails if email.get("priority") == "medium"]

def get_low_priority_emails() -> List[Dict[str, Any]]:
    """Get low priority emails"""
    all_emails = get_unread_emails()
    return [email for email in all_emails if email.get("priority") == "low"]

def generate_email_summary(unread_emails: List[Dict[str, Any]], priority_emails: List[Dict[str, Any]]) -> str:
    """Generate text summary of emails"""
    total = len(unread_emails)
    high_priority = len(priority_emails)
    
    summary = f"You have {total} unread emails"
    if high_priority > 0:
        summary += f", {high_priority} are high priority"
    summary += "."

    return summary

def generate_voice_summary(unread_emails: List[Dict[str, Any]], priority_emails: List[Dict[str, Any]]) -> str:
    """Generate voice-optimized summary with proper breaks"""
    total = len(unread_emails)
    high_priority = len(priority_emails)
    
    if total == 0:
        return "You have no unread emails. Your inbox is clear!"
    
    # Build voice summary with natural breaks
    summary_parts = []
    
    # 1. Opening summary with pause
    summary_parts.append(f"You have {total} unread email{'s' if total != 1 else ''}")
    
    if high_priority > 0:
        summary_parts.append(f"{high_priority} {'are' if high_priority != 1 else 'is'} high priority")
    
    # 2. Priority emails section with clear break
    if priority_emails:
        summary_parts.append("Priority emails")  # Clear section header
        for email in priority_emails[:2]:  # Limit to first 2 for voice
            priority_text = f"{email['sender']} says {email['subject']}"
            summary_parts.append(priority_text)
    
    # 3. Other emails section with clear break
    other_emails = [email for email in unread_emails if email.get("priority") != "high"]
    if other_emails:
        summary_parts.append("Other emails")  # Clear section header
        for email in other_emails[:3]:  # Limit to first 3 for voice
            other_text = f"{email['sender']}: {email['subject']}"
            summary_parts.append(other_text)
    
    # Join with periods for natural TTS pauses
    return ". ".join(summary_parts) + "."

# Utility Functions for Calendar  
def get_todays_events() -> List[Dict[str, Any]]:
    """Get today's calendar events"""
    return MOCK_CALENDAR_EVENTS

def get_high_priority_events() -> List[Dict[str, Any]]:
    """Get only high priority calendar events"""
    return [event for event in MOCK_CALENDAR_EVENTS if event.get("priority") == "high"]

def get_next_meeting() -> Dict[str, Any]:
    """Get the next upcoming meeting"""
    events = get_todays_events()
    if events:
        return events[0]  # Return first event as "next"
    return {}

def generate_calendar_summary(events: List[Dict[str, Any]]) -> str:
    """Generate text summary of calendar events"""
    total = len(events)
    high_priority = len([e for e in events if e.get("priority") == "high"])
    
    if total == 0:
        return "You have no meetings scheduled for today."
    
    summary = f"You have {total} meeting{'s' if total != 1 else ''} today"
    if high_priority > 0:
        summary += f", {high_priority} {'are' if high_priority != 1 else 'is'} high priority"
    summary += "."
    
    return summary

def generate_calendar_voice_summary(events: List[Dict[str, Any]]) -> str:
    """Generate voice-optimized calendar summary"""
    total = len(events)
    high_priority_events = [e for e in events if e.get("priority") == "high"]
    
    if total == 0:
        return "You have a clear schedule today. No meetings planned!"
    
    summary_parts = []
    summary_parts.append(f"You have {total} meeting{'s' if total != 1 else ''} today")
    
    # Mention high priority meetings
    if high_priority_events:
        summary_parts.append(f"Your priority meeting{'s' if len(high_priority_events) != 1 else ''} {'are' if len(high_priority_events) != 1 else 'is'}:")
        for event in high_priority_events:
            summary_parts.append(f"{event['title']} at {event['start_time']}")
    
    # Mention first meeting
    if events:
        first_meeting = events[0]
        summary_parts.append(f"Your day starts with {first_meeting['title']} at {first_meeting['start_time']}")
    
    # Mention when the day ends
    if events:
        last_meeting = events[-1]
        summary_parts.append(f"You'll be free after {last_meeting['end_time']}")
    
    return ". ".join(summary_parts) + "."

# Additional Helper Functions
def get_email_count_by_priority() -> Dict[str, int]:
    """Get email count grouped by priority"""
    all_emails = get_unread_emails()
    
    counts = {
        "high": 0,
        "medium": 0, 
        "low": 0,
        "total": len(all_emails)
    }
    
    for email in all_emails:
        priority = email.get("priority", "low")
        if priority in counts:
            counts[priority] += 1
    
    return counts

def get_meeting_count_by_priority() -> Dict[str, int]:
    """Get meeting count grouped by priority"""
    all_events = get_todays_events()
    
    counts = {
        "high": 0,
        "medium": 0,
        "low": 0, 
        "total": len(all_events)
    }
    
    for event in all_events:
        priority = event.get("priority", "medium")
        if priority in counts:
            counts[priority] += 1
            
    return counts

def get_daily_summary() -> Dict[str, Any]:
    """Get comprehensive daily summary"""
    emails = get_unread_emails()
    priority_emails = get_high_priority_emails()
    events = get_todays_events()
    priority_events = get_high_priority_events()
    
    return {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "emails": {
            "total": len(emails),
            "priority": len(priority_emails),
            "summary": generate_email_summary(emails, priority_emails)
        },
        "calendar": {
            "total": len(events),
            "priority": len(priority_events),
            "summary": generate_calendar_summary(events)
        },
        "voice_summary": f"{generate_voice_summary(emails, priority_emails)} {generate_calendar_voice_summary(events)}"
    }