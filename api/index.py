import os
import sys
from datetime import datetime as dt
from flask import Flask, render_template_string, jsonify, request

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from timetable_parser import TimetableParser, DEFAULT_HTML_NAME

app = Flask(__name__)

# Cache parser instance
_parser = None

def get_parser():
    global _parser
    if _parser is None:
        # Search for HTML file in current or parent dirs
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        
        path1 = os.path.join(parent_dir, DEFAULT_HTML_NAME)
        path2 = os.path.join(current_dir, DEFAULT_HTML_NAME)
        path3 = os.path.join(os.getcwd(), DEFAULT_HTML_NAME)
        
        target = path1 if os.path.exists(path1) else (path2 if os.path.exists(path2) else path3)
        _parser = TimetableParser(target)
    return _parser

def get_room_category(room_name):
    r = room_name.upper().strip()
    if r.startswith("A"):
        return "Block A"
    elif r.startswith("B"):
        return "Block B"
    elif r.startswith("F"):
        return "Block F"
    elif r.startswith("G"):
        return "Block G"
    elif "DC" in r or "LINUX" in r or "EMBEDDED" in r or "LAB" in r:
        return "Special Labs"
    elif r.startswith("E"):
        return "Engineering (Block E)"
    return "Other Halls"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SLIIT University Lecture Hall Tracker</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Outfit', sans-serif;
            background: radial-gradient(circle at 10% 10%, #0f172a 0%, #090d16 100%);
            color: #f1f5f9;
            min-height: 100vh;
            padding: 30px 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        /* Hero Banner */
        .hero {
            background: linear-gradient(135deg, rgba(30, 58, 138, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%);
            border: 1px solid rgba(59, 130, 246, 0.3);
            border-radius: 20px;
            padding: 24px 30px;
            margin-bottom: 24px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.4);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 16px;
        }
        .hero h1 {
            font-size: 26px;
            font-weight: 800;
            background: linear-gradient(90deg, #60a5fa, #38bdf8, #a78bfa);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 6px;
        }
        .hero p { color: #94a3b8; font-size: 14px; }
        
        /* Clock Badge */
        .clock-badge {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(16, 185, 129, 0.15);
            border: 1px solid rgba(16, 185, 129, 0.4);
            color: #34d399;
            padding: 8px 16px;
            border-radius: 9999px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 13px;
            font-weight: 600;
        }
        .dot {
            width: 8px;
            height: 8px;
            background-color: #10b981;
            border-radius: 50%;
            box-shadow: 0 0 10px #10b981;
            animation: pulse 1.8s infinite;
        }
        @keyframes pulse {
            0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
            70% { transform: scale(1.1); box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }
            100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
        }
        
        /* Controls & Filter Bar */
        .controls-bar {
            background: rgba(30, 41, 59, 0.5);
            border: 1px solid rgba(148, 163, 184, 0.15);
            border-radius: 16px;
            padding: 16px 20px;
            margin-bottom: 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 16px;
        }
        .status-pill {
            background: rgba(59, 130, 246, 0.15);
            border: 1px solid rgba(59, 130, 246, 0.35);
            color: #60a5fa;
            padding: 6px 12px;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 600;
        }
        select, input[type="text"] {
            background: #1e293b;
            color: #f8fafc;
            border: 1px solid #334155;
            padding: 8px 12px;
            border-radius: 8px;
            font-family: inherit;
            font-size: 13px;
            outline: none;
        }
        select:focus { border-color: #38bdf8; }

        /* KPI Cards */
        .grid-kpi {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 16px;
            margin-bottom: 28px;
        }
        .card-kpi {
            background: rgba(30, 41, 59, 0.6);
            border: 1px solid rgba(148, 163, 184, 0.15);
            border-radius: 16px;
            padding: 18px 20px;
            text-align: center;
            backdrop-filter: blur(8px);
        }
        .kpi-title { font-size: 12px; text-transform: uppercase; color: #94a3b8; font-weight: 600; letter-spacing: 0.5px; }
        .kpi-num { font-size: 34px; font-weight: 800; margin: 4px 0; font-family: 'JetBrains Mono', monospace; }
        
        /* Tabs */
        .tabs {
            display: flex;
            gap: 8px;
            border-bottom: 1px solid #334155;
            margin-bottom: 20px;
            overflow-x: auto;
        }
        .tab-btn {
            background: transparent;
            border: none;
            color: #94a3b8;
            padding: 10px 18px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            border-bottom: 2px solid transparent;
            transition: all 0.2s;
            font-family: inherit;
        }
        .tab-btn.active {
            color: #38bdf8;
            border-bottom-color: #38bdf8;
        }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        
        /* Room Grid */
        .room-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
            gap: 16px;
        }
        .room-card {
            background: linear-gradient(145deg, rgba(16, 185, 129, 0.08) 0%, rgba(30, 41, 59, 0.6) 100%);
            border: 1px solid rgba(16, 185, 129, 0.3);
            border-radius: 14px;
            padding: 16px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            min-height: 110px;
            transition: all 0.2s ease;
        }
        .room-card:hover {
            border-color: #34d399;
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(16, 185, 129, 0.15);
        }
        .room-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .room-name {
            font-size: 20px;
            font-weight: 700;
            color: #f8fafc;
        }
        .badge-free {
            background: rgba(16, 185, 129, 0.2);
            color: #34d399;
            padding: 3px 8px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 700;
        }
        .badge-occ {
            background: rgba(239, 68, 68, 0.2);
            color: #f87171;
            padding: 3px 8px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 700;
        }
        .room-building { font-size: 12px; color: #94a3b8; margin-top: 4px; }
        
        .occ-card {
            background: linear-gradient(145deg, rgba(239, 68, 68, 0.08) 0%, rgba(30, 41, 59, 0.6) 100%);
            border: 1px solid rgba(239, 68, 68, 0.3);
            border-radius: 14px;
            padding: 16px;
            margin-bottom: 12px;
        }
        .booking-row {
            background: rgba(15, 23, 42, 0.5);
            border-left: 3px solid #ef4444;
            padding: 10px 14px;
            border-radius: 6px;
            margin-top: 10px;
            font-size: 13px;
        }
        
        /* Table view */
        table.matrix-table {
            width: 100%;
            border-collapse: collapse;
            background: #1e293b;
            border-radius: 10px;
            overflow: hidden;
            font-size: 13px;
        }
        table.matrix-table th, table.matrix-table td {
            padding: 12px 14px;
            border-bottom: 1px solid #334155;
            text-align: left;
        }
        table.matrix-table th { background: #0f172a; color: #94a3b8; font-weight: 600; }
        
        footer {
            margin-top: 40px;
            text-align: center;
            color: #64748b;
            font-size: 12px;
            border-top: 1px solid #1e293b;
            padding-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Hero Header -->
        <div class="hero">
            <div>
                <h1>🏛️ SLIIT University Lecture Hall Tracker</h1>
                <p>Real-time room occupancy analysis based on official university timetable</p>
            </div>
            <div>
                <div class="clock-badge">
                    <span class="dot"></span>
                    <span id="live-clock">Loading clock...</span>
                </div>
            </div>
        </div>

        <!-- Controls Bar -->
        <div class="controls-bar">
            <div style="display: flex; gap: 14px; align-items: center; flex-wrap: wrap;">
                <div>
                    <span style="color:#94a3b8; font-size:12px; display:block;">Active Day:</span>
                    <strong style="color: #60a5fa; font-size: 15px;" id="disp-day">{{ current_day }}</strong>
                </div>
                <div>
                    <span style="color:#94a3b8; font-size:12px; display:block;">Matched Slot:</span>
                    <strong style="color: #38bdf8; font-size: 15px;" id="disp-slot">{{ matched_slot }}</strong>
                </div>
                <div class="status-pill">{{ slot_status_msg }}</div>
            </div>
            <div style="display: flex; gap: 10px; align-items: center; flex-wrap: wrap;">
                <label style="font-size: 12px; color: #94a3b8;">Explore Day:</label>
                <select id="day-select" onchange="applyFilter()">
                    {% for d in all_days %}
                    <option value="{{ d }}" {% if d == active_day %}selected{% endif %}>{{ d }}</option>
                    {% endfor %}
                </select>
                <label style="font-size: 12px; color: #94a3b8;">Slot:</label>
                <select id="slot-select" onchange="applyFilter()">
                    {% for s in all_slots %}
                    <option value="{{ s }}" {% if s == active_slot %}selected{% endif %}>{{ s }}</option>
                    {% endfor %}
                </select>
                <label style="font-size: 12px; color: #94a3b8;">Building:</label>
                <select id="bldg-select" onchange="applyFilter()">
                    <option value="All">All Buildings</option>
                    <option value="Block A">Block A</option>
                    <option value="Block B">Block B</option>
                    <option value="Block F">Block F</option>
                    <option value="Block G">Block G</option>
                    <option value="Special Labs">Special Labs</option>
                </select>
            </div>
        </div>

        <!-- KPI Cards -->
        <div class="grid-kpi">
            <div class="card-kpi">
                <div class="kpi-title">Master Rooms</div>
                <div class="kpi-num" style="color: #93c5fd;">{{ room_status.total_rooms }}</div>
                <div style="font-size: 11px; color: #64748b;">All Recognized Halls</div>
            </div>
            <div class="card-kpi" style="border-color: rgba(16, 185, 129, 0.4);">
                <div class="kpi-title" style="color: #34d399;">Available Halls</div>
                <div class="kpi-num" style="color: #34d399;" id="kpi-free">{{ room_status.free_rooms|length }}</div>
                <div style="font-size: 11px; color: #10b981;">Vacant for Current Slot</div>
            </div>
            <div class="card-kpi" style="border-color: rgba(239, 68, 68, 0.3);">
                <div class="kpi-title" style="color: #f87171;">Occupied Halls</div>
                <div class="kpi-num" style="color: #f87171;" id="kpi-occ">{{ room_status.occupied_rooms|length }}</div>
                <div style="font-size: 11px; color: #ef4444;">Classes in Progress</div>
            </div>
            <div class="card-kpi">
                <div class="kpi-title">Utilization</div>
                <div class="kpi-num" style="color: #c084fc;">{{ room_status.occupancy_pct }}%</div>
                <div style="font-size: 11px; color: #64748b;">Slot Occupancy Rate</div>
            </div>
        </div>

        <!-- Tabs -->
        <div class="tabs">
            <button class="tab-btn active" onclick="switchTab('tab-free')">🟢 Free Halls (<span id="tab-free-count">{{ room_status.free_rooms|length }}</span>)</button>
            <button class="tab-btn" onclick="switchTab('tab-occ')">🔴 Occupied Halls (<span id="tab-occ-count">{{ room_status.occupied_rooms|length }}</span>)</button>
            <button class="tab-btn" onclick="switchTab('tab-matrix')">📊 Full Day Matrix</button>
        </div>

        <!-- Tab 1: Free Rooms -->
        <div id="tab-free" class="tab-content active">
            <div class="room-grid" id="free-rooms-container">
                {% for room in room_status.free_rooms %}
                <div class="room-card" data-building="{{ get_bldg(room) }}">
                    <div class="room-header">
                        <span class="room-name">🚪 {{ room }}</span>
                        <span class="badge-free">VACANT</span>
                    </div>
                    <div class="room-building">📍 {{ get_bldg(room) }}</div>
                    <div style="margin-top: 10px; font-size: 11px; color: #64748b;">Free for slot {{ active_slot }}</div>
                </div>
                {% endfor %}
            </div>
        </div>

        <!-- Tab 2: Occupied Rooms -->
        <div id="tab-occ" class="tab-content">
            <div id="occ-rooms-container">
                {% if room_status.occupied_rooms %}
                    {% for room in room_status.occupied_rooms %}
                    <div class="occ-card" data-building="{{ get_bldg(room) }}">
                        <div class="room-header">
                            <span style="font-size: 18px; font-weight: 700; color: #fca5a5;">🚪 {{ room }} ({{ get_bldg(room) }})</span>
                            <span class="badge-occ">OCCUPIED</span>
                        </div>
                        {% for b in room_status.occupied_details.get(room, []) %}
                        <div class="booking-row">
                            <div style="font-weight: 600; color: #f1f5f9;">📖 {{ b.subject }}</div>
                            <div style="color: #94a3b8; font-size: 12px;">👨‍🏫 Lecturer: {{ b.lecturer }} | 👥 Group: {{ b.group }}</div>
                            <div style="color: #38bdf8; font-size: 11px; margin-top: 3px;">
                                {% if b.is_span %}⏳ Continuing from earlier slot (Rowspan){% else %}⏱️ Started this slot{% endif %}
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                    {% endfor %}
                {% else %}
                    <div style="padding: 20px; background: rgba(16,185,129,0.1); border-radius: 12px; color: #34d399; text-align: center;">
                        🎉 All lecture halls are currently free during this slot!
                    </div>
                {% endif %}
            </div>
        </div>

        <!-- Tab 3: Full Day Matrix -->
        <div id="tab-matrix" class="tab-content">
            <table class="matrix-table">
                <thead>
                    <tr>
                        <th>Time Slot</th>
                        <th>Free Count</th>
                        <th>Occupied Count</th>
                        <th>Utilization</th>
                        <th>Occupied Rooms</th>
                    </tr>
                </thead>
                <tbody>
                    {% for m in matrix_data %}
                    <tr>
                        <td><strong>{{ m.slot }}</strong></td>
                        <td style="color: #34d399; font-weight: 700;">{{ m.free_count }}</td>
                        <td style="color: #f87171; font-weight: 700;">{{ m.occ_count }}</td>
                        <td>{{ m.pct }}%</td>
                        <td style="color: #94a3b8;">{{ m.occ_rooms }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <footer>
            SLIIT Timetable Real-Time Engine • Python BeautifulSoup4 • Automatic Slot & Rowspan Tracking • Ready for Vercel & Streamlit Cloud
        </footer>
    </div>

    <script>
        function updateLiveClock() {
            const now = new Date();
            const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
            const dayName = days[now.getDay()];
            const timeStr = now.toLocaleTimeString();
            document.getElementById('live-clock').innerText = `SYSTEM CLOCK: ${dayName}, ${timeStr}`;
        }
        setInterval(updateLiveClock, 1000);
        updateLiveClock();

        function switchTab(tabId) {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            event.target.classList.add('active');
            document.getElementById(tabId).classList.add('active');
        }

        function applyFilter() {
            const day = document.getElementById('day-select').value;
            const slot = document.getElementById('slot-select').value;
            const bldg = document.getElementById('bldg-select').value;
            window.location.href = `/?day=${encodeURIComponent(day)}&slot=${encodeURIComponent(slot)}&bldg=${encodeURIComponent(bldg)}`;
        }

        // Client-side building filtering
        document.getElementById('bldg-select').addEventListener('change', function() {
            const val = this.value;
            const cards = document.querySelectorAll('.room-card');
            let visibleFree = 0;
            cards.forEach(c => {
                if (val === 'All' || c.getAttribute('data-building') === val) {
                    c.style.display = 'flex';
                    visibleFree++;
                } else {
                    c.style.display = 'none';
                }
            });
            document.getElementById('tab-free-count').innerText = visibleFree;
        });
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    parser = get_parser()
    now_dt = dt.now()
    current_day = now_dt.strftime("%A")
    matched_slot, slot_status_msg = parser.match_time_to_slot(now_dt.time())
    
    # Query params for interactive preview
    req_day = request.args.get("day")
    req_slot = request.args.get("slot")
    req_bldg = request.args.get("bldg", "All")
    
    active_day = req_day if req_day in parser.all_days else (current_day if current_day in parser.all_days else parser.all_days[0])
    active_slot = req_slot if req_slot in parser.all_slots else matched_slot
    
    room_status = parser.get_room_status(active_day, active_slot)
    
    # Full day matrix
    matrix_data = []
    for slot in parser.all_slots:
        st_data = parser.get_room_status(active_day, slot)
        matrix_data.append({
            "slot": slot,
            "free_count": len(st_data["free_rooms"]),
            "occ_count": len(st_data["occupied_rooms"]),
            "pct": st_data["occupancy_pct"],
            "occ_rooms": ", ".join(st_data["occupied_rooms"]) if st_data["occupied_rooms"] else "None (All Free)"
        })

    return render_template_string(
        HTML_TEMPLATE,
        current_day=current_day,
        matched_slot=matched_slot,
        slot_status_msg=slot_status_msg,
        active_day=active_day,
        active_slot=active_slot,
        all_days=parser.all_days,
        all_slots=parser.all_slots,
        room_status=room_status,
        matrix_data=matrix_data,
        get_bldg=get_room_category
    )

@app.route("/api/status")
def api_status():
    parser = get_parser()
    now_dt = dt.now()
    current_day = now_dt.strftime("%A")
    matched_slot, msg = parser.match_time_to_slot(now_dt.time())
    
    day = request.args.get("day", current_day if current_day in parser.all_days else parser.all_days[0])
    slot = request.args.get("slot", matched_slot)
    
    status = parser.get_room_status(day, slot)
    return jsonify({
        "system_time": now_dt.strftime("%Y-%m-%d %H:%M:%S"),
        "current_day": current_day,
        "matched_slot": matched_slot,
        "status_message": msg,
        "active_day": day,
        "active_slot": slot,
        "total_rooms": status["total_rooms"],
        "free_rooms": status["free_rooms"],
        "occupied_rooms": status["occupied_rooms"],
        "occupancy_pct": status["occupancy_pct"],
        "occupied_details": status["occupied_details"]
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
