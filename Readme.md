# ระบบจัดการการเช็คชื่อด้วย RFID บน Raspberry Pi

โปรเจกต์นี้เป็นการพัฒนาและติดตั้งระบบการเช็คชื่อโดยใช้ RFID และ Raspberry Pi โดยระบบนี้สามารถบันทึกข้อมูลการเข้าชั้นเรียน ลงทะเบียนนักเรียนใหม่ และจัดการฐานข้อมูลทั้งหมดผ่านสคริปต์ Python

---

## 1. **การตั้งค่าและตรวจจับอุปกรณ์**

- ตั้งค่า **Raspberry Pi** ให้สามารถตรวจจับอุปกรณ์ **RFID Reader** และ **USB Flash Drive** ได้สำเร็จ
- ทดสอบการเชื่อมต่อกับ RFID Reader และ Flash Drive โดยสามารถตรวจจับและแสดงผลในระบบไฟล์ได้

---

## 2. **การจัดการฐานข้อมูล**

- สร้างและตั้งค่าฐานข้อมูล **MariaDB** บน Raspberry Pi สำหรับระบบ **`attendance_db`**
- เพิ่ม **ตารางที่สำคัญ**:
  - **`students`**: เก็บข้อมูลนักเรียน (`student_id`, `name`, `rfid`)
  - **`courses`**: เก็บข้อมูลวิชา (`course_id`, `course_name`, `start_time`, `end_time`, `day_of_week`)
  - **`student_courses`**: ตารางกลางที่เชื่อมระหว่างนักเรียนกับวิชา
  - **`attendance`**: บันทึกข้อมูลการเช็คชื่อ (`student_id`, `course_id`, `timestamp`, `status`)

---

## 3. **การทำงานของสคริปต์ Python**

## ฟีเจอร์ที่พัฒนา

### 1. **ออกแบบฐานข้อมูล**
   - ตารางต่างๆ:
     - `students`: เก็บข้อมูลนักเรียน (เช่น รหัส, ชื่อ, RFID)
     - `courses`: เก็บข้อมูลวิชา (เช่น รหัสวิชา, ชื่อวิชา, ชื่ออาจารย์)
     - `course_schedule`: เก็บข้อมูลตารางเรียนของวิชา (เช่น วัน, เวลา)
     - `student_courses`: ลิงก์นักเรียนกับวิชาที่เรียน
     - `attendance`: บันทึกข้อมูลการเช็คชื่อ พร้อมเวลาและสถานะ (มา, มาสาย, ขาด)

---

### 2. **การทำงานหลัก**
#### A. **เพิ่มนักเรียนใหม่**
   - **การสแกน RFID**: หลังจากสแกนบัตร RFID ระบบจะตรวจสอบว่ามีการลงทะเบียนนักเรียนซ้ำในตาราง `students` หรือไม่
   - **ลงทะเบียนนักเรียนใหม่**: หากยังไม่มีการลงทะเบียน ระบบจะถามรหัสนักเรียนและเพิ่มลงในฐานข้อมูล
   - **ลงทะเบียนเรียน**: แสดงรายวิชาที่มีในตาราง `course_schedule` และอนุญาตให้นักเรียนลงทะเบียนวิชาที่ต้องการ

#### B. **การเช็คชื่อ**
   - **การสแกน RFID**: หลังจากสแกนบัตร RFID ระบบจะ:
     1. ดึงรหัสนักเรียนจากฐานข้อมูล
     2. ตรวจสอบว่ามีการเช็คชื่อซ้ำในเวลาไม่เกิน 1 ชั่วโมงหรือไม่
     3. ตรวจสอบวันและเวลาปัจจุบันจากตาราง `course_schedule` เพื่อตรวจสอบว่านักเรียนอยู่ในคาบเรียนที่กำหนดหรือไม่
   - **บันทึกการเช็คชื่อ**: สถานะการเช็คชื่อจะถูกบันทึกเป็น:
     - `Present`: มาภายใน 10 นาทีหลังเริ่มคาบเรียน
     - `Late`: มาภายใน 10-15 นาทีหลังเริ่มคาบเรียน
     - `Absent`: มาหลังจาก 15 นาทีขึ้นไป

