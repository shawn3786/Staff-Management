# simple_shift_manager_v2.py
"""
Simple Shift Manager v2 — Tabbed Streamlit app
Features:
- Tabbed UI: Employees | Assign Task | Today's Tasks
- Add / Edit / Remove employees
- Per-employee token links for employee view
- Manager copies a message for manual WhatsApp/SMS sending
- Employees open link (with ?token=...) to see today's tasks, upload photo proof and mark complete
- Local persistence: data.json + uploads/ directory
"""
import streamlit as st
from uuid import uuid4
from pathlib import Path
from datetime import date, datetime
import json
import urllib.parse

# ---------------- Config ----------------
DATA_FILE = Path("data.json")
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# ---------------- Persistence helpers ----------------
def load_data():
    if not DATA_FILE.exists():
        # initial 6 empty employees
        employees = [
            {"id": str(i+1), "name": f"Employee {i+1}", "phone": "", "email": "", "token": str(uuid4())}
            for i in range(6)
        ]
        data = {"employees": employees, "tasks": []}
        save_data(data)
        return data
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except Exception:
        # corrupt file fallback
        return {"employees": [], "tasks": []}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# ---------------- Task functions ----------------
def add_task(employee_id, task_text, shift_label, task_date):
    data = load_data()
    task = {
        "task_id": str(uuid4()),
        "employee_id": employee_id,
        "task_text": task_text,
        "shift": shift_label,
        "date": task_date.isoformat(),
        "assigned_at": datetime.utcnow().isoformat(),
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
            t["completed_at"] = datetime.utcnow().isoformat()
            break
    save_data(data)

def delete_employee(emp_id):
    data = load_data()
    # remove employee
    data["employees"] = [e for e in data["employees"] if e["id"] != emp_id]
    # optionally remove tasks for that employee
    data["tasks"] = [t for t in data["tasks"] if t["employee_id"] != emp_id]
    save_data(data)

# ---------------- Streamlit UI ----------------
st.set_page_config(page_title="Simple Shift Manager v2", layout="wide")
st.title("👷 Simple Shift Manager v2 — Tabbed Dashboard")

data = load_data()
employees = data.get("employees", [])
tasks = data.get("tasks", [])

# ---- Top info row ----
col_info1, col_info2 = st.columns([3,1])
with col_info1:
    st.markdown("**Quick:** Use the *Employees* tab to add or remove people. Use *Assign Task* to assign today's tasks. Employees open the link you copy & paste into WhatsApp/SMS to view & complete tasks on their phones.")
with col_info2:
    if st.button("Refresh"):
        st.experimental_rerun()

# ---- Tabs ----
tab_emp, tab_assign, tab_today = st.tabs(["🧑‍💼 Employees", "📝 Assign Task", "📅 Today's Tasks"])

# ---------------- Employees Tab ----------------
with tab_emp:
    st.header("Employees — Add / Edit / Remove")
    # Add new employee
    with st.expander("➕ Add new employee"):
        new_name = st.text_input("Name", key="new_name")
        new_phone = st.text_input("Phone (with country code, e.g. 4915...)", key="new_phone")
        new_email = st.text_input("Email (optional)", key="new_email")
        if st.button("Add Employee"):
            if not new_name.strip():
                st.error("Name required")
            else:
                # new id as next integer string, ensure unique
                next_id = str(max([int(e["id"]) for e in employees] + [0]) + 1)
                employees.append({
                    "id": next_id,
                    "name": new_name.strip(),
                    "phone": new_phone.strip(),
                    "email": new_email.strip(),
                    "token": str(uuid4())
                })
                save_data({"employees": employees, "tasks": tasks})
                st.success(f"Added {new_name.strip()}")
                st.experimental_rerun()

    st.markdown("---")
    # Show editable list
    if not employees:
        st.info("No employees yet. Add one above.")
    else:
        for emp in employees:
            with st.container():
                c1, c2, c3, c4 = st.columns([3,2,2,1])
                with c1:
                    name = st.text_input(f"Name - ID {emp['id']}", value=emp['name'], key=f"name_{emp['id']}")
                with c2:
                    phone = st.text_input(f"Phone", value=emp.get("phone",""), key=f"phone_{emp['id']}")
                with c3:
                    email = st.text_input(f"Email", value=emp.get("email",""), key=f"email_{emp['id']}")
                with c4:
                    if st.button("Save", key=f"save_emp_{emp['id']}"):
                        emp['name'] = name.strip()
                        emp['phone'] = phone.strip()
                        emp['email'] = email.strip()
                        save_data({"employees": employees, "tasks": tasks})
                        st.success("Saved")
                        st.experimental_rerun()
                    if st.button("Remove", key=f"remove_emp_{emp['id']}"):
                        delete_employee(emp['id'])
                        st.warning(f"Removed employee {emp['name']} and their tasks")
                        st.experimental_rerun()

# ---------------- Assign Task Tab ----------------
with tab_assign:
    st.header("Assign Task")
    if not employees:
        st.warning("Add employees first in the Employees tab.")
    else:
        col_a, col_b = st.columns([2,3])
        with col_a:
            emp_choice = st.selectbox("Choose employee", options=employees, format_func=lambda e: f"{e['name']} (ID:{e['id']})")
            shift = st.selectbox("Shift", ["Morning", "Afternoon", "Night"])
            task_date = st.date_input("Date", value=date.today())
        with col_b:
            task_text = st.text_area("Task description", height=140)
            if st.button("Assign Task"):
                if not task_text.strip():
                    st.error("Task description cannot be empty")
                else:
                    add_task(emp_choice['id'], task_text.strip(), shift, task_date)
                    st.success(f"Task assigned to {emp_choice['name']} for {task_date.isoformat()}")
                    st.experimental_rerun()

    st.markdown("---")
    st.subheader("Share link & message for each employee")
    base_url = st.experimental_get_url()
    if not base_url:
        st.info("If deploying, open the app URL in browser and copy the link shown below (some dev URLs are partial).")

    for emp in employees:
        st.write(f"**{emp['name']}** — Phone: {emp.get('phone','(not set)')}")
        if not emp.get("token"):
            emp["token"] = str(uuid4())
            save_data({"employees": employees, "tasks": tasks})
        token = emp["token"]
        if base_url:
            link = f"{base_url}?token={token}"
        else:
            link = f"?token={token}"
        msg = f"Hello {emp['name']}, your task for {date.today().isoformat()} is ready. Open: {link}"
        wa_link = (f"https://wa.me/{emp.get('phone','')}?text={urllib.parse.quote(msg)}") if emp.get('phone') else None

        cols = st.columns([3,4,2])
        cols[0].code(link)
        cols[1].text_area("Message to send (copy)", value=msg, height=60, key=f"msg_{emp['id']}")
        if wa_link:
            cols[2].markdown(f"[Open WhatsApp link (paste to phone/browser)]({wa_link})")
        else:
            cols[2].write("Set phone to use WhatsApp link")

# ---------------- Today's Tasks Tab ----------------
with tab_today:
    st.header("Today's Tasks & Proofs")
    today_str = date.today().isoformat()
    tasks_today = [t for t in tasks if t.get("date") == today_str]
    if not tasks_today:
        st.info("No tasks for today.")
    else:
        for t in tasks_today:
            emp = next((e for e in employees if e["id"] == t["employee_id"]), {"name": "Unknown"})
            st.markdown("---")
            st.subheader(f"{t['task_text']} — {emp['name']}")
            st.write(f"Shift: **{t['shift']}** — Assigned: {t.get('assigned_at','-')}")
            if t.get("completed"):
                st.success("Completed")
                if t.get("proof"):
                    p = UPLOAD_DIR / t["proof"]
                    if p.exists():
                        st.image(str(p))
                    else:
                        st.write("Proof file not found.")
                st.write(f"Completed at: {t.get('completed_at','-')}")
            else:
                st.warning("Pending")
                # Provide manager option to mark complete manually and upload proof
                uploaded = st.file_uploader(f"Upload proof for manager (task {t['task_id']})", type=["png","jpg","jpeg"], key=f"mgr_upload_{t['task_id']}")
                if st.button("Mark complete (manager)", key=f"mgr_complete_{t['task_id']}"):
                    fname = None
                    if uploaded:
                        ext = Path(uploaded.name).suffix
                        fname = f"{t['task_id']}{ext}"
                        with open(UPLOAD_DIR / fname, "wb") as f:
                            f.write(uploaded.getbuffer())
                    mark_complete(t['task_id'], proof_fname=fname)
                    st.success("Marked complete and saved proof (if uploaded).")
                    st.experimental_rerun()

# ---------------- Employee view helper ----------------
# Provide instructions for employees to open their token link (useful when testing)
st.markdown("---")
st.caption("Employee view: open the app with `?token=<employee-token>` (copy the token from Employees tab code field). Example: https://your-app-url/?token=...")

# End of file
