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
            flex-direction: column;
            gap: 16px;
        }
        .controls-top {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 14px;
        }
        .controls-form {
            display: flex;
            gap: 12px;
            align-items: center;
            flex-wrap: wrap;
            padding-top: 14px;
            border-top: 1px solid rgba(255,255,255,0.08);
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
        
        .preset-btn {
            background: rgba(56, 189, 248, 0.15);
            border: 1px solid rgba(56, 189, 248, 0.35);
            color: #38bdf8;
            padding: 6px 12px;
            border-radius: 8px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.15s;
        }
        .preset-btn:hover {
            background: rgba(56, 189, 248, 0.25);
            border-color: #38bdf8;
        }

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
        .badge-block {
            background: rgba(56, 189, 248, 0.2);
            color: #38bdf8;
            padding: 3px 8px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 700;
        }
        .badge-partial {
            background: rgba(245, 158, 11, 0.2);
            color: #fbbf24;
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
        .partial-card {
            background: linear-gradient(145deg, rgba(245, 158, 11, 0.08) 0%, rgba(30, 41, 59, 0.6) 100%);
            border: 1px solid rgba(245, 158, 11, 0.35);
            border-radius: 14px;
            padding: 16px;
            margin-bottom: 12px;
        }
        .booking-row {
            background: rgba(15, 23, 42, 0.5);
            border-left: 3px solid #ef4444;
            padding: 10px 14px;
            border-radius: 6px;
            margin-top: 8px;
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
                <p>Real-time room occupancy analysis & multi-hour consecutive hall allocation</p>
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
            <div class="controls-top">
                <div style="display: flex; gap: 14px; align-items: center; flex-wrap: wrap;">
                    <div>
                        <span style="color:#94a3b8; font-size:12px; display:block;">Active Day:</span>
                        <strong style="color: #60a5fa; font-size: 15px;">{{ active_day }}</strong>
                    </div>
                    <div>
                        <span style="color:#94a3b8; font-size:12px; display:block;">Target Period / Slot:</span>
                        <strong style="color: #38bdf8; font-size: 15px;">{{ active_slot_display }}</strong>
                    </div>
                    <div class="status-pill">{{ slot_status_msg }}</div>
                </div>
                <div>
                    <button class="preset-btn" onclick="applyPreset('Monday', '08:30', '11:30')">⚡ 8:30 - 11:30 AM (3 Hours Free)</button>
                    <button class="preset-btn" onclick="applyPreset('Monday', '13:30', '16:30')">⚡ 1:30 - 4:30 PM (3 Hours Free)</button>
                    <button class="preset-btn" style="color: #34d399; border-color: rgba(52,211,153,0.4);" onclick="resetRealtime()">🕒 Real-Time</button>
                </div>
            </div>
            
            <div class="controls-form">
                <label style="font-size: 12px; color: #94a3b8;">Day:</label>
                <select id="day-select">
                    {% for d in all_days %}
                    <option value="{{ d }}" {% if d == active_day %}selected{% endif %}>{{ d }}</option>
                    {% endfor %}
                </select>
                
                <label style="font-size: 12px; color: #94a3b8;">Start Slot:</label>
                <select id="start-select">
                    {% for s in all_slots %}
                    <option value="{{ s }}" {% if s == active_start %}selected{% endif %}>{{ s }}</option>
                    {% endfor %}
                </select>
                
                <label style="font-size: 12px; color: #94a3b8;">End Time:</label>
                <select id="end-select">
                    {% for e in all_ends %}
                    <option value="{{ e }}" {% if e == active_end %}selected{% endif %}>{{ e }}</option>
                    {% endfor %}
                </select>
                
                <label style="font-size: 12px; color: #94a3b8;">Building:</label>
                <select id="bldg-select">
                    <option value="All">All Buildings</option>
                    <option value="Block A">Block A</option>
                    <option value="Block B">Block B</option>
                    <option value="Block F">Block F</option>
                    <option value="Block G">Block G</option>
                    <option value="Special Labs">Special Labs</option>
                </select>
                
                <button class="preset-btn" style="background:#3b82f6; color:#fff; border:none; padding:8px 16px;" onclick="applyControls()">Apply Schedule</button>
            </div>
        </div>

        <!-- KPI Cards -->
        <div class="grid-kpi">
            <div class="card-kpi">
                <div class="kpi-title">Master Rooms</div>
                <div class="kpi-num" style="color: #93c5fd;">{{ total_rooms }}</div>
                <div style="font-size: 11px; color: #64748b;">Total Recognized Halls</div>
            </div>
            <div class="card-kpi" style="border-color: rgba(16, 185, 129, 0.4);">
                <div class="kpi-title" style="color: #34d399;">
                    {% if is_period %}{{ period_data.consecutive_hours_count }}-Hour Free Halls{% else %}Available Halls{% endif %}
                </div>
                <div class="kpi-num" style="color: #34d399;" id="kpi-free">{{ free_rooms|length }}</div>
                <div style="font-size: 11px; color: #10b981;">
                    {% if is_period %}Uninterrupted for {{ period_data.duration_hours }} hours{% else %}Vacant for current slot{% endif %}
                </div>
            </div>
            <div class="card-kpi" style="border-color: {% if is_period %}rgba(245, 158, 11, 0.4){% else %}rgba(239, 68, 68, 0.3){% endif %};">
                <div class="kpi-title" style="color: {% if is_period %}#fbbf24{% else %}#f87171{% endif %};">
                    {% if is_period %}Partially Occupied{% else %}Occupied Halls{% endif %}
                </div>
                <div class="kpi-num" style="color: {% if is_period %}#fbbf24{% else %}#f87171{% endif %};" id="kpi-occ">
                    {% if is_period %}{{ period_data.partially_occupied_rooms|length }}{% else %}{{ occupied_rooms|length }}{% endif %}
                </div>
                <div style="font-size: 11px; color: #94a3b8;">
                    {% if is_period %}Free for part of the period{% else %}Classes in progress{% endif %}
                </div>
            </div>
            <div class="card-kpi">
                <div class="kpi-title">Period Utilization</div>
                <div class="kpi-num" style="color: #c084fc;">{{ occupancy_pct }}%</div>
                <div style="font-size: 11px; color: #64748b;">Halls Booked in Range</div>
            </div>
        </div>

        <!-- Tabs -->
        <div class="tabs">
            <button class="tab-btn active" onclick="switchTab('tab-free')">
                🟢 {% if is_period %}All {{ period_data.consecutive_hours_count }} Hours Free{% else %}Free Halls{% endif %} (<span id="tab-free-count">{{ free_rooms|length }}</span>)
            </button>
            {% if is_period %}
            <button class="tab-btn" onclick="switchTab('tab-partial')">
                🟡 Partially Free ({{ period_data.partially_occupied_rooms|length }})
            </button>
            <button class="tab-btn" onclick="switchTab('tab-occ')">
                🔴 Occupied in Range ({{ period_data.all_occupied_rooms|length }})
            </button>
            <button class="tab-btn" onclick="switchTab('tab-matrix')">
                📊 Consecutive Slots Breakdown ({{ period_data.slots|length }})
            </button>
            {% else %}
            <button class="tab-btn" onclick="switchTab('tab-occ')">
                🔴 Occupied Halls ({{ occupied_rooms|length }})
            </button>
            <button class="tab-btn" onclick="switchTab('tab-matrix')">
                📊 Full Day Matrix
            </button>
            {% endif %}
        </div>

        <!-- Tab 1: Free Rooms -->
        <div id="tab-free" class="tab-content active">
            <div class="room-grid" id="free-rooms-container">
                {% for room in free_rooms %}
                <div class="room-card" data-building="{{ get_bldg(room) }}">
                    <div class="room-header">
                        <span class="room-name">🚪 {{ room }}</span>
                        {% if is_period %}
                        <span class="badge-block">{{ period_data.consecutive_hours_count }} HRS FREE</span>
                        {% else %}
                        <span class="badge-free">VACANT</span>
                        {% endif %}
                    </div>
                    <div class="room-building">📍 {{ get_bldg(room) }}</div>
                    <div style="margin-top: 10px; font-size: 11px; color: #64748b;">
                        {% if is_period %}Continuous free block: {{ active_slot_display }}{% else %}Free for slot {{ active_slot_display }}{% endif %}
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>

        {% if is_period %}
        <!-- Tab 2: Partially Occupied Rooms -->
        <div id="tab-partial" class="tab-content">
            <div id="partial-rooms-container">
                {% if period_data.partially_occupied_rooms %}
                    {% for p in period_data.partially_occupied_rooms %}
                    <div class="partial-card" data-building="{{ get_bldg(p.room) }}">
                        <div class="room-header">
                            <span style="font-size: 18px; font-weight: 700; color: #fde68a;">🚪 {{ p.room }} ({{ get_bldg(p.room) }})</span>
                            <span class="badge-partial">PARTIALLY FREE</span>
                        </div>
                        <div style="margin-top: 6px; font-size: 12px;">
                            <span style="color: #34d399; font-weight:600;">✅ Free at:</span> {{ p.free_slots|join(', ') }} &nbsp;|&nbsp;
                            <span style="color: #f87171; font-weight:600;">❌ Booked at:</span> {{ p.occupied_slots|join(', ') }}
                        </div>
                        {% for b in p.bookings %}
                        <div class="booking-row" style="border-left-color: #fbbf24;">
                            <strong>Slot {{ b.slot }}:</strong> 📖 {{ b.subject }} | 👨‍🏫 {{ b.lecturer }} ({{ b.group }})
                        </div>
                        {% endfor %}
                    </div>
                    {% endfor %}
                {% else %}
                    <div style="padding: 20px; background: rgba(59,130,246,0.1); border-radius: 12px; color: #38bdf8; text-align: center;">
                        No halls have partial occupancy during this time block.
                    </div>
                {% endif %}
            </div>
        </div>
        {% endif %}

        <!-- Tab: Occupied Rooms -->
        <div id="tab-occ" class="tab-content">
            <div id="occ-rooms-container">
                {% if occupied_rooms %}
                    {% for room in occupied_rooms %}
                    <div class="occ-card" data-building="{{ get_bldg(room) }}">
                        <div class="room-header">
                            <span style="font-size: 18px; font-weight: 700; color: #fca5a5;">🚪 {{ room }} ({{ get_bldg(room) }})</span>
                            <span class="badge-occ">OCCUPIED</span>
                        </div>
                        {% for b in occupied_details.get(room, []) %}
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
                        🎉 All lecture halls are currently free during this time period!
                    </div>
                {% endif %}
            </div>
        </div>

        <!-- Tab: Matrix / Breakdown -->
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
            SLIIT Timetable Real-Time Engine • Time & Slot Controls with 3-Hour Block Allocation • Ready for Vercel & Streamlit Cloud
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

        function applyControls() {
            const day = document.getElementById('day-select').value;
            const start = document.getElementById('start-select').value;
            const end = document.getElementById('end-select').value;
            window.location.href = `/?day=${encodeURIComponent(day)}&start=${encodeURIComponent(start)}&end=${encodeURIComponent(end)}`;
        }

        function applyPreset(day, start, end) {
            window.location.href = `/?day=${encodeURIComponent(day)}&start=${encodeURIComponent(start)}&end=${encodeURIComponent(end)}`;
        }

        function resetRealtime() {
            window.location.href = `/`;
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
    matched_slot, auto_msg = parser.match_time_to_slot(now_dt.time())
    all_ends = parser.get_all_end_times()
    
    req_day = request.args.get("day")
    req_start = request.args.get("start")
    req_end = request.args.get("end")
    req_slot = request.args.get("slot")
    
    active_day = req_day if req_day in parser.all_days else (current_day if current_day in parser.all_days else parser.all_days[0])
    
    # Check if multi-hour period requested
    if req_start and req_end:
        is_period = True
        active_start = req_start
        active_end = req_end
        period_data = parser.get_time_period_status(active_day, active_start, active_end)
        active_slot_display = f"{active_start} – {active_end} ({period_data['consecutive_hours_count']} Hours)"
        slot_status_msg = f"Allocated: {period_data['consecutive_hours_count']} Consecutive Hours ({', '.join(period_data['slots'])})"
        
        free_rooms = period_data["fully_free_rooms"]
        occupied_rooms = period_data["all_occupied_rooms"]
        occupancy_pct = period_data["occupancy_pct"]
        
        # Details across slots in period
        occupied_details = {}
        for s in period_data["slots"]:
            s_det = parser.occupied_details.get(active_day, {}).get(s, [])
            for item in s_det:
                r = item.get("room")
                if r:
                    if r not in occupied_details:
                        occupied_details[r] = []
                    occupied_details[r].append({**item, "slot": s})
                    
        # Matrix data for the slots in the period
        matrix_data = []
        for s in period_data["slots"]:
            s_data = period_data["slot_breakdown"][s]
            matrix_data.append({
                "slot": s,
                "free_count": len(s_data["free_rooms"]),
                "occ_count": len(s_data["occupied_rooms"]),
                "pct": s_data["occupancy_pct"],
                "occ_rooms": ", ".join(s_data["occupied_rooms"]) if s_data["occupied_rooms"] else "None (All Free)"
            })
    else:
        is_period = False
        active_start = req_slot if req_slot in parser.all_slots else matched_slot
        active_end = parser.get_slot_end_time(active_start)
        active_slot_display = active_start
        slot_status_msg = auto_msg if not req_slot else f"Selected Single Slot: {active_start}"
        
        room_status = parser.get_room_status(active_day, active_start)
        free_rooms = room_status["free_rooms"]
        occupied_rooms = room_status["occupied_rooms"]
        occupancy_pct = room_status["occupancy_pct"]
        occupied_details = room_status["occupied_details"]
        period_data = None
        
        matrix_data = []
        for s in parser.all_slots:
            s_data = parser.get_room_status(active_day, s)
            matrix_data.append({
                "slot": s,
                "free_count": len(s_data["free_rooms"]),
                "occ_count": len(s_data["occupied_rooms"]),
                "pct": s_data["occupancy_pct"],
                "occ_rooms": ", ".join(s_data["occupied_rooms"]) if s_data["occupied_rooms"] else "None (All Free)"
            })

    return render_template_string(
        HTML_TEMPLATE,
        current_day=current_day,
        active_day=active_day,
        active_start=active_start,
        active_end=active_end,
        active_slot_display=active_slot_display,
        slot_status_msg=slot_status_msg,
        all_days=parser.all_days,
        all_slots=parser.all_slots,
        all_ends=all_ends,
        total_rooms=len(parser.master_rooms),
        free_rooms=free_rooms,
        occupied_rooms=occupied_rooms,
        occupied_details=occupied_details,
        occupancy_pct=occupancy_pct,
        is_period=is_period,
        period_data=period_data,
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
    start = request.args.get("start")
    end = request.args.get("end")
    
    if start and end:
        res = parser.get_time_period_status(day, start, end)
        return jsonify({
            "mode": "time_period",
            "system_time": now_dt.strftime("%Y-%m-%d %H:%M:%S"),
            "day": day,
            "start_slot": start,
            "end_time": end,
            "duration_hours": res["duration_hours"],
            "slots": res["slots"],
            "total_rooms": res["total_rooms"],
            "fully_free_rooms": res["fully_free_rooms"],
            "partially_occupied_rooms": res["partially_occupied_rooms"],
            "all_occupied_rooms": res["all_occupied_rooms"],
            "occupancy_pct": res["occupancy_pct"]
        })
    else:
        slot = request.args.get("slot", matched_slot)
        status = parser.get_room_status(day, slot)
        return jsonify({
            "mode": "single_slot",
            "system_time": now_dt.strftime("%Y-%m-%d %H:%M:%S"),
            "current_day": current_day,
            "matched_slot": matched_slot,
            "status_message": msg,
            "active_day": day,
            "active_slot": slot,
            "total_rooms": status["total_rooms"],
            "free_rooms": status["free_rooms"],
            "occupied_rooms": status["occupied_rooms"],
            "occupancy_pct": status["occupancy_pct"]
        })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
