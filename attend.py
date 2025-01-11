from datetime import datetime, timedelta
import time as t  # เปลี่ยนชื่อ alias เป็น t
import pytz
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import mysql.connector
import os
import subprocess

# ตั้งค่า Reader
reader = SimpleMFRC522()

# ตั้งค่า Timezone เป็น Asia/Bangkok
bangkok_tz = pytz.timezone('Asia/Bangkok')

# ตั้งค่าพินสำหรับ Buzzer
BUZZER_PIN = 40

# ตั้งค่า GPIO
GPIO.setmode(GPIO.BOARD)  # ใช้หมายเลข Pin ตาม Physical Pin
GPIO.setup(BUZZER_PIN, GPIO.OUT)

def play_buzzer_success():
    """ส่งเสียงกรณีบันทึกสำเร็จ"""
    GPIO.output(BUZZER_PIN, GPIO.HIGH)
    t.sleep(0.2)  # เปลี่ยน time.sleep เป็น t.sleep
    GPIO.output(BUZZER_PIN, GPIO.LOW)
    t.sleep(0.2)
    GPIO.output(BUZZER_PIN, GPIO.HIGH)
    t.sleep(0.2)
    GPIO.output(BUZZER_PIN, GPIO.LOW)

def play_buzzer_error():
    """ส่งเสียงกรณีเกิดข้อผิดพลาด"""
    GPIO.output(BUZZER_PIN, GPIO.HIGH)
    t.sleep(2)  # เปลี่ยน time.sleep เป็น t.sleep
    GPIO.output(BUZZER_PIN, GPIO.LOW)

def connect_to_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="os123",  # แก้ไขตามรหัสผ่านของฐานข้อมูลคุณ
        database="attendance_db"
    )

def dump_database():
    """Dump the database and save to USB Flash Drive"""
    try:
        # ตรวจสอบตำแหน่งที่เมานต์ USB Drive
        usb_mount_path = "/media/os/ESD-USB"
        if not os.path.exists(usb_mount_path):
            print("USB Flash Drive not found. Please insert the drive.")
            return

        # สร้างชื่อไฟล์ dump พร้อมเวลา
        now = datetime.now(bangkok_tz).strftime("%Y%m%d_%H%M%S")
        dump_file_path = os.path.join(usb_mount_path, f"attendance_db_{now}.sql")

        # รันคำสั่ง mysqldump
        dump_command = [
            "mysqldump",
            "-u", "root",
            "--password=os123",
            "attendance_db"
        ]
        with open(dump_file_path, "w") as dump_file:
            subprocess.run(dump_command, stdout=dump_file, check=True)

        print(f"Database dumped successfully to {dump_file_path}")
        play_buzzer_success()
    except subprocess.CalledProcessError as e:
        print("Failed to dump database:", e)
        play_buzzer_error()

