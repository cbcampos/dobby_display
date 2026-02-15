#!/usr/bin/env python3
"""
Dobby Display Receiver
A simple Flask server that displays content pushed from Dobby.
Runs on the Lenovo Duet Chromebook.
"""

from flask import Flask, render_template, request, jsonify, redirect
import os
import logging
from datetime import datetime

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory storage for current display state
display_state = {
    "mode": "quickglance",  # dashboard, run, meals, routine, custom, quickglance
    "title": "Quick Look",
    "content": {},
    "updated": None
}

@app.route('/')
def index():
    """Main display page - renders based on current mode"""
    return render_template('display.html', state=display_state)

@app.route('/api/status')
def status():
    """Return current display state"""
    return jsonify(display_state)

@app.route('/api/update', methods=['POST'])
def update():
    """Update the display content"""
    global display_state
    
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    display_state = {
        "mode": data.get("mode", "custom"),
        "title": data.get("title", "Dobby Display"),
        "content": data.get("content", {}),
        "updated": datetime.now().isoformat()
    }
    
    logger.info(f"Display updated: {display_state['mode']} - {display_state['title']}")
    return jsonify({"success": True, "state": display_state})

@app.route('/api/dashboard')
def dashboard():
    """Set display to dashboard mode"""
    global display_state
    display_state = {
        "mode": "dashboard",
        "title": "Family Dashboard",
        "content": {},
        "updated": datetime.now().isoformat()
    }
    return jsonify({"success": True})

@app.route('/api/clear')
def clear():
    """Clear display back to dashboard"""
    return dashboard()

@app.route('/api/template/<template_name>', methods=['POST'])
def update_template(template_name):
    """Update a template file directly"""
    import os
    content = request.json.get('content', '')
    safe_name = os.path.basename(template_name)
    if not safe_name.endswith('.html'):
        safe_name += '.html'
    template_path = os.path.join(os.path.dirname(__file__), 'templates', safe_name)
    with open(template_path, 'w') as f:
        f.write(content)
    return jsonify({"success": True, "template": safe_name})

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok", "time": datetime.now().isoformat()})

if __name__ == '__main__':
    print("🎬 Dobby Display Receiver starting...")
    print("Open http://localhost:5000 in browser")
    print("Use /api/update to push content")
    app.run(host='0.0.0.0', port=5000, debug=False)
