import os
import time as t
import mysql.connector
from mfrc522 import SimpleMFRC522
import tkinter as tk
from tkinter import messagebox

# RFID Reader
reader = SimpleMFRC522()

# ฟังก์ชันเชื่อมต่อฐานข้อมูล
def connect_to_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="os123",  # เปลี่ยนตาม password ของคุณ
        database="attendance_db"
    )

# ฟังก์ชันสำหรับอัปเดต RFID ของนักเรียน
def update_student_rfid(student_id):
    db = connect_to_db()
    cursor = db.cursor()

    try:
        # ค้นหานักเรียนจาก student_id
        cursor.execute("SELECT student_id, name, rfid FROM students WHERE student_id = %s", (student_id,))
        student = cursor.fetchone()

        if student:
            existing_student_id, existing_student_name, existing_rfid = student
            print(f"Student found: {existing_student_name} (ID: {existing_student_id})")
            print(f"Current RFID: {existing_rfid}")
            print("Place your card to update RFID...")

            # อ่าน RFID ใหม่
            id, text = reader.read()
            new_rfid = str(id).strip()
            print(f"New RFID: {new_rfid}")

            # อัปเดต RFID ในฐานข้อมูล
            cursor.execute("UPDATE students SET rfid = %s WHERE student_id = %s", (new_rfid, student_id))
            db.commit()
            print(f"RFID for student {existing_student_name} updated successfully!")
            messagebox.showinfo("Success", f"RFID for student {existing_student_name} updated successfully!")
        else:
            messagebox.showerror("Error", "Student not found with the provided ID.")

    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Database error: {err}")
    finally:
        cursor.close()
        db.close()

# ฟังก์ชันที่เรียกเมื่อกดปุ่ม Next
def on_next_button_click():
    student_id = entry_student_id.get()  # รับค่า student_id จากช่องกรอกข้อความ
    if student_id:
        print(f"Looking up student with ID: {student_id}")
        status_label.config(text="Place your Student card")  # อัปเดตข้อความแสดงสถานะ
        root.update()  # อัปเดตหน้าจอ GUI
        update_student_rfid(student_id)
    else:
        messagebox.showwarning("Input Error", "Please enter a student ID.")

# สร้างหน้าต่าง GUI ด้วย Tkinter
root = tk.Tk()
root.title("Update Student RFID")

# กำหนดขนาดหน้าต่าง
root.geometry("400x250")

# ส่วนข้อความ
label = tk.Label(root, text="Enter Student ID:", font=("Arial", 14), anchor="w")
label.pack(pady=10)

# ช่องกรอก student_id
entry_student_id = tk.Entry(root, font=("Arial", 14))
entry_student_id.pack(pady=10)

# ปุ่ม Next
next_button = tk.Button(root, text="Next", font=("Arial", 14), command=on_next_button_click)
next_button.pack(pady=10)

# ป้ายข้อความสถานะ
status_label = tk.Label(root, text="", font=("Arial", 14))
status_label.pack(pady=10)

# เริ่ม GUI
root.mainloop()
