import os
import sys
import re
from datetime import datetime, time
from bs4 import BeautifulSoup
from collections import defaultdict

DEFAULT_HTML_NAME = "Y1S1-September Intake 2026 Weekend Version I.html"

def find_timetable_file(base_dir=None):
    if base_dir is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Check exact match
    exact_path = os.path.join(base_dir, DEFAULT_HTML_NAME)
    if os.path.exists(exact_path):
        return exact_path
        
    # Check current working directory
    cwd_path = os.path.join(os.getcwd(), DEFAULT_HTML_NAME)
    if os.path.exists(cwd_path):
        return cwd_path
        
    # Scan for any html with September or Timetable or Intake
    for root, _, files in os.walk(base_dir):
        for f in files:
            if f.endswith(".html") and ("September" in f or "Timetable" in f or "Intake" in f or "SLIIT" in f):
                return os.path.join(root, f)
                
    return exact_path

def is_valid_room(name):
    if not name:
        return False
    name_clean = name.strip()
    if not name_clean or name_clean in ("---", "-x-", "None"):
        return False
    # Avoid lecturer titles
    if name_clean.startswith(("Mr.", "Ms.", "Mrs.", "Dr.", "Prof.", "Eng.", "Rev.")):
        return False
    if "online" in name_clean.lower():
        return False
    return True

def extract_cell_info(td):
    rooms = []
    classes_info = []
    
    # 1. Nested table with class 'detailed'
    detailed_tables = td.find_all("table", class_="detailed")
    if detailed_tables:
        for d_table in detailed_tables:
            trs = d_table.find_all("tr", recursive=False)
            if len(trs) >= 4:
                subgroups = [c.get_text(strip=True) for c in trs[0].find_all("td", class_="detailed")]
                subjects = [c.get_text(separator=" ", strip=True) for c in trs[1].find_all("td", class_="detailed")]
                lecturers = [c.get_text(separator=" ", strip=True) for c in trs[2].find_all("td", class_="detailed")]
                room_tds = [c.get_text(strip=True) for c in trs[3].find_all("td", class_="detailed")]
                
                for i in range(len(room_tds)):
                    r = room_tds[i] if i < len(room_tds) else ""
                    if is_valid_room(r):
                        rooms.append(r)
                        classes_info.append({
                            "room": r,
                            "subject": subjects[i] if i < len(subjects) else "",
                            "subgroup": subgroups[i] if i < len(subgroups) else "",
                            "lecturer": lecturers[i] if i < len(lecturers) else ""
                        })
            else:
                for r_td in trs[-1].find_all("td", class_="detailed"):
                    r = r_td.get_text(strip=True)
                    if is_valid_room(r):
                        rooms.append(r)
                        classes_info.append({"room": r, "subject": "", "subgroup": "", "lecturer": ""})
        return rooms, classes_info

    # 2. Standalone cell
    text = td.get_text(separator="\n", strip=True)
    if not text or text in ("---", "-x-"):
        return [], []

    lines = [l.strip() for l in text.split("\n") if l.strip() and l.strip() not in ("---", "-x-")]
    if not lines:
        return [], []

    # If class is explicitly online and no room follows
    if any("online" in l.lower() for l in lines):
        last_line = lines[-1]
        if is_valid_room(last_line):
            rooms.append(last_line)
            classes_info.append({"room": last_line, "subject": lines[0], "lecturer": lines[1] if len(lines) > 1 else ""})
        return rooms, classes_info

    last_line = lines[-1]
    if is_valid_room(last_line):
        rooms.append(last_line)
        classes_info.append({
            "room": last_line,
            "subject": lines[1] if len(lines) > 2 else lines[0],
            "lecturer": lines[-2] if len(lines) >= 3 else "",
            "details": " | ".join(lines[:-1])
        })
    return rooms, classes_info

