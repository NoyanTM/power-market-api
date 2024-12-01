import tkinter as tk
from tkinter import messagebox, font
from tkcalendar import Calendar
import subprocess
from datetime import datetime

# Welcome Message Function
def show_welcome_message():
    messagebox.showinfo(
        "Welcome to Data Visualization Tool",
        "Welcome to the Data Visualization and Modeling Tool!\n\n"
        "Use the buttons below to select different data analysis options.\n"
        "For 2D plots, make sure to choose your start and end dates.\n\n"
        "Enjoy exploring your data!"
    )
    

# Function to show the calendar and select a date
def toggle_calendar(calendar, entry_var, button):
    def select_date():
        entry_var.set(calendar.get_date())
        calendar.grid_remove()
        button.config(state="normal")

    if not calendar.winfo_ismapped():
        button.config(state="disabled")
        calendar.grid(row=calendar.grid_info().get('row', 0), column=calendar.grid_info().get('column', 0),
                      columnspan=3, pady=5)
        calendar.bind("<<CalendarSelected>>", lambda event: select_date())
    else:
        calendar.grid_remove()

# Function to validate the date range
def validate_dates():
    start_date = datetime.strptime(start_date_var.get(), "%m/%d/%y")
    end_date = datetime.strptime(end_date_var.get(), "%m/%d/%y")

    if start_date > end_date:
        messagebox.showerror("Date Selection Error", "The start date cannot be after the end date.")
        return False
    return True

# Function to run the 2D plot script
def run_plot_2d_script():
    if not validate_dates():
        return

    start_date = datetime.strptime(start_date_var.get(), "%m/%d/%y")
    end_date = datetime.strptime(end_date_var.get(), "%m/%d/%y")

    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")

    print(f"Running 2D plot for Start Date: {start_date_str}, End Date: {end_date_str}")

    try:
        result = subprocess.run(
            ["python3", "plot_data.py", start_date_str, end_date_str],
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error running 2D plot script: {e}\n{e.stderr}")

# Function to run the model scripts
def run_model_script(model_script):
    try:
        result = subprocess.run(
            ["python3", model_script],
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error running {model_script}: {e}\n{e.stderr}")

# Function to display the date selection inputs for the 2D plot
# Function to display the date selection inputs for the 2D plot
def show_date_selection():
    date_frame.pack(pady=10)
    start_date_label.grid(row=0, column=0, padx=5, pady=5)
    start_date_entry.grid(row=0, column=1, padx=5, pady=5)
    btn_start_calendar.grid(row=0, column=2, padx=5, pady=5)

    end_date_label.grid(row=1, column=0, padx=5, pady=5)
    end_date_entry.grid(row=1, column=1, padx=5, pady=5)
    btn_end_calendar.grid(row=1, column=2, padx=5, pady=5)

    # Use grid for btn_run_2d_plot to match the geometry manager
    btn_run_2d_plot.grid(row=2, column=0, columnspan=3, pady=10)


# Function to display model buttons
def show_model_buttons():
    model_frame.pack(pady=10)
    model_buttons = [
        ("ARIMA", lambda: run_model_script("model_1.py")),
        ("FB Prophet", lambda: run_model_script("model_2_probhet.py")),
        ("XGBoost", lambda: run_model_script("model_3.py")),
    ]
    for text, command in model_buttons:
        button = tk.Button(model_frame, text=text, command=command, width=15, font=('Helvetica', 12, 'bold'), bg="#a3d2ca")
        button.pack(pady=5)

# Tkinter GUI setup
root = tk.Tk()
root.title("Data Visualization Tool")
root.geometry("400x600")
root.config(bg="#f5f5f5")

# Show the welcome message when the application starts
root.after(100, show_welcome_message)

# Title label
title_label = tk.Label(root, text="Data Plot and Modeling Tool", font=("Helvetica", 16, "bold"), bg="#f5f5f5", pady=10)
title_label.pack()

# Instruction label
instruction_label = tk.Label(root, text="Select an option below to analyze your data", font=("Helvetica", 10), bg="#f5f5f5")
instruction_label.pack()

# Frame for date pickers and model buttons
date_frame = tk.Frame(root, bg="#f5f5f5", padx=10, pady=10, relief="groove", borderwidth=2)
model_frame = tk.Frame(root, bg="#f5f5f5", padx=10, pady=10, relief="groove", borderwidth=2)

# Labels and Entry widgets for start and end dates with Calendar buttons
start_date_label = tk.Label(date_frame, text="Select Start Date:", bg="#f5f5f5")
start_date_var = tk.StringVar()
start_date_entry = tk.Entry(date_frame, textvariable=start_date_var, width=15)
btn_start_calendar = tk.Button(date_frame, text="📅", command=lambda: toggle_calendar(cal_start, start_date_var, btn_start_calendar))

cal_start = Calendar(
    date_frame, selectmode='day', year=2023, month=1, day=1,
    mindate=datetime(2023, 1, 1), maxdate=datetime(2024, 7, 1)
)
cal_start.grid_remove()

end_date_label = tk.Label(date_frame, text="Select End Date:", bg="#f5f5f5")
end_date_var = tk.StringVar()
end_date_entry = tk.Entry(date_frame, textvariable=end_date_var, width=15)
btn_end_calendar = tk.Button(date_frame, text="📅", command=lambda: toggle_calendar(cal_end, end_date_var, btn_end_calendar))

cal_end = Calendar(
    date_frame, selectmode='day', year=2024, month=7, day=1,
    mindate=datetime(2023, 1, 1), maxdate=datetime(2024, 7, 1)
)
cal_end.grid_remove()

# Button for running the 2D plot script
btn_run_2d_plot = tk.Button(date_frame, text="Run 2D Plot", command=run_plot_2d_script, font=("Helvetica", 12), bg="#ffab73", width=15)

# Main buttons to show options
btn_show_date_selection = tk.Button(root, text="Show Plan vs Fact 2D Plot", command=show_date_selection, font=("Helvetica", 12), bg="#6fa8dc", width=25)
btn_show_date_selection.pack(pady=10)

btn_show_3d_generation_plot = tk.Button(root, text="Show Solar Generation 3D Plot",
                                        command=lambda: run_model_script("generation.py"), font=("Helvetica", 12), bg="#6fa8dc", width=25)
btn_show_3d_generation_plot.pack(pady=10)

btn_show_3d_weather_plot = tk.Button(root, text="Show Weather Temperature 3D Plot",
                                     command=lambda: run_model_script("plot_weather_3d.py"), font=("Helvetica", 12), bg="#6fa8dc", width=25)
btn_show_3d_weather_plot.pack(pady=10)

btn_show_correlation_plot = tk.Button(root, text="Show Correlation Heatmap",
                                      command=lambda: run_model_script("correlation.py"), font=("Helvetica", 12), bg="#6fa8dc", width=25)
btn_show_correlation_plot.pack(pady=10)

btn_show_models = tk.Button(root, text="Show Models", command=show_model_buttons, font=("Helvetica", 12, "bold"), bg="#d4a5a5", width=25)
btn_show_models.pack(pady=10)

root.mainloop()
