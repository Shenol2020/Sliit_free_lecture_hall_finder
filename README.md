# 🏛️ SLIIT University Empty Lecture Hall Tracker

A real-time Python web application built using **Streamlit**, **BeautifulSoup4**, and **Flask** that parses the official local university timetable HTML file (`Y1S1-September Intake 2026 Weekend Version I.html`), detects the current day and time using the real-time system clock, and automatically displays all empty lecture halls for the active time slot.

---

## 🌟 Key Features

1. **Hardcoded Data Loading**:
   - Automatically loads and parses `Y1S1-September Intake 2026 Weekend Version I.html` in the project directory without requiring manual file uploads.
2. **HTML Parsing & Rowspan Carry-Over Logic**:
   - Dynamically parses timetable `<table>` structures (`class="odd_table"` and `class="even_table"`).
   - Extracts all days (`<th class="xAxis">`) and time slots (`<th class="yAxis">`).
   - Extracts all distinct rooms from standard cells as well as nested parallel activity tables (`table.detailed`).
   - **Rowspan Tracking**: If a class has `rowspan="2"` (e.g., from `08:30` to `10:30`), the room remains marked as occupied for subsequent slots.
3. **Instant Real-Time Slot Matching**:
   - Uses Python's `datetime.now()` to determine the current day of the week and system time.
   - Automatically maps current time to the active timetable slot (e.g., `10:25 AM` maps to the current active slot).
   - Instant calculation on page load without requiring user input.
4. **Interactive Dashboard**:
   - **Live Clock Badge**: Real-time pulsing clock showing current system time and day.
   - **KPI Metrics**: Total Recognized Halls, Empty/Available Halls, Occupied Halls, and Hall Utilization %.
   - **Building / Wing Filters**: Filter free rooms by Block A, Block B, Block F, Block G, or Special Labs.
   - **Full Day Matrix**: Comprehensive overview table of room occupancy for every slot of the day.
   - **Room Schedule Finder**: Check the entire weekly timetable for any selected room.
   - **Test & Preview Mode**: Optional toggle in the sidebar to simulate any day or time slot.

---

## 📁 Project Structure

```text
time_table_system/
├── Y1S1-September Intake 2026 Weekend Version I.html  # University timetable HTML
├── timetable_parser.py                                # Core parsing & rowspan engine
├── app.py                                             # Streamlit Web Application
├── api/
│   └── index.py                                       # Vercel serverless / Flask endpoint
├── vercel.json                                        # Vercel deployment configuration
├── requirements.txt                                   # Python dependencies
├── .gitignore                                         # Git ignore file
└── README.md                                          # Documentation & guides
```

---

## 🚀 Running Locally

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run with Streamlit
```bash
streamlit run app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

### 3. Run with Flask (Vercel Serverless Simulator)
```bash
python api/index.py
```
Open [http://localhost:5000](http://localhost:5000) in your browser.

---

## ☁️ Deployment Guides (Via GitHub)

### Option 1: Deploy on Vercel with GitHub (Simple 1-Click)
The repository includes pre-configured `vercel.json` and `api/index.py` ready for Vercel:

1. Push your repository to **GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit of timetable tracker"
   git branch -M main
   git remote add origin https://github.com/<YOUR_USERNAME>/<YOUR_REPO>.git
   git push -u origin main
   ```
2. Go to [vercel.com](https://vercel.com) and log in with your GitHub account.
3. Click **"Add New Project"** and select your GitHub repository.
4. Keep the default settings and click **"Deploy"**.
5. Vercel will automatically build the Python function in `api/index.py` and provide a live public URL!

### Option 2: Deploy on Streamlit Community Cloud (Official Free Streamlit Host)
Streamlit Cloud offers free, instant hosting with native WebSocket support:

1. Push your repository to **GitHub**.
2. Visit [share.streamlit.io](https://share.streamlit.io) and log in with GitHub.
3. Click **"New App"**.
4. Choose your repository, branch (`main`), and set **Main file path** to:
   ```text
   app.py
   ```
5. Click **"Deploy"**! Your interactive Streamlit app will be live in under 1 minute.

---

## 🏛️ Master Room Set Example

The parser dynamically recognizes all distinct lecture rooms and labs across the campus, including:
- **Block A**: `A304`, `A405`, `A412`, `A506`
- **Block B**: `B401`, `B402`, `B403`, `B501`, `B502`
- **Block F**: `F301`, `F302`, `F303`, `F304 Lab`, `F305`, `F403`, `F405`, `F406`, `F407`, `F1105 EMBEDDED`, `F1301 + F1302 Lab`, `F1305 Lab`, `F1307`, `F1308`
- **Block G**: `G606`, `G1302`, `G1303`, `G1304`, `G1305 LINUX`
- **Other Facilities**: `EA1`, `DClab`
