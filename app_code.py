"""
Simple Shift Manager — Streamlit (free, manual notifications)

Features (final design):
- Single-file Streamlit app with two modes: Manager (default) and Employee (via token in URL).
- Manager assigns tasks to employees by date and shift, generates a per-employee link, and gets a ready-to-copy message for WhatsApp/SMS.
- Employees open their unique link on phone, see today’s tasks, mark them complete, and upload a photo as proof.
- Data stored in a local JSON file (`data.json`) and uploaded images stored in `uploads/`.
- No paid APIs required — manager manually sends the generated WhatsApp/SMS message.

How to run:
1. pip install streamlit
2. streamlit run simple_shift_manager_streamlit.py
3. Open the app in your browser (manager view). To test employee behavior, open the generated link in a new tab or on a phone.

Notes & next steps:
- For small teams this local JSON storage is fine. For production use Google Sheets, Firebase, or a proper database and cloud storage.
- Optional later upgrade: integrate Twilio/WhatsApp Cloud API or SendGrid for automated notifications.
"""

import streamlit as st
from uuid import uuid4
from pathlib import Path
from datetime import date
import json
import urllib.parse

# -------------------- Config --------------------
DATA_FILE = Path("data.json")
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# -------------------- Persistence --------------------

def load_data():
    if not DATA_FILE.exists():
        # initialize 6 employees
        employees = [
            {"id": str(i+1), "name": f"Employee {i+1}", "phone": "", "email": "", "token": str(uuid4())}
            for i in range(6)
        ]
        data = {"employees": employees, "tasks": []}
        save_data(data)
        return data
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# -------------------- Task helpers --------------------

def add_task(employee_id, task_text, shift_label, task_date):
    data = load_data()
    task = {
        "task_id": str(uuid4()),
        "employee_id": employee_id,
        "task_text": task_text,
        "shift": shift_label,
        "date": task_date.isoformat(),
        "completed": False,
        "proof": None
    }
    data["tasks"].append(task)
    save_data(data)
    return task


def mark_complete(task_id, proof_fname=None):
    data = load_data()
    for t in data["tasks"]:
        if t["task_id"] == task_id:
            t["completed"] = True
            if proof_fname:
                t["proof"] = proof_fname
            break
    save_data(data)

# -------------------- Streamlit UI --------------------

st.set_page_config(page_title="Simple Shift Manager", layout="wide")
query_params = st.experimental_get_query_params()

# Employee mode if token present
if "token" in query_params:
    token = query_params.get("token")[0]
    data = load_data()
    emp = next((e for e in data["employees"] if e["token"] == token), None)
    if not emp:
        st.title("Invalid link")
        st.error("This task link is invalid. Contact your manager.")
    else:
        st.title(f"Hello, {emp['name']}")
        st.write("Your tasks for today")
        today = date.today().isoformat()
        tasks = [t for t in data["tasks"] if t["employee_id"] == emp["id"] and t["date"] == today]
        if not tasks:
            st.info("No tasks assigned for today.")
        for t in tasks:
            st.markdown("---")
            st.subheader(t["task_text"])
            st.write(f"Shift: **{t['shift']}** — Date: {t['date']}")
            if t["completed"]:
                st.success("Completed")
                if t.get("proof"):
                    p = UPLOAD_DIR / t["proof"]
                    if p.exists():
                        st.image(str(p))
            else:
                uploaded = st.file_uploader(f"Upload proof for: {t['task_text']}", type=["png","jpg","jpeg"], key=t['task_id'])
                if st.button("Mark complete", key="btn_"+t['task_id']):
                    filename = None
                    if uploaded:
                        ext = Path(uploaded.name).suffix
                        filename = f"{t['task_id']}{ext}"
                        with open(UPLOAD_DIR / filename, "wb") as f:
                            f.write(uploaded.getbuffer())
                    mark_complete(t['task_id'], proof_fname=filename)
                    st.success("Marked complete. Thank you!")
        st.markdown("---")
        st.write("If you can't see your tasks or something's wrong, contact your manager.")

