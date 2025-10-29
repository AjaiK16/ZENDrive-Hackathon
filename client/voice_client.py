import requests
import http.server
import socketserver
import threading
import webbrowser
import json
import os
import time
import queue
from urllib.parse import urlparse, parse_qs

# Try to import voice packages, fallback if not available
try:
    import pyttsx3
    TTS_AVAILABLE = True
    print("✅ Text-to-Speech loaded successfully!")
except ImportError as e:
    TTS_AVAILABLE = False
    print(f"⚠️ Voice packages not available: {e}")

class VoiceCommandHandler(http.server.BaseHTTPRequestHandler):
    """HTTP handler for receiving voice commands from browser"""
    
    def __init__(self, *args, voice_client=None, **kwargs):
        self.voice_client = voice_client
        super().__init__(*args, **kwargs)
    
    def do_POST(self):
        """Handle POST requests from browser with voice commands"""
        print("🌐 HTTP POST REQUEST RECEIVED")
        try:
            if self.path == '/voice-command':
                print("🌐 Processing /voice-command endpoint")
                
                # Read the command from browser
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                command_data = json.loads(post_data.decode('utf-8'))
                
                command = command_data.get('command', '').lower().strip()
                print(f"🎤 VOICE COMMAND RECEIVED: '{command}'")
                
                # Process the command INSTANTLY
                if command and command != 'wake':
                    print(f"🔄 About to call process_voice_command with: '{command}'")
                    result = self.voice_client.process_voice_command(command)
                    print(f"✅ process_voice_command returned: {result}")
                    
                    # Send response back to browser
                    response = {
                        'status': 'success',
                        'command': command,
                        'result': result
                    }
                else:
                    response = {
                        'status': 'activated',
                        'message': 'ZenDrive activated - listening for commands'
                    }
                
                # Send JSON response
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'POST')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return
                
        except Exception as e:
            print(f"❌ Error processing voice command: {e}")
            import traceback
            traceback.print_exc()
        
        # Default response
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(b'OK')
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress server log messages"""
        pass

def create_voice_handler(voice_client):
    """Create handler class with voice client reference"""
    print(f"🔧 Creating handler with voice_client: {voice_client}")
    def handler(*args, **kwargs):
        print("🔧 Handler instance being created")
        return VoiceCommandHandler(*args, voice_client=voice_client, **kwargs)
    return handler

class ZenDriveVoiceClient:
    def __init__(self):
        """Initialize voice client for ZenDrive"""
        self.tts_enabled = TTS_AVAILABLE
        self.api_base_url = "http://localhost:8000/api"
        self.voice_server_port = 8001
        self.current_command = None
        self.server_running = False
        
        # Initialize TTS with queue-based system
        if self.tts_enabled:
            try:
                self.tts_queue = queue.Queue()
                self.tts_engine = None
                self.tts_thread = None
                self._start_tts_worker()
                print("🎤 ZenDrive Voice Client initialized!")
            except Exception as e:
                print(f"⚠️ TTS initialization failed: {e}")
                self.tts_enabled = False

    def _start_tts_worker(self):
        """Start a single TTS worker thread that processes the queue"""
        def tts_worker():
            try:
                # Initialize TTS engine in this dedicated thread
                self.tts_engine = pyttsx3.init()
                
                # Configure TTS settings for better performance and reliability
                voices = self.tts_engine.getProperty('voices')
                if voices:
                    # Try to use a female voice if available, otherwise use first voice
                    female_voice = None
                    for voice in voices:
                        if 'female' in voice.name.lower() or 'zira' in voice.name.lower() or 'hazel' in voice.name.lower():
                            female_voice = voice
                            break
                    
                    if female_voice:
                        self.tts_engine.setProperty('voice', female_voice.id)
                        print(f"🎵 Using voice: {female_voice.name}")
                    else:
                        self.tts_engine.setProperty('voice', voices[0].id)
                        print(f"🎵 Using default voice: {voices[0].name}")
                
                # Optimized TTS settings for clear, structured delivery
                self.tts_engine.setProperty('rate', 150)  # Balanced speed for clarity
                self.tts_engine.setProperty('volume', 1.0)  # Full volume
                
                print("🎵 TTS worker thread started with optimized delivery settings")
                
                while True:
                    try:
                        # Get text from queue (blocks until available)
                        text = self.tts_queue.get(timeout=30)
                        
                        if text == "STOP":
                            break
                        
                        print(f"🎵 TTS worker processing: {text[:50]}...")
                        print(f"🎵 Message length: {len(text)} characters")
                        
                        # Clear any existing speech and speak the text
                        try:
                            # Stop any current speech
                            self.tts_engine.stop()
                            
                            # Minimal delay to ensure engine is ready
                            time.sleep(0.1)
                            
                            # Speak the entire message
                            print("🎵 Speaking message...")
                            self.tts_engine.say(text)
                            
                            start_time = time.time()
                            self.tts_engine.runAndWait()  # Block until speech completes
                            actual_duration = time.time() - start_time
                            
                            print(f"✅ TTS completed successfully in {actual_duration:.1f} seconds")
                            
                            # Minimal pause to ensure audio clears
                            time.sleep(0.2)
                            
                        except Exception as speech_error:
                            print(f"❌ TTS speech error: {speech_error}")
                            # Try recovery
                            try:
                                print("🔄 Attempting TTS recovery...")
                                self.tts_engine = pyttsx3.init()
                                self.tts_engine.setProperty('rate', 150)
                                self.tts_engine.setProperty('volume', 1.0)
                                self.tts_engine.say(text)
                                self.tts_engine.runAndWait()
                                print("✅ TTS recovery successful")
                            except Exception as fallback_error:
                                print(f"❌ TTS recovery failed: {fallback_error}")
                        
                        # Mark task as done
                        self.tts_queue.task_done()
                        
                    except queue.Empty:
                        print("🎵 TTS worker waiting for next message...")
                        continue
                    except Exception as e:
                        print(f"❌ TTS worker error: {e}")
                        
            except Exception as e:
                print(f"❌ TTS worker thread error: {e}")
        
        # Start the worker thread
        self.tts_thread = threading.Thread(target=tts_worker, daemon=True)
        self.tts_thread.start()

    def speak(self, text: str, section_pause: float = 0):
        """Convert text to speech with optional section pause (max 2 seconds)"""
        print(f"🔊 Message: {text}")
        
        if self.tts_enabled and self.tts_queue:
            try:
                # Add text to queue
                self.tts_queue.put(text)
                print("🎵 Text added to TTS queue")
                
                # OPTIMIZED wait times - keep attention span
                estimated_time = len(text) / 18 + 1  # Faster estimate: 18 chars per second at 150 WPM
                actual_wait = max(1.5, min(estimated_time, 4))  # Between 1.5-4 seconds only
                
                if section_pause > 0:
                    # Cap section pause at 2 seconds maximum
                    capped_pause = min(section_pause, 2.0)
                    actual_wait += capped_pause
                    print(f"🕐 Waiting {actual_wait:.1f}s (including {capped_pause:.1f}s section pause)")
                else:
                    print(f"🕐 Waiting {actual_wait:.1f}s for TTS")
                
                time.sleep(actual_wait)
                
                # Debug queue status
                print(f"🔍 TTS Queue size: {self.tts_queue.qsize()}")
                
            except Exception as e:
                print(f"⚠️ TTS queue error: {e}")
                print("💬 (Fallback to text display)")
        else:
            print("💬 (Text-only mode)")

    def get_mail_digest(self):
        """Get comprehensive email digest with SHORT structured pauses"""
        print("🚀 ENTERING get_mail_digest() method - START")
        
        try:
            print("📡 Calling comprehensive email API...")
            print(f"🔗 DEBUG: Full API URL = {self.api_base_url}/mail-digest")
            
            response = requests.get(f"{self.api_base_url}/mail-digest", timeout=15)
            
            print(f"📊 Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"📧 Comprehensive email data received successfully")
                
                # Extract structured data
                total_count = data.get("total_unread", 0)
                priority_count = data.get("priority_count", 0)
                priority_emails = data.get("priority_emails", [])
                regular_emails = data.get("regular_emails", [])
                
                print(f"🔊 Speaking structured email digest with SHORT pauses...")
                
                try:
                    # Section 1: Overview with SHORT pause
                    overview = f"You have {total_count} unread emails"
                    if priority_count > 0:
                        overview += f". {priority_count} are high priority"
                    
                    self.speak(overview, section_pause=1.0)  # 1 second pause
                    
                    # Section 2: Priority emails with SHORT pauses
                    if priority_emails:
                        self.speak("Priority emails", section_pause=0.5)  # 0.5 second pause
                        
                        for i, email in enumerate(priority_emails):
                            sender = email.get('sender', 'Unknown sender')
                            subject = email.get('subject', 'No subject')
                            priority_text = f"{sender} says {subject}"
                            
                            # SHORT pauses between priority emails
                            pause_time = 0.8 if i < len(priority_emails) - 1 else 1.0  # 0.8-1.0 seconds
                            self.speak(priority_text, section_pause=pause_time)
                    
                    # Section 3: Other emails with SHORT pauses
                    if regular_emails:
                        self.speak("Other emails", section_pause=0.5)  # 0.5 second pause
                        
                        # Limit to first 3 regular emails for voice
                        display_emails = regular_emails[:3]
                        
                        for i, email in enumerate(display_emails):
                            sender = email.get('sender', 'Unknown sender')
                            subject = email.get('subject', 'No subject')
                            other_text = f"{sender}: {subject}"
                            
                            # SHORT pauses between emails
                            pause_time = 0.6 if i < len(display_emails) - 1 else 0.8  # 0.6-0.8 seconds
                            self.speak(other_text, section_pause=pause_time)
                        
                        # If there are more emails, mention count
                        if len(regular_emails) > 3:
                            remaining = len(regular_emails) - 3
                            self.speak(f"Plus {remaining} more emails", section_pause=0.3)  # 0.3 seconds
                    
                    print("✅ Structured email digest completed with SHORT pauses")
                    
                except Exception as speech_error:
                    print(f"❌ Speech error: {speech_error}")
                    # Fallback to single speech
                    fallback_speech = data.get("speech", "Error retrieving email summary")
                    self.speak(fallback_speech)
                
                return data
            else:
                print(f"❌ API Error: Status {response.status_code}")
                self.speak("Sorry, I couldn't retrieve your emails right now.")
                return None
                
        except Exception as e:
            print(f"❌ Exception in get_mail_digest: {e}")
            import traceback
            traceback.print_exc()
            self.speak("Sorry, there was an unexpected error with the email service.")
            return None
        finally:
            print("🏁 EXITING get_mail_digest() method - END")

    def get_priority_emails(self):
        """Get only high priority emails - quick urgent check with SHORT pauses"""
        print("🚀 ENTERING get_priority_emails() method - START")
        
        try:
            print("📡 Getting priority emails only...")
            print(f"🔗 DEBUG: Full API URL = {self.api_base_url}/mail-digest/priority")
            
            response = requests.get(f"{self.api_base_url}/mail-digest/priority", timeout=15)
            
            print(f"📊 Priority response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"⚡ Priority data received: {data}")
                
                priority_count = data.get("priority_count", 0)
                priority_emails = data.get("priority_emails", [])
                
                if priority_count == 0:
                    self.speak("You have no priority emails right now. All clear!")
                else:
                    # Speak count first with SHORT pause
                    count_text = f"You have {priority_count} priority email{'s' if priority_count != 1 else ''}"
                    self.speak(count_text, section_pause=0.7)  # 0.7 seconds
                    
                    # Speak each priority email with SHORT pauses
                    for i, email in enumerate(priority_emails):
                        sender = email.get('sender', 'Unknown sender')
                        subject = email.get('subject', 'No subject')
                        email_text = f"{sender} says {subject}"
                        
                        # SHORT pauses between emails
                        pause_time = 0.8 if i < len(priority_emails) - 1 else 0.3  # 0.8/0.3 seconds
                        self.speak(email_text, section_pause=pause_time)
                
                print("✅ Priority emails spoken with SHORT pauses")
                
                return data
            else:
                print(f"❌ Priority API Error: Status {response.status_code}")
                self.speak("Sorry, couldn't get priority emails right now.")
                return None
        except Exception as e:
            print(f"❌ Priority Error: {e}")
            self.speak("Error getting priority emails.")
            return None
        finally:
            print("🏁 EXITING get_priority_emails() method - END")

    def get_calendar_digest(self):
        """Get today's calendar summary with structured speaking and SHORT pauses"""
        print("🚀 ENTERING get_calendar_digest() method - START")
        
        try:
            print("📅 Getting your calendar...")
            print(f"🔗 DEBUG: Full API URL = {self.api_base_url}/calendar-digest")
            
            response = requests.get(f"{self.api_base_url}/calendar-digest", timeout=15)
            
            print(f"📊 Calendar response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"📅 Calendar data received: {data}")
                
                total_events = data.get("total_events", 0)
                events = data.get("events", [])
                high_priority_count = data.get("high_priority_count", 0)
                
                print(f"🔊 Speaking structured calendar digest with SHORT pauses...")
                
                try:
                    if total_events == 0:
                        self.speak("You have no meetings scheduled for today. Your calendar is free!")
                    else:
                        # Overview with SHORT pause
                        overview = f"You have {total_events} meeting{'s' if total_events != 1 else ''} today"
                        if high_priority_count > 0:
                            overview += f". {high_priority_count} high priority"
                        
                        self.speak(overview, section_pause=1.0)  # 1.0 seconds
                        
                        # High priority meetings first with SHORT pause
                        high_priority_events = [e for e in events if e.get("priority") == "high"]
                        if high_priority_events:
                            self.speak("Priority meetings", section_pause=0.5)  # 0.5 seconds
                            
                            for event in high_priority_events:
                                time_str = event.get("time", "Unknown time")
                                title = event.get("title", "Untitled meeting")
                                meeting_text = f"{title} at {time_str}"
                                self.speak(meeting_text, section_pause=0.8)  # 0.8 seconds
                        
                        # First meeting of the day with SHORT pause
                        if events:
                            first_meeting = events[0]
                            if first_meeting.get("priority") != "high":  # Don't repeat if already mentioned
                                first_text = f"Your day starts with {first_meeting.get('title', 'a meeting')} at {first_meeting.get('time', 'unknown time')}"
                                self.speak(first_text, section_pause=0.6)  # 0.6 seconds
                        
                        # End time with SHORT pause
                        if events:
                            last_meeting = events[-1]
                            end_time = last_meeting.get("time", "unknown time")
                            try:
                                duration = last_meeting.get("duration", "30 minutes")
                                self.speak(f"You'll be free after your last meeting", section_pause=0.3)  # 0.3 seconds
                            except:
                                self.speak(f"Your last meeting is at {end_time}", section_pause=0.3)  # 0.3 seconds
                    
                    print("✅ Calendar digest spoken with SHORT pauses")
                    
                except Exception as speech_error:
                    print(f"❌ Calendar speech error: {speech_error}")
                    # Fallback to original speech
                    fallback_speech = data.get("speech", "Error retrieving calendar")
                    self.speak(fallback_speech)
                
                return data
            else:
                print(f"❌ Calendar API Error: Status {response.status_code}")
                self.speak("Sorry, I couldn't retrieve your calendar right now.")
                return None
                
        except Exception as e:
            print(f"❌ Calendar Error: {e}")
            self.speak("Sorry, there was an error getting your calendar.")
            return None
        finally:
            print("🏁 EXITING get_calendar_digest() method - END")

    def test_tts_functionality(self):
        """Test TTS with structured sections and SHORT pauses"""
        print("🧪 Testing TTS functionality with SHORT pauses...")
        
        # Test 1: Short message
        print("🧪 Test 1: Short message")
        self.speak("Testing short TTS message", section_pause=0.6)  # 0.6 seconds
        
        # Test 2: Medium message with sections
        print("🧪 Test 2: Structured medium message")
        self.speak("Testing structured TTS delivery", section_pause=0.5)  # 0.5 seconds
        self.speak("This message has multiple sections", section_pause=0.5)  # 0.5 seconds
        self.speak("Each section has SHORT pauses", section_pause=0.6)  # 0.6 seconds
        
        # Test 3: Email-like structured message
        print("🧪 Test 3: Email digest simulation with SHORT pauses")
        self.speak("You have 3 test emails", section_pause=0.7)  # 0.7 seconds
        self.speak("Priority emails", section_pause=0.5)  # 0.5 seconds
        self.speak("Test sender says Important test message", section_pause=0.8)  # 0.8 seconds
        self.speak("Other emails", section_pause=0.5)  # 0.5 seconds
        self.speak("Another sender: Regular test message", section_pause=0.3)  # 0.3 seconds
        
        print("🧪 Structured TTS test completed with SHORT pauses")

    def process_voice_command(self, command):
        """Process voice command and execute action"""
        command = command.lower().strip()
        print(f"🔍 Processing VOICE command: '{command}'")
        
        if any(word in command for word in ["stop", "quit", "exit", "goodbye"]):
            self.speak("Safe driving! ZenDrive signing off.")
            return "stop"
            
        elif any(word in command for word in ["priority", "urgent", "important"]):
            self.speak("Getting your priority emails now.")
            self.get_priority_emails()
            return "continue"
            
        elif any(word in command for word in ["email", "mail", "message", "get", "digest"]):
            self.speak("Getting your complete email digest now.")
            self.get_mail_digest()
            return "continue"
            
        elif any(word in command for word in ["calendar", "schedule", "meetings", "today"]):
            self.speak("Getting your calendar for today.")
            self.get_calendar_digest()
            return "continue"
            
        else:
            self.speak("I didn't understand. Try saying emails, priority, calendar, or stop.")
            return "continue"

    def create_voice_interface(self):
        """Create HTML interface with enhanced voice recognition"""
        html_content = '''<!DOCTYPE html>
<html>
<head>
    <title>ZenDrive Voice Assistant</title>
    <meta charset="UTF-8">
    <style>
        body { 
            font-family: Arial, sans-serif; 
            text-align: center; 
            padding: 30px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            margin: 0;
        }
        .container { max-width: 600px; margin: 0 auto; }
        h1 { font-size: 2.5em; margin-bottom: 30px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
        
        button { 
            padding: 20px 40px; 
            font-size: 18px; 
            margin: 15px; 
            cursor: pointer; 
            border: none;
            border-radius: 12px;
            background: #4CAF50;
            color: white;
            transition: all 0.3s;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            font-weight: bold;
        }
        button:hover { 
            background: #45a049; 
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.3);
        }
        
        #status { 
            font-size: 24px; 
            margin: 40px 0; 
            padding: 25px;
            background: rgba(255,255,255,0.15);
            border-radius: 15px;
            min-height: 60px;
            display: flex;
            align-items: center;
            justify-content: center;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
        }
        
        .listening { 
            background: #ff4444 !important; 
            animation: pulse 1.5s infinite;
            box-shadow: 0 0 20px rgba(255,68,68,0.5);
        }
        .ready { background: #4CAF50 !important; }
        .activated { background: rgba(76,175,80,0.3) !important; border: 2px solid #4CAF50 !important; }
        .processing { background: rgba(33,150,243,0.3) !important; border: 2px solid #2196F3 !important; }
        
        @keyframes pulse { 
            0% { opacity: 1; transform: scale(1); } 
            50% { opacity: 0.8; transform: scale(1.05); } 
            100% { opacity: 1; transform: scale(1); } 
        }
        
        .mic-icon {
            font-size: 4em;
            margin: 20px 0;
            opacity: 0.8;
        }
        
        .start-btn {
            background: #FF9800;
            font-size: 24px;
            padding: 25px 50px;
            box-shadow: 0 6px 15px rgba(255,152,0,0.3);
        }
        .start-btn:hover { 
            background: #e68900; 
            box-shadow: 0 8px 20px rgba(255,152,0,0.4);
        }
        
        .command-btn {
            background: #2196F3;
            font-size: 20px;
            padding: 20px 30px;
            margin: 10px;
        }
        .command-btn:hover { background: #0b7dda; }
        
        .commands-section {
            margin: 30px 0;
            display: none;
        }
        
        .info {
            margin-top: 40px;
            font-size: 16px;
            opacity: 0.9;
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 10px;
            backdrop-filter: blur(5px);
        }
        
        .confidence-bar {
            width: 300px;
            height: 6px;
            background: rgba(255,255,255,0.3);
            border-radius: 3px;
            margin: 15px auto;
            overflow: hidden;
        }
        
        .confidence-fill {
            height: 100%;
            background: #4CAF50;
            width: 0%;
            transition: width 0.3s ease;
        }
        
        .debug-info {
            margin-top: 20px;
            font-size: 14px;
            background: rgba(0,0,0,0.3);
            padding: 15px;
            border-radius: 8px;
            text-align: left;
            max-height: 200px;
            overflow-y: auto;
        }

        .commands-info {
            background: rgba(255,255,255,0.1);
            padding: 15px;
            border-radius: 10px;
            margin: 20px 0;
            font-size: 14px;
        }

        .command-type {
            margin: 10px 0;
            padding: 10px;
            background: rgba(255,255,255,0.05);
            border-radius: 5px;
            border-left: 4px solid #4CAF50;
        }
        
        .timing-info {
            background: rgba(255,193,7,0.1);
            border: 1px solid rgba(255,193,7,0.3);
            padding: 15px;
            border-radius: 10px;
            margin: 20px 0;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚗 ZenDrive Voice Assistant</h1>
        
        <div class="mic-icon" id="micIcon">🎤</div>
        
        <div id="status">Ready to listen for voice commands</div>
        
        <div class="confidence-bar">
            <div class="confidence-fill" id="confidenceBar"></div>
        </div>
        
        <button id="startBtn" class="start-btn" onclick="initializeVoice()">
            🎤 Start Voice Assistant
        </button>
        
        <div class="commands-section" id="commandsSection">
            <button class="command-btn" onclick="sendCommand('get emails')">📧 Full Digest</button>
            <button class="command-btn" onclick="sendCommand('priority')">⚡ Priority Only</button>
            <button class="command-btn" onclick="sendCommand('calendar')">📅 Calendar</button>
            <button class="command-btn" onclick="sendCommand('stop')">⏹️ Stop</button>
        </div>
        
        <div class="info">
            <h3>🗣️ Voice Commands:</h3>
            <p><strong>Wake Word:</strong> Say "ZenDrive" first</p>
            
            <div class="commands-info">
                <div class="command-type">
                    <strong>📧 "Get Emails" / "Email Digest"</strong><br>
                    <small>Structured delivery: Overview → Priority emails → Other emails<br>
                    Perfect for: Complete information with clear sections and SHORT pauses</small>
                </div>
                
                <div class="command-type">
                    <strong>⚡ "Priority" / "Urgent"</strong><br>
                    <small>Quick priority check with SHORT pauses between items<br>
                    Perfect for: Fast urgent updates while driving safely</small>
                </div>
                
                <div class="command-type">
                    <strong>📅 "Calendar" / "Schedule"</strong><br>
                    <small>Structured: Overview → Priority meetings → Schedule flow<br>
                    Perfect for: Clear day planning with digestible sections</small>
                </div>
                
                <div class="command-type">
                    <strong>⏹️ "Stop" / "Quit"</strong><br>
                    <small>Deactivate ZenDrive voice assistant</small>
                </div>
            </div>
            
            <div class="timing-info">
                <h4>⚡ Optimized Timing:</h4>
                <p><strong>TTS Speed:</strong> 150 WPM (balanced clarity/speed)</p>
                <p><strong>Section Pauses:</strong> 0.3-1.0 seconds (keeps attention)</p>
                <p><strong>Wait Times:</strong> 1.5-4 seconds max (no long delays)</p>
                <p><strong>Result:</strong> Fast, structured delivery without attention loss!</p>
            </div>
            
            <p><strong>✨ Fixed: Structured Speech with SHORT Natural Pauses!</strong></p>
            <p>Each section is delivered clearly with optimal breaks for better comprehension while keeping your attention.</p>
        </div>
        
        <div class="debug-info" id="debugInfo">
            <strong>Debug Info:</strong><br>
            Voice Client Port: 8001<br>
            FastAPI Server: localhost:8000<br>
            TTS Timing: OPTIMIZED (SHORT pauses)<br>
            Status: Initializing...
        </div>
    </div>
    
    <script>
    let recognition = null;
    let isListening = false;
    let isActivated = false;
    let continuousMode = false;
    
    function updateDebugInfo(message) {
        const debugDiv = document.getElementById('debugInfo');
        const timestamp = new Date().toLocaleTimeString();
        debugDiv.innerHTML += `<br>${timestamp}: ${message}`;
        debugDiv.scrollTop = debugDiv.scrollHeight;
    }
    
    function initializeVoice() {
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            document.getElementById('status').innerHTML = '❌ Voice recognition not supported. Please use Chrome or Edge browser.';
            updateDebugInfo('❌ Speech Recognition API not available');
            return;
        }
        
        document.getElementById('status').innerHTML = '🎤 Initializing voice recognition...';
        updateDebugInfo('🎤 Initializing Speech Recognition API');
        
        try {
            recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = 'en-US';
            recognition.maxAlternatives = 1;
            
            updateDebugInfo('✅ Speech Recognition configured');
            setupEventHandlers();
            
            document.getElementById('startBtn').style.display = 'none';
            document.getElementById('commandsSection').style.display = 'block';
            document.getElementById('status').innerHTML = '✅ Voice assistant ready! Say "ZenDrive" to activate.';
            document.getElementById('status').className = 'ready';
            
            updateDebugInfo('✅ Voice assistant initialized, starting listener');
            startListening();
            
        } catch (error) {
            console.error('Voice initialization error:', error);
            updateDebugInfo('❌ Initialization error: ' + error.message);
            document.getElementById('status').innerHTML = '❌ Failed to initialize voice recognition. Please refresh and try again.';
        }
    }
    
    function setupEventHandlers() {
        recognition.onstart = function() {
            console.log('🎤 Voice recognition started');
            updateDebugInfo('🎤 Voice recognition started');
            isListening = true;
            document.getElementById('micIcon').innerHTML = '🔴';
            
            if (!isActivated) {
                document.getElementById('status').innerHTML = '🎤 Listening... Say "ZenDrive" now!';
            } else {
                document.getElementById('status').innerHTML = '🎤 Activated! Say your command now!';
            }
            document.getElementById('status').className = 'listening';
        };
        
        recognition.onresult = function(event) {
            const result = event.results[0];
            const command = result[0].transcript.toLowerCase().trim();
            const confidence = result[0].confidence;
            
            console.log('Recognized:', command, 'Confidence:', confidence);
            updateDebugInfo(`🗣️ Recognized: "${command}" (${Math.round(confidence*100)}% confidence)`);
            
            document.getElementById('confidenceBar').style.width = (confidence * 100) + '%';
            processVoiceCommand(command);
        };
        
        recognition.onerror = function(event) {
            console.error('Speech recognition error:', event.error);
            updateDebugInfo('❌ Speech error: ' + event.error);
            
            isListening = false;
            document.getElementById('micIcon').innerHTML = '🎤';
            
            let errorMessage = '';
            switch(event.error) {
                case 'network':
                    errorMessage = '🌐 Network error. Check your internet connection and try again.';
                    break;
                case 'not-allowed':
                case 'service-not-allowed':
                    errorMessage = '🎤 Microphone access denied. Please allow microphone access and refresh the page.';
                    break;
                case 'no-speech':
                    errorMessage = '🤫 No speech detected. Please try speaking again.';
                    setTimeout(() => {
                        if (!isListening) {
                            startListening();
                        }
                    }, 2000);
                    break;
                case 'audio-capture':
                    errorMessage = '🎤 No microphone found. Please check your microphone connection.';
                    break;
                default:
                    errorMessage = '❌ Voice recognition error: ' + event.error + '. Please try again.';
                    break;
            }
            
            document.getElementById('status').innerHTML = errorMessage;
            document.getElementById('status').className = 'ready';
        };
        
        recognition.onend = function() {
            console.log('🎤 Voice recognition ended');
            updateDebugInfo('🎤 Voice recognition session ended');
            isListening = false;
            document.getElementById('micIcon').innerHTML = '🎤';
            
            if (continuousMode && isActivated) {
                setTimeout(() => {
                    startListening();
                }, 1000);
            } else if (!isActivated) {
                setTimeout(() => {
                    startListening();
                }, 1500);
            }
        };
    }
    
    function processVoiceCommand(command) {
        console.log('Processing command:', command);
        updateDebugInfo(`🔍 Processing command: "${command}"`);
        
        if (!isActivated && (command.includes('zendrive') || command.includes('zen drive'))) {
            isActivated = true;
            continuousMode = true;
            
            document.getElementById('status').innerHTML = '✅ ZenDrive activated! Now say your command.';
            document.getElementById('status').className = 'activated';
            document.getElementById('micIcon').innerHTML = '✅';
            
            updateDebugInfo('✅ Wake word detected - ZenDrive activated');
            sendCommand('wake');
            
            setTimeout(() => {
                if (!isListening) {
                    startListening();
                }
            }, 2000);
            
        } else if (isActivated) {
            document.getElementById('status').innerHTML = '🔄 Processing: "' + command + '"';
            document.getElementById('status').className = 'processing';
            document.getElementById('micIcon').innerHTML = '🔄';
            
            updateDebugInfo(`📡 Sending command to Python: "${command}"`);
            sendCommand(command);
            
            if (command.includes('stop') || command.includes('quit')) {
                isActivated = false;
                continuousMode = false;
                updateDebugInfo('⏹️ Stop command received - deactivating');
                setTimeout(() => {
                    document.getElementById('status').innerHTML = '✅ ZenDrive stopped. Say "ZenDrive" to reactivate.';
                    document.getElementById('status').className = 'ready';
                    document.getElementById('micIcon').innerHTML = '🎤';
                }, 3000);
            } else {
                setTimeout(() => {
                    if (isActivated) {
                        document.getElementById('status').innerHTML = '✅ Ready for next command!';
                        document.getElementById('status').className = 'activated';
                        document.getElementById('micIcon').innerHTML = '🎤';
                    }
                }, 3000);
            }
            
        } else {
            document.getElementById('status').innerHTML = 'Say "ZenDrive" first to activate! (Heard: "' + command + '")';
            document.getElementById('status').className = 'ready';
            document.getElementById('micIcon').innerHTML = '⚠️';
            
            updateDebugInfo(`⚠️ Command without wake word: "${command}"`);
            
            setTimeout(() => {
                document.getElementById('status').innerHTML = '🎤 Say "ZenDrive" to activate...';
                document.getElementById('micIcon').innerHTML = '🎤';
            }, 3000);
        }
    }
    
    function startListening() {
        if (!isListening && recognition) {
            try {
                updateDebugInfo('🎧 Starting voice recognition listener');
                recognition.start();
            } catch (error) {
                console.error('Error starting recognition:', error);
                updateDebugInfo('❌ Error starting listener: ' + error.message);
                document.getElementById('status').innerHTML = '❌ Error starting voice recognition. Please try refreshing the page.';
            }
        }
    }
    
    function sendCommand(command) {
        console.log('📡 Sending command to Python:', command);
        updateDebugInfo(`📡 HTTP POST to localhost:8001/voice-command`);
        
        fetch('http://localhost:8001/voice-command', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({command: command})
        })
        .then(response => {
            updateDebugInfo(`📨 Response status: ${response.status}`);
            return response.json();
        })
        .then(data => {
            console.log('✅ Command processed:', data);
            updateDebugInfo(`✅ Command processed successfully`);
        })
        .catch(error => {
            console.error('❌ Command error:', error);
            updateDebugInfo(`❌ Connection error: ${error.message}`);
            document.getElementById('status').innerHTML = '❌ Connection error. Is the Python server running on port 8001?';
        });
    }
    
    window.addEventListener('load', function() {
        updateDebugInfo('🌐 Page loaded, requesting microphone permission');
        
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            navigator.mediaDevices.getUserMedia({ audio: true })
                .then(function(stream) {
                    console.log('✅ Microphone permission granted');
                    updateDebugInfo('✅ Microphone permission granted');
                    stream.getTracks().forEach(track => track.stop());
                })
                .catch(function(error) {
                    console.log('⚠️ Microphone permission denied:', error);
                    updateDebugInfo('⚠️ Microphone permission denied: ' + error.message);
                });
        }
    });
    </script>
</body>
</html>'''
        
        # Save HTML file
        with open('zendrive_voice.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return 'zendrive_voice.html'

    def start_voice_server(self):
        """Start HTTP server to receive voice commands from browser"""
        print("🔧 Creating voice command handler...")
        handler = create_voice_handler(self)
        print(f"✅ Handler created with voice_client: {self}")
        
        try:
            with socketserver.TCPServer(("", self.voice_server_port), handler) as httpd:
                print(f"🌐 Voice command server started on port {self.voice_server_port}")
                print("🎯 Server ready to receive HTTP POST requests...")
                self.server_running = True
                httpd.serve_forever()
        except Exception as e:
            print(f"❌ Error starting voice server: {e}")
            import traceback
            traceback.print_exc()
            self.server_running = False

    def start_web_voice_mode(self):
        """Start voice-first web interface"""
        print("🌐 Starting ZenDrive Voice Interface...")
        
        # Check if FastAPI server is reachable
        try:
            test_response = requests.get(f"{self.api_base_url}/mail-digest", timeout=10)
            print(f"✅ FastAPI server test: Status {test_response.status_code}")
        except Exception as e:
            print(f"⚠️ WARNING: Cannot reach FastAPI server at {self.api_base_url}")
            print(f"⚠️ Error: {e}")
            print("⚠️ Make sure to run: python -m uvicorn backend.main:app --reload --port 8000")
        
        # Start voice command server in background
        server_thread = threading.Thread(target=self.start_voice_server, daemon=True)
        server_thread.start()
        
        # Wait for server to start
        time.sleep(2)
        
        if not self.server_running:
            print("❌ Failed to start voice server")
            return
        
        # Create HTML interface
        html_file = self.create_voice_interface()
        
        print("✅ Voice interface created!")
        print("🌐 Opening browser...")
        
        # Open browser
        webbrowser.open(html_file)
        
        self.speak("ZenDrive voice interface is ready with optimized SHORT pause delivery.")
        
        print("\n" + "="*80)
        print("🎤 ZENDRIVE VOICE INTERFACE - COMPLETELY FIXED TTS VERSION")
        print("🌐 Browser opened with voice recognition")
        print("")
        print("📋 IMPORTANT: Make sure FastAPI server is running:")
        print("   python -m uvicorn backend.main:app --reload --port 8000")
        print("")
        print("⚡ TTS OPTIMIZATION FIXES:")
        print("✅ Speech Rate: 150 WPM (balanced speed/clarity)")
        print("✅ Section Pauses: 0.3-1.0 seconds (SHORT - keeps attention)")
        print("✅ Wait Times: 1.5-4 seconds max (no long delays)")
        print("✅ Estimation: 18 chars/second (faster processing)")
        print("✅ Hard Cap: 2 second maximum pause anywhere")
        print("")
        print("🎯 STRUCTURED SPEECH FEATURES:")
        print("✨ Email Digest: Overview → Priority Emails → Other Emails")
        print("✨ Natural SHORT pauses between sections and items")
        print("✨ Clear section headers ('Priority emails', 'Other emails')")
        print("✨ No attention span loss - fast, clear delivery")
        print("")
        print("📧 Available commands:")
        print("• 📧 'get emails' - FAST structured comprehensive digest")
        print("• ⚡ 'priority' - FAST structured priority-only check")
        print("• 📅 'calendar' - FAST structured calendar overview")
        print("• ⏹️ 'stop' - Deactivate ZenDrive")
        print("="*80)
        
        try:
            # Keep the main thread alive
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 ZenDrive shutting down...")
        
        print("🌐 Voice interface ended.")

    def keyboard_simulation_mode(self):
        """Keyboard simulation for testing optimized SHORT pause speech"""
        self.speak("ZenDrive keyboard simulation mode with optimized SHORT pauses activated.")
        
        print("\n" + "="*70)
        print("⌨️ KEYBOARD SIMULATION - COMPLETELY FIXED TTS VERSION")
        print("Available commands:")
        print("• 'emails' / 'digest' - Get FAST structured email digest") 
        print("• 'priority' / 'urgent' - Get FAST structured priority emails")
        print("• 'calendar' - Get FAST structured calendar")
        print("• 'test' - Test OPTIMIZED TTS functionality")
        print("• 'stop' - Exit")
        print("")
        print("⚡ Timing: SHORT pauses (0.3-1.0s), Fast delivery, No attention loss")
        print("="*70)
        
        while True:
            command = input("\n🗣️ [Type your command]: ").lower().strip()
            
            if not command:
                continue
            
            if command == "test":
                self.test_tts_functionality()
                continue
                
            result = self.process_voice_command(command)
            if result == "stop":
                break

# Test the client
if __name__ == "__main__":
    client = ZenDriveVoiceClient()
    client.speak("Hello! ZenDrive voice assistant ready with completely fixed TTS and SHORT pauses.")
    
    print("\n🧪 Choose mode:")
    print("1. 📧 FAST structured email digest test")
    print("2. ⚡ FAST structured priority emails test")
    print("3. 📅 FAST structured calendar digest test") 
    print("4. 🧪 OPTIMIZED TTS functionality test (SHORT pauses)")
    print("5. ⌨️ Keyboard simulation mode")
    print("6. 🚗 Voice Assistant Interface")
    
    choice = input("Enter 1, 2, 3, 4, 5, or 6: ")
    
    if choice == "1":
        client.speak("Getting your FAST structured email digest")
        client.get_mail_digest()
    elif choice == "2":
        client.speak("Getting your FAST structured priority emails")
        client.get_priority_emails()
    elif choice == "3":
        client.speak("Getting your FAST structured calendar digest")
        client.get_calendar_digest()
    elif choice == "4":
        client.test_tts_functionality()
    elif choice == "5":
        client.keyboard_simulation_mode()
    elif choice == "6":
        client.start_web_voice_mode()
    else:
        client.speak("Invalid choice. Goodbye!")