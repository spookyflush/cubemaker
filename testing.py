import os
import requests
import zipfile
import tkinter as tk
from tkinter import Button, messagebox
import subprocess

# Get the directory where the script is located
script_directory = os.path.dirname(os.path.abspath(__file__))

# Function to download and extract ADB
def download_and_extract_adb():
    # Define the URL for ADB download
    adb_download_url = "https://dl.google.com/android/repository/platform-tools-latest-windows.zip"

    # Define the path for the downloaded ZIP file
    zip_file_path = os.path.join(script_directory, "platform-tools-latest-windows.zip")

    try:
        # Download the ADB ZIP file
        response = requests.get(adb_download_url)
        with open(zip_file_path, "wb") as zip_file:
            zip_file.write(response.content)

        # Extract the ZIP file to the script directory
        with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
            zip_ref.extractall(script_directory)

        success_message = "ADB downloaded and extracted successfully to the script directory.\n"
        success_message += "Please move the 'platform-tools' folder to your C drive (e.g., C:\\platform-tools) "
        success_message += "and then proceed to the next step."

        messagebox.showinfo("Success", success_message)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to download and extract ADB: {str(e)}")

# Function to open the Environment Variables window
def open_environment_variables():
    try:
        subprocess.Popen(["rundll32.exe", "sysdm.cpl,EditEnvironmentVariables"])
    except Exception as e:
        messagebox.showerror("Error", f"Failed to open Environment Variables: {str(e)}")

# Function to close the window
def close_window():
    root.destroy()

# Create the main application window
root = tk.Tk()
root.title("ADB Downloader")

# Create a label with instructions for the user
instructions_label = tk.Label(
    root,
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

# Create a frame to hold the buttons and place it at the bottom of the window
button_frame = tk.Frame(root)
button_frame.pack(side=tk.BOTTOM, padx=20, pady=20)

# Create a button to trigger ADB download and extraction
download_button = Button(button_frame, text="Download ADB", command=download_and_extract_adb, width=25)
download_button.pack(side=tk.LEFT, padx=10, pady=10)

# Create a button to open the Environment Variables window
env_vars_button = Button(button_frame, text="Open Environment Variables", command=open_environment_variables, width=25)
env_vars_button.pack(side=tk.LEFT, padx=10, pady=10)

# Create a button to close the window
close_button = Button(button_frame, text="Close", command=close_window, width=15)
close_button.pack(side=tk.RIGHT, padx=10, pady=10)

root.mainloop()
