#!/usr/bin/env python3
"""
Quick Glance Data Fetcher
Fetches all data needed for the quick glance display and pushes to the Duet.
"""

import os
import sys

# Fix PATH for cron jobs - include home bin where gog lives
os.environ["PATH"] = os.environ.get("PATH", "") + ":/home/ccampos/bin:/usr/local/bin"

import json
import subprocess
import requests
from datetime import datetime, timedelta, timezone
import yaml

# Load secrets if available
secrets_path = os.path.expanduser("~/.openclaw/.secrets/todoist.env")
if os.path.exists(secrets_path):
    with open(secrets_path) as f:
        for line in f:
            if line.strip() and "=" in line:
                key, val = line.strip().split("=", 1)
                os.environ.setdefault(key, val)

# Config
DISPLAY_URL = os.environ.get("DOBBY_DISPLAY_URL", "http://100.76.87.63:5000")
TODOIST_TOKEN = os.environ.get("TODOIST_API_TOKEN", "79267f117496088bbc215416cb4c355893432553")
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".cache")
CACHE_FILE = os.path.join(CACHE_DIR, "events_cache.json")

# Ensure cache directory exists
os.makedirs(CACHE_DIR, exist_ok=True)

def load_cache():
    """Load cached events from file"""
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, "r") as f:
                return json.load(f)
    except:
        pass
    return {"events": [], "timestamp": None}

def save_cache(events):
    """Save events to cache file"""
    try:
        with open(CACHE_FILE, "w") as f:
            json.dump({"events": events, "timestamp": datetime.now().isoformat()}, f)
    except:
        pass
CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))

# Central timezone offset
CENTRAL_OFFSET = timedelta(hours=-6)

def load_config():
    """Load routines configuration"""
    config_path = os.path.join(CONFIG_DIR, "config", "routines.yaml")
    try:
        with open(config_path) as f:
            return yaml.safe_load(f)
    except:
        return {"routines": []}

def get_calendar_events(calendar_name="Me and You"):
    """Fetch today's events from Google Calendar, excluding all-day events"""
    cache = load_cache()
    cached_today = cache.get("events_today", [])
    
    try:
        result = subprocess.run(
            ["gog", "calendar", "events", calendar_name, "--today", "--json"],
            capture_output=True, text=True, timeout=30
        )
        # Check if gog returned valid data
        if not result.stdout or not result.stdout.strip():
            print("Calendar: Empty response, using cache")
            return cached_today
            
        data = json.loads(result.stdout)
        events = data.get("events", [])
        # Filter out all-day events (they start at midnight 00:00:00 in the time portion)
        filtered = []
        for event in events:
            start = event.get("start", {})
            dateTime = start.get("dateTime", "")
            # Exclude events that start at midnight (all-day events) - check for T00:00:00 pattern
            if dateTime and "T00:00:00" not in dateTime:
                filtered.append(event)
        
        # Save to cache
        cache["events_today"] = filtered
        save_cache(cache)
        
        return filtered
    except Exception as e:
        print(f"Calendar error: {e}, using cache")
        return cached_today

def get_upcoming_events(calendar_name="Me and You", days=7):
    """Fetch upcoming events for the next N days, excluding all-day events"""
    cache = load_cache()
    cached_upcoming = cache.get("events_upcoming", [])
    
    try:
        result = subprocess.run(
            ["gog", "calendar", "events", calendar_name, "--days", str(days), "--json"],
            capture_output=True, text=True, timeout=30
        )
        # Check if gog returned valid data
        if not result.stdout or not result.stdout.strip():
            print("Upcoming: Empty response, using cache")
            return cached_upcoming
            
        data = json.loads(result.stdout)
        events = data.get("events", [])
    except Exception as e:
        print(f"Upcoming error: {e}")
        return cached_upcoming
    
    # Filter out all-day events (they start at midnight 00:00:00) and sort by time
    filtered = []
    for event in events:
        start = event.get("start", {})
        dateTime = start.get("dateTime", "")
        if dateTime and "T00:00:00" not in dateTime:
            try:
                event_start = parse_event_time(dateTime)
                if event_start:
                    event["_sort_time"] = event_start
                    filtered.append(event)
            except:
                pass
    
    # Sort by start time
    filtered.sort(key=lambda e: e.get("_sort_time", datetime.max))
    
    # Save to cache
    cache = load_cache()
    cache["events_upcoming"] = filtered
    save_cache(cache)
    
    return filtered