def check_attendance():
    db = connect_to_db()
    cursor = db.cursor()

    try:
        # อ่านข้อมูลจากบัตร RFID
        print("Place your card to read")
        id, text = reader.read()
        rfid = str(id).strip()
        print(f"RFID: {rfid}")
        print(f"Name on Card: {text.strip()}")

        # หากพบ RFID ตรงกับเงื่อนไข ให้หยุดการทำงานทันที
        if rfid == "732749633633":
            print("RFID Admin detected. Switching to Admin mode.")
            return rfid

        # ตรวจสอบนักเรียนจาก RFID
        cursor.execute("SELECT student_id FROM students WHERE rfid = %s", (rfid,))
        result = cursor.fetchone()
        if not result:
            print("ไม่พบนักเรียน")
            play_buzzer_error()  # ส่งเสียงกรณีไม่มีนักเรียน
            return rfid
        student_id = result[0]

        # ตรวจสอบเวลาและวิชา
        now = datetime.now(bangkok_tz)  # ใช้เวลาใน Timezone ประเทศไทย
        current_time = now.time()
        current_day = now.strftime("%A")
        print(f"Current Datetime (Bangkok): {now}")
        print(f"Current Day: {current_day}")

        # ค้นหาคอร์สที่ตรงกับวันปัจจุบัน
        cursor.execute("""
            SELECT c.course_id, c.start_time, c.end_time 
            FROM courses c 
            JOIN student_courses sc ON c.course_id = sc.course_id 
            WHERE sc.student_id = %s AND FIND_IN_SET(%s, c.day_of_week)
        """, (student_id, current_day))
        courses = cursor.fetchall()

        for course_id, start_time, end_time in courses:
            # Debug: พิมพ์ค่าดิบที่ได้จากฐานข้อมูล
            print(f"Raw Start Time: {start_time}, Raw End Time: {end_time}, Type: {type(start_time)}, {type(end_time)}")

            # แปลง start_time และ end_time หากจำเป็น
            if isinstance(start_time, timedelta):
                start_time = (datetime.min + start_time).time()
            elif isinstance(start_time, str):
                start_time = datetime.strptime(start_time, "%H:%M:%S").time()

            if isinstance(end_time, timedelta):
                end_time = (datetime.min + end_time).time()
            elif isinstance(end_time, str):
                end_time = datetime.strptime(end_time, "%H:%M:%S").time()

            # Debug: ดูค่าแปลงแล้ว
            print(f"Processed Start Time: {start_time}, End Time: {end_time}")

            # แปลง start_time และ end_time เป็น offset-aware datetime เพื่อเปรียบเทียบ
            start_datetime = bangkok_tz.localize(datetime.combine(now.date(), start_time))
            if end_time < start_time:  # หาก end_time ข้ามวัน
                end_datetime = bangkok_tz.localize(datetime.combine(now.date() + timedelta(days=1), end_time))
            else:
                end_datetime = bangkok_tz.localize(datetime.combine(now.date(), end_time))

            current_datetime = now

            # Debug: พิมพ์ค่าที่เกี่ยวข้อง
            print(f"Start Datetime: {start_datetime}, Current Datetime: {current_datetime}, End Datetime: {end_datetime}")

            if start_datetime <= current_datetime <= end_datetime:
                # ตรวจสอบว่าเคยเช็คชื่อไปแล้วหรือยัง
                cursor.execute("""
                    SELECT * FROM attendance 
                    WHERE student_id = %s AND course_id = %s AND DATE(timestamp) = CURDATE()
                """, (student_id, course_id))
                attendance_check = cursor.fetchone()
                if attendance_check:
                    print("Debug: Attendance record already exists:", attendance_check)
                    print("นักเรียนเช็คชื่อแล้ว")
                    play_buzzer_error()  # ส่งเสียงกรณีเช็คชื่อซ้ำ
                    return rfid

                # บันทึกการเช็คชื่อ
                sql = "INSERT INTO attendance (student_id, course_id, timestamp, status) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, (student_id, course_id, now, "Present"))
                db.commit()
                print("เช็คชื่อสำเร็จ")
                play_buzzer_success()  # ส่งเสียงกรณีบันทึกสำเร็จ
                return rfid

        print("ไม่มีวิชาที่กำลังเรียนในขณะนี้")
        play_buzzer_error()  # ส่งเสียงกรณีไม่มีวิชาเรียน
        return rfid
    except mysql.connector.Error as err:
        print(f"เกิดข้อผิดพลาด: {err}")
        play_buzzer_error()  # ส่งเสียงกรณีเกิดข้อผิดพลาด
        return None
    finally:
        cursor.close()
        db.close()

def main_loop():
    try:
        while True:
            print("\n--- Waiting for card scan ---")
            rfid = check_attendance()
            if rfid == "732749633633":
                while True:
                    print("\n--- Admin Menu ---")
                    print("1. Run attend.py")
                    print("2. Run newstd.py")
                    print("3. Dump database to USB Flash Drive")
                    print("0. Exit Program")
                    choice = input("Enter your choice: ")
                    if choice == "1":
                        print("Running attend.py...")
                        os.system("python3 attend.py")
                    elif choice == "2":
                        print("Running newstd.py...")
                        os.system("python3 newstd.py")
                    elif choice == "3":
                        print("Dumping database...")
                        dump_database()
                    elif choice == "0":
                        print("Exiting program.")
                        return
                    else:
                        print("Invalid choice. Please try again.")
            t.sleep(2)  # หน่วงเวลา 2 วินาทีก่อนเริ่มรอบใหม่
    except KeyboardInterrupt:
        print("Program interrupted by keyboard.")
    finally:
        GPIO.cleanup()
        print("GPIO cleaned up.")

# เรียกใช้โปรแกรมหลัก
main_loop()

