import tkinter as tk
from tkinter import ttk, messagebox, Label, Entry, Button, Checkbutton, BooleanVar
import subprocess
import concurrent.futures
import threading
import time
import configparser
import webbrowser
import os
import requests
import zipfile

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

# Open Discord link
def open_discord():
    webbrowser.open("https://discord.gg/6KhRWcMK")

def run_single_action(port, link, loop_count, countdown_time, remaining_time):
    global stop_threads

    for _ in range(loop_count):
        if stop_threads:
            break  # Stop

        adb_clear(port)
        adb_start_activity(port, link)
        time.sleep(1.5)

        for sec in range(countdown_time):
            if stop_threads:
                break  # Stop

            remaining_time -= 1

            countdown_label.config(text=f"Countdown: {remaining_time} seconds")
            root.update_idletasks()

            time.sleep(1)

        remaining_time = countdown_time

def adb_clear(port):
    subprocess.Popen(["adb", "-s", f"localhost:{port}", "shell", "pm", "clear", "com.scopely.monopolygo"], creationflags=subprocess.CREATE_NO_WINDOW)
    subprocess.Popen(["adb", "-s", f"localhost:{port}", "shell", "pm", "clear", "com.google.android.gms"], creationflags=subprocess.CREATE_NO_WINDOW)

def adb_start_activity(port, link):
    subprocess.Popen(["adb", "-s", f"localhost:{port}", "shell", "am", "start", "-a", "android.intent.action.VIEW", "-d", link], creationflags=subprocess.CREATE_NO_WINDOW)
    subprocess.Popen(["adb", "-s", f"localhost:{port}", "shell", "input", "keyevent", "KEYCODE_ENTER"], creationflags=subprocess.CREATE_NO_WINDOW)

    if not remove_delay_var.get():
        time.sleep(4)


# Function to start the ADB server and connect the ports
def start_adb_and_connect_ports():
    try:
        start_adb_server()
        connect_adb_ports(device_entry.get().strip().split())
        messagebox.showinfo("Info", "ADB server started and ports connected successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start ADB server and connect ports: {str(e)}")

def start_adb_server():
    subprocess.run(["adb", "start-server"], capture_output=True, text=True)

def connect_adb_ports(device_ports):
    def connect_single_device(device_port):
        try:
            subprocess.run(["adb", "connect", f"localhost:{device_port}"], capture_output=True, text=True)
        except Exception as e:
            pass

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(device_ports)) as executor:
        executor.map(connect_single_device, device_ports)

def run_actions():
    global stop_threads
    stop_threads = False

    links = link_entry.get().split()  # Split links by spaces
    loop_count = -1 if is_forever.get() else int(loop_count_entry.get())
    selected_ports_str = device_entry.get().strip()
    selected_ports = selected_ports_str.split()
    countdown_time = int(countdown_entry.get())

    total_actions = len(selected_ports) * loop_count * len(links) if loop_count != -1 else -1
    remaining_time = countdown_time

    countdown_label.config(text=f"Countdown: {remaining_time} seconds")

    run_button.config(state=tk.DISABLED)
    stop_button.config(state=tk.NORMAL)

    if loop_count == -1:  # Run forever
        action_thread = threading.Thread(target=run_actions_forever, args=(links, selected_ports, countdown_time, remaining_time))
    else:
        action_thread = threading.Thread(target=run_actions_thread, args=(links, loop_count, selected_ports, countdown_time, remaining_time))

    action_thread.start()

def run_actions_forever(links, selected_ports, countdown_time, remaining_time):
    global stop_threads

    while not stop_threads:
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(selected_ports)) as executor:
            futures = []

            for link in links:
                if stop_threads:
                    break
                for port in selected_ports:
                    if stop_threads:
                        break
                    future = executor.submit(run_single_action, port, link, 1, countdown_time, remaining_time)
                    futures.append(future)

            concurrent.futures.wait(futures)

    run_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.DISABLED)

    if not stop_threads:
        messagebox.showinfo("Info", "Script completed.")
    else:
        messagebox.showinfo("Info", "Script stopped.")

def run_actions_thread(links, loop_count, selected_ports, countdown_time, remaining_time):
    global stop_threads

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(selected_ports)) as executor:
        futures = []

        for link in links:
            if stop_threads:
                break
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

def toggle_forever():
    loop_count_entry.config(state=tk.DISABLED if is_forever.get() else tk.NORMAL)

# Create the main application window
root = tk.Tk()
root.title("Cube Maker")
root.configure(bg="#f0f0f0")

frame = ttk.Frame(root, padding=10)
frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

header_label = Label(frame, text="Cube Maker", font=("Helvetica", 16, "bold"), padx=10, pady=10)
header_label.grid(row=0, column=0, columnspan=4, sticky="ew")