def check_popup_routines():
    """Check if any popup routines should trigger. Returns (should_popup, message_data)"""
    config = load_config()
    routines = config.get("routines", [])
    
    now = datetime.now().replace(tzinfo=timezone(CENTRAL_OFFSET))
    today_dow = now.weekday()
    
    # Load popup tracking
    cache = load_cache()
    last_popup = cache.get("last_popup", {})
    
    for routine in routines:
        if not routine.get("enabled", True):
            continue
        
        # Only process popup routines
        if routine.get("show_on_quickglance", True):
            continue
        
        # Check if today matches allowed days
        trigger_days = routine.get("trigger_days", [])
        if today_dow not in trigger_days:
            continue
        
        calendar_name = routine.get("trigger_calendar", "Me and You")
        minutes_before = routine.get("minutes_before", 15)
        
        # Check upcoming events
        events = get_upcoming_events(calendar_name)
        
        for event in events:
            summary = event.get("summary", "")
            start = event.get("start", {}).get("dateTime", "")
            if not start:
                continue
            
            event_start = parse_event_time(start)
            if not event_start or event_start <= now:
                continue
            
            # Check if within the window
            diff = event_start - now
            mins_until = diff.total_seconds() / 60
            
            if mins_until <= minutes_before and mins_until > 0:
                # Check if we already showed this popup recently (within 20 min)
                event_id = f"{summary}_{event_start.strftime('%Y%m%d%H%M')}"
                if last_popup.get("event_id") == event_id:
                    continue  # Already shown
                
                # Calculate countdown
                hours = int(mins_until // 60)
                mins = int(mins_until % 60)
                if hours > 0:
                    countdown = f"{hours}h {mins}m"
                else:
                    countdown = f"{mins}m"
                
                # Update cache to prevent repeat
                cache["last_popup"] = {"event_id": event_id, "time": now.isoformat()}
                save_cache(cache)
                
                return True, {
                    "event": summary,
                    "countdown": countdown,
                    "time": event_start.strftime("%-I:%M %p")
                }
    
    return False, None

def get_routine_countdown():
    """Check configured routines and return quickglance countdown data"""
    config = load_config()
    routines = config.get("routines", [])
    
    now = datetime.now().replace(tzinfo=timezone(CENTRAL_OFFSET))
    today_dow = now.weekday()  # 0=Monday, 6=Sunday
    
    for routine in routines:
        if not routine.get("enabled", True):
            continue
        
        # Skip popup routines - they're handled separately
        if not routine.get("show_on_quickglance", True):
            continue
        
        # Check if today matches allowed days
        trigger_days = routine.get("trigger_days", [])
        if today_dow not in trigger_days:
            continue
        
        # Check calendar for matching event
        calendar_name = routine.get("trigger_calendar", "Me and You")
        event_match = routine.get("trigger_event_contains", "")
        
        # Only check calendar events if there's a specific event_match
        # Otherwise, use default_time only (for fixed routines like School/Bedtime)
        found_event = False
        
        if event_match:  # Only search calendar if trigger_event_contains is set
            events = get_calendar_events(calendar_name)
            
            for event in events:
                summary = event.get("summary", "")
                
                # Only match events containing the trigger string
                if event_match.lower() not in summary.lower():
                    continue
                    
                found_event = True
                start = event.get("start", {}).get("dateTime", "")
                if start:
                    event_start = parse_event_time(start)
                    if event_start and event_start > now:
                        leave_time = event_start - timedelta(minutes=routine.get("leave_minutes_before", 15))
                        if leave_time > now:
                            diff = leave_time - now
                            hours = diff.seconds // 3600
                            mins = (diff.seconds % 3600) // 60
                            if hours > 0:
                                countdown = f"{hours}h {mins}m"
                            else:
                                countdown = f"{mins}m"
                            
                            # Check if this is bedtime (leave_minutes_before = 0)
                            if routine.get("leave_minutes_before", 15) == 0:
                                return countdown, routine.get("name", "Event"), routine.get("name", "Event")
                            else:
                                # Format leave time
                                leave_str = leave_time.strftime("%-I:%M")
                                return countdown, f"Leave ({leave_str})", routine.get("name", "Event")
                            countdown = f"{hours}h {mins}m"
                        else:
                            countdown = f"{mins}m"
                        
                        # Check if this is bedtime (leave_minutes_before = 0)
                        if routine.get("leave_minutes_before", 15) == 0:
                            return countdown, routine.get("name", "Event"), routine.get("name", "Event")
                        else:
                            # Format leave time
                            leave_str = leave_time.strftime("%-I:%M")
                            return countdown, f"Leave ({leave_str})", routine.get("name", "Event")
        
        # Check if we have a default time for this routine
        default_time = routine.get("event_time", "")
        require_event = routine.get("require_event", False)
        
        # If require_event is true, only show countdown if a calendar event matched above
        # Skip the default time fallback if require_event is true
        if require_event and not found_event:
            continue
        
        if default_time:
            # Parse default time
            hour, minute = map(int, default_time.split(":"))
            event_time = now.replace(hour=hour, minute=minute, second=0)
            leave_time = event_time - timedelta(minutes=routine.get("leave_minutes_before", 15))
            if leave_time > now:
                diff = leave_time - now
                hours = diff.seconds // 3600
                mins = (diff.seconds % 3600) // 60
                # Only show countdown if within 2 hours (otherwise it's not useful)
                if hours >= 2:
                    return "", "", ""
                if hours > 0:
                    countdown = f"{hours}h {mins}m"
                else:
                    countdown = f"{mins}m"
                
                # Check if this is bedtime (leave_minutes_before = 0)
                if routine.get("leave_minutes_before", 15) == 0:
                    return countdown, routine.get("name", "Event"), routine.get("name", "Event")
                else:
                    leave_str = leave_time.strftime("%-I:%M")
                    return countdown, f"Leave ({leave_str})", routine.get("name", "Event")
    
    return "", "", ""

def parse_event_time(start_str):
    """Fetch today's events from Google Calendar"""
    try:
        result = subprocess.run(
            ["gog", "calendar", "events", "Me and You", "--today", "--json"],
            capture_output=True, text=True, timeout=30
        )
        data = json.loads(result.stdout)
        return data.get("events", [])
    except Exception as e:
        print(f"Calendar error: {e}")
        return []

def get_todoist_dinner():
    """Fetch today's dinner from Todoist"""
    token = os.environ.get("TODOIST_API_TOKEN") or os.environ.get("TODOIST_TOKEN")
    if not token:
        print("Todoist error: No API token")
        return "TBD"
    try:
        result = subprocess.run(
            ["curl", "-s", "https://api.todoist.com/api/v2/projects", 
             "-H", f"Authorization: Bearer {token}"],
            capture_output=True, text=True, timeout=15
        )
        projects = json.loads(result.stdout)
        dinner_id = None
        for p in projects:
            if p.get("name") == "Dinner":
                dinner_id = p.get("id")
                break
        
        if not dinner_id:
            return "TBD"
            
        today = datetime.now().strftime("%Y-%m-%d")
        result = subprocess.run(
            ["curl", "-s", f"https://api.todoist.com/api/v2/tasks?project_id={dinner_id}",
             "-H", f"Authorization: Bearer {token}"],
            capture_output=True, text=True, timeout=15
        )
        tasks = json.loads(result.stdout)
        for task in tasks:
            due = task.get("due", {})
            if due.get("date") == today:
                return task.get("content", "TBD")
        return "TBD"
    except Exception as e:
        print(f"Todoist error: {e}")
        return "TBD"

def get_weather():
    """Get weather (placeholder)"""
    return {"icon": "☀️", "temp": "58°", "high": "62", "low": "40", "desc": "Sunny"}

def get_family_tasks():
    """Fetch family tasks from Todoist"""
    token = os.environ.get("TODOIST_API_TOKEN") or os.environ.get("TODOIST_TOKEN")
    if not token:
        print("Family tasks error: No TODOIST_API_TOKEN")
        return ["Set up Todoist", "Check API key"]
    try:
        result = subprocess.run(
            ["curl", "-s", "https://api.todoist.com/api/v2/tasks?project_id=2366876876",
             "-H", f"Authorization: Bearer {token}"],
            capture_output=True, text=True, timeout=15
        )
        tasks = json.loads(result.stdout)
        task_list = []
        for t in tasks[:3]:
            content = t.get("content", "")
            due = t.get("due", {})
            due_date = due.get("date") if due else None
            due_str = None
            if due_date:
                # Format date nicely
                try:
                    from datetime import datetime
                    dt = datetime.strptime(due_date, "%Y-%m-%d")
                    due_str = dt.strftime("%b %d")
                except:
                    due_str = due_date
            task_list.append({"name": content, "due": due_str})
        return task_list
    except Exception as e:
        print(f"Family tasks error: {e}")
        return [{"name": "Set up Todoist", "due": None}, {"name": "Check API key", "due": None}]

def parse_event_time(start_str):
    """Parse event time string to datetime"""
    if not start_str:
        return None
    try:
        if start_str.endswith("Z"):
            dt = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
            # Convert to Central
            return dt + CENTRAL_OFFSET
        else:
            dt = datetime.fromisoformat(start_str)
            if dt.tzinfo is None:
                return dt + CENTRAL_OFFSET
            return dt
    except:
        return None

def build_quickglance():
    """Build the quick glance data"""
    now = datetime.now().replace(tzinfo=timezone(CENTRAL_OFFSET))
    
    # Today's events for current event (from Me and You)
    events = get_calendar_events()
    # Upcoming events (next 7 days) for next event (Me and You only)
    upcoming_events = get_upcoming_events("Me and You")
    
    current_event = None
    current_event_time = None
    current_location = None
    next_event = None
    next_event_time = None
    next_location = None
    
    # Find current event (from today's events)
    for event in events:
        start = event.get("start", {}).get("dateTime", "")
        end = event.get("end", {}).get("dateTime", "")
        event_start = parse_event_time(start)
        event_end = parse_event_time(end) if end else None
        
        if event_start and event_start <= now:
            # Check if event hasn't ended yet
            if not event_end or event_end > now:
                current_event = event.get("summary", "Event")
                # Show END time of current event
                current_event_time = event_end.strftime("%-I:%M %p") if event_end else ""
                current_location = event.get("location", "")
    
    # Find next event (from upcoming events)
    for event in upcoming_events:
        start = event.get("start", {}).get("dateTime", "")
        event_start = parse_event_time(start)
        
        if event_start and event_start > now:
            next_event = event.get("summary", "Event")
            next_event_time = event_start.strftime("%-I:%M %p")
            next_location = event.get("location", "")
            # Check if it's tomorrow or later for date display
            if event_start.date() > now.date():
                next_event_time = event_start.strftime("%a %-I:%M %p")
            break
    
    dinner = get_todoist_dinner()
    weather = get_weather()
    family_tasks = get_family_tasks()
    
    # Get routine countdown
    countdown, countdown_label, countdown_routine = get_routine_countdown()
    
    # Only show countdown for Church/School/Bedtime - skip fallback for other events
    # If routine returned nothing, don't show countdown for regular events
    
    # Calculate urgency
    urgency = "safe"
    if countdown:
        parts = countdown.replace('h','').replace('m','').split()
        total_mins = int(parts[0]) * 60 + int(parts[1]) if len(parts) > 1 else int(parts[0])
        if total_mins <= 5:
            urgency = "critical"
        elif total_mins <= 15:
            urgency = "urgent"
    
    data = {
        "time": now.strftime("%-I:%M %p"),
        "date": now.strftime("%A, %b %d"),
        "weather_icon": weather["icon"],
        "weather_temp": weather["temp"],
        "weather_high": weather["high"],
        "weather_low": weather["low"],
        "weather_desc": weather["desc"],
        "current_event": current_event if current_event else "Free Time",
        "current_event_time": current_event_time if current_event_time else "",
        "current_location": current_location if current_location else "",
        "next_event": next_event if next_event else "None",
        "next_event_time": next_event_time if next_event_time else "",
        "next_location": next_location if next_location else "",
        "dinner": dinner,
        "tasks": family_tasks,
        "countdown_label": countdown_label,
        "countdown": countdown,
        "countdown_urgency": urgency
    }
    
    return data

def push_template(force=False):
    """Push template to display automatically"""
    if not force:
        print("Skipping template push (use --force-template to push)")
        return
        
    template_path = os.path.join(os.path.dirname(__file__), "templates", "quickglance.html")
    try:
        with open(template_path, "r") as f:
            content = f.read()
        r = requests.post(f"{DISPLAY_URL}/api/template/quickglance.html", 
                         json={"content": content}, timeout=10)
        if r.status_code == 200:
            print(f"Template pushed: {r.json()}")
        else:
            print(f"Template push failed: {r.status_code}")
    except Exception as e:
        print(f"Template push error: {e}")

def push_display(data, force=False):
    """Push data to display only if it changed"""
    # Get current display state
    try:
        r = requests.get(f"{DISPLAY_URL}/api/status", timeout=5)
        if r.status_code == 200:
            current = r.json().get("content", {})
            # Fields that matter for display continuity
            key_fields = ["current_event", "next_event", "next_event_time", "dinner", "countdown", "countdown_label"]
            current_subset = {k: current.get(k) for k in key_fields}
            new_subset = {k: data.get(k) for k in key_fields}
            
            if not force and current_subset == new_subset:
                print("Data unchanged, skipping push")
                return
            else:
                print(f"Data changed: {current_subset} -> {new_subset}")
    except Exception as e:
        print(f"Status check error: {e}")
    
    payload = {"mode": "quickglance", "title": "Quick Look", "content": data}
    try:
        r = requests.post(f"{DISPLAY_URL}/api/update", json=payload, timeout=10)
        print(f"Pushed: {r.json()}")
    except Exception as e:
        print(f"Push error: {e}")

import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch and push quick glance data")
    parser.add_argument("--force-template", action="store_true", help="Force push template to display")
    parser.add_argument("--force-push", action="store_true", help="Force push even if data unchanged")
    args = parser.parse_args()
    
    print("Building quick glance...")
    data = build_quickglance()
    print(json.dumps(data, indent=2))
    
    # Check for popup triggers
    print("\nChecking for popup triggers...")
    should_popup, popup_data = check_popup_routines()
    popup_mode = False
    if should_popup and popup_data:
        print(f"Triggering popup: {popup_data}")
        # Push countdown popup
        countdown_payload = {
            "mode": "countdown",
            "title": "Upcoming Event",
            "content": {
                "event": popup_data["event"],
                "days": 0,
                "hours": 0,
                "minutes": int(popup_data["countdown"].replace("m", "").replace("h", " ").split()[0]) if "m" in popup_data["countdown"] else 0,
                "message": f"Starts at {popup_data['time']}"
            }
        }
        try:
            r = requests.post(f"{DISPLAY_URL}/api/update", json=countdown_payload, timeout=10)
            print(f"Popup pushed: {r.json()}")
        except Exception as e:
            print(f"Popup error: {e}")
        
        popup_mode = True
    else:
        print("No popup triggers")
    
    print("\nPushing template...")
    push_template(force=args.force_template)
    print("\nPushing to display...")
    if popup_mode:
        print("Skipping quickglance push - popup is displaying")
    else:
        push_display(data, force=args.force_push)

