
from datetime import datetime, timedelta
import time as t  # เปลี่ยนชื่อ alias เป็น t
import pytz
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import mysql.connector
import os
import sqlite3
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
    t.sleep(0.1)  # เปลี่ยน time.sleep เป็น t.sleep
    GPIO.output(BUZZER_PIN, GPIO.LOW)

def play_buzzer_error():
    """ส่งเสียงกรณีเกิดข้อผิดพลาด"""
    GPIO.output(BUZZER_PIN, GPIO.HIGH)
    t.sleep(0.1)  # เปลี่ยน time.sleep เป็น t.sleep
    GPIO.output(BUZZER_PIN, GPIO.LOW)
    t.sleep(0.1)
    GPIO.output(BUZZER_PIN, GPIO.HIGH)
    t.sleep(0.1)
    GPIO.output(BUZZER_PIN, GPIO.LOW)
    t.sleep(0.1)
    GPIO.output(BUZZER_PIN, GPIO.HIGH)
    t.sleep(0.1)
    GPIO.output(BUZZER_PIN, GPIO.LOW)

    

def connect_to_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="os123",  # แก้ไขตามรหัสผ่านของฐานข้อมูลคุณ
        database="attendance_db"
    )


def check_attendance():
    db = connect_to_db()
    cursor = db.cursor()

    try:
        # อ่านข้อมูลจากบัตร RFID
        print("Place your card to read")
        id, text = reader.read()
        rfid = str(id).strip()
        print(f"Name on Card: {text.strip()}")

        # ตรวจสอบ RFID Admin
        if rfid == "664667101308":
            print("RFID Admin detected. Switching to Admin mode.")
            return rfid

        # ตรวจสอบนักเรียนจาก RFID
        cursor.execute("SELECT student_id FROM students WHERE rfid = %s", (rfid,))
        result = cursor.fetchone()
        if not result:
            print("ไม่พบนักเรียน")
            play_buzzer_error()
            return rfid
        student_id = result[0]

        # ตรวจสอบการเช็คชื่อซ้ำในเวลาไม่เกิน 1 ชั่วโมง
        cursor.execute("""
            SELECT timestamp FROM attendance 
            WHERE student_id = %s 
            ORDER BY timestamp DESC 
            LIMIT 1
        """, (student_id,))
        last_attendance = cursor.fetchone()
        now = datetime.now(bangkok_tz)
        if last_attendance:
            last_timestamp = last_attendance[0]
    
            # แปลง last_timestamp ให้มี timezone
            if last_timestamp.tzinfo is None:
                last_timestamp = bangkok_tz.localize(last_timestamp)

            time_difference = (now - last_timestamp).total_seconds() / 3600
            if time_difference <= 1:
                print("การเช็คชื่อซ้ำ")
                play_buzzer_error()
                return rfid


        # ตรวจสอบวันและเวลาเรียน
        current_day = now.strftime("%A")
        current_time = now.time()

        # ดึงข้อมูลวิชาที่ตรงกับวันและเวลา
        cursor.execute("""
            SELECT cs.schedule_id, cs.start_time, cs.end_time, cs.day_of_week, cs.course_id
            FROM course_schedule cs
            JOIN student_courses sc ON cs.course_id = sc.course_id
            WHERE sc.student_id = %s AND cs.day_of_week = %s AND %s BETWEEN cs.start_time AND cs.end_time
        """, (student_id, current_day, current_time))
        course = cursor.fetchone()

        if not course:
            print("ไม่มีวิชาที่กำลังเรียนในขณะนี้")
            play_buzzer_error()
            return rfid

        schedule_id, start_time, end_time, day_of_week, course_id = course

        # ตรวจสอบและแปลง start_time และ end_time หากเป็น timedelta
        if isinstance(start_time, timedelta):
            start_time = (datetime.min + start_time).time()
        if isinstance(end_time, timedelta):
            end_time = (datetime.min + end_time).time()

        print(f"Course: {course_id}, Start: {start_time}, End: {end_time}, Day: {day_of_week}")

        # ตรวจสอบสถานะ (Present, Late, Absent)
        start_datetime = datetime.combine(now.date(), start_time).astimezone(bangkok_tz)
        delay = (now - start_datetime).total_seconds() / 60
        if delay <= 10:
            status = "Present"
        elif delay <= 15:
            status = "Late"
        else:
            status = "Absent"

        # บันทึกการเช็คชื่อ
        cursor.execute("""
            INSERT INTO attendance (student_id, schedule_id, timestamp, status)
            VALUES (%s, %s, %s, %s)
        """, (student_id, schedule_id, now, status))
        db.commit()

        print(f"เช็คชื่อสำเร็จ: {status}")
        play_buzzer_success()
        return rfid

    except mysql.connector.Error as err:
        print(f"เกิดข้อผิดพลาด: {err}")
        play_buzzer_error()
        return None

    finally:
        cursor.close()
        db.close()




def main_loop():
    try:
        while True:
            print("\n--- Waiting for card scan ---")
            rfid = check_attendance()
            if rfid == "664667101308":
                while True:
                    print("\n--- Admin Menu ---")
                    print("1. Run Attendance")
                    print("2. Run Add New Students")
                    print("3. Dump database to USB Flash Drive")
                    print("4. Reset Database")
                    print("5. Upload New Database")
                    print("0. Exit Program")
                    choice = input("Enter your choice: ")
                    if choice == "1":
                        print("Running Attendence...")
                        check_attendance()
                    elif choice == "2":
                        print("Running Add New Students...")
                        os.system("python3 newstd.py")
                    elif choice == "3":
                        print("Dumping Database...")
                        os.system("python3 dumpdb.py")
                    elif choice == "4":
                        print("Running Reset...")
                        os.system("python3 reset.py")
                    elif choice == "5":
                        print("Running Upload...")
                        os.system("python3 upload.py")
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