class TimetableParser:
    def __init__(self, file_path=None):
        self.file_path = file_path or find_timetable_file()
        self.master_rooms = set()
        self.all_days = []
        self.all_slots = []
        self.groups = []
        # occupied_schedule[day][slot] = set of rooms
        self.occupied_schedule = defaultdict(lambda: defaultdict(set))
        # occupied_details[day][slot] = list of class dicts
        self.occupied_details = defaultdict(lambda: defaultdict(list))
        self.parse()

    def parse(self):
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Timetable file not found at: {self.file_path}")

        with open(self.file_path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")

        tables = soup.find_all("table", class_=lambda c: c and ("odd_table" in c or "even_table" in c))
        
        for t_idx, table in enumerate(tables):
            caption = table.find("caption")
            group_name = caption.get_text(separator=" ", strip=True) if caption else f"Group_{t_idx}"
            if group_name not in self.groups:
                self.groups.append(group_name)

            thead = table.find("thead")
            if not thead:
                continue
            days = [th.get_text(strip=True) for th in thead.find_all("th", class_="xAxis")]
            for d in days:
                if d not in self.all_days:
                    self.all_days.append(d)

            tbody = table.find("tbody")
            if not tbody:
                continue

            num_days = len(days)
            active_spans = {}  # col_idx -> {'remaining': count, 'rooms': list, 'classes': list}

            for tr in tbody.find_all("tr", recursive=False):
                th = tr.find("th", class_="yAxis")
                if not th:
                    continue
                slot = th.get_text(strip=True)
                if slot not in self.all_slots:
                    self.all_slots.append(slot)

                tds = tr.find_all("td", recursive=False)
                td_ptr = 0
                col = 0

                while col < num_days:
                    day = days[col]

                    if col in active_spans and active_spans[col]['remaining'] > 0:
                        # Carry-over from previous rowspan
                        span_data = active_spans[col]
                        for r in span_data['rooms']:
                            self.occupied_schedule[day][slot].add(r)
                        for ci in span_data['classes']:
                            self.occupied_details[day][slot].append({**ci, "group": group_name, "is_span": True})

                        span_data['remaining'] -= 1
                        if span_data['remaining'] == 0:
                            del active_spans[col]
                        col += 1
                    else:
                        if td_ptr < len(tds):
                            td = tds[td_ptr]
                            td_ptr += 1

                            rowspan = int(td.get("rowspan", 1))
                            colspan = int(td.get("colspan", 1))

                            rooms, classes_info = extract_cell_info(td)
                            for r in rooms:
                                self.master_rooms.add(r)
                                self.occupied_schedule[day][slot].add(r)
                            for ci in classes_info:
                                self.occupied_details[day][slot].append({**ci, "group": group_name, "is_span": False})

                            if rowspan > 1:
                                active_spans[col] = {
                                    'remaining': rowspan - 1,
                                    'rooms': rooms,
                                    'classes': classes_info
                                }
                            col += colspan
                        else:
                            col += 1

        # Sort slots chronologically
        self.all_slots = sorted(self.all_slots, key=self._slot_to_minutes)
        # Order days Monday -> Sunday
        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        self.all_days = sorted(self.all_days, key=lambda d: day_order.index(d) if d in day_order else 99)

    @staticmethod
    def _slot_to_minutes(slot_str):
        try:
            parts = slot_str.split(":")
            return int(parts[0]) * 60 + int(parts[1])
        except Exception:
            return 0

    def match_time_to_slot(self, check_time=None):
        """
        Maps a datetime.time or current time to the closest active timetable slot.
        Returns (matched_slot, status_msg)
        """
        if not self.all_slots:
            return None, "No timetable slots found"

        if check_time is None:
            check_time = datetime.now().time()

        now_mins = check_time.hour * 60 + check_time.minute
        slot_mins = [(s, self._slot_to_minutes(s)) for s in self.all_slots]

        # Check if before first slot
        if now_mins < slot_mins[0][1]:
            diff = slot_mins[0][1] - now_mins
            return slot_mins[0][0], f"Before first slot (Starts in {diff // 60}h {diff % 60}m at {slot_mins[0][0]})"

        # Check interval between consecutive slots
        for i in range(len(slot_mins) - 1):
            curr_slot, curr_m = slot_mins[i]
            next_slot, next_m = slot_mins[i + 1]
            if curr_m <= now_mins < next_m:
                return curr_slot, f"Current active slot ({curr_slot} - {next_slot})"

        # Check after last slot
        last_slot, last_m = slot_mins[-1]
        # Assume last slot lasts 60 minutes
        if now_mins < last_m + 60:
            return last_slot, f"Current active slot ({last_slot} - {last_m // 60 + 1}:{last_m % 60:02d})"
        else:
            return last_slot, f"Classes ended for today (showing last slot {last_slot})"

    def get_room_status(self, day, slot):
        """
        Returns {
            'day': day,
            'slot': slot,
            'total_rooms': int,
            'master_rooms': list,
            'occupied_rooms': list,
            'free_rooms': list,
            'occupancy_pct': float,
            'occupied_details': dict (room -> list of bookings)
        }
        """
        all_sorted = sorted(list(self.master_rooms))
        occupied_set = self.occupied_schedule.get(day, {}).get(slot, set())
        occupied_sorted = sorted(list(occupied_set))
        free_sorted = sorted([r for r in all_sorted if r not in occupied_set])
        
        details_for_slot = defaultdict(list)
        for item in self.occupied_details.get(day, {}).get(slot, []):
            r = item.get("room")
            if r:
                details_for_slot[r].append(item)

        total = len(all_sorted)
        occ_count = len(occupied_sorted)
        pct = round((occ_count / total * 100), 1) if total > 0 else 0.0

        return {
            "day": day,
            "slot": slot,
            "total_rooms": total,
            "master_rooms": all_sorted,
            "occupied_rooms": occupied_sorted,
            "free_rooms": free_sorted,
            "occupancy_pct": pct,
            "occupied_details": dict(details_for_slot)
        }

if __name__ == "__main__":
    parser = TimetableParser()
    print("Parsed successfully!")
    print(f"File: {parser.file_path}")
    print(f"Master Rooms ({len(parser.master_rooms)}): {sorted(list(parser.master_rooms))}")
    print(f"Days: {parser.all_days}")
    print(f"Slots: {parser.all_slots}")
    now_slot, msg = parser.match_time_to_slot()
    print(f"Now slot: {now_slot} ({msg})")
    status = parser.get_room_status("Monday", "08:30")
    print(f"Monday 08:30 Free rooms: {len(status['free_rooms'])}, Occupied: {len(status['occupied_rooms'])}")
