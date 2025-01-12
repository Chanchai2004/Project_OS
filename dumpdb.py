import os
import time as t
import mysql.connector

# ฟังก์ชันสำหรับเชื่อมต่อฐานข้อมูล
def connect_to_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="os123",  # แก้ไขตามรหัสผ่านของฐานข้อมูลคุณ
        database="attendance_db"
    )

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

# ฟังก์ชันหลัก
def main():
    print("Dumping database to USB Flash Drive...")
    dump_database()
    print("Program completed. Exiting now.")

# เรียกใช้โปรแกรมหลัก
if __name__ == "__main__":
    main()