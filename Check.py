import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import os
import pytz
import subprocess  # เพิ่มบรรทัดนี้
import mysql.connector
from datetime import timedelta
from mfrc522 import SimpleMFRC522

# ตัวแปรที่ใช้สำหรับ Reader
reader = SimpleMFRC522()

# Timezone
bangkok_tz = pytz.timezone('Asia/Bangkok')

# ฟังก์ชันเชื่อมต่อกับฐานข้อมูล
def connect_to_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="os123",
        database="attendance_db"
    )

def auto_close_error(title, message, duration=2000):
    error_window = tk.Toplevel()
    error_window.title(title)
    error_window.geometry("300x100")
    error_window.resizable(False, False)
    label = tk.Label(error_window, text=message, font=("Arial", 12), wraplength=280, justify="center")
    label.pack(pady=20)
    error_window.after(duration, error_window.destroy)

def auto_close_error2(title, message, duration=2000):
    error_window = tk.Toplevel()
    error_window.title(title)
    error_window.geometry("400x200")
    error_window.resizable(False, False)
    label = tk.Label(error_window, text=message, font=("Arial", 12), wraplength=280, justify="center")
    label.pack(pady=20)
    error_window.after(duration, error_window.destroy)

# ฟังก์ชันเช็คการเข้าเรียน
def check_attendance():
    db = connect_to_db()
    cursor = db.cursor()

    try:
        rfid = str(reader.read()[0]).strip()
        print(f"RFID: {rfid}")

        if rfid == "732749633633":
            print("Detected RFID for switching to main_menu.py")
            cursor.close()
            db.close()
            
            # ตรวจสอบว่า main_menu.py กำลังทำงานอยู่หรือไม่
            process_check = subprocess.run(
                ["pgrep", "-f", "main_menu.py"],  # ค้นหา process ด้วยชื่อ main_menu.py
                stdout=subprocess.PIPE,          # เก็บผลลัพธ์
                text=True
            )
            
            if process_check.stdout.strip():  # ถ้ามีผลลัพธ์แสดงว่ากำลังรันอยู่
                print("main_menu.py is already running.")
            else:
                print("Starting main_menu.py...")
                os.system("python3 /home/os/main_menu.py &")  # รัน main_menu.py ใน background

            root.destroy()  # ปิด tkinter
            exit()  # ออกจากโปรแกรม

        cursor.execute("SELECT student_id FROM students WHERE rfid = %s", (rfid,))
        student = cursor.fetchone()
        if not student:
            auto_close_error("Error", "ไม่พบข้อมูลนักเรียน", duration=3000)
            return
        student_id = student[0]

        cursor.execute("SELECT course_id FROM student_courses WHERE student_id = %s", (student_id,))
        courses = cursor.fetchall()
        if not courses:
            auto_close_error("Error", "นักเรียนยังไม่ได้ลงทะเบียนวิชาเรียน", duration=3000)
            return

        now = datetime.now(bangkok_tz)
        valid_schedule_id = None
        course_name = None
        start_time = None
        end_time = None

        for course in courses:
            course_id = course[0]
            cursor.execute(
                """
                SELECT schedule_id, course_name, start_time, end_time FROM course_schedule
                INNER JOIN courses ON course_schedule.course_id = courses.course_id
                WHERE course_schedule.course_id = %s AND start_time <= %s AND end_time >= %s
                """,
                (course_id, now.time(), now.time())
            )
            schedule = cursor.fetchone()
            if schedule:
                valid_schedule_id, course_name, start_time, end_time = schedule
                break

        if not valid_schedule_id:
            auto_close_error("Error", "ไม่พบวิชาที่มีการเรียนในเวลานี้", duration=3000)
            return

        # ตรวจสอบและแปลง start_time และ end_time เป็น datetime.time
        if isinstance(start_time, timedelta):
            start_time = (datetime.min + start_time).time()
        if isinstance(end_time, timedelta):
            end_time = (datetime.min + end_time).time()

        start_time = datetime.combine(now.date(), start_time).replace(tzinfo=bangkok_tz)
        end_time = datetime.combine(now.date(), end_time).replace(tzinfo=bangkok_tz)

        print(f"Start Time: {start_time}")
        print(f"End Time: {end_time}")

        cursor.execute(
            "SELECT * FROM attendance WHERE student_id = %s AND schedule_id = %s",
            (student_id, valid_schedule_id)
        )
        if cursor.fetchone():
            auto_close_error("Warning", "นักเรียนคนนี้ได้เช็คชื่อในวิชานี้ไปแล้ว", duration=2000)
            return
        print(">>>>>>>>>>>>>>>>>>>>>1",now)
        print(">>>>>>>>>>>>>>>>>>>>>2",start_time+ timedelta(minutes=15))
        print(">>>>>>>>>>>>>>>>>>>>>3",start_time+ timedelta(minutes=30))
        if start_time + timedelta(minutes=15) >= now :
            status = "Present"
        elif start_time + timedelta(minutes=30) >= now :
            status = "Late"
        else:
            status = "Absent"

        print(f"Status: {status}")

        cursor.execute(
            """
            INSERT INTO attendance (student_id, schedule_id, timestamp, status)
            VALUES (%s, %s, %s, %s)
            """,
            (student_id, valid_schedule_id, now, status)
        )
        db.commit()
        auto_close_error2("Success", f"เช็คชื่อสำเร็จ!\n\n"
            f"Student ID: {student_id}\n"
            f"Course ID: {course_id}\n"
            f"Course Name: {course_name}\n"
            f"Timestamp: {now.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Status: {status}", duration=2000)
        

    except mysql.connector.Error as err:
        print(f"เกิดข้อผิดพลาด: {err}")
        auto_close_error("Error", f"เกิดข้อผิดพลาด: {err}", duration=3000)

    finally:
        cursor.close()
        db.close()

# UI Components
root = tk.Tk()
root.title("ระบบเช็คชื่อ")
root.geometry("400x300")

instruction_label = tk.Label(root, text="โปรดสแกนบัตรนักศึกษา", font=("Arial", 20))
instruction_label.pack(pady=20)

result_label = tk.Label(root, text="ผลลัพธ์จะปรากฏที่นี่", font=("Arial", 12))
result_label.pack(pady=20)

def loop_check_attendance():
    check_attendance()
    root.after(2000, loop_check_attendance)

loop_check_attendance()

root.mainloop()
