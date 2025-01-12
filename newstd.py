import os
import time as t
import mysql.connector
from mfrc522 import SimpleMFRC522
import sqlite3
# ตั้งค่า Reader
reader = SimpleMFRC522()

# เชื่อมต่อฐานข้อมูล
def connect_to_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="os123",  # แก้ไขตามรหัสผ่านของฐานข้อมูลคุณ
        database="attendance_db"
    )


def add_new_student():
    db = connect_to_db()
    cursor = db.cursor()

    try:
        # สแกนบัตร RFID
        print("Place your card to register")
        id, text = reader.read()
        rfid = str(id).strip()
        name = text.strip()
        print(f"RFID: {rfid}")
        print(f"Name: {name}")

        # หากพบ RFID Admin ให้หยุดทำงานทันที
        if rfid == "732749633633":
            print("RFID Admin detected. Switching to Admin mode.")
            return rfid
        
        # ตรวจสอบการลงทะเบียนซ้ำในตาราง students
        cursor.execute("SELECT student_id, name FROM students WHERE rfid = %s", (rfid,))
        existing_student = cursor.fetchone()
        if existing_student:
            existing_student_id, existing_student_name = existing_student
            print(f"นักเรียน {existing_student_name} (ID: {existing_student_id}) ได้ลงทะเบียนแล้ว")
            return

        # รับ student_id
        student_id = input("Enter student ID: ")

        # เพิ่มข้อมูลนักเรียนลงในตาราง students
        sql_insert_student = "INSERT INTO students (student_id, name, rfid) VALUES (%s, %s, %s)"
        cursor.execute(sql_insert_student, (student_id, name, rfid))
        db.commit()
        print(f"Student {name} (ID: {student_id}) added successfully!")

        # ดึงข้อมูลตาราง course_schedules เพื่อแสดงคอร์ส
        cursor.execute("""
            SELECT c.course_id, cs.day_of_week, cs.start_time, cs.end_time
            FROM course_schedule cs
            JOIN courses c ON cs.course_id = c.course_id
        """)
        schedules = cursor.fetchall()

        # แสดงรายการคอร์สที่มี
        print("\nAvailable courses:")
        course_mapping = {}
        for idx, schedule in enumerate(schedules, start=1):
            course_id, day_of_week, start_time, end_time = schedule
            course_mapping[idx] = course_id
            print(f"{idx}. {course_id} - {day_of_week} ({start_time} - {end_time})")
        print("0. Finish selection")

        # รับคอร์สที่ต้องการลงทะเบียน
        selected_courses = []
        while True:
            try:
                choice = int(input("Select a course by number (or 0 to finish): "))
                if choice == 0:
                    break
                if choice in course_mapping:
                    selected_courses.append(course_mapping[choice])
                    course_id = course_mapping[choice]
                    print(f"Course {course_id} added to student.")
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")

        # เพิ่มข้อมูลการเชื่อมโยงนักเรียนและวิชาลงใน student_courses
        sql_insert_student_course = """
            INSERT INTO student_courses (student_id, course_id) VALUES (%s, %s)
        """
        for course_id in selected_courses:
            cursor.execute(sql_insert_student_course, (student_id, course_id))
        db.commit()
        print("Student and courses linked successfully!")

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    finally:
        cursor.close()
        db.close()





def main_loop():
    try:
        while True:
            print("\n--- Waiting for card scan ---")
            rfid = add_new_student()
            if rfid == "732749633633":
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
                        os.system("python3 attend.py")
                    elif choice == "2":
                        print("Running Add New Students...")
                        add_new_student()
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


                    
