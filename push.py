#!/usr/bin/env python3
"""
Dobby Display Pusher
Push content to the Duet display from OpenClaw.
"""

import requests
import argparse
import json
import sys
import os

# Default URL - should be overridden via config or environment
DEFAULT_URL = os.environ.get("DOBBY_DISPLAY_URL", "http://100.105.30.20:5000")

def push_dashboard():
    """Reset to dashboard mode"""
    r = requests.get(f"{DEFAULT_URL}/api/dashboard")
    try:
        return r.json()
    except:
        return {"success": True, "raw": r.text}

def push_run(data: dict):
    """Show running stats"""
    payload = {
        "mode": "run",
        "title": "🏃 Latest Run",
        "content": data
    }
    r = requests.post(f"{DEFAULT_URL}/api/update", json=payload)
    return r.json()

def push_meals(data: dict):
    """Show weekly meals"""
    payload = {
        "mode": "meals",
        "title": "🍽️ This Week's Meals",
        "content": data
    }
    r = requests.post(f"{DEFAULT_URL}/api/update", json=payload)
    return r.json()

def push_routine(steps: list):
    """Show a routine (bedtime, morning, etc.)"""
    payload = {
        "mode": "routine",
        "title": "Bedtime Routine",
        "content": {"steps": steps}
    }
    r = requests.post(f"{DEFAULT_URL}/api/update", json=payload)
    return r.json()

def push_custom(title: str, text: str, speak: str = None):
    """Show custom content"""
    payload = {
        "mode": "custom",
        "title": title,
        "content": {"text": text},
        "speak": speak
    }
    r = requests.post(f"{DEFAULT_URL}/api/update", json=payload)
    try:
        return r.json()
    except:
        return {"success": True, "raw": r.text}

def push_quickglance(data: dict):
    """Show quick glance dashboard"""
    payload = {
        "mode": "quickglance",
        "title": "Quick Look",
        "content": data
    }
    r = requests.post(f"{DEFAULT_URL}/api/update", json=payload)
    try:
        return r.json()
    except:
        return {"success": True, "raw": r.text}

def push_weather(temp: str, description: str, icon: str, nudge: str, time: str = ""):
    """Show weather with nudge"""
    payload = {
        "mode": "weather",
        "title": "Weather",
        "content": {
            "temp": temp,
            "description": description,
            "icon": icon,
            "nudge": nudge,
            "time": time
        }
    }
    r = requests.post(f"{DEFAULT_URL}/api/update", json=payload)
    return r.json()

def push_celebration(name: str, age: str = "", date: str = "", icon: str = "🎂", message: str = ""):
    """Show birthday/celebration"""
    payload = {
        "mode": "celebration",
        "title": "Celebration",
        "content": {
            "name": name,
            "age": age,
            "date": date,
            "icon": icon,
            "message": message
        }
    }
    r = requests.post(f"{DEFAULT_URL}/api/update", json=payload)
    return r.json()

def push_countdown(event: str, days: int = None, hours: int = None, minutes: int = None, message: str = ""):
    """Show countdown to event"""
    content = {"event": event, "message": message}
    if days is not None: content["days"] = str(days)
    if hours is not None: content["hours"] = str(hours)
    if minutes is not None: content["minutes"] = str(minutes)
    payload = {
        "mode": "countdown",
        "title": "Countdown",
        "content": content
    }
    r = requests.post(f"{DEFAULT_URL}/api/update", json=payload)
    return r.json()

def push_verse(text: str, reference: str = "", verse_type: str = "verse", label: str = ""):
    """Show verse of the day or inspiration"""
    payload = {
        "mode": "verse",
        "title": "Verse",
        "content": {
            "type": verse_type,
            "text": text,
            "reference": reference,
            "label": label
        }
    }
    r = requests.post(f"{DEFAULT_URL}/api/update", json=payload)
    return r.json()

def push_alert(message: str, severity: str = "info", title: str = "", details: list = None, action: str = ""):
    """Show weather alert or announcement"""
    payload = {
        "mode": "alert",
        "title": title,
        "content": {
            "severity": severity,
            "message": message,
            "details": details or [],
            "action": action
        }
    }
    r = requests.post(f"{DEFAULT_URL}/api/update", json=payload)
    return r.json()

