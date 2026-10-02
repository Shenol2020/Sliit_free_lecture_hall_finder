import os
import datetime
from datetime import datetime as dt, time as dtime
import streamlit as st
from timetable_parser import TimetableParser, DEFAULT_HTML_NAME

# Page configuration
st.set_page_config(
    page_title="SLIIT Empty Lecture Hall Finder",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');
    
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

# Sidebar controls
st.sidebar.markdown("### ⚙️ Time & Slot Controls")
is_manual = st.sidebar.toggle("Override Day / Slot (Test Mode)", value=False, help="Disable real-time clock and manually pick any day and time slot to preview.")

if not is_manual:
    # Automatic Real-time mode (Requirement: zero user input needed)
    active_day = current_day_name if current_day_name in parser.all_days else parser.all_days[0]
    active_slot = matched_slot
    is_weekend_or_off = current_day_name not in parser.all_days
else:
    active_day = st.sidebar.selectbox("Select Day of Week:", parser.all_days, index=parser.all_days.index(current_day_name) if current_day_name in parser.all_days else 0)
    slot_idx = parser.all_slots.index(matched_slot) if matched_slot in parser.all_slots else 0
    active_slot = st.sidebar.selectbox("Select Time Slot:", parser.all_slots, index=slot_idx)
    is_weekend_or_off = False
    slot_status_msg = "Manual Test Selection"

# Sidebar building filter
st.sidebar.markdown("---")
st.sidebar.markdown("### 🏢 Building / Wing Filter")
categories = ["All Buildings", "Block A", "Block B", "Block F", "Block G", "Special Labs", "Engineering (Block E)"]
selected_category = st.sidebar.radio("Filter Rooms by:", categories, index=0)

# Sidebar metadata
st.sidebar.markdown("---")
st.sidebar.markdown(f"**Loaded File:**  \n`{os.path.basename(parser.file_path)}`")
st.sidebar.markdown(f"**Total Master Rooms:** `{len(parser.master_rooms)}`")
st.sidebar.markdown(f"**Scheduled Groups:** `{len(parser.groups)}`")
st.sidebar.caption("ScheduleMate Timetable Engine © 2026")

# Fetch room status for active day and slot
room_status = parser.get_room_status(active_day, active_slot)
free_rooms = room_status["free_rooms"]
occupied_rooms = room_status["occupied_rooms"]
occupied_details = room_status["occupied_details"]

# Filter free rooms if building selected
if selected_category != "All Buildings":
    filtered_free_rooms = [r for r in free_rooms if get_room_category(r) == selected_category]
    filtered_occupied_rooms = [r for r in occupied_rooms if get_room_category(r) == selected_category]
else:
    filtered_free_rooms = free_rooms
    filtered_occupied_rooms = occupied_rooms

# Main Header
st.markdown(f"""
<div class="hero-container">
    <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 12px;">
        <div>
            <div class="hero-title">
                <span>🏛️</span> SLIIT University Lecture Hall Tracker
            </div>
            <p class="hero-subtitle">Real-time room occupancy analysis based on official university timetable</p>
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
            <span style="color: #94a3b8; font-size: 13px;">📅 Active Day:</span> 
            <strong style="color: #60a5fa; font-size: 15px; margin-left: 4px;">{active_day}</strong>
        </div>
        <div>
            <span style="color: #94a3b8; font-size: 13px;">⏰ Matched Slot:</span> 
            <strong style="color: #38bdf8; font-size: 15px; margin-left: 4px;">{active_slot}</strong>
        </div>
        <div>
            <span class="slot-pill">{slot_status_msg}</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

if is_weekend_or_off and not is_manual:
    st.info(f"💡 **Notice:** Today is **{current_day_name}**, which is outside the Monday–Friday timetable schedule. Showing preview for **{active_day}** at slot **{active_slot}**. Use the sidebar toggle to explore other slots.")

# KPI Metrics Bar
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Master Rooms Count</div>
        <div class="metric-value" style="color: #93c5fd;">{room_status['total_rooms']}</div>
        <div style="font-size: 11px; color: #64748b;">All Recognized Halls</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card" style="border-color: rgba(16, 185, 129, 0.4);">
        <div class="metric-label" style="color: #34d399;">Available / Empty Halls</div>
        <div class="metric-value" style="color: #34d399;">{len(free_rooms)}</div>
        <div style="font-size: 11px; color: #10b981;">Ready for study / sessions</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card" style="border-color: rgba(239, 68, 68, 0.3);">
        <div class="metric-label" style="color: #f87171;">Occupied Halls</div>
        <div class="metric-value" style="color: #f87171;">{len(occupied_rooms)}</div>
        <div style="font-size: 11px; color: #ef4444;">Classes in progress</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Hall Utilization</div>
        <div class="metric-value" style="color: #c084fc;">{room_status['occupancy_pct']}%</div>
        <div style="font-size: 11px; color: #64748b;">Slot Occupancy Rate</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

# Main Content Tabs
tab_available, tab_occupied, tab_matrix, tab_room_search = st.tabs([
    f"🟢 Available Empty Halls ({len(filtered_free_rooms)})",
    f"🔴 Occupied Halls ({len(filtered_occupied_rooms)})",
    "📅 Full Day Matrix",
    "🔍 Room Schedule Search"
])

# TAB 1: Empty Lecture Halls
with tab_available:
    st.markdown(f"#### 🟢 Currently Free Lecture Halls — {active_day} @ {active_slot}")
    st.caption(f"Showing **{len(filtered_free_rooms)}** empty halls (Master Room List minus Occupied Rooms for {active_slot}).")
    
    if filtered_free_rooms:
        # Display in responsive grid (4 columns)
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

# TAB 2: Occupied Halls
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
                
                # Show booking details
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

# TAB 3: Full Day Matrix
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
    
    st.dataframe(matrix_data, use_container_width=True, hide_index=True)

# TAB 4: Room Schedule Search
with tab_room_search:
    st.markdown("#### 🔍 Search a Specific Room's Weekly Schedule")
    selected_room = st.selectbox("Select a Room to Inspect:", sorted(list(parser.master_rooms)))
    
    st.markdown(f"##### Weekly Schedule for Room: `{selected_room}` ({get_room_category(selected_room)})")
    
    room_week_data = []
    for day in parser.all_days:
        for slot in parser.all_slots:
            occ_set = parser.occupied_schedule.get(day, {}).get(slot, set())
            if selected_room in occ_set:
                # Find details
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
    
    st.dataframe(room_week_data, use_container_width=True, hide_index=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; font-size: 12px; padding: 10px;">
    SLIIT Timetable Real-Time Lecture Hall Engine • Streamlit & BeautifulSoup4 • Automatic Slot & Rowspan Detection
</div>
""", unsafe_allow_html=True)
