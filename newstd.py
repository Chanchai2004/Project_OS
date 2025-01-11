import os
import time as t
import mysql.connector
from mfrc522 import SimpleMFRC522

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

        # หากพบ RFID ตรงกับเงื่อนไข ให้หยุดการทำงานทันที
        if rfid == "732749633633":
            print("RFID Admin detected. Switching to Admin mode.")
            return rfid

        # รับ student_id
        student_id = input("Enter student ID: ")

        # เพิ่มข้อมูลนักเรียนลงในตาราง students
        sql_insert_student = "INSERT INTO students (student_id, name, rfid) VALUES (%s, %s, %s)"
        cursor.execute(sql_insert_student, (student_id, name, rfid))
        db.commit()
        print(f"Student {name} (ID: {student_id}) added successfully!")

        # ดึงข้อมูลวิชาจากตาราง courses
        cursor.execute("SELECT course_id, course_name FROM courses")
        courses = cursor.fetchall()

        # แสดงรายการวิชา
        print("\nAvailable courses:")
        course_mapping = {}
        for idx, course in enumerate(courses, start=1):
            course_id, course_name = course
            course_mapping[idx] = course_id
            print(f"{idx}. {course_name} ({course_id})")
        print("0. Finish selection")

        # รับวิชาที่เลือก
        selected_courses = []
        while True:
            try:
                choice = int(input("Select a course by number (or 0 to finish): "))
                if choice == 0:
                    break
                if choice in course_mapping:
                    selected_courses.append(course_mapping[choice])
                    print(f"Course {course_mapping[choice]} added to student.")
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")

        # เพิ่มข้อมูลการเชื่อมโยงนักเรียนและวิชาลงใน student_courses
        sql_insert_student_course = "INSERT INTO student_courses (student_id, course_id) VALUES (%s, %s)"
        for course_id in selected_courses:
            cursor.execute(sql_insert_student_course, (student_id, course_id))
        db.commit()
        print("Student and courses linked successfully!")

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    finally:
        cursor.close()
        db.close()

def dump_database():
    """Dump the database and save to USB Flash Drive"""
    try:
        usb_mount_path = "/media/os/ESD-USB"
        if not os.path.exists(usb_mount_path):
            print("USB Flash Drive not found. Please insert the drive.")
            return

        now = t.strftime("%Y%m%d_%H%M%S")
        dump_file_path = os.path.join(usb_mount_path, f"attendance_db_{now}.sql")

        dump_command = [
            "mysqldump",
            "-u", "root",
            "--password=os123",
            "attendance_db"
        ]

        with open(dump_file_path, "w") as dump_file:
            os.system(" ".join(dump_command))

        print(f"Database dumped successfully to {dump_file_path}")

    except Exception as e:
        print("Failed to dump database:", e)

def main_loop():
    try:
        while True:
            print("\n--- Waiting for card scan ---")
            rfid = add_new_student()
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