def push_message(
    message: str,
    message_type: str = "info",
    sub_message: str = "",
    auto_dismiss: int = 10,
    sticky: bool = False,
    color: str = None,
    font_size: str = "4rem",
    sub_size: str = "2rem",
    speak: str = None,
    countdown_to: str = None,
    countdown_label: str = None
):
    """
    Push a message to the display with auto-dismiss support.
    
    Args:
        message: Main message text
        message_type: info|warning|alert|celebration|sticky
        sub_message: Optional subtitle
        auto_dismiss: Seconds until auto-return to quickglance (0=stay forever)
        sticky: If True, message stays until manually cleared (overrides auto_dismiss)
        color: Custom hex color (optional)
        font_size: Main message font size
        sub_size: Sub-message font size
        speak: Text to speak aloud via TTS
        countdown_to: ISO datetime for countdown (e.g., "2025-02-15T10:00:00")
        countdown_label: Label for countdown event
    """
    payload = {
        "message": message,
        "sub_message": sub_message,
        "type": message_type,
        "auto_dismiss": auto_dismiss,
        "sticky": sticky,
        "font_size": font_size,
        "sub_size": sub_size
    }
    
    if color:
        payload["color"] = color
    if speak:
        payload["speak"] = speak
    if countdown_to:
        payload["countdown_to"] = countdown_to
        payload["countdown_label"] = countdown_label or message
    
    r = requests.post(f"{DEFAULT_URL}/api/message", json=payload)
    try:
        return r.json()
    except:
        return {"success": True, "raw": r.text}

def clear_display():
    """Clear current message and return to quickglance"""
    r = requests.post(f"{DEFAULT_URL}/api/clear-message")
    try:
        return r.json()
    except:
        return {"success": True, "raw": r.text}

def push_template(template_name: str, content: str):
    """Update a template file on the display"""
    r = requests.post(f"{DEFAULT_URL}/api/template/{template_name}", json={"content": content})
    try:
        return r.json()
    except:
        return {"success": True, "raw": r.text}

def main():
    parser = argparse.ArgumentParser(description="Push content to Dobby Display")
    parser.add_argument("--url", default=DEFAULT_URL, help="Display receiver URL")
    parser.add_argument("--mode", required=True, 
                        choices=["dashboard", "run", "meals", "routine", "custom", "quickglance", "message", "clear"])
    parser.add_argument("--data", help="JSON data for the content")
    parser.add_argument("--title", help="Title for custom mode")
    parser.add_argument("--speak", help="Text to speak aloud")
    
    # Message-specific args
    parser.add_argument("--message", "-m", help="Main message text (for message mode)")
    parser.add_argument("--sub-message", "-s", help="Sub-message text (for message mode)")
    parser.add_argument("--type", "-t", default="info", 
                        choices=["info", "warning", "alert", "celebration", "sticky"],
                        help="Message type")
    parser.add_argument("--auto-dismiss", "-d", type=int, default=10,
                        help="Seconds until auto-dismiss (0=stay forever)")
    parser.add_argument("--sticky", action="store_true",
                        help="Make message sticky (stays until manually cleared)")
    parser.add_argument("--color", help="Custom hex color (e.g., #667eea)")
    parser.add_argument("--font-size", default="4rem", help="Main message font size")
    parser.add_argument("--sub-size", default="2rem", help="Sub-message font size")
    
    args = parser.parse_args()
    
    url = args.url if args.url else DEFAULT_URL
    
    try:
        if args.mode == "dashboard":
            result = push_dashboard()
        elif args.mode == "run":
            data = json.loads(args.data) if args.data else {}
            result = push_run(data)
        elif args.mode == "meals":
            data = json.loads(args.data) if args.data else {}
            result = push_meals(data)
        elif args.mode == "routine":
            data = json.loads(args.data) if args.data else []
            result = push_routine(data)
        elif args.mode == "quickglance":
            data = json.loads(args.data) if args.data else {}
            result = push_quickglance(data)
        elif args.mode == "custom":
            result = push_custom(args.title or "Dobby", args.data or "Hello!", args.speak)
        elif args.mode == "message":
            result = push_message(
                message=args.message or "Hello!",
                message_type=args.type,
                sub_message=args.sub_message or "",
                auto_dismiss=args.auto_dismiss,
                sticky=args.sticky,
                color=args.color,
                font_size=args.font_size,
                sub_size=args.sub_size,
                speak=args.speak
            )
        elif args.mode == "clear":
            result = clear_display()
        
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
