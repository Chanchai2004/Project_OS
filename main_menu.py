import os
import tkinter as tk
from tkinter import messagebox

def import_student():
    try:
        os.system("python Import.py")  # รัน Import.py
    except Exception as e:
        messagebox.showerror("Error", f"Failed to run Import.py: {e}")

def add_course():
    try:
        os.system("python Add.py")  # รัน Add.py
    except Exception as e:
        messagebox.showerror("Error", f"Failed to run Add.py: {e}")

def register_course():
    try:
        os.system("python Registercourse.py")  # รัน Add.py
    except Exception as e:
        messagebox.showerror("Error", f"Failed to run Registercourse.py.py: {e}")

#def register_student():
#   messagebox.showinfo("Register Student", "Feature: Register students for courses. (Not implemented yet)")
def register_student():
    try:
        os.system("python Register.py")  # รัน Add.py
    except Exception as e:
        messagebox.showerror("Error", f"Failed to run Register.py: {e}")

#def check_in():
#    messagebox.showinfo("Check In", "Feature: Record student attendance. (Not implemented yet)")
def check_in():
    try:
        os.system("python Check.py")  # รัน Add.py
    except Exception as e:
        messagebox.showerror("Error", f"Failed to run Check.py: {e}")

def export():
    try:
        os.system("python Export.py")  # รัน Add.py
    except Exception as e:
        messagebox.showerror("Error", f"Failed to run Export.py: {e}")

def dump_database():
    try:
        os.system("python dumpdb.py")  # รัน dumpdb.py
    except Exception as e:
        messagebox.showerror("Error", f"Failed to run dumpdb.py: {e}")

def upload_database():
    try:
        os.system("python upload.py")  # รัน upload.py
    except Exception as e:
        messagebox.showerror("Error", f"Failed to run upload.py: {e}")

def reset_database():
    try:
        os.system("python reset.py")  # รัน reset.py
    except Exception as e:
        messagebox.showerror("Error", f"Failed to run reset.py: {e}")


def main_menu():
    root = tk.Tk()
    root.title("Main Menu")
    root.geometry("400x700")

    title_label = tk.Label(root, text="Main Menu", font=("Arial", 18, "bold"))
    title_label.pack(pady=20)

    buttons = [
        {"text": "Import Student", "command": import_student},
        {"text": "Add Course", "command": add_course},
        {"text": "Add RFID for Student", "command": register_student},
        {"text": "Register Course", "command": register_course},
        {"text": "Check In", "command": check_in},
        {"text": "Export", "command": export},
        {"text": "Dump Database", "command": dump_database},
        {"text": "Reset Database", "command": reset_database},
        {"text": "Upload Database", "command": upload_database},
    ]

    for button in buttons:
        btn = tk.Button(root, text=button["text"], font=("Arial", 14), command=button["command"], width=20, height=2)
        btn.pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    main_menu()
