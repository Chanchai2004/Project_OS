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

### **สคริปต์ที่พัฒนา**
#### **`attend.py`**
- ใช้สำหรับเช็คชื่อการเข้าชั้นเรียนของนักเรียนโดยการสแกนบัตร RFID
- ตรวจสอบข้อมูลวิชาและบันทึกสถานะการเข้าเรียน (`Present`, `Late`, `Absent`) ลงใน **attendance**

#### **`newstd.py`**
- ใช้สำหรับลงทะเบียนนักเรียนใหม่ผ่านการสแกนบัตร RFID
- เพิ่มข้อมูลนักเรียนลงใน **students** และให้เลือกวิชาที่ต้องการเรียนผ่านเมนู
- บันทึกข้อมูลนักเรียนและวิชาที่เลือกลงใน **student_courses**

### **ฟีเจอร์ที่เพิ่มเข้ามา**
#### **การแจ้งเตือนด้วยเสียง Buzzer**
- **กรณีสำเร็จ**: ส่งเสียงสั้น 2 ครั้ง
- **กรณีเกิดข้อผิดพลาด**: ส่งเสียงยาว 2 วินาที

#### **ฟังก์ชันสำรองฐานข้อมูล**
- สำรองฐานข้อมูลเป็นไฟล์ `.sql` ลงใน USB Flash Drive
- ตั้งชื่อไฟล์ตามวันที่และเวลาปัจจุบัน

### **ลูปหลัก (Main Loop)**
- ระบบจะรอการสแกน RFID และประมวลผลตามข้อมูลที่ได้รับ
- หากตรวจพบ RFID Admin (`732749633633`):
  - แสดงเมนูให้เลือกคำสั่ง:
    1. รัน **`attend.py`**
    2. รัน **`newstd.py`**
    3. สำรองฐานข้อมูล
    4. ออกจากโปรแกรม

---

## 4. **การปรับปรุงโค้ดและการทดสอบ**

- ปรับปรุงโค้ดให้รองรับการทำงานที่เชื่อถือได้:
  - จัดการการแปลงเวลาให้รองรับ Timezone **Asia/Bangkok**
  - รองรับกรณีเวลา `end_time` ข้ามวัน
  - แก้ไขข้อจำกัดของ **Foreign Key** เพื่อจัดการการลบข้อมูล
  - ทดสอบการทำงานในหลากหลายสถานการณ์ รวมถึงการปิดโปรแกรมด้วย `KeyboardInterrupt`

---

## 5. **ผลลัพธ์ที่ได้**

ระบบทำงานได้อย่างสมบูรณ์ โดยมีความสามารถดังนี้:
- การเชื่อมต่อฐานข้อมูลเพื่อจัดเก็บและดึงข้อมูลการเข้าเรียน
- การลงทะเบียนนักเรียนใหม่พร้อมเลือกวิชา
- การเช็คชื่อด้วย RFID และบันทึกสถานะการเข้าเรียน
- การสำรองฐานข้อมูลไปยัง USB Flash Drive
- การแจ้งเตือนด้วยเสียงเมื่อทำงานสำเร็จหรือเกิดข้อผิดพลาด

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

CREATE TABLE students (
    student_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100),
    rfid VARCHAR(20) UNIQUE
);

CREATE TABLE courses (
    course_id VARCHAR(10) PRIMARY KEY,
    course_name VARCHAR(100),
    start_time TIME,
    end_time TIME,
    teacher_name VARCHAR(100),
    day_of_week VARCHAR(20)
);

CREATE TABLE student_courses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(20),
    course_id VARCHAR(10),
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
);

CREATE TABLE attendance (
    attendance_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(20),
    course_id VARCHAR(10),
    timestamp DATETIME,
    status ENUM('Present', 'Late', 'Absent'),
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
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