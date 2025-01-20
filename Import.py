import tkinter as tk
from tkinter import filedialog, messagebox
import os
import pandas as pd
import mysql.connector

def select_file():
    """เปิดหน้าต่างเลือกไฟล์ .xlsx"""
    filepath = filedialog.askopenfilename(
        title="Select an Excel file",
        filetypes=(("Excel Files", "*.xlsx"), ("All Files", "*.*"))
    )
    if filepath:
        entry_file_path.delete(0, tk.END)
        entry_file_path.insert(0, filepath)

def fill_rfid_with_unknown(df, column_name):
    """เติมค่าที่ว่างในคอลัมน์ rfid ด้วย unknown1, unknown2, ..."""
    unknown_counter = 1
    def fill_value(value):
        nonlocal unknown_counter
        if pd.isna(value) or value == "":
            filled_value = f"unknown{unknown_counter}"
            unknown_counter += 1
            return filled_value
        return value

    df[column_name] = df[column_name].apply(fill_value)
    return df

def upload_file():
    """อัปโหลดไฟล์ .xlsx ไปยัง MySQL"""
    filepath = entry_file_path.get()

    # กำหนดค่า default สำหรับ MySQL
    mysql_user = "root"
    mysql_password = "os123"

    if not filepath or not os.path.exists(filepath):
        messagebox.showerror("Error", "Please select a valid Excel file.")
        return

    try:
        # อ่านไฟล์ Excel
        df = pd.read_excel(filepath)

        # ตัวอย่างคอลัมน์
        table_name = "students"
        table_columns = ["student_id", "name", "rfid"]

        # ตรวจสอบคอลัมน์
        if not all(col in df.columns for col in table_columns):
            messagebox.showerror("Error", "Excel columns do not match the table structure.")
            return

        # เติมค่าที่ว่างในคอลัมน์ rfid ด้วย unknown1, unknown2, ...
        df = fill_rfid_with_unknown(df, "rfid")

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

        for _, row in df.iterrows():
            sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            try:
                cursor.execute(sql, tuple(row))
            except mysql.connector.IntegrityError as e:
                print(f"Skipped row due to error: {e}")

        conn.commit()
        cursor.close()
        conn.close()

        messagebox.showinfo("Success", "Data uploaded successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to upload file: {e}")

def create_gui():
    """สร้างหน้าต่าง GUI สำหรับ Import"""
    global entry_file_path

    root = tk.Tk()
    root.title("Import Students")
    root.geometry("500x300")

    # Label และ Entry สำหรับเลือกไฟล์
    lbl_file = tk.Label(root, text="Select Excel File:", font=("Arial", 12))
    lbl_file.pack(pady=10)
    entry_file_path = tk.Entry(root, width=50, font=("Arial", 12))
    entry_file_path.pack(pady=5)
    btn_browse = tk.Button(root, text="Browse", command=select_file, font=("Arial", 10))
    btn_browse.pack(pady=5)

    # ปุ่ม Upload
    btn_upload = tk.Button(root, text="Upload File", command=upload_file, font=("Arial", 14), bg="green", fg="white")
    btn_upload.pack(pady=20)

    # เริ่ม GUI
    root.mainloop()

if __name__ == "__main__":
    create_gui()
