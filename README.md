# Dobby Display System

A smart family dashboard for the Lenovo Duet Chrome OS tablet. Displays countdown timers, calendar events, dinner, tasks, and weather.

## Quick Start (Duet)

```bash
cd ~/dobby_display && ./start_display.sh
```

## Files

- `receiver.py` — Flask server on the Duet (runs on port 5000)
- `push.py` — Script to push content from OpenClaw to the Duet
- `fetch_data.py` — Fetches all data (calendar, Todoist, weather) and pushes to display
- `templates/quickglance.html` — Main display template with live updates

## Pushing Updates

From OpenClaw:

```bash
cd ~/dobby_display && python3 fetch_data.py
```

This fetches fresh data and auto-refreshes the display.

## Configuration

Edit `config/routines.yaml` to configure countdown routines:

```yaml
routines:
  - name: "Church"
    trigger_calendar: "Me and You"
    trigger_event_contains: "Church"
    trigger_days: [0]  # Sunday
    event_time: "10:00"
    leave_minutes_before: 15
    enabled: true

  - name: "Franklin to School"
    trigger_calendar: "Me and You"
    trigger_event_contains: "Franklin"
    trigger_days: [1, 2, 3, 4, 5]  # Mon-Fri
    leave_minutes_before: 15
    enabled: true
```

## Data Sources

- **Calendar**: Google Calendar via `gog` (Me and You calendar)
- **Tasks**: Todoist Family project (ID: 2366876876)
- **Dinner**: Todoist Dinner project (ID: 2366877406)
- **Weather**: Placeholder (add API if needed)

## Features

- Live clock (updates every second)
- Countdown timer (appears 60 min before event, gets urgent under 15 min)
- Auto-refreshes display when data changes
- Dark theme throughout
- Responsive layout (2/3 + 1/3 columns)

## Troubleshooting

Display not responding? Restart:

```bash
cd ~/dobby_display && ./start_display.sh
```

Check connection:

```bash
curl http://100.105.30.20:5000/api/status
```