else:
    # Manager dashboard
    st.title("Manager Dashboard — Simple Shift Manager")
    data = load_data()
    employees = data["employees"]

    # Employee editor on sidebar
    st.sidebar.header("Employees")
    for emp in employees:
        with st.sidebar.expander(emp['name']):
            name = st.text_input(f"Name ({emp['id']})", value=emp['name'], key=f"name_{emp['id']}")
            phone = st.text_input(f"Phone ({emp['id']}) — include country code (e.g. 49151...)", value=emp.get('phone',''), key=f"phone_{emp['id']}")
            email = st.text_input(f"Email ({emp['id']})", value=emp.get('email',''), key=f"email_{emp['id']}")
            if st.button(f"Save {emp['name']}", key=f"save_{emp['id']}"):
                emp['name'] = name
                emp['phone'] = phone
                emp['email'] = email
                save_data(data)
                st.experimental_rerun()

    st.header("Assign Task")
    col1, col2, col3 = st.columns([2,2,1])
    with col1:
        emp_choice = st.selectbox("Employee", options=employees, format_func=lambda e: e['name'])
    with col2:
        shift = st.selectbox("Shift", ["Morning","Afternoon","Night"]) 
    with col3:
        task_date = st.date_input("Date", value=date.today())

    task_text = st.text_input("Task description")
    if st.button("Assign"):
        if not task_text.strip():
            st.error("Task description cannot be empty")
        else:
            add_task(emp_choice['id'], task_text.strip(), shift, task_date)
            st.success("Task assigned")

    st.markdown("---")
    st.header("Share links & send message")
    base_url = st.experimental_get_url()
    if not base_url:
        st.warning("Note: your deployment might not provide a full base URL. When sharing, open the app in a real server and copy the full link shown below.")

    for emp in employees:
        st.write(f"**{emp['name']}** — Phone: {emp.get('phone','(not set)')}")
        # ensure token
        if not emp.get('token'):
            emp['token'] = str(uuid4())
            save_data(data)
        token = emp['token']
        if base_url:
            link = f"{base_url}?token={token}"
        else:
            link = f"?token={token}"

        # Pre-filled WhatsApp message (manager will copy-paste into their phone)
        msg = f"Hello {emp['name']}, your task for {date.today().isoformat()} is ready. Open: {link}"
        wa_link = f"https://wa.me/{emp.get('phone','')}?text={urllib.parse.quote(msg)}" if emp.get('phone') else None

        cols = st.columns([2,2,2,1])
        cols[0].code(link)
        cols[1].text_area("Message to send", value=msg, height=60, key=f"msg_{emp['id']}")
        if wa_link:
            cols[2].markdown(f"[Open WhatsApp link (paste on phone/browser)]({wa_link})")
        else:
            cols[2].write("Set phone to use WhatsApp link")
        if cols[3].button("Copy link", key=f"copy_{emp['id']}"):
            st.write("Tip: use your browser or OS copy shortcut — Streamlit cannot access clipboard from server-side.")

    st.markdown("---")
    st.header("Today's tasks & proofs")
    today = date.today().isoformat()
    tasks_today = [t for t in data['tasks'] if t['date'] == today]
    if not tasks_today:
        st.info("No tasks for today")
    for t in tasks_today:
        emp = next(e for e in employees if e['id'] == t['employee_id'])
        st.write(f"**{emp['name']}** — {t['task_text']} — Shift: {t['shift']} — Completed: {t['completed']}")
        if t.get('proof'):
            p = UPLOAD_DIR / t['proof']
            if p.exists():
                st.image(str(p))

    st.markdown("---")
    st.write("**How to use (quick):** Manager assigns task → copies message or link → pastes to employee via WhatsApp/SMS → employee opens link on phone and uploads proof.")
    st.write("When you're ready to automate notifications later, we can add Twilio or WhatsApp Cloud API integration.")

