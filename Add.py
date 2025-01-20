import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

def add_course_to_db(course_id, course_name, teacher_name, day_of_week, start_time, end_time):
    """เพิ่มข้อมูลลงในฐานข้อมูล"""
    try:
        # เชื่อมต่อกับฐานข้อมูล
        conn = mysql.connector.connect(
            host="localhost",
            user="root",  # เปลี่ยนตาม username ฐานข้อมูลของคุณ
            password="os123",  # เปลี่ยนตาม password ฐานข้อมูลของคุณ
            database="attendance_db"
        )
        cursor = conn.cursor()

        # เพิ่มข้อมูลลงในตาราง courses
        cursor.execute(
            "INSERT INTO courses (course_id, course_name, teacher_name) VALUES (%s, %s, %s)",
            (course_id, course_name, teacher_name)
        )

        # เพิ่มข้อมูลลงในตาราง course_schedule
        cursor.execute(
            "INSERT INTO course_schedule (course_id, day_of_week, start_time, end_time) VALUES (%s, %s, %s, %s)",
            (course_id, day_of_week, start_time, end_time)
        )

        conn.commit()
        cursor.close()
        conn.close()
        messagebox.showinfo("Success", "Course added successfully!")
    except mysql.connector.Error as e:
        messagebox.showerror("Error", f"Failed to add course: {e}")

def create_add_course_gui():
    """สร้าง GUI สำหรับ Add Course"""
    def handle_create():
        # ดึงค่าจาก input fields
        course_id = entry_course_id.get()
        course_name = entry_course_name.get()
        teacher_name = entry_teacher_name.get()
        day_of_week = combobox_day_of_week.get()  # ใช้ค่าจาก combobox แทน
        start_time = combobox_start_time.get()
        end_time = combobox_end_time.get()

        if not (course_id and course_name and teacher_name and day_of_week and start_time and end_time):
            messagebox.showwarning("Warning", "Please fill in all fields.")
            return

        add_course_to_db(course_id, course_name, teacher_name, day_of_week, start_time, end_time)
        
        # ปิดหน้าต่างหลังจากเพิ่มข้อมูลเสร็จ
        root.destroy()

    root = tk.Tk()
    root.title("Add Course")
    root.geometry("400x400")

    # ตั้งค่า Grid Layout
    root.columnconfigure(1, weight=1)

    # Row 0: Course ID
    tk.Label(root, text="Course ID:", font=("Arial", 12), anchor="w").grid(row=0, column=0, padx=10, pady=5, sticky="w")
    entry_course_id = tk.Entry(root, font=("Arial", 12))
    entry_course_id.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

    # Row 1: Course Name
    tk.Label(root, text="Course Name:", font=("Arial", 12), anchor="w").grid(row=1, column=0, padx=10, pady=5, sticky="w")
    entry_course_name = tk.Entry(root, font=("Arial", 12))
    entry_course_name.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

    # Row 2: Teacher Name
    tk.Label(root, text="Teacher Name:", font=("Arial", 12), anchor="w").grid(row=2, column=0, padx=10, pady=5, sticky="w")
    entry_teacher_name = tk.Entry(root, font=("Arial", 12))
    entry_teacher_name.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

    # Row 3: Day of Week
    tk.Label(root, text="Day of Week:", font=("Arial", 12), anchor="w").grid(row=3, column=0, padx=10, pady=5, sticky="w")
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    combobox_day_of_week = ttk.Combobox(root, values=days_of_week, font=("Arial", 12))
    combobox_day_of_week.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

    # Row 4: Start Time
    tk.Label(root, text="Start Time:", font=("Arial", 12), anchor="w").grid(row=4, column=0, padx=10, pady=5, sticky="w")
    start_times = [f"{h:02}:00" for h in range(24)]  # สร้างรายการเวลา 00:00 - 23:00
    combobox_start_time = ttk.Combobox(root, values=start_times, font=("Arial", 12))
    combobox_start_time.grid(row=4, column=1, padx=10, pady=5, sticky="ew")

    # Row 5: End Time
    tk.Label(root, text="End Time:", font=("Arial", 12), anchor="w").grid(row=5, column=0, padx=10, pady=5, sticky="w")
    end_times = [f"{h:02}:00" for h in range(24)]  # สร้างรายการเวลา 00:00 - 23:00
    combobox_end_time = ttk.Combobox(root, values=end_times, font=("Arial", 12))
    combobox_end_time.grid(row=5, column=1, padx=10, pady=5, sticky="ew")

    # Row 6: Button Create
    tk.Button(root, text="Create", font=("Arial", 14), bg="green", fg="white", command=handle_create).grid(
        row=6, column=0, columnspan=2, padx=10, pady=20, sticky="ew"
    )

    root.mainloop()

if __name__ == "__main__":
    create_add_course_gui()
