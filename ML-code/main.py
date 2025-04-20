import tkinter as tk
from tkinter import ttk, simpledialog
import subprocess
import os

def run_script(script_path, specific_object=None):
    """Runs a Python script in a new process, sending input to its stdin."""
    try:
        command = ["python", script_path]
        process = subprocess.Popen(command, stdin=subprocess.PIPE, text=True)  # Capture stdin

        if specific_object:
            process.communicate(input=specific_object + "\n")  # Send input and newline
            print(f"Running script: {script_path} with object: {specific_object}")
        else:
            process.communicate() # Needed to avoid hanging on Windows

    except FileNotFoundError:
        print(f"Error: Script not found at {script_path}")
    except Exception as e:
        print(f"Error running script: {e}")


def get_specific_object():
    """Opens a dialog box to get the specific object from the user."""
    object_name = simpledialog.askstring("Specific Object", "Enter the object to detect:")
    return object_name


def main():
    # ... (rest of the GUI code is the same)
    window = tk.Tk()
    window.title("Object Detection Control")

    # Styling (same as before)
    style = ttk.Style()
    style.configure('TButton', padding=6, font=('Courier New', 14), background="#00008B", foreground="Black")
    style.configure('TLabel', font=('Times New Roman', 20), background="#FFFFFF")
    style.configure('TFrame', background="#FFFFFF")
    style.configure('TNotebook.Tab', font=('Arial', 20), background="#000000")
    style.configure('TNotebook', background="#000000")

    notebook = ttk.Notebook(window)
    notebook.pack(fill=tk.BOTH, expand=True)

    tab1 = ttk.Frame(notebook)
    notebook.add(tab1, text="TAB 1")

    title_label = ttk.Label(tab1, text="OBJECT DETECTION")
    title_label.pack(pady=10)

    description_label = ttk.Label(tab1, text="CONTROLS")
    description_label.pack(pady=50)

    button_frame = ttk.Frame(tab1)
    button_frame.pack(pady=0)

    description_label = ttk.Label(tab1, text="'q' or 'Q' to Quit the Operation Here......", font=('Arial', 14))
    description_label.pack(pady=200)

    start_button = ttk.Button(button_frame, text="Start Detection", command=lambda: run_script("object detection project/real_time.py"))
    start_button.pack(side=tk.LEFT, padx=10)

    def specific_detection_command():
        object_name = get_specific_object()
        if object_name:
            run_script("object detection project/specfic_detection.py", object_name)

    # ... (rest of the GUI code is the same)
    specific_button = ttk.Button(button_frame, text="Specific Object Detection", command=specific_detection_command)
    specific_button.pack(side=tk.LEFT, padx=10)

    others_button = ttk.Button(button_frame, text="User Defined Detection", command=lambda: run_script("other_script.py"))
    others_button.pack(side=tk.LEFT, padx=10)

    window.mainloop()

if __name__ == "__main__":
    main()