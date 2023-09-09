import tkinter as tk
from tkinter import ttk, messagebox, Label, Entry, Button
import subprocess
import concurrent.futures
import threading
import time
import configparser
import webbrowser

# Create or load a configuration file
config = configparser.ConfigParser()
config_filename = "config.ini"

if config.read(config_filename):
    saved_link = config.get("UserInput", "link")
    saved_loop_count = config.get("UserInput", "loop_count")
    saved_device_ports = config.get("UserInput", "device_ports")
    saved_countdown_time = config.get("UserInput", "countdown_time")
else:
    saved_link = ""
    saved_loop_count = ""
    saved_device_ports = ""
    saved_countdown_time = ""

def save_user_input():
    user_input_data = {
        "link": link_entry.get(),
        "loop_count": loop_count_entry.get(),
        "device_ports": device_entry.get(),
        "countdown_time": countdown_entry.get()
    }

    config["UserInput"] = user_input_data
    with open(config_filename, "w") as configfile:
        config.write(configfile)

# Function to open the Discord link
def open_discord():
    webbrowser.open("https://discord.gg/6KhRWcMK")

# Function to run a single action on a specific port
def run_single_action(port, link, loop_count, countdown_time, remaining_time):
    global stop_threads

    for _ in range(loop_count):
        if stop_threads:
            break  # Stop

        adb_clear(port)
        adb_start_activity(port, link)

        # Countdown before the next loop
        for sec in range(countdown_time):
            if stop_threads:
                break  # Stop

            remaining_time -= 1

            countdown_label.config(text=f"Countdown: {remaining_time} seconds")
            root.update_idletasks()

            time.sleep(1)

        remaining_time = countdown_time


def adb_clear(port):
    subprocess.run(["adb", "-s", f"localhost:{port}", "shell", "pm", "clear", "com.scopely.monopolygo"])
    subprocess.run(["adb", "-s", f"localhost:{port}", "shell", "pm", "clear", "com.google.android.gms"])

def adb_start_activity(port, link):
    subprocess.run(["adb", "-s", f"localhost:{port}", "shell", "am", "start", "-a", "android.intent.action.VIEW", "-d", link])
    subprocess.run(["adb", "-s", f"localhost:{port}", "shell", "input", "keyevent", "KEYCODE_ENTER"])

def run_actions():
    global stop_threads
    stop_threads = False
    
    link = link_entry.get()
    loop_count = int(loop_count_entry.get())
    selected_ports = device_entry.get().strip().split()
    countdown_time = int(countdown_entry.get())

    total_actions = len(selected_ports) * loop_count
    remaining_time = countdown_time

    countdown_label.config(text=f"Countdown: {remaining_time} seconds")

    run_button.config(state=tk.DISABLED)
    stop_button.config(state=tk.NORMAL)

    action_thread = threading.Thread(target=run_actions_thread, args=(link, loop_count, selected_ports, countdown_time, remaining_time))
    action_thread.start()

def run_actions_thread(link, loop_count, selected_ports, countdown_time, remaining_time):
    global stop_threads

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(selected_ports)) as executor:
        futures = []

        for port in selected_ports:
            if stop_threads:
                break
            future = executor.submit(run_single_action, port, link, loop_count, countdown_time, remaining_time)
            futures.append(future)

        concurrent.futures.wait(futures)

    run_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.DISABLED)

    if not stop_threads:
        messagebox.showinfo("Info", "Script completed.")
    else:
        messagebox.showinfo("Info", "Script stopped.")

# Function to stop all looping
def stop_actions():
    global stop_threads
    stop_threads = True

    stop_button.config(state=tk.DISABLED)

root = tk.Tk()
root.title("Cube Maker")
root.configure(bg="#f0f0f0")

frame = ttk.Frame(root, padding=10)
frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

header_label = Label(frame, text="Cube Maker", font=("Helvetica", 16, "bold"), padx=10, pady=10)
header_label.grid(row=0, column=0, columnspan=4, sticky="ew")

link_label = Label(frame, text="Enter the HTTP link:")
link_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
link_entry = Entry(frame, width=40)
link_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")
link_entry.insert(0, saved_link)

loop_count_label = Label(frame, text="Enter the number of times to run the loop:")
loop_count_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
loop_count_entry = Entry(frame, width=10)
loop_count_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")
loop_count_entry.insert(0, saved_loop_count)

device_label = Label(frame, text="Enter device port numbers (space-separated):")
device_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")
device_entry = Entry(frame, width=40)
device_entry.grid(row=3, column=1, padx=10, pady=5, sticky="w")
device_entry.insert(0, saved_device_ports)

countdown_label = Label(frame, text="Enter countdown time (in seconds):")
countdown_label.grid(row=4, column=0, padx=10, pady=5, sticky="w")
countdown_entry = Entry(frame, width=10)
countdown_entry.grid(row=4, column=1, padx=10, pady=5, sticky="w")
countdown_entry.insert(0, saved_countdown_time)

countdown_label = Label(frame, text="Countdown: 0 seconds")
countdown_label.grid(row=5, column=0, columnspan=2, padx=10, pady=5)

save_button = Button(frame, text="Save Input", command=save_user_input, padx=20)
save_button.grid(row=6, column=0, padx=(5, 7.5), pady=10, sticky="e")

run_button = Button(frame, text="Run Actions", command=run_actions, padx=20)
run_button.grid(row=6, column=1, padx=(7.5, 5), pady=10, sticky="w")

stop_button = Button(frame, text="STOP", command=stop_actions, state=tk.DISABLED, padx=20, width=10)
stop_button.grid(row=7, column=0, columnspan=2, padx=10, pady=10, sticky="ew")


footer_frame = ttk.Frame(root, padding=10)
footer_frame.grid(row=1, column=0, padx=10, pady=10, sticky="n")


footer_label = Label(footer_frame, text="Developed by SpookyFlush. Special thanks to otreborob for the method.", bg="#f0f0f0")
footer_label.grid(row=0, column=0, padx=10, pady=5, sticky="n")


discord_label = ttk.Label(footer_frame, text="Discord", cursor="hand2", foreground="blue")
discord_label.grid(row=1, column=0, padx=10, pady=5)
discord_label.bind("<Button-1>", lambda e: open_discord())

root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=1)

stop_threads = False
remaining_time = 0
root.mainloop()
