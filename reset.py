import os
import time as t
import mysql.connector
from mfrc522 import SimpleMFRC522

# ตั้งค่า Reader
reader = SimpleMFRC522()

# ฟังก์ชันสำหรับเชื่อมต่อฐานข้อมูล
def connect_to_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="os123",  # แก้ไขตามรหัสผ่านของฐานข้อมูลคุณ
        database="attendance_db"
    )

def reset_database():
    db = connect_to_db()
    cursor = db.cursor()

    print("Place your card to Authentication")
    id, text = reader.read()
    rfid = str(id).strip()

    if rfid == "732749633633":
        try:
            print("Resetting database...")

            # Save database ??????
            dump_database()

            # ????????????? Foreign Key Constraints ????????
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

            # ???????????????? attendance
            cursor.execute("DELETE FROM attendance")
            print("Cleared attendance table.")

            # ???????????????? student_courses
            cursor.execute("DELETE FROM student_courses")
            print("Cleared student_courses table.")

            # ???????????????? course_schedules
            cursor.execute("DELETE FROM course_schedule")
            print("Cleared course_schedule table.")

            # ???????????????? courses
            cursor.execute("DELETE FROM courses")
            print("Cleared courses table.")

            # ???????????????? students ??????? rfid = '732749633633'
            cursor.execute("DELETE FROM students")
            print("Cleared students table.")

            # ?????????????? Foreign Key Constraints ????????
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

            # ?????????????????
            db.commit()
            print("Database reset successfully.")
            print(" ")
            print("Task completed successfully.")

        except mysql.connector.Error as err:
            print(f"Database error: {err}")
        finally:
            cursor.close()
            db.close()
    else:
        print(" ")
        print("Authentication failed.")




# ฟังก์ชันสำหรับสำรองฐานข้อมูล
def dump_database():
    """ฟังก์ชันสำหรับสำรองฐานข้อมูล MySQL เป็นไฟล์ .sql บน USB Flash Drive"""
    try:
        # ตรวจสอบ USB Mount
        usb_mount_path = "/media/os/ESD-USB"
        if not os.path.exists(usb_mount_path):
            print("USB Flash Drive not found. Please insert the drive.")
            return

        # สร้างชื่อไฟล์ .sql
        now = t.strftime("%Y%m%d_%H%M%S")
        dump_file_path = os.path.join(usb_mount_path, f"attendance_db_{now}.sql")

        # ใช้คำสั่ง mysqldump เพื่อสำรองข้อมูล
        dump_command = f"mysqldump -u root --password=os123 attendance_db > {dump_file_path}"

        print(f"Running dump command: {dump_command}")
        result = os.system(dump_command)

        # ตรวจสอบว่าไฟล์ถูกสร้างขึ้นสำเร็จหรือไม่
        if result == 0 and os.path.exists(dump_file_path):
            print(f"Database dumped successfully to {dump_file_path}")
        else:
            print("Failed to create the dump file. Please check your mysqldump configuration.")

    except Exception as e:
        print("Failed to dump database:", e)

def main():
    try:
        print("Starting automatic task...")
        # เรียกฟังก์ชันที่ต้องการทำงาน
        reset_database()  # เปลี่ยนเป็นฟังก์ชันอื่นได้ เช่น reset_database()
        
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print("Program terminated.")

# เรียกใช้โปรแกรมหลัก
if __name__ == "__main__":
    main()
