import os
import time as t
import mysql.connector
from mfrc522 import SimpleMFRC522
import tkinter as tk
from tkinter import messagebox

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

# ฟังก์ชันสำหรับรีเซ็ตฐานข้อมูล
def reset_database():
    db = connect_to_db()
    cursor = db.cursor()

    try:
        # อ่านข้อมูล RFID สำหรับยืนยัน
        messagebox.showinfo("Authentication", "กรุณาวางบัตรเจ้าหน้าที่เพื่อยืนยันการรีเซ็ตฐานข้อมูล")
        id, text = reader.read()
        rfid = str(id).strip()

        # ตรวจสอบว่า RFID ตรงกับรหัสที่กำหนด
        if rfid == "732749633633":
            messagebox.showinfo("Processing", "กำลังสำรองและรีเซ็ตฐานข้อมูล...")

            # ปิด Foreign Key Constraints
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

            # ลบข้อมูลในแต่ละตาราง
            cursor.execute("DELETE FROM attendance")
            cursor.execute("DELETE FROM student_courses")
            cursor.execute("DELETE FROM course_schedule")
            cursor.execute("DELETE FROM courses")
            cursor.execute("DELETE FROM students")

            # เปิด Foreign Key Constraints
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

            # Commit การเปลี่ยนแปลง
            db.commit()
            messagebox.showinfo("Success", "รีเซ็ตฐานข้อมูลสำเร็จ!")
        else:
            messagebox.showerror("Error", "การยืนยันล้มเหลว กรุณาลองใหม่อีกครั้ง")

    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"เกิดข้อผิดพลาด: {err}")
    except Exception as e:
        messagebox.showerror("Error", f"เกิดข้อผิดพลาด: {e}")
    finally:
        cursor.close()
        db.close()

# ฟังก์ชันสำหรับเริ่มกระบวนการรีเซ็ต
def on_reset():
    reset_database()
    root.destroy()  # ปิดหน้าต่างหลังจากเสร็จสิ้น

# UI Components
root = tk.Tk()
root.title("Reset Database")
root.geometry("400x200")

# Label อธิบายการทำงาน
info_label = tk.Label(root, text="คลิกปุ่มด้านล่างเพื่อรีเซ็ตฐานข้อมูล", font=("Arial", 12))
info_label.pack(pady=20)

# ปุ่มสำหรับเริ่มกระบวนการรีเซ็ต
reset_button = tk.Button(root, text="Reset Database", font=("Arial", 12), command=on_reset)
reset_button.pack(pady=20)

# เริ่มต้น UI
root.mainloop()
