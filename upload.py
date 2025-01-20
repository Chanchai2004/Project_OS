import os
import subprocess
import tkinter as tk
from tkinter import messagebox, filedialog

# ฟังก์ชันสำหรับอัปโหลดไฟล์ SQL เข้าสู่ MySQL
def upload_sql_to_mysql(sql_file, mysql_user, mysql_password):
    try:
        # ใช้คำสั่ง mysql สำหรับนำเข้าข้อมูล
        command = f"mysql -u {mysql_user} --password={mysql_password} attendance_db < {sql_file}"
        print(f"Running command: {command}")
        result = subprocess.run(command, shell=True)

        if result.returncode == 0:
            messagebox.showinfo("Success", f"กู้คืนฐานข้อมูลสำเร็จจาก {sql_file}")
        else:
            messagebox.showerror("Error", f"เกิดข้อผิดพลาดในการกู้คืนฐานข้อมูล\nReturn code: {result.returncode}")
    except Exception as e:
        messagebox.showerror("Error", f"เกิดข้อผิดพลาดในการอัปโหลดไฟล์ SQL:\n{e}")

# ฟังก์ชันสำหรับเรียกอัปโหลด SQL
def on_upload_sql():
    # เปิดหน้าต่างให้เลือกไฟล์ .sql
    sql_file = filedialog.askopenfilename(
        title="เลือกไฟล์ .sql สำหรับกู้คืน",
        filetypes=[("SQL Files", "*.sql")]
    )
    if not sql_file:
        messagebox.showerror("Error", "ไม่ได้เลือกไฟล์ .sql")
        return

    # ขอข้อมูล MySQL User และ Password
    mysql_user = user_entry.get()
    mysql_password = password_entry.get()

    if not mysql_user or not mysql_password:
        messagebox.showerror("Error", "กรุณากรอกข้อมูล MySQL username และ password")
        return

    # นำเข้าไฟล์ SQL เข้าสู่ฐานข้อมูล
    upload_sql_to_mysql(sql_file, mysql_user, mysql_password)

    # ปิดโปรแกรมหลังจากเสร็จสิ้น
    root.destroy()

# UI Components
root = tk.Tk()
root.title("Upload SQL File to Restore Database")
root.geometry("500x300")

# Label สำหรับกรอกข้อมูล MySQL User
user_label = tk.Label(root, text="MySQL Username:", font=("Arial", 12))
user_label.pack(pady=5)
user_entry = tk.Entry(root, font=("Arial", 12))
user_entry.pack(pady=5)

# Label สำหรับกรอกข้อมูล MySQL Password
password_label = tk.Label(root, text="MySQL Password:", font=("Arial", 12))
password_label.pack(pady=5)
password_entry = tk.Entry(root, font=("Arial", 12), show="*")
password_entry.pack(pady=5)

# ปุ่มสำหรับอัปโหลด SQL
upload_button = tk.Button(root, text="Upload SQL File", font=("Arial", 12), command=on_upload_sql)
upload_button.pack(pady=20)

# เริ่มต้น UI
root.mainloop()
