import tkinter as tk
from tkinter import messagebox, filedialog
import pandas as pd
import mysql.connector
from datetime import datetime

# ฟังก์ชันเชื่อมต่อกับฐานข้อมูล
def connect_to_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="os123",
        database="attendance_db"
    )

# ฟังก์ชันเพื่อดึงข้อมูลจากฐานข้อมูลและส่งออกเป็น Excel
def export_to_excel(course_id, save_path):
    db = connect_to_db()
    cursor = db.cursor()

    try:
        # ค้นหา schedule_id จาก course_id ในตาราง course_schedule
        cursor.execute(
            "SELECT schedule_id FROM course_schedule WHERE course_id = %s", (course_id,)
        )
        schedule = cursor.fetchone()
        if not schedule:
            messagebox.showerror("Error", "ไม่พบตารางเรียนสำหรับ course_id นี้")
            return

        schedule_id = schedule[0]

        # ทำการ LEFT JOIN ระหว่าง attendance, student, และ course_schedule
        query = """
            SELECT 
                s.student_id, s.name, cs.course_id, a.timestamp, a.status
            FROM 
                attendance a
            LEFT JOIN students s ON a.student_id = s.student_id
            LEFT JOIN course_schedule cs ON a.schedule_id = cs.schedule_id
            WHERE cs.course_id = %s
        """

        cursor.execute(query, (course_id,))
        result = cursor.fetchall()

        if not result:
            messagebox.showerror("Error", "ไม่พบข้อมูลการเข้าเรียนสำหรับวิชานี้")
            return

        # สร้าง DataFrame จากผลลัพธ์
        df = pd.DataFrame(result, columns=["student_id", "name", "course_id", "timestamp", "status"])

        # ส่งออกข้อมูลไปยังไฟล์ Excel
        df.to_excel(save_path, index=False, engine='openpyxl')

        messagebox.showinfo("Success", f"ส่งออกข้อมูลสำเร็จที่ {save_path}")

    except mysql.connector.Error as err:
        print(f"เกิดข้อผิดพลาด: {err}")
        messagebox.showerror("Error", f"เกิดข้อผิดพลาด: {err}")

    finally:
        cursor.close()
        db.close()

# ฟังก์ชันสำหรับเปิดหน้าต่างกรอกข้อมูลและเลือก path
def on_export():
    course_id = course_id_entry.get()
    if not course_id:
        messagebox.showerror("Error", "กรุณากรอกรายวิชา")
        return

    # เปิดหน้าต่างให้เลือก path สำหรับบันทึกไฟล์
    save_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])
    if save_path:
        export_to_excel(course_id, save_path)

# UI Components
root = tk.Tk()
root.title("Export Attendance to Excel")
root.geometry("400x200")

# Label และ Input สำหรับกรอกรายวิชา
course_id_label = tk.Label(root, text="กรุณากรอกรายวิชาที่ต้องการ Export (course_id):", font=("Arial", 12))
course_id_label.pack(pady=10)

course_id_entry = tk.Entry(root, font=("Arial", 12))
course_id_entry.pack(pady=5)

# ปุ่มสำหรับการส่งออกข้อมูล
export_button = tk.Button(root, text="Export", font=("Arial", 12), command=on_export)
export_button.pack(pady=20)

# เริ่มต้น UI
root.mainloop()
