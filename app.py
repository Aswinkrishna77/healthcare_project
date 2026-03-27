import streamlit as st
import mysql.connector
from datetime import date

# ---------------- CONFIG ----------------
st.set_page_config(page_title="HealthCare Pro", layout="centered")

# ---------------- DB CONNECTION ----------------
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="healthcare_db"
    )

# ---------------- SESSION ----------------
if "role" not in st.session_state:
    st.session_state.role = None
if "doctor_id" not in st.session_state:
    st.session_state.doctor_id = None
if "dark" not in st.session_state:
    st.session_state.dark = False

# ---------------- THEME TOGGLE ----------------
if st.button("🌙 Toggle Theme"):
    st.session_state.dark = not st.session_state.dark

# ---------------- STYLES ----------------
def apply_styles():
    if st.session_state.dark:
        bg = "#1f4037"
    else:
        bg = "#99f2c8"

    st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(135deg, #1f4037, {bg});
    }}

    .login-box {{
        width: 360px;
        margin: auto;
        margin-top: 120px;
        padding: 40px;
        border-radius: 20px;
        background: rgba(255,255,255,0.15);
        backdrop-filter: blur(15px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.3);
        text-align: center;
        color: white;
    }}

    .stButton>button {{
        width: 100%;
        border-radius: 10px;
        background: linear-gradient(to right,#0072ff,#00c6ff);
        color: white;
        font-size: 16px;
        padding: 10px;
        border: none;
    }}

    input {{
        border-radius: 10px !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# ---------------- LOGIN ----------------
def login():
    apply_styles()

    st.markdown('<div class="login-box">', unsafe_allow_html=True)

    st.markdown("## 🏥 HealthCare Pro")
    st.markdown("Smart Hospital Management")

    role = st.radio("Select Role", ["admin", "doctor"])
    password = st.text_input("Enter Password", type="password")

    if st.button("Login"):
        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute("SELECT * FROM users WHERE role=%s", (role,))
        user = cursor.fetchone()

        if user:
            st.session_state.role = role
            st.session_state.doctor_id = user["id"]
            st.success("Login Successful!")
            st.rerun()
        else:
            st.error("Invalid Login")

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- ADMIN DASHBOARD ----------------
def admin_dashboard():
    st.title("📊 Admin Dashboard")

    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT COUNT(*) FROM patients")
    patients = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM appointments")
    appointments = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM doctors")
    doctors = cursor.fetchone()[0]

    col1, col2, col3 = st.columns(3)
    col1.metric("Patients", patients)
    col2.metric("Appointments", appointments)
    col3.metric("Doctors", doctors)

    menu = st.sidebar.selectbox("Menu", ["Add Patient", "Book Appointment", "Statistics"])

    # ADD PATIENT
    if menu == "Add Patient":
        st.subheader("➕ Add Patient")

        name = st.text_input("Name")
        age = st.number_input("Age")
        gender = st.selectbox("Gender", ["Male", "Female"])
        phone = st.text_input("Phone")
        address = st.text_area("Address")

        if st.button("Add Patient"):
            cursor.execute("""
            INSERT INTO patients(name,age,gender,phone,address)
            VALUES(%s,%s,%s,%s,%s)
            """,(name,age,gender,phone,address))
            db.commit()
            st.success("Patient Added!")

    # BOOK APPOINTMENT
    elif menu == "Book Appointment":
        st.subheader("📅 Book Appointment")

        cursor.execute("SELECT * FROM patients")
        patients = cursor.fetchall()

        cursor.execute("SELECT * FROM doctors")
        doctors = cursor.fetchall()

        patient = st.selectbox("Patient", patients, format_func=lambda x: x[1])
        doctor = st.selectbox("Doctor", doctors, format_func=lambda x: x[1])

        date_input = st.date_input("Date")
        time_input = st.time_input("Time")

        if st.button("Book Appointment"):
            cursor.execute("""
            INSERT INTO appointments(patient_id,doctor_id,appointment_date,time_slot)
            VALUES(%s,%s,%s,%s)
            """,(patient[0],doctor[0],date_input,time_input))
            db.commit()

            st.success("Appointment Booked!")
            st.info("⚡ Trigger auto-set status!")

    # STATISTICS (VIEW)
    elif menu == "Statistics":
        st.subheader("📈 Doctor Statistics")

        cursor.execute("SELECT name,total_appointments FROM doctor_stats_view")
        data = cursor.fetchall()

        chart_data = {row[0]: row[1] for row in data}
        st.bar_chart(chart_data)

# ---------------- DOCTOR DASHBOARD ----------------
def doctor_dashboard():
    st.title("👨‍⚕️ Doctor Panel")

    db = get_db()
    cursor = db.cursor(dictionary=True)

    menu = st.sidebar.selectbox("Menu", ["Appointments", "Add Prescription"])

    if menu == "Appointments":
        cursor.execute("""
        SELECT p.name, a.appointment_date, a.time_slot, a.status
        FROM appointments a
        JOIN patients p ON a.patient_id=p.id
        """)

        rows = cursor.fetchall()
        st.table(rows)

    elif menu == "Add Prescription":
        st.subheader("💊 Add Prescription")

        cursor.execute("SELECT * FROM patients")
        patients = cursor.fetchall()

        patient = st.selectbox("Patient", patients, format_func=lambda x: x[1])
        medicine = st.text_area("Medicine")

        if st.button("Save Prescription"):
            cursor.execute("""
            INSERT INTO prescriptions(patient_id,doctor_id,medicine,prescription_date)
            VALUES(%s,%s,%s,%s)
            """,(patient[0],st.session_state.doctor_id,medicine,date.today()))
            db.commit()
            st.success("Saved!")

# ---------------- LOGOUT ----------------
def logout():
    st.session_state.role = None
    st.session_state.doctor_id = None
    st.rerun()

# ---------------- MAIN ----------------
if st.session_state.role is None:
    login()
else:
    if st.sidebar.button("Logout"):
        logout()

    if st.session_state.role == "admin":
        admin_dashboard()
    else:
        doctor_dashboard()