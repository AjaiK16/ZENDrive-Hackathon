from fastapi import APIRouter
# Add these imports to get our mock data
from backend.utils.mock_data import get_unread_emails, get_high_priority_emails, generate_email_summary, generate_voice_summary

# Create router for mail-related endpoints
router = APIRouter()

@router.get("/mail-digest")
async def get_mail_digest():
    """Get comprehensive email digest - quick overview + all emails"""
    
    # Get all unread emails
    unread_emails = get_unread_emails()
    priority_emails = get_high_priority_emails()
    
    # Create comprehensive summary for full digest
    total_count = len(unread_emails)
    priority_count = len(priority_emails)
    regular_count = total_count - priority_count
    
    # Build detailed speech summary
    speech_parts = []
    
    # 1. Quick overview
    speech_parts.append(f"You have {total_count} unread emails.")
    if priority_count > 0:
        speech_parts.append(f"{priority_count} are high priority.")
    
    # 2. Priority emails first (if any)
    if priority_emails:
        speech_parts.append("Priority emails:")
        for email in priority_emails:
            speech_parts.append(f"{email['sender']} says {email['subject']}")
    
    # 3. Regular emails summary  
    regular_emails = [email for email in unread_emails if email not in priority_emails]
    if regular_emails:
        if priority_emails:  # If we had priority emails, transition
            speech_parts.append("Other emails:")
        
        # Group regular emails by type or just list first few
        if len(regular_emails) <= 3:
            # List all if 3 or fewer
            for email in regular_emails:
                speech_parts.append(f"{email['sender']}: {email['subject']}")
        else:
            # List first 2 and summarize rest
            for email in regular_emails[:2]:
                speech_parts.append(f"{email['sender']}: {email['subject']}")
            remaining = len(regular_emails) - 2
            speech_parts.append(f"Plus {remaining} more emails from various senders.")
    
    # Join all parts
    speech_summary = " ".join(speech_parts)
    
    # Create text summary
    text_summary = generate_email_summary(unread_emails, priority_emails)
    
    return {
        "total_unread": total_count,
        "priority_count": priority_count,
        "regular_count": regular_count,
        "priority_emails": priority_emails,
        "regular_emails": regular_emails,
        "all_emails": unread_emails,
        "summary": text_summary,
        "speech": speech_summary
    }

@router.get("/mail-digest/priority")
async def get_priority_mail_digest():
    """Get only high priority emails - quick urgent check"""
    
    # Get only priority emails
    priority_emails = get_high_priority_emails()
    
    if not priority_emails:
        speech_summary = "You have no priority emails right now. All clear!"
        return {
            "priority_count": 0,
            "priority_emails": [],
            "summary": "No priority emails",
            "speech": speech_summary
        }
    
    # Build concise priority summary
    count = len(priority_emails)
    speech_parts = []
    
    if count == 1:
        email = priority_emails[0]
        speech_summary = f"You have 1 priority email: {email['sender']} says {email['subject']}"
    else:
        speech_parts.append(f"You have {count} priority emails:")
        for email in priority_emails:
            speech_parts.append(f"{email['sender']} says {email['subject']}")
        speech_summary = " ".join(speech_parts)
    
    return {
        "priority_count": count,
        "priority_emails": priority_emails, 
        "summary": f"{count} priority emails",
        "speech": speech_summary
    }