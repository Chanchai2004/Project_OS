import os
import mysql.connector
import subprocess

# ฟังก์ชันสำหรับเชื่อมต่อ MySQL Database
def connect_to_mysql_db(user, password):
    return mysql.connector.connect(
        host="localhost",
        user=user,
        password=password,
        database="attendance_db"
    )

# ฟังก์ชันสำหรับค้นหาไฟล์ .sql ใน Flash Drive
def find_sql_files(flash_drive_path):
    if not os.path.exists(flash_drive_path):
        print("Flash drive not found. Please insert the drive.")
        return []

    return [f for f in os.listdir(flash_drive_path) if f.endswith(".sql")]

# ฟังก์ชันสำหรับอัปโหลดไฟล์ SQL เข้าสู่ MySQL
def upload_sql_to_mysql(sql_file, mysql_user, mysql_password):
    try:
        # ใช้คำสั่ง mysql สำหรับนำเข้าข้อมูล
        command = f"mysql -u {mysql_user} --password={mysql_password} attendance_db < {sql_file}"
        print(f"Running command: {command}")
        result = subprocess.run(command, shell=True)

        if result.returncode == 0:
            print(f"Database successfully restored from {sql_file}")
        else:
            print(f"Error restoring database from {sql_file}. Return code: {result.returncode}")
    except Exception as e:
        print(f"Error uploading SQL file: {e}")

# Main Function
def main():
    flash_drive_path = "/media/os/ESD-USB"
    sql_files = find_sql_files(flash_drive_path)

    if not sql_files:
        print("No .sql files found on the flash drive.")
        return

    print("\nAvailable .sql files:")
    for idx, file in enumerate(sql_files, start=1):
        print(f"{idx}. {file}")
    print("0. Exit")

    while True:
        try:
            choice = int(input("Select a file by number (or 0 to exit): "))
            if choice == 0:
                print("Exiting...")
                return
            if 1 <= choice <= len(sql_files):
                selected_file = os.path.join(flash_drive_path, sql_files[choice - 1])
                print(f"Selected file: {selected_file}")
                break
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    # รับข้อมูล User และ Password สำหรับ MySQL
    mysql_user = input("Enter MySQL username: ")
    mysql_password = input("Enter MySQL password: ")

    # นำเข้าไฟล์ SQL เข้าสู่ฐานข้อมูล
    upload_sql_to_mysql(selected_file, mysql_user, mysql_password)

if __name__ == "__main__":
    main()
