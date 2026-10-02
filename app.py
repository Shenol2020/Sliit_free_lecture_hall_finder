import os
import datetime
from datetime import datetime as dt, time as dtime
import streamlit as st
from timetable_parser import TimetableParser, DEFAULT_HTML_NAME

# Page configuration
st.set_page_config(
    page_title="SLIIT University Lecture Hall Tracker",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    .stApp {
        background: radial-gradient(circle at 10% 10%, #0f172a 0%, #090d16 100%);
        color: #f1f5f9;
    }
    
    /* Header Banner */
    .hero-container {
        background: linear-gradient(135deg, rgba(30, 58, 138, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%);
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 20px;
        padding: 24px 32px;
        margin-bottom: 24px;
        backdrop-filter: blur(12px);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
    }
    
    .hero-title {
        font-size: 28px;
        font-weight: 800;
        background: linear-gradient(90deg, #60a5fa, #38bdf8, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0 0 6px 0;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .hero-subtitle {
        color: #94a3b8;
        font-size: 14px;
        margin: 0;
    }
    
    /* Live clock badge */
    .live-clock-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(16, 185, 129, 0.15);
        border: 1px solid rgba(16, 185, 129, 0.4);
        color: #34d399;
        padding: 6px 14px;
        border-radius: 9999px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 13px;
        font-weight: 600;
    }
    
    .pulsing-dot {
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
    
    /* KPI Metric Cards */
    .metric-card {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(148, 163, 184, 0.15);
        border-radius: 16px;
        padding: 18px 20px;
        text-align: center;
        backdrop-filter: blur(8px);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: rgba(96, 165, 250, 0.4);
    }
    .metric-value {
        font-size: 32px;
        font-weight: 800;
        margin: 4px 0;
        font-family: 'JetBrains Mono', monospace;
    }
    .metric-label {
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        color: #94a3b8;
    }
    
    /* Room Cards */
    .room-card {
        background: linear-gradient(145deg, rgba(16, 185, 129, 0.08) 0%, rgba(30, 41, 59, 0.5) 100%);
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 12px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 110px;
        transition: all 0.2s ease;
    }
    .room-card:hover {
        border-color: #34d399;
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.2);
        transform: translateY(-2px);
    }
    .room-name {
        font-size: 20px;
        font-weight: 700;
        color: #f8fafc;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .room-tag-free {
        background: rgba(16, 185, 129, 0.2);
        color: #34d399;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    .room-tag-block {
        background: rgba(14, 165, 233, 0.2);
        color: #38bdf8;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    .room-building {
        font-size: 12px;
        color: #94a3b8;
        margin-top: 4px;
    }
    
    /* Occupied Room Cards */
    .room-card-occupied {
        background: linear-gradient(145deg, rgba(239, 68, 68, 0.08) 0%, rgba(30, 41, 59, 0.5) 100%);
        border: 1px solid rgba(239, 68, 68, 0.3);
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 12px;
        transition: all 0.2s ease;
    }
    .room-card-occupied:hover {
        border-color: #f87171;
        box-shadow: 0 6px 20px rgba(239, 68, 68, 0.2);
    }
    .room-tag-occ {
        background: rgba(239, 68, 68, 0.2);
        color: #f87171;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    
    /* Partial Occupancy Card */
    .room-card-partial {
        background: linear-gradient(145deg, rgba(245, 158, 11, 0.08) 0%, rgba(30, 41, 59, 0.5) 100%);
        border: 1px solid rgba(245, 158, 11, 0.35);
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 12px;
        transition: all 0.2s ease;
    }
    .room-card-partial:hover {
        border-color: #fbbf24;
        box-shadow: 0 6px 20px rgba(245, 158, 11, 0.2);
    }
    .room-tag-partial {
        background: rgba(245, 158, 11, 0.2);
        color: #fbbf24;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    
    /* Slot pill */
    .slot-pill {
        background: rgba(59, 130, 246, 0.15);
        border: 1px solid rgba(59, 130, 246, 0.35);
        color: #60a5fa;
        padding: 4px 10px;
        border-radius: 8px;
        font-size: 12px;
        font-weight: 600;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to categorize room to building
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

@st.cache_resource(show_spinner="Parsing timetable HTML file...")
def load_timetable_data():
    app_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(app_dir, DEFAULT_HTML_NAME)
    if not os.path.exists(file_path):
        file_path = os.path.join(os.getcwd(), DEFAULT_HTML_NAME)
    
    parser = TimetableParser(file_path)
    return parser

try:
    parser = load_timetable_data()
except Exception as e:
    st.error(f"❌ Error loading timetable file: {str(e)}")
    st.stop()

# Real-time System Clock
now_dt = dt.now()
current_day_name = now_dt.strftime("%A")
current_time_str = now_dt.strftime("%I:%M:%S %p")
system_time_val = now_dt.time()

# Determine initial slot automatically on load
matched_slot, slot_status_msg = parser.match_time_to_slot(system_time_val)

# Sidebar: Time and Slot Controls
st.sidebar.markdown("## ⚙️ Time and Slot Controls")
st.sidebar.caption("Override the standard daily schedule or allocate multi-hour blocks of free hall time.")

# Control Mode Selection
control_mode = st.sidebar.radio(
    "Schedule Control Mode:",
    [
        "🕒 Real-Time Clock (Live)",
        "⏳ Custom Time Period (e.g. 8:30 - 11:30)",
        "🎯 Single Slot Explorer"
    ],
    index=0,
    help="Select 'Custom Time Period' to allocate consecutive hours of free hall time (e.g. 8:30 AM to 11:30 AM)."
)

# Building Filter in Sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### 🏢 Building / Wing Filter")
categories = ["All Buildings", "Block A", "Block B", "Block F", "Block G", "Special Labs", "Engineering (Block E)"]
selected_category = st.sidebar.selectbox("Filter Rooms by:", categories, index=0)

is_period_mode = (control_mode == "⏳ Custom Time Period (e.g. 8:30 - 11:30)")
is_single_slot = (control_mode == "🎯 Single Slot Explorer")

all_end_times = parser.get_all_end_times()

if is_period_mode:
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⏱️ Time Period Settings")
    
    default_day_idx = parser.all_days.index(current_day_name) if current_day_name in parser.all_days else 0
    active_day = st.sidebar.selectbox("Select Day of Week:", parser.all_days, index=default_day_idx, key="period_day")
    
    # Preset period quick selection
    period_preset = st.sidebar.selectbox(
        "Quick Presets:",
        [
            "8:30 AM – 11:30 AM (3 Consecutive Hours)",
            "1:30 PM – 4:30 PM (3 Consecutive Hours)",
            "8:30 AM – 10:30 AM (2 Consecutive Hours)",
            "10:30 AM – 1:30 PM (3 Consecutive Hours)",
            "Custom Time Range"
        ],
        index=0
    )
    
    if period_preset == "8:30 AM – 11:30 AM (3 Consecutive Hours)":
        start_slot = "08:30"
        end_time = "11:30"
    elif period_preset == "1:30 PM – 4:30 PM (3 Consecutive Hours)":
        start_slot = "13:30"
        end_time = "16:30"
    elif period_preset == "8:30 AM – 10:30 AM (2 Consecutive Hours)":
        start_slot = "08:30"
        end_time = "10:30"
    elif period_preset == "10:30 AM – 1:30 PM (3 Consecutive Hours)":
        start_slot = "10:30"
        end_time = "13:30"
    else:
        start_slot = st.sidebar.selectbox("Start Time Slot:", parser.all_slots, index=0, key="custom_start")
        # Filter end times after start slot
        start_mins = parser._slot_to_minutes(start_slot)
        valid_ends = [e for e in all_end_times if parser._slot_to_minutes(e) > start_m]
        end_time = st.sidebar.selectbox("End Time:", valid_ends, index=min(2, len(valid_ends)-1), key="custom_end")
        
    period_status = parser.get_time_period_status(active_day, start_slot, end_time)
    active_slot = f"{start_slot} – {end_time}"
    slot_status_msg = f"Allocated: {period_status['consecutive_hours_count']} Consecutive Hours ({len(period_status['slots'])} slots: {', '.join(period_status['slots'])})"
    is_weekend_or_off = False

elif is_single_slot:
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎯 Single Slot Selection")
    default_day_idx = parser.all_days.index(current_day_name) if current_day_name in parser.all_days else 0
    active_day = st.sidebar.selectbox("Select Day of Week:", parser.all_days, index=default_day_idx, key="single_day")
    slot_idx = parser.all_slots.index(matched_slot) if matched_slot in parser.all_slots else 0
    active_slot = st.sidebar.selectbox("Select Time Slot:", parser.all_slots, index=slot_idx, key="single_slot")
    is_weekend_or_off = False
    slot_status_msg = f"Manual Single Slot Explorer: {active_slot}"
    period_status = None
    
else:
    # Real-Time Clock Mode (Zero input required on load)
    active_day = current_day_name if current_day_name in parser.all_days else parser.all_days[0]
    active_slot = matched_slot
    is_weekend_or_off = current_day_name not in parser.all_days
    period_status = None

# Sidebar metadata
st.sidebar.markdown("---")
st.sidebar.markdown(f"**Loaded File:**  \n`{os.path.basename(parser.file_path)}`")
st.sidebar.markdown(f"**Total Master Rooms:** `{len(parser.master_rooms)}`")
st.sidebar.markdown(f"**Timetable Slots:** `{len(parser.all_slots)}`")
st.sidebar.caption("ScheduleMate Timetable Engine © 2026")

# Calculate room availability based on mode
if is_period_mode:
    free_rooms = period_status["fully_free_rooms"]
    partially_occupied = period_status["partially_occupied_rooms"]
    fully_occupied = period_status["fully_occupied_rooms"]
    all_occupied_rooms = period_status["all_occupied_rooms"]
    
    # Building filtering
    if selected_category != "All Buildings":
        filtered_free_rooms = [r for r in free_rooms if get_room_category(r) == selected_category]
        filtered_partial = [p for p in partially_occupied if get_room_category(p["room"]) == selected_category]
        filtered_occupied_rooms = [r for r in all_occupied_rooms if get_room_category(r) == selected_category]
    else:
        filtered_free_rooms = free_rooms
        filtered_partial = partially_occupied
        filtered_occupied_rooms = all_occupied_rooms
else:
    room_status = parser.get_room_status(active_day, active_slot)
    free_rooms = room_status["free_rooms"]
    occupied_rooms = room_status["occupied_rooms"]
    occupied_details = room_status["occupied_details"]
    
    if selected_category != "All Buildings":
        filtered_free_rooms = [r for r in free_rooms if get_room_category(r) == selected_category]
        filtered_occupied_rooms = [r for r in occupied_rooms if get_room_category(r) == selected_category]
    else:
        filtered_free_rooms = free_rooms
        filtered_occupied_rooms = occupied_rooms

# Main Hero Header
st.markdown(f"""
<div class="hero-container">
    <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 12px;">
        <div>
            <div class="hero-title">
                <span>🏛️</span> SLIIT University Lecture Hall Tracker
            </div>
            <p class="hero-subtitle">Real-time room occupancy analysis & multi-hour consecutive hall allocation</p>
        </div>
        <div>
            <div class="live-clock-badge">
                <span class="pulsing-dot"></span>
                <span>SYSTEM CLOCK: {current_day_name}, {current_time_str}</span>
            </div>
        </div>
    </div>
    <div style="margin-top: 18px; padding-top: 14px; border-top: 1px solid rgba(255,255,255,0.1); display: flex; flex-wrap: wrap; gap: 20px; align-items: center;">
        <div>
            <span style="color: #94a3b8; font-size: 13px;">📅 Target Day:</span> 
            <strong style="color: #60a5fa; font-size: 15px; margin-left: 4px;">{active_day}</strong>
        </div>
        <div>
            <span style="color: #94a3b8; font-size: 13px;">⏰ Selected Time / Slot:</span> 
            <strong style="color: #38bdf8; font-size: 15px; margin-left: 4px;">{active_slot}</strong>
        </div>
        <div>
            <span class="slot-pill">{slot_status_msg}</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

if is_weekend_or_off and control_mode == "🕒 Real-Time Clock (Live)":
    st.info(f"💡 **Notice:** Today is **{current_day_name}**, which is outside the Monday–Friday timetable schedule. Showing preview for **{active_day}** at slot **{active_slot}**. Use the 'Time and Slot Controls' in the sidebar to allocate custom multi-hour periods.")

# KPI Metrics Bar
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Master Rooms</div>
        <div class="metric-value" style="color: #93c5fd;">{len(parser.master_rooms)}</div>
        <div style="font-size: 11px; color: #64748b;">Total Recognized Halls</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    if is_period_mode:
        free_label = f"{period_status['consecutive_hours_count']}-Hr Free Halls"
        sub_label = f"Uninterrupted for {period_status['duration_hours']} hours"
    else:
        free_label = "Available Empty Halls"
        sub_label = f"Vacant for slot {active_slot}"
    st.markdown(f"""
    <div class="metric-card" style="border-color: rgba(16, 185, 129, 0.4);">
        <div class="metric-label" style="color: #34d399;">{free_label}</div>
        <div class="metric-value" style="color: #34d399;">{len(free_rooms)}</div>
        <div style="font-size: 11px; color: #10b981;">{sub_label}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    if is_period_mode:
        occ_label = "Partially Occupied"
        occ_val = len(partially_occupied)
        occ_sub = "Free for part of the period"
        occ_color = "#fbbf24"
        occ_border = "rgba(245, 158, 11, 0.4)"
    else:
        occ_label = "Occupied Halls"
        occ_val = len(occupied_rooms)
        occ_sub = "Classes in progress"
        occ_color = "#f87171"
        occ_border = "rgba(239, 68, 68, 0.3)"
    st.markdown(f"""
    <div class="metric-card" style="border-color: {occ_border};">
        <div class="metric-label" style="color: {occ_color};">{occ_label}</div>
        <div class="metric-value" style="color: {occ_color};">{occ_val}</div>
        <div style="font-size: 11px; color: #94a3b8;">{occ_sub}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    pct_val = period_status["occupancy_pct"] if is_period_mode else room_status["occupancy_pct"]
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Period Utilization</div>
        <div class="metric-value" style="color: #c084fc;">{pct_val}%</div>
        <div style="font-size: 11px; color: #64748b;">Halls Booked in Range</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

# Main Content Rendering based on mode
if is_period_mode:
    # PERIOD MODE TABS
    tab_block_free, tab_block_partial, tab_block_occ, tab_block_matrix = st.tabs([
        f"🟢 Continuously Free for All {period_status['consecutive_hours_count']} Hours ({len(filtered_free_rooms)})",
        f"🟡 Partially Free ({len(filtered_partial)})",
        f"🔴 Occupied in Period ({len(filtered_occupied_rooms)})",
        f"📊 Hour-by-Hour Breakdown ({len(period_status['slots'])} Slots)"
    ])
    
    with tab_block_free:
        st.markdown(f"#### 🟢 Uninterrupted Free Lecture Halls: {active_day} ({start_slot} – {end_time})")
        st.caption(f"The system has allocated **{len(filtered_free_rooms)} lecture halls** that are completely vacant for the entire **{period_status['consecutive_hours_count']} consecutive hours** (Slots: {', '.join(period_status['slots'])}).")
        
        if filtered_free_rooms:
            grid_cols = st.columns(4)
            for idx, room in enumerate(filtered_free_rooms):
                b_cat = get_room_category(room)
                with grid_cols[idx % 4]:
                    st.markdown(f"""
                    <div class="room-card">
                        <div>
                            <div class="room-name">
                                <span>🚪</span> {room}
                            </div>
                            <div class="room-building">📍 {b_cat}</div>
                        </div>
                        <div style="margin-top: 10px; display: flex; justify-content: space-between; align-items: center;">
                            <span class="room-tag-block">{period_status['consecutive_hours_count']} HRS FREE</span>
                            <span style="font-size: 11px; color: #64748b;">{start_slot} – {end_time}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("⚠️ No lecture halls are continuously free for this entire multi-hour period.")
            
    with tab_block_partial:
        st.markdown(f"#### 🟡 Partially Occupied Halls: {active_day} ({start_slot} – {end_time})")
        st.caption(f"These halls are free for part of the period, but have scheduled sessions during some slots.")
        
        if filtered_partial:
            for p in filtered_partial:
                room = p["room"]
                b_cat = get_room_category(room)
                free_slots_str = ", ".join(p["free_slots"])
                occ_slots_str = ", ".join(p["occupied_slots"])
                
                with st.container():
                    st.markdown(f"""
                    <div class="room-card-partial">
                        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                            <div style="font-size: 18px; font-weight: 700; color: #fde68a;">
                                🚪 {room} <span style="font-size: 12px; font-weight: normal; color: #94a3b8; margin-left: 8px;">({b_cat})</span>
                            </div>
                            <span class="room-tag-partial">PARTIALLY FREE</span>
                        </div>
                        <div style="margin-top: 8px; font-size: 12px;">
                            <span style="color: #34d399; font-weight: 600;">✅ Free at:</span> {free_slots_str} &nbsp;|&nbsp; 
                            <span style="color: #f87171; font-weight: 600;">❌ Booked at:</span> {occ_slots_str}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    for b in p["bookings"]:
                        st.markdown(f"""
                        <div style="background: rgba(15, 23, 42, 0.4); border-left: 3px solid #fbbf24; padding: 6px 12px; margin-left: 12px; margin-bottom: 6px; border-radius: 4px; font-size: 12px;">
                            <strong>Slot {b.get('slot')}:</strong> {b.get('subject')} ({b.get('lecturer')}) — <em>{b.get('group')}</em>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.info("No rooms have partial overlap during this time block.")
            
    with tab_block_occ:
        st.markdown(f"#### 🔴 Halls with Scheduled Classes during {active_day} ({start_slot} – {end_time})")
        if filtered_occupied_rooms:
            for room in filtered_occupied_rooms:
                b_cat = get_room_category(room)
                # Find all bookings for this room across the period
                all_b = []
                for s in period_status["slots"]:
                    for d in period_status["slot_breakdown"][s]["occupied_details"].get(room, []):
                        all_b.append({**d, "slot": s})
                        
                with st.container():
                    st.markdown(f"""
                    <div class="room-card-occupied">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div style="font-size: 18px; font-weight: 700; color: #fca5a5;">
                                🚪 {room} <span style="font-size: 12px; color: #94a3b8; font-weight: normal;">({b_cat})</span>
                            </div>
                            <span class="room-tag-occ">BUSY IN RANGE</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    for b in all_b:
                        span_txt = "⏳ Continuing from earlier slot (Rowspan)" if b.get("is_span") else "⏱️ Started this slot"
                        st.markdown(f"""
                        <div style="background: rgba(15, 23, 42, 0.4); border-left: 3px solid #ef4444; padding: 6px 12px; margin-left: 12px; margin-bottom: 6px; border-radius: 4px; font-size: 12px;">
                            <strong>Slot {b.get('slot')}:</strong> 📖 {b.get('subject')} | 👨‍🏫 {b.get('lecturer')} | 👥 {b.get('group')}
                            <div style="color: #38bdf8; font-size: 11px;">{span_txt}</div>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.success("🎉 All lecture halls are completely vacant during this time period!")
            
    with tab_block_matrix:
        st.markdown(f"#### 📊 Slot-by-Slot Comparison for {active_day} ({start_slot} – {end_time})")
        period_matrix = []
        for s in period_status["slots"]:
            s_data = period_status["slot_breakdown"][s]
            period_matrix.append({
                "Slot": s,
                "Free Halls Count": len(s_data["free_rooms"]),
                "Occupied Halls Count": len(s_data["occupied_rooms"]),
                "Utilization": f"{s_data['occupancy_pct']}%",
                "Occupied Halls": ", ".join(s_data["occupied_rooms"]) if s_data["occupied_rooms"] else "None (All Free)"
            })
        st.dataframe(period_matrix, width="stretch", hide_index=True)

else:
    # STANDARD SINGLE SLOT / REAL-TIME TABS
    tab_available, tab_occupied, tab_matrix, tab_room_search = st.tabs([
        f"🟢 Available Empty Halls ({len(filtered_free_rooms)})",
        f"🔴 Occupied Halls ({len(filtered_occupied_rooms)})",
        "📅 Full Day Matrix",
        "🔍 Room Schedule Search"
    ])

    with tab_available:
        st.markdown(f"#### 🟢 Currently Free Lecture Halls — {active_day} @ {active_slot}")
        st.caption(f"Showing **{len(filtered_free_rooms)}** empty halls (Master Room List minus Occupied Rooms for {active_slot}).")
        
        if filtered_free_rooms:
            grid_cols = st.columns(4)
            for idx, room in enumerate(filtered_free_rooms):
                b_cat = get_room_category(room)
                with grid_cols[idx % 4]:
                    st.markdown(f"""
                    <div class="room-card">
                        <div>
                            <div class="room-name">
                                <span>🚪</span> {room}
                            </div>
                            <div class="room-building">📍 {b_cat}</div>
                        </div>
                        <div style="margin-top: 10px; display: flex; justify-content: space-between; align-items: center;">
                            <span class="room-tag-free">VACANT</span>
                            <span style="font-size: 11px; color: #64748b;">Slot {active_slot}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("⚠️ No empty halls available in the selected category for this slot.")

    with tab_occupied:
        st.markdown(f"#### 🔴 Occupied Halls & Ongoing Activities — {active_day} @ {active_slot}")
        st.caption("Includes rooms with active `rowspan` carry-over from preceding hours.")
        
        if filtered_occupied_rooms:
            for room in filtered_occupied_rooms:
                bookings = occupied_details.get(room, [])
                b_cat = get_room_category(room)
                
                with st.container():
                    st.markdown(f"""
                    <div class="room-card-occupied">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div style="font-size: 18px; font-weight: 700; color: #fca5a5;">
                                🚪 {room} <span style="font-size: 12px; font-weight: normal; color: #94a3b8; margin-left: 8px;">({b_cat})</span>
                            </div>
                            <span class="room-tag-occ">OCCUPIED</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if bookings:
                        for b in bookings:
                            subj = b.get("subject", "Class Activity")
                            lect = b.get("lecturer", "Staff")
                            grp = b.get("group", "Student Group")
                            span_badge = "⏳ Continuing from earlier slot (Rowspan)" if b.get("is_span") else "⏱️ Started this slot"
                            
                            st.markdown(f"""
                            <div style="background: rgba(15, 23, 42, 0.4); border-left: 3px solid #ef4444; padding: 8px 14px; margin-left: 12px; margin-bottom: 8px; border-radius: 4px;">
                                <div style="font-size: 13px; font-weight: 600; color: #e2e8f0;">📖 {subj}</div>
                                <div style="font-size: 12px; color: #94a3b8;">👨‍🏫 Lecturer: {lect} | 👥 Group: {grp}</div>
                                <div style="font-size: 11px; color: #38bdf8; margin-top: 2px;">{span_badge}</div>
                            </div>
                            """, unsafe_allow_html=True)
        else:
            st.success("🎉 All lecture halls are currently free during this slot!")

    with tab_matrix:
        st.markdown(f"#### 📊 Full Day Occupancy Overview for {active_day}")
        st.caption("Summary of occupied and free rooms across all timetable slots today.")
        
        matrix_data = []
        for slot in parser.all_slots:
            st_data = parser.get_room_status(active_day, slot)
            occ = st_data["occupied_rooms"]
            free = st_data["free_rooms"]
            matrix_data.append({
                "Time Slot": slot,
                "Free Halls Count": len(free),
                "Occupied Halls Count": len(occ),
                "Utilization Rate": f"{st_data['occupancy_pct']}%",
                "Occupied Rooms": ", ".join(occ) if occ else "None (All Free)"
            })
        
        st.dataframe(matrix_data, width="stretch", hide_index=True)

    with tab_room_search:
        st.markdown("#### 🔍 Search a Specific Room's Weekly Schedule")
        selected_room = st.selectbox("Select a Room to Inspect:", sorted(list(parser.master_rooms)))
        
        st.markdown(f"##### Weekly Schedule for Room: `{selected_room}` ({get_room_category(selected_room)})")
        
        room_week_data = []
        for day in parser.all_days:
            for slot in parser.all_slots:
                occ_set = parser.occupied_schedule.get(day, {}).get(slot, set())
                if selected_room in occ_set:
                    details = parser.occupied_details.get(day, {}).get(slot, [])
                    r_details = [d for d in details if d.get("room") == selected_room]
                    desc = "Occupied"
                    if r_details:
                        desc = f"{r_details[0].get('subject', '')} ({r_details[0].get('group', '')})"
                    status_str = f"🔴 {desc}"
                else:
                    status_str = "🟢 VACANT"
                
                room_week_data.append({
                    "Day": day,
                    "Slot": slot,
                    "Status": status_str
                })
        
        st.dataframe(room_week_data, width="stretch", hide_index=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; font-size: 12px; padding: 10px;">
    SLIIT Timetable Real-Time Lecture Hall Engine • Streamlit & BeautifulSoup4 • Time and Slot Controls with Multi-Hour Block Allocation
</div>
""", unsafe_allow_html=True)
