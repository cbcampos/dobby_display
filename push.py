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
DEFAULT_URL = os.environ.get("DOBBY_DISPLAY_URL", "http://100.95.129.14:5000")

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
    parser.add_argument("--mode", required=True, choices=["dashboard", "run", "meals", "routine", "custom", "quickglance"])
    parser.add_argument("--data", help="JSON data for the content")
    parser.add_argument("--title", help="Title for custom mode")
    parser.add_argument("--speak", help="Text to speak aloud")
    
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
        
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