#### C. **รีเซ็ตฐานข้อมูล**
   - ลบข้อมูลทั้งหมดในตาราง `attendance`, `student_courses`, `course_schedule`, `courses` และ `students`
   - ยกเว้นนักเรียนที่มี RFID (`732749633633`) จากการลบในตาราง `students`

#### D. **สำรองฐานข้อมูล**
   - ส่งออกฐานข้อมูล MySQL (`attendance_db`) ไปยังไฟล์ `.sql` บน USB Flash Drive
   - ไฟล์ `.sql` จะถูกตั้งชื่อโดยใช้วันที่และเวลาปัจจุบัน (เช่น `attendance_db_YYYYMMDD_HHMMSS.sql`)

#### E. **อัปโหลดฐานข้อมูล**
   - อ่านไฟล์ `.sql` จาก USB Flash Drive และอนุญาตให้ผู้ใช้เลือกไฟล์สำหรับอัปโหลด
   - นำเข้าไฟล์ `.sql` ที่เลือกกลับเข้าสู่ฐานข้อมูล MySQL (`attendance_db`)

---

## การติดตั้งแพ็กเกจที่จำเป็น

### 1. ติดตั้งไลบรารี Python
ใช้คำสั่งต่อไปนี้เพื่อติดตั้งไลบรารีที่จำเป็น:
```bash
pip3 install mfrc522 --break-system-packages
pip3 install RPi.GPIO --break-system-packages
pip3 install mysql-connector-python --break-system-packages
pip3 install pytz --break-system-packages
pip3 install spidev --break-system-packages

ติดตั้ง MariaDB Server

sudo apt install mysql-server

สร้างฐานข้อมูลและตาราง

-- สร้างตาราง students
CREATE TABLE students (
    student_id VARCHAR(20) NOT NULL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    rfid VARCHAR(20) NOT NULL UNIQUE
);

-- สร้างตาราง courses
CREATE TABLE courses (
    course_id VARCHAR(10) NOT NULL PRIMARY KEY,
    course_name VARCHAR(100) NOT NULL,
    teacher_name VARCHAR(100) NOT NULL
);

-- สร้างตาราง course_schedule
CREATE TABLE course_schedule (
    schedule_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    course_id VARCHAR(10) NOT NULL,
    day_of_week VARCHAR(20) NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
);

-- สร้างตาราง student_courses
CREATE TABLE student_courses (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(20) NOT NULL,
    course_id VARCHAR(10) NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
);

-- สร้างตาราง attendance
CREATE TABLE attendance (
    attendance_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(20) NOT NULL,
    schedule_id INT NOT NULL,
    timestamp DATETIME NOT NULL,
    status ENUM('Present', 'Late', 'Absent') NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (schedule_id) REFERENCES course_schedule(schedule_id)
);


การต่อสาย RC522 RFID Module และ Buzzer กับ Raspberry Pi
การต่อสาย RC522
RC522 Pin	Raspberry Pi Pin (BCM)	Physical Pin	หมายเหตุ
SDA	        GPIO 8	            Pin 24	SPI0 CS (Chip Select)
SCK	        GPIO 11	            Pin 23	SPI0 SCK (Clock)
MOSI	    GPIO 10	            Pin 19	SPI0 MOSI (Master Out)
MISO	    GPIO 9	            Pin 21	SPI0 MISO (Master In)
GND	        Ground (GND)        Pin 6	เชื่อมต่อ Ground
RST	        GPIO 25	            Pin 22	Reset
3.3V	    3.3V Power	        Pin 1	แหล่งจ่ายไฟ 3.3V


การต่อสาย Buzzer
Buzzer Pin	Raspberry Pi Pin (BCM)	Physical Pin	หมายเหตุ
+ (บวก)	    GPIO 21	    Pin 40	สัญญาณควบคุม
- (ลบ)	    GND	        Pin 39	เชื่อมต่อกับ Ground