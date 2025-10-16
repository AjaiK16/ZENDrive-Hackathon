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

# Utility Functions
def get_unread_emails(limit: int = 8) -> List[Dict[str, Any]]:
    """Get most recent unread emails"""
    return sorted(MOCK_EMAILS, key=lambda x: x['received'], reverse=True)[:limit]

def get_high_priority_emails() -> List[Dict[str, Any]]:
    """Get high priority emails only"""
    return [email for email in MOCK_EMAILS if email.get('importance') == 'high']

def generate_email_summary(emails: List[Dict[str, Any]]) -> str:
    """Generate AI-style summary of emails"""
    total = len(emails)
    high_priority = len([e for e in emails if e.get('importance') == 'high'])
    
    summary = f"You have {total} unread emails"
    if high_priority > 0:
        summary += f", including {high_priority} high priority"
    
    return summary + "."

def generate_voice_summary(emails: List[Dict[str, Any]]) -> str:
    """Generate voice-optimized summary for TTS"""
    high_priority = [e for e in emails if e.get('importance') == 'high']
    
    speech = f"You have {len(emails)} unread emails. "
    
    if high_priority:
        speech += f"{len(high_priority)} are high priority: "
        for email in high_priority[:2]:  # Mention top 2 high priority
            sender_name = email['from_name'].split()[0]  # First name only
            speech += f"{sender_name} says {email['subject']}. "
    
    return speech