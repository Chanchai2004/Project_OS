import os
import pandas as pd
import mysql.connector

def find_xlsx_files(directory):
    """ค้นหาไฟล์ .xlsx ในไดเรกทอรีที่กำหนด"""
    if not os.path.exists(directory):
        print(f"Directory not found: {directory}")
        return []

    return [f for f in os.listdir(directory) if f.endswith(".xlsx")]

def fill_nan_with_unknown(df, table_columns):
    """แทนค่าที่เป็น NaN ด้วย unknown ไล่ไปเรื่อยๆ"""
    counter = {col: 1 for col in table_columns}

    def replace_nan(value, column):
        if pd.isna(value):  # ถ้าเป็น NaN
            current_count = counter[column]
            counter[column] += 1
            return f"unknown{current_count}"
        return value

    for column in table_columns:
        df[column] = df[column].apply(lambda x: replace_nan(x, column))
    
    return df

def upload_xlsx_to_mysql(xlsx_file, mysql_user, mysql_password, table_name, table_columns):
    try:
        # อ่านไฟล์ Excel
        df = pd.read_excel(xlsx_file)

        # ตรวจสอบว่า DataFrame มีคอลัมน์ที่ตรงกับตารางหรือไม่
        if not all(col in df.columns for col in table_columns):
            print(f"Error: Columns in the Excel file do not match the target table '{table_name}'.")
            return

        # กรองเฉพาะคอลัมน์ที่ตรงกับตาราง
        df = df[table_columns]

        # แทนค่าที่เป็น NaN ด้วย unknown ไล่ไปเรื่อย ๆ
        df = fill_nan_with_unknown(df, table_columns)

        # เชื่อมต่อกับ MySQL
        conn = mysql.connector.connect(
            host="localhost",
            user=mysql_user,
            password=mysql_password,
            database="attendance_db"
        )
        cursor = conn.cursor()

        # เตรียมคำสั่ง SQL
        columns = ", ".join(table_columns)
        placeholders = ", ".join(["%s"] * len(table_columns))

        # เพิ่มข้อมูลในแต่ละแถวลงในตาราง
        for _, row in df.iterrows():
            sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            try:
                cursor.execute(sql, tuple(row))
            except mysql.connector.IntegrityError as e:
                print(f"Skipped row with duplicate entry or error: {e}")

        conn.commit()
        print(f"Data successfully uploaded to the '{table_name}' table.")

    except Exception as e:
        print(f"Error uploading Excel file: {e}")

    finally:
        cursor.close()
        conn.close()

def main():
    # กำหนดไดเรกทอรีของไฟล์ .xlsx
    directory = "/media/os/ESD-USB"

    # ค้นหาไฟล์ .xlsx ในไดเรกทอรี
    xlsx_files = find_xlsx_files(directory)

    if not xlsx_files:
        print("No .xlsx files found in the specified directory.")
        return

    print("\nAvailable .xlsx files:")
    for idx, file in enumerate(xlsx_files, start=1):
        print(f"{idx}. {file}")
    print("0. Exit")

    # เลือกไฟล์
    while True:
        try:
            choice = int(input("Select a file by number (or 0 to exit): "))
            if choice == 0:
                print("Exiting...")
                return
            if 1 <= choice <= len(xlsx_files):
                selected_file = os.path.join(directory, xlsx_files[choice - 1])
                print(f"Selected file: {selected_file}")
                break
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    # แสดงตัวเลือกตาราง
    tables = {
        1: {"name": "students", "columns": ["student_id", "name", "rfid"]},
        2: {"name": "courses", "columns": ["course_id", "course_name", "teacher_name"]}
    }

    print("\nAvailable tables:")
    for idx, table in tables.items():
        print(f"{idx}. {table['name']} ({', '.join(table['columns'])})")
    print("0. Exit")

    # เลือกตาราง
    while True:
        try:
            table_choice = int(input("Select a table by number (or 0 to exit): "))
            if table_choice == 0:
                print("Exiting...")
                return
            if table_choice in tables:
                selected_table = tables[table_choice]
                print(f"Selected table: {selected_table['name']}")
                break
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    # รับข้อมูล MySQL username และ password
    mysql_user = input("Enter MySQL username: ")
    mysql_password = input("Enter MySQL password: ")

    # อัปโหลดข้อมูล
    upload_xlsx_to_mysql(
        selected_file,
        mysql_user,
        mysql_password,
        selected_table["name"],
        selected_table["columns"]
    )

if __name__ == "__main__":
    main()
