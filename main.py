import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Database Connection
from credentials import get_db_connection

# Fetch Unique IPs
def fetch_unique_ips():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT ip FROM script_event")
    ips = [row["ip"] for row in cursor.fetchall()]
    conn.close()
    return ips

# Fetch Program Details
def fetch_program_details(selected_ip=None, selected_date=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT ip, script_path, start_time, end_time
        FROM script_event
        WHERE 1=1
    """
    params = []

    if selected_ip:
        query += " AND ip = %s"
        params.append(selected_ip)
    if selected_date:
        query += " AND DATE(start_time) = %s"
        params.append(selected_date)

    query += " ORDER BY start_time"
    cursor.execute(query, tuple(params))
    data = cursor.fetchall()
    conn.close()

    for entry in data:
        if entry['end_time']:
            duration = entry['end_time'] - entry['start_time']
            entry['duration'] = str(duration)
        else:
            entry['duration'] = "Running"
    return data

# Generate 24-hour time slots
def generate_time_slots():
    return [(datetime.strptime(f"{hour}:00", "%H:%M"), datetime.strptime(f"{hour}:59", "%H:%M")) for hour in range(24)]

# Map Programs to Time Slots
def map_programs_to_slots(programs, time_slots):
    slot_status = []
    for start, end in time_slots:
        slot_programs = [p["script_path"] for p in programs if p["start_time"].hour == start.hour]
        status = "Running" if slot_programs else "Free"
        slot_status.append({
            "Time Slot": start.strftime("%H:%M"),
            "Status": status,
            "Programs": "\n".join(slot_programs) if slot_programs else "None"
        })
    return slot_status

# Highlight Running Slots
def highlight_slots(val):
    return 'background-color: #ff6961' if val == "Running" else 'background-color: #77dd77'

# Streamlit UI
st.set_page_config(page_title="System Monitoring Dashboard", layout="wide")
st.title("System Monitoring Dashboard")

# Sidebar Filters
st.sidebar.header("Filters")
ips = fetch_unique_ips()
selected_ip = st.sidebar.selectbox("Select IP", [None] + ips)
selected_date = st.sidebar.date_input("Select Date", datetime.today())
status_filter = st.sidebar.multiselect("Filter by Status", ["Running", "Free"], default=["Running", "Free"])



if st.sidebar.button("🔄 Refresh Now"):
    st.rerun()

# Fetch Data
data = fetch_program_details(selected_ip, selected_date)

# Summary Metrics
st.markdown("### 📊 Summary")
total_scripts = len(data)
completed = sum(1 for d in data if d["end_time"])
running = total_scripts - completed

col1, col2, col3 = st.columns(3)
col1.metric("Total Scripts", total_scripts)
col2.metric("Completed", completed)
col3.metric("Running", running)

# Calendar View
st.header("Daily System Activity")
time_slots = generate_time_slots()
slot_data = map_programs_to_slots(data, time_slots)
df_slots = pd.DataFrame(slot_data)
df_slots = df_slots[df_slots["Status"].isin(status_filter)]
styled_df = df_slots.style.applymap(highlight_slots, subset=["Status"])
st.dataframe(styled_df, hide_index=True, column_config={"Programs": {"tooltip": True}})



# Details View
st.header("Detailed Program Data")
st.dataframe(pd.DataFrame(data), use_container_width=True)

# Download Option
st.download_button("📥 Download Data", pd.DataFrame(data).to_csv(index=False), "script_data.csv", "text/csv")
