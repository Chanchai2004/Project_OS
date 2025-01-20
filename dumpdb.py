import os
import tkinter as tk
from tkinter import messagebox, filedialog
import time as t

# ฟังก์ชันสำหรับสำรองฐานข้อมูล
def dump_database(save_path):
    """ฟังก์ชันสำหรับสำรองฐานข้อมูล MySQL เป็นไฟล์ .sql ไปยัง path ที่เลือก"""
    try:
        # ใช้คำสั่ง mysqldump เพื่อสำรองข้อมูล
        dump_command = f"mysqldump -u root --password=os123 attendance_db > {save_path}"
        print(f"Running dump command: {dump_command}")
        result = os.system(dump_command)

        # ตรวจสอบว่าไฟล์ถูกสร้างขึ้นสำเร็จหรือไม่
        if result == 0 and os.path.exists(save_path):
            print(f"Database dumped successfully to {save_path}")
            messagebox.showinfo("Success", f"สำรองข้อมูลสำเร็จที่ {save_path}")
        else:
            print("Failed to create the dump file. Please check your mysqldump configuration.")
            messagebox.showerror("Error", "สำรองข้อมูลไม่สำเร็จ กรุณาตรวจสอบการตั้งค่า")

    except Exception as e:
        print("Failed to dump database:", e)
        messagebox.showerror("Error", f"เกิดข้อผิดพลาด: {e}")

# ฟังก์ชันสำหรับเลือก path และเรียก dump_database
def on_dump():
    # เปิดหน้าต่างให้เลือก path สำหรับบันทึกไฟล์
    save_path = filedialog.asksaveasfilename(defaultextension=".sql", filetypes=[("SQL Files", "*.sql")])
    if save_path:
        dump_database(save_path)

# UI Components
root = tk.Tk()
root.title("Dump Database to SQL File")
root.geometry("400x200")

# Label อธิบายการทำงาน
info_label = tk.Label(root, text="สำรองฐานข้อมูล MySQL ไปยังไฟล์ .sql", font=("Arial", 12))
info_label.pack(pady=20)

# ปุ่มสำหรับเริ่มสำรองข้อมูล
dump_button = tk.Button(root, text="Dump Database", font=("Arial", 12), command=on_dump)
dump_button.pack(pady=20)

# เริ่มต้น UI
root.mainloop()