# Open ADB downloader window
def open_adb_downloader_window():
    script_directory = os.path.dirname(os.path.abspath(__file__))
    
    def download_and_extract_adb():
        # Define the URL for ADB download
        adb_download_url = "https://dl.google.com/android/repository/platform-tools-latest-windows.zip"

        # Define the path for the downloaded ZIP file
        zip_file_path = os.path.join(script_directory, "platform-tools-latest-windows.zip")

        try:
            # Download ADB zip
            response = requests.get(adb_download_url)
            with open(zip_file_path, "wb") as zip_file:
                zip_file.write(response.content)

            # Extract zip file to the script directory
            with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
                zip_ref.extractall(script_directory)

            success_message = "ADB downloaded and extracted successfully to the script directory.\n"
            success_message += "Please move the 'platform-tools' folder to your C drive (e.g., C:\\platform-tools) "
            success_message += "and then proceed to the next step."

            messagebox.showinfo("Success", success_message)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to download and extract ADB: {str(e)}")

    def open_environment_variables():
        try:
            subprocess.Popen(["rundll32.exe", "sysdm.cpl,EditEnvironmentVariables"])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Environment Variables: {str(e)}")

    def close_window():
        adb_root.destroy()

    adb_root = tk.Toplevel(root)  # Create a new top-level window for ADB downloader
    adb_root.title("ADB Downloader")
    
    instructions_label = tk.Label(
        adb_root,
        text="1. Click 'Download ADB' to download and extract ADB files.\n\n"
        "2. Move the 'platform-tools' folder to your C drive (e.g., C:\\platform-tools).\n\n"
        "3. Click 'Open Environment Variables' to set up ADB in your system's PATH.\n\n"
        "4. In the 'Edit Environment Variable' window, under 'User variables for [your username],' "
        "double-click 'Path'.\n\n"
        "5. Click 'New'.\n\n"
        "6. Paste 'C:\\platform-tools'.\n\n"
        "7. Click 'OK' to save the changes.",
        padx=20,
        pady=20,
    )
    instructions_label.pack()
    
    button_frame = tk.Frame(adb_root)
    button_frame.pack(side=tk.BOTTOM, padx=20, pady=20)
    
    download_button = Button(button_frame, text="Download ADB", command=download_and_extract_adb, width=25)
    download_button.pack(side=tk.LEFT, padx=10, pady=10)
    
    env_vars_button = Button(button_frame, text="Open Environment Variables", command=open_environment_variables, width=25)
    env_vars_button.pack(side=tk.LEFT, padx=10, pady=10)
    
    close_button = Button(button_frame, text="Close", command=close_window, width=15)
    close_button.pack(side=tk.RIGHT, padx=10, pady=10)

adb_downloader_button = Button(frame, text="Download and install ADB", command=open_adb_downloader_window)
adb_downloader_button.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")



adb_button = Button(frame, text="Start ADB and Connect Ports", command=start_adb_and_connect_ports, padx=20)
adb_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

link_label = Label(frame, text="Enter the HTTP link (space if multilink):")
link_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")
link_entry = Entry(frame, width=40)
link_entry.grid(row=3, column=1, padx=10, pady=5, sticky="w")
link_entry.insert(0, saved_link)

loop_count_label = Label(frame, text="Enter the number of times to run the loop:")
loop_count_label.grid(row=4, column=0, padx=10, pady=5, sticky="w")
loop_count_entry = Entry(frame, width=10)
loop_count_entry.grid(row=4, column=1, padx=10, pady=5, sticky="w")
loop_count_entry.insert(0, saved_loop_count)

is_forever = BooleanVar()
forever_button = Checkbutton(frame, text="FOREVER!", variable=is_forever, command=toggle_forever)
forever_button.grid(row=4, column=1, padx=(100, 10), pady=5, sticky="w")

device_label = Label(frame, text="Enter device port numbers (space-separated):")
device_label.grid(row=5, column=0, padx=10, pady=5, sticky="w")
device_entry = Entry(frame, width=40)
device_entry.grid(row=5, column=1, padx=10, pady=5, sticky="w")
device_entry.insert(0, saved_device_ports)

countdown_label = Label(frame, text="Enter countdown time (in seconds):")
countdown_label.grid(row=6, column=0, padx=10, pady=5, sticky="w")
countdown_entry = Entry(frame, width=10)
countdown_entry.grid(row=6, column=1, padx=10, pady=5, sticky="w")
countdown_entry.insert(0, saved_countdown_time)

remove_delay_var = BooleanVar()
remove_delay_button = Checkbutton(frame, text="Remove Delay", variable=remove_delay_var)
remove_delay_button.grid(row=6, column=1, padx=(100, 10), pady=5, sticky="w")


countdown_label = Label(frame, text="Countdown: 0 seconds")
countdown_label.grid(row=7, column=0, columnspan=2, padx=10, pady=5)

save_button = Button(frame, text="Save Input", command=save_user_input, padx=20)
save_button.grid(row=8, column=0, padx=(5, 7.5), pady=10, sticky="e")

run_button = Button(frame, text="Run Actions", command=run_actions, padx=20)
run_button.grid(row=8, column=1, padx=(7.5, 5), pady=10, sticky="w")

stop_button = Button(frame, text="STOP", command=stop_actions, state=tk.DISABLED, padx=20, width=10)
stop_button.grid(row=9, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

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