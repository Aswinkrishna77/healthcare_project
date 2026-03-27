CREATE DATABASE healthcare_db;
USE healthcare_db;

-- USERS
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    password VARCHAR(255),
    role ENUM('admin','doctor')
);

-- DOCTORS
CREATE TABLE doctors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    specialization VARCHAR(100)
);

-- PATIENTS
CREATE TABLE patients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    age INT,
    gender VARCHAR(10),
    phone VARCHAR(15),
    address TEXT
);

-- APPOINTMENTS
CREATE TABLE appointments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT,
    doctor_id INT,
    appointment_date DATE,
    time_slot TIME,
    status VARCHAR(20) DEFAULT 'Active',
    FOREIGN KEY (patient_id) REFERENCES patients(id),
    FOREIGN KEY (doctor_id) REFERENCES doctors(id)
);

-- PRESCRIPTIONS
CREATE TABLE prescriptions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT,
    doctor_id INT,
    medicine TEXT,
    prescription_date DATE,
    FOREIGN KEY (patient_id) REFERENCES patients(id),
    FOREIGN KEY (doctor_id) REFERENCES doctors(id)
);

---------------------------------------------------
-- ✅ VIEW (Doctor Statistics)
---------------------------------------------------
CREATE VIEW doctor_stats_view AS
SELECT d.id, d.name,
COUNT(a.id) AS total_appointments
FROM doctors d
LEFT JOIN appointments a ON d.id = a.doctor_id
GROUP BY d.id;

---------------------------------------------------
-- ✅ TRIGGER (Auto set status)
---------------------------------------------------
DELIMITER //

DELIMITER //

CREATE TRIGGER set_appointment_status
BEFORE INSERT ON appointments
FOR EACH ROW
BEGIN
    IF NEW.appointment_date < CURDATE() THEN
        SET NEW.status = 'Completed';
    ELSE
        SET NEW.status = 'Active';
    END IF;
END//

DELIMITER ;