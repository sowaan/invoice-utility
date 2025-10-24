# Import necessary modules
import os
import platform
import sqlite3
import subprocess
import requests
import tkinter as tk
from tkinter import *
from tkinter import messagebox, ttk, filedialog
from tkcalendar import DateEntry
import threading
import time
import config as config
from tkinter import Tk, Toplevel, messagebox, Scrollbar, Button, Label, Entry, Frame
from tkinter.simpledialog import askstring
from tkinter import Listbox
import csv
import json

# Create a connection that is thread-safe
conn = sqlite3.connect(config.DATABASE_CONFIG['DB_PATH'], check_same_thread=config.DATABASE_CONFIG['CHECK_SAME_THREAD'])
cursor = conn.cursor()

# Your ERPNext API details (replace with actual credentials)
site_url = config.ERP_CONFIG['SITE_URL']
shipment_api_url = f"{site_url}{config.ERP_CONFIG['SHIPMENT_API_URL']}"
generate_invoice_api_url = f"{site_url}{config.ERP_CONFIG['GENERATE_SALES_INVOICE_API_URL']}"
headers = config.ERP_CONFIG['HEADERS']
api_key = config.ERP_CONFIG['API_KEY']
api_secret = config.ERP_CONFIG['API_SECRET']
selected_parent_id = None
logged_in_username = None
is_login = False




def check_connections():
    """Check database and API connections, exit if any fail."""
    # Check SQLite connection
    try:
        with sqlite3.connect(
            config.DATABASE_CONFIG['DB_PATH'],
            check_same_thread=config.DATABASE_CONFIG['CHECK_SAME_THREAD']
        ) as conn:
            conn.execute("SELECT 1")  # Simple connection test
        # print("✅ SQLite connected successfully")
    except sqlite3.Error as e:
        # print(f"❌ SQLite connection failed: {e}")
        messagebox.showerror("Connection Error", "SQLite connection failed")
        exit(1)

    # Check ERPNext API connection
    try:
        response = requests.get(
            url=f"{config.ERP_CONFIG['SITE_URL'].rstrip('/')}/api/method/ping",
            headers=config.ERP_CONFIG['HEADERS'],
            timeout=5
        )
        if response.status_code == 200:
            print("✅ ERPNext API connected successfully")
        else:
            raise requests.exceptions.RequestException(
                f"{response.status_code} - {response.text}"
            )
    except requests.exceptions.RequestException as e:
        # print(f"❌ ERPNext API error: {e}")
        messagebox.showerror(
            "Connection Error", 
            f"ERPNext API connection failed:\n\n{str(e)}"
        )
        exit(1)

check_connections()


cursor.execute("""
    CREATE TABLE IF NOT EXISTS credentials (
        username TEXT PRIMARY KEY,
        password TEXT
    )
""")
conn.commit()


def save_credentials(username, password):
    cursor.execute("""
        INSERT INTO credentials (username, password)
        VALUES (?, ?)
        ON CONFLICT(username) DO UPDATE SET password=excluded.password
    """, (username, password))
    conn.commit()


def get_saved_usernames_and_passwords():
    cursor.execute("SELECT username, password FROM credentials")
    rows = cursor.fetchall()
    return dict(rows)



credentials = get_saved_usernames_and_passwords()



def on_username_selected(event):
    selected_user = username_combo.get()
    if selected_user in credentials:
        password_entry.delete(0, tk.END)
        password_entry.insert(0, credentials[selected_user])
    else:
        password_entry.delete(0, tk.END)





def check_login():
    global is_login
    global logged_in_username
    entered_username = username_combo.get()
    entered_password = password_entry.get()

    print(entered_username)
    print(entered_password)
    print(site_url)

    login_url = f"{site_url}api/method/login"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    try:
        response = requests.post(
            login_url,
            data={"usr": entered_username, "pwd": entered_password},
            headers=headers
        )
        print(str(response.json()))
        if response.status_code == 200 and response.json().get("message") == "Logged In":
            logged_in_username = entered_username
            is_login = True

            if remember_var.get():
                save_credentials(entered_username, entered_password)

            login_window.destroy()

        else:
            messagebox.showerror("Login Failed", "Invalid username or password")
    except Exception as e:
        messagebox.showerror("Error", f"Could not connect to ERP site.\n{str(e)}")


def toggle_password():
    if password_entry.cget("show") == "":
        password_entry.config(show="*")
        toggle_btn.config(text="Show")
    else:
        password_entry.config(show="")
        toggle_btn.config(text="Hide")
        

# Create login window
login_window = tk.Tk()
login_window.title("Login")
login_window.resizable(False, False)  # Disable window resizing

# Color scheme
bg_color = "#f0f0f0"
entry_bg = "#ffffff"
button_color = "#4a6fa5"
button_fg = "#ffffff"
hover_color = "#3a5a80"
remember_hover = "#e0e0e0"  # New hover color for remember me

# Font styles
label_font = ("Arial", 12, "bold")
entry_font = ("Arial", 12)
button_font = ("Arial", 12, "bold")

# Configure window background
login_window.configure(bg=bg_color)

# Window size and centering
width = 520
height = 320
screen_width = login_window.winfo_screenwidth()
screen_height = login_window.winfo_screenheight()
x = (screen_width // 2) - (width // 2)
y = (screen_height // 2) - (height // 2)
login_window.geometry(f"{width}x{height}+{x}+{y}")

# Padding values
pad_x = 30
pad_y = 8
inner_pad = 5

style = ttk.Style()
style.configure('TEntry', fieldbackground=entry_bg, foreground="#333333")
style.configure('TButton', background="#e0e0e0", foreground="#333333")
style.map('TButton',
    background=[('active', '#d0d0d0')],
    foreground=[('active', '#333333')]
)

# Main container frame
main_frame = tk.Frame(login_window, bg=bg_color)
main_frame.pack(pady=20, padx=20, fill="both", expand=True)



# Username Section (made same size as password)
username_frame = tk.Frame(main_frame, bg=bg_color)
username_frame.pack(fill="x", pady=(0, pad_y))

tk.Label(
    username_frame, 
    text="Username:", 
    font=label_font, 
    bg=bg_color,
    anchor="w"
).pack(fill="x", padx=pad_x)

username_combo = ttk.Combobox(
    username_frame, 
    values=list(credentials.keys()), 
    font=entry_font,
    background=entry_bg
)
username_combo.pack(fill="x", padx=pad_x, pady=(inner_pad, 0))
username_combo.bind("<<ComboboxSelected>>", on_username_selected)






password_frame = tk.Frame(main_frame, bg=bg_color)
password_frame.pack(fill="x", pady=(pad_y, pad_y))

tk.Label(
    password_frame, 
    text="Password:", 
    font=label_font, 
    bg=bg_color,
    anchor="w"
).pack(fill="x", padx=pad_x)

# Create a single border frame (like the combobox)
password_container = ttk.Frame(password_frame, style='TEntry')
password_container.pack(fill="x", padx=pad_x, pady=(inner_pad, 0))

# Password entry - borderless inside the container
password_entry = tk.Entry(
    password_container,
    show="*",
    font=entry_font,
    bg=entry_bg,
    bd=0,
    highlightthickness=0,
    relief="flat"
)
password_entry.pack(side="left", fill="x", expand=True, padx=2)

# Toggle button - borderless inside the container
toggle_btn = tk.Button(
    password_container,
    text="Show",
    font=("Arial", 10),
    bg=button_color,  # Using your login button color
    fg=button_fg,    # Using your login button text color
    bd=0,
    highlightthickness=0,
    activebackground=hover_color,  # Using your login hover color
    activeforeground=button_fg,
    relief="flat",
    width=6,
    command=toggle_password
)
toggle_btn.pack(side="right")

# Add hover effects to match login button
def on_toggle_enter(e):
    toggle_btn.config(bg=hover_color)
    
def on_toggle_leave(e):
    toggle_btn.config(bg=button_color)

toggle_btn.bind("<Enter>", on_toggle_enter)
toggle_btn.bind("<Leave>", on_toggle_leave)

# Remember Me with hover effect
remember_frame = tk.Frame(main_frame, bg=bg_color)
remember_frame.pack(fill="x", padx=pad_x, pady=(0, pad_y))

remember_var = tk.BooleanVar()
remember_check = tk.Checkbutton(
    remember_frame, 
    text="Remember Me", 
    variable=remember_var, 
    font=("Arial", 11),
    bg=bg_color,
    activebackground=remember_hover,  # Hover background
    selectcolor=bg_color,
    bd=0,
    highlightthickness=0
)

# Hover effects for remember me
def on_remember_enter(e):
    remember_check.config(bg=remember_hover)
    
def on_remember_leave(e):
    remember_check.config(bg=bg_color)

remember_check.pack(side="left")
remember_check.bind("<Enter>", on_remember_enter)
remember_check.bind("<Leave>", on_remember_leave)

# Login Button
login_button = tk.Button(
    main_frame, 
    text="LOGIN", 
    command=check_login, 
    font=button_font,
    bg=button_color,
    fg=button_fg,
    activebackground=hover_color,
    activeforeground=button_fg,
    bd=0,
    padx=20,
    pady=8
)
login_button.pack(fill="x", padx=pad_x, pady=(pad_y, 0))

# Login button hover effects
def on_enter(e):
    e.widget.config(bg=hover_color)
    
def on_leave(e):
    e.widget.config(bg=button_color)

login_button.bind("<Enter>", on_enter)
login_button.bind("<Leave>", on_leave)

login_window.mainloop()




if not is_login:
    print("Exiting the application due to failed login.")
    exit(0)


# Create the 'records' table if it doesn't exist
# cursor.execute("""
# CREATE TABLE IF NOT EXISTS records (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     export_import TEXT,  
#     start_date TEXT,
#     end_date TEXT,
#     billing_type TEXT,
#     station TEXT,
#     customer TEXT,
#     icris_number TEXT,
#     date_type TEXT,
#     gateway TEXT,
#     manifest_file_type TEXT,
#     sales_invoice_definition TEXT,
#     posting_date TEXT
# )
# """)
# # cursor.execute("DROP TABLE records")
# conn.commit()
cursor.execute("""
CREATE TABLE IF NOT EXISTS records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    export_import TEXT,  
    start_date TEXT,
    end_date TEXT,
    billing_type TEXT,
    station TEXT,
    customer TEXT,
    icris_number TEXT,
    date_type TEXT,
    gateway TEXT,
    manifest_file_type TEXT,
    sales_invoice_definition TEXT,
    posting_date TEXT
)
""")
conn.commit()
print("Records table created successfully.")


# cursor.execute("ALTER TABLE records ADD COLUMN date_type TEXT")
# cursor.execute("ALTER TABLE records DROP COLUMN custom_id")
# ALTER TABLE records DROP COLUMN date_type;
# conn.commit()

# Create the 'shipment_numbers' table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS shipment_numbers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    parent_id INTEGER,
    shipment_number TEXT,
    sales_invoice TEXT,
    logs TEXT,
    shipment_index INTEGER,
    FOREIGN KEY (parent_id) REFERENCES records(id)
)
""")
conn.commit()

cursor.execute("""
CREATE TABLE IF NOT EXISTS Customer (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
)
""")
conn.commit()

cursor.execute("""
CREATE TABLE IF NOT EXISTS IcrisNumber (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    icris_no TEXT NOT NULL
)
""")
conn.commit()


cursor.execute("""
CREATE TABLE IF NOT EXISTS Gateway (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
)
""")
# cursor.execute("DROP TABLE Gateway")
conn.commit()





system = platform.system()


# def load_child_after_getting_shipments(parent_id):
#     """
#     Load child records (shipment numbers) after fetching them via the script.
#     This function is called after the script execution completes from get_shipment_numbers file.
#     """
#     if parent_id:
#         print('run')
#         load_shipment_numbers(parent_id)
#     else:
#         messagebox.showerror("Error", "No parent record selected to load shipment numbers.")



# Load shipment numbers in the child table
def load_shipment_numbers(parent_id):
    # Clear any existing data in the child table
    shipment_table.delete(*shipment_table.get_children())

    if parent_id is None:
        return

    cursor.execute("SELECT shipment_index, shipment_number, sales_invoice, logs FROM shipment_numbers WHERE parent_id = ?", (parent_id,))

    records = cursor.fetchall()

    # print(f"Fetched records for parent_id {parent_id}: {records}")  # Debugging output

    if records:
        # print('record not empty!')
        for record in records:
            shipment_table.insert("", "end", values=record)
    else:
        # print('record is empty!')
        # Show a message when no child records are available for the selected parent
        shipment_table.insert("", "end", values=("No shipment records", "", "", ""))
    





def fetch_shipment_numbers_via_script():

    selected_item = table.selection()
    if not selected_item:
        messagebox.showerror("Error", "No parent record selected!")
        return
    parent_id = table.item(selected_item)["values"][0]
    
    if os.name == 'nt':
        command = f"python get_shipment_numbers.py --parent_id={parent_id}"
        # subprocess.run(f'start cmd /k {command}', shell = True)
        # subprocess.run(f'start cmd /c {command}', shell=True)
        subprocess.run(f'start /wait cmd /c {command}', shell=True)
    else:
        # command = f"xterm -hold -e 'python3 get_shipment_numbers.py --parent_id={parent_id}'"
        command = f"xterm -e 'python3 get_shipment_numbers.py --parent_id={parent_id}'"
        process = subprocess.Popen(command, shell=True)    # Use subprocess to execute the command
        process.wait()  # Wait for the process to complete
    load_shipment_numbers(parent_id)




# Function to handle "Get Shipment Numbers" button click
# def get_shipment_numbers_for_selected_parent():
#     selected_item = table.selection()
#     if not selected_item:
#         messagebox.showerror("Error", "No parent record selected!")
#         return

#     parent_id = table.item(selected_item)["values"][0]  # Get the parent record ID
#     load_shipment_numbers(parent_id)


# Function to handle "Delete Record" button click
def delete_parent_record():
    selected_item = table.selection()
    if not selected_item:
        messagebox.showerror("Error", "No parent record selected!")
        return

    parent_id = table.item(selected_item)["values"][0]  # Get the parent record ID

    # Ask for confirmation before deletion
    if messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this record and its associated shipments?"):
        try:
            # Delete the associated shipment numbers first (to maintain foreign key integrity)
            cursor.execute("DELETE FROM shipment_numbers WHERE parent_id = ?", (parent_id,))
            conn.commit()

            # Now delete the parent record
            cursor.execute("DELETE FROM records WHERE id = ?", (parent_id,))
            conn.commit()

            # messagebox.showinfo("Success", "Record and associated shipment numbers deleted successfully.")
            load_parent_records()  # Reload the parent records table after deletion
            load_shipment_numbers(None)  # Clear shipment numbers for the deleted record
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete record: {e}")


def copied_popup(event):
    popup = tk.Toplevel(root)
    popup.overrideredirect(True)  # Remove window border
    popup.configure(bg="black")

    # Place the popup near the mouse click
    x = event.x_root + 10
    y = event.y_root + 10
    popup.geometry(f"+{x}+{y}")

    # Message label
    label = tk.Label(popup, text="Copied!", bg="black", fg="white", padx=10, pady=5)
    label.pack()

    # Auto-close after 0.4 second (400 ms)
    root.after(400, popup.destroy)



def copy_cell_value_child(event):
    """
    Copy the value of the clicked cell in the child table to the clipboard.
    """
    selected_item = shipment_table.selection()  # Get the selected row
    if not selected_item:
        messagebox.showerror("Error", "No shipment record selected!")
        return

    column = shipment_table.identify_column(event.x)  # Get the column where the click occurred
    column_index = int(column.replace("#", "")) - 1  # Convert column identifier to index (0-based)
    
    # Get the value of the clicked cell
    cell_value = shipment_table.item(selected_item)["values"][column_index]
    
    # Copy the value to clipboard
    root.clipboard_clear()  # Clear previous clipboard content
    root.clipboard_append(cell_value)  # Append new value to clipboard
    copied_popup(event)
    # messagebox.showinfo("Copied", f"Copied: {cell_value}")  # Show confirmation message

def copy_cell_value_parent(event):
    """
    Copy the value of the clicked cell in the parent table to the clipboard.
    """
    selected_item = table.selection()  # Get the selected row
    if not selected_item:
        messagebox.showerror("Error", "No record selected!")
        return

    column = table.identify_column(event.x)  # Get the column where the click occurred
    column_index = int(column.replace("#", "")) - 1  # Convert column identifier to index (0-based)
    
    # Get the value of the clicked cell
    cell_value = table.item(selected_item)["values"][column_index]
    
    # Copy the value to clipboard
    root.clipboard_clear()  # Clear previous clipboard content
    root.clipboard_append(cell_value)  # Append new value to clipboard
    copied_popup(event)
    # messagebox.showinfo("Copied", f"Copied: {cell_value}")  # Show confirmation message



def on_parent_record_click(event):
    selected_item = table.selection()  # Get the selected row
    if not selected_item:
        # messagebox.showerror("Error", "No parent record selected!")
        return

    selected_parent_id = table.item(selected_item)["values"][0]  # Store the selected parent record ID
    load_shipment_numbers(selected_parent_id)

def download_selected_shipment_numbers():
    selected_item = table.selection()  # Get the selected row
    if not selected_item:
        messagebox.showerror("Error", "No parent record selected!")
        return
    selected_parent_id = table.item(selected_item)["values"][0]
    # global selected_parent_id
    # if not selected_parent_id:
    #     messagebox.showerror("Error", "No parent record selected!")
    #     return

    # Fetch shipment numbers for the selected parent ID
    cursor.execute("""
        SELECT shipment_index, shipment_number, sales_invoice, logs
        FROM shipment_numbers
        WHERE parent_id = ?
    """, (selected_parent_id,))
    records = cursor.fetchall()

    if not records:
        messagebox.showinfo("Info", "No shipment numbers found for the selected parent ID.")
        return

    # Ask the user for a save location
    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv")],
        title="Save Shipment Numbers"
    )
    if not file_path:
        # User canceled the save dialog
        return

    # Write data to the CSV file
    try:
        with open(file_path, mode="w", newline="") as file:
            writer = csv.writer(file)
            # Write the header row
            writer.writerow(["Shipment Index", "Shipment Number", "Sales Invoice", "Logs"])
            # Write the data rows
            writer.writerows(records)

        messagebox.showinfo("Success", f"Shipment numbers successfully saved to {file_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save shipment numbers to CSV: {str(e)}")

def fetch_sales_invoice_definitions():
    """
    Fetch all available Sales Invoice Definitions from the ERPNext system.
    """
    # Define the API URL
    definition_url = f"{config.ERP_CONFIG['SITE_URL']}{config.ERP_CONFIG['DEFINITION_URL']}"

    try:
        # Send the GET request
        response = requests.get(definition_url, headers=config.ERP_CONFIG['HEADERS'])
        if response.status_code == 200:
            data = response.json()  # Parse the JSON response
            # Extract 'name' from each entry in the 'data' list
            invoice_definitions = [item['name'] for item in data.get('data', [])]
            return invoice_definitions
        else:
            messagebox.showerror("Error", f"Failed to fetch Sales Invoice Definitions. Status code: {response.status_code}")
            return []
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while fetching Sales Invoice Definitions: {str(e)}")
        return []

def refresh_shipment_table():
    selected_item = table.selection()
    if not selected_item:
        # messagebox.showerror("Error", "No parent record selected!")
        return
    selected_parent_id = table.item(selected_item)["values"][0]
    load_shipment_numbers(selected_parent_id)

def fetch_and_store_icris_numbers():
    icris_numbers_url = f"{config.ERP_CONFIG['SITE_URL']}{config.ERP_CONFIG['ICRIS_NUMBER_URL']}"
    
    try:
        response = requests.get(icris_numbers_url, headers=config.ERP_CONFIG['HEADERS'])
        
        # Debug: print response details
        # print(f"Status Code: {response.status_code}")
        # print(f"Response Content: {response.content}")  # Print raw content

        if response.status_code == 200:
            data = response.json()  # Parse the JSON response
            
            # Debug: print the response data structure
            # print(f"Response JSON: {data}")

            # Extract Icris Numbers from the 'data' field
            icris_numbers = data.get('data', [])
            # print(f"Extracted Icris Numbers: {icris_numbers}")  # Check if the data is extracted correctly
            
            if icris_numbers:
                cursor.execute("DELETE FROM IcrisNumber")
                conn.commit()
                for icris_number in icris_numbers:
                    shipper_no = icris_number.get('shipper_no')
                    # print(f"Added shipper_no: {shipper_no}")  # Debug: print each shipper_no

                    # Ensure the shipper_no exists and is not empty
                    if shipper_no:
                        cursor.execute("SELECT * FROM IcrisNumber WHERE icris_no = ?", (shipper_no,))
                        if not cursor.fetchone():  # If shipper_no does not already exist
                            cursor.execute("""
                            INSERT INTO IcrisNumber (icris_no) VALUES (?)
                            """, (shipper_no,))
                conn.commit()
                print("Icris Numbers stored successfully.")
            else:
                print("No Icris Numbers found in the response.")
        else:
            print(f"Failed to fetch Icris Numbers. Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")



# Fetch all available Icris Numbers from the IcrisNumber table in the database
def fetch_icris_numbers(search_term=None, limit=20):
    """
    Fetch all available Icris Numbers from the 'IcrisNumber' table in the database,
    optionally filtering by a search term.
    """
    try:
        if search_term:
            # Use the search term to filter the Icris numbers
            cursor.execute("SELECT icris_no FROM IcrisNumber WHERE icris_no LIKE ?", (f"%{search_term}%",))
        else:
            # Fetch all Icris numbers
            cursor.execute("SELECT icris_no FROM IcrisNumber LIMIT ?", (limit,))
        
        # Extract the 'icris_no' field from each row
        icris_numbers = [row[0] for row in cursor.fetchall()]
        return icris_numbers
    except Exception as e:
        print(f"An error occurred while fetching Icris Numbers from the database: {str(e)}")
        return []
# print(icris_numbers_list)


# Fetch customers from the ERPNext API
def fetch_and_store_customers():
    customers_url = f"{config.ERP_CONFIG['SITE_URL']}{config.ERP_CONFIG['CUSTOMER_URL']}"
    try:
        response = requests.get(customers_url, headers=config.ERP_CONFIG['HEADERS'])
        if response.status_code == 200:
            data = response.json()  # Parse the JSON response
            customers = data.get('data', [])  # Get the customer list
            if customers:
                cursor.execute("DELETE FROM Customer")
                conn.commit()
                # Insert customers into the database
                cursor.executemany("""
                INSERT INTO Customer (name) VALUES (?)
                """, [(customer['name'],) for customer in customers])
                conn.commit()
                print("Customers stored successfully.")
            else:
                print("No customers found in the response.")
        else:
            print(f"Failed to fetch customers. Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


def fetch_customers(search_term="",limit =20):
    """
    Fetch all available Customers from the 'Customer' table in the database.
    """
    # limit=20
    try:
        if search_term.strip():  # If a search term is provided
            query = "SELECT name FROM Customer WHERE name LIKE ? LIMIT ?"
            cursor.execute(query, (f"%{search_term}%", limit))
        else:  # If no search term is provided, fetch the first 'limit' customers
            query = "SELECT name FROM Customer LIMIT ?"
            cursor.execute(query, (limit,))

        customers = [row[0] for row in cursor.fetchall()]  # Extract 'name' field from results
        # print("Fetched customers:", customers)  # Debugging output
        return customers
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while fetching customers from the database: {str(e)}")
        return []


def fetch_and_store_gateway():
    gateway_url = f"{config.ERP_CONFIG['SITE_URL']}{config.ERP_CONFIG['GATEWAY_URL']}"
    try:
        response = requests.get(gateway_url, headers=config.ERP_CONFIG['HEADERS'])
        if response.status_code == 200:
            data = response.json()  # Parse the JSON response
            gateways = data.get('data', [])  # Get the customer list
            if gateways:
                cursor.execute("DELETE FROM Gateway")
                conn.commit()
                # Insert gateway into the database
                cursor.executemany("""
                INSERT INTO Gateway (name) VALUES (?)
                """, [(gateway['name'],) for gateway in gateways])
                conn.commit()
                print("Gateway stored successfully.")
            else:
                print("No gateway found in the response.")
        else:
            print(f"Failed to fetch gateway. Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def fetch_gateways(search_term="",limit =20):
    """
    Fetch all available Gateways from the 'Customer' table in the database.
    """
    # limit=20
    try:
        if search_term.strip():  # If a search term is provided
            query = "SELECT name FROM Gateway WHERE name LIKE ? LIMIT ?"
            cursor.execute(query, (f"%{search_term}%", limit))
        else:  # If no search term is provided, fetch the first 'limit' gateways
            query = "SELECT name FROM Gateway LIMIT ?"
            cursor.execute(query, (limit,))

        gateways = [row[0] for row in cursor.fetchall()]  # Extract 'name' field from results
        # print("Fetched gateways:", gateways)  # Debugging output
        return gateways
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while fetching gateways from the database: {str(e)}")
        return []



def create_new_record():
    create_window = Toplevel(root)
    create_window.title("Create New Record")
    field_width = 25
    # Set the size of the window
    create_window.geometry("600x450")  # Adjust window size (width x height)

    # fields = ["Start Date", "End Date", "Billing Type", "Station", "Customer", "Icris Number", "Export/Import", "Sales Invoice Definition","Posting Date"]
    # fields = ["Start Date", "End Date", "Billing Type", "Station", "Customer", "Icris Number", "Export/Import", "Date Type", "Gateway", "Manifest File Type", "Sales Invoice Definition", "Posting Date"]
    fields = ["Export/Import", "Start Date", "End Date", "Billing Type", "Station", "Customer", "Icris Number", "Date Type", "Gateway", "Manifest File Type", "Sales Invoice Definition", "Posting Date"]
    entries = {}
    # def hide_listbox_on_outside_click(entry_widget, listbox_frame_widget, parent_window):
    #     def handler(event):
    #         x, y = event.x_root, event.y_root
    #         inside_entry = entry_widget.winfo_containing(x, y)
    #         inside_listbox = listbox_frame_widget.winfo_containing(x, y)

    #         if not (inside_entry or inside_listbox):
    #             listbox_frame_widget.place_forget()

    #     parent_window.bind("<Button-1>", handler, add="+")


    # Fetch Icris numbers from the database
    # icris_numbers_list = fetch_icris_numbers()  # Fetch Icris Numbers from the database

    # Create the fields
    for idx, field in enumerate(fields[:-1]):  # Exclude "Sales Invoice Definition" from the fields list
        Label(create_window, text=field).grid(row=idx, column=0, padx=10, pady=5, sticky="w")

        if field in ["Start Date", "End Date"]:  # Use DateEntry for date fields
            entry = DateEntry(create_window, width=field_width, date_pattern="yyyy-MM-dd", background="purple", foreground="white", borderwidth=2)
            entry.grid(row=idx, column=1, padx=10, pady=5, sticky="w")
            entries[field] = entry
        elif field == "Billing Type":  # Use Combobox for Billing Type
            entry = ttk.Combobox(create_window, width=field_width)
            entry['values'] = ["", "Monthly", "Weekly", "Daily", "Single"]
            entry.set("Monthly")  # Set default value to "Monthly"
            entry.grid(row=idx, column=1, padx=10, pady=5, sticky="w")
            entries[field] = entry  # Add it to the entries dictionary
        elif field == "Station":  # Add Station Field
            stations = config.ERP_CONFIG["STATIONS"]

            entry = ttk.Combobox(create_window, width=field_width)
            entry['values'] = stations  # Populate the dropdown with the stations
            entry.set(stations[0])  # Set the default value to the first station in the list
            entry.grid(row=idx, column=1, padx=10, pady=5, sticky="w")
            entries[field] = entry
        elif field == "Export/Import":  # Modify this field to only have "Export"
            entry = ttk.Combobox(create_window, width=field_width)
            entry['values'] = ["", "Export", "Import"]  # Only "Export" and "Import" options
            entry.set("Export")  # Set default value to "Export"
            entry.grid(row=idx, column=1, padx=10, pady=5, sticky="w")
            entries[field] = entry
        elif field == "Customer":  # Change this to an Entry field
            customer_entry = Entry(create_window, width=field_width)  # Use Entry instead of Combobox
            customer_entry.grid(row=idx, column=1, padx=10, pady=5, sticky="w")
            entries[field] = customer_entry

            # Listbox for customer suggestions
            listbox_frame_customer = tk.Frame(create_window, bd=1, relief=tk.RAISED)
            listbox_customer = tk.Listbox(listbox_frame_customer, height=8, selectmode=tk.SINGLE, font=("Arial", 11), activestyle="none")
            listbox_customer.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar = ttk.Scrollbar(listbox_frame_customer, orient=tk.VERTICAL, command=listbox_customer.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            listbox_customer.config(yscrollcommand=scrollbar.set)

            # Initially hide the listbox frame
            listbox_frame_customer.place_forget()

            def show_default_customers(event=None):
                """
                Show the default 20 customers when the customer_entry is clicked and no text is typed.
                """
                if not customer_entry.get().strip():  # If the entry field is empty
                    customers = fetch_customers(limit=20)  # Fetch the first 20 customers
                    # print("Fetched Customers (default):", customers)  # Debugging

                    listbox_customer.delete(0, tk.END)  # Clear previous results
                    for customer in customers:
                        listbox_customer.insert(tk.END, customer)

                    if customers:
                        # Correctly position the listbox relative to the entry field
                        # Place the listbox just below the customer_entry, using its absolute position
                        listbox_frame_customer.place(
                            x=customer_entry.winfo_x(),  # X coordinate of the customer entry
                            y=customer_entry.winfo_y() + customer_entry.winfo_height(),  # Y coordinate just below the entry field
                            width=customer_entry.winfo_width()  # Align the listbox width with the customer entry field
                        )
                        listbox_frame_customer.lift()  # Ensure the listbox appears above other widgets
                        # print("Listbox frame placed.")
                    else:
                        listbox_frame_customer.place_forget()  # Hide the listbox if no customers
                        # print("No customers to show, listbox hidden.")

            def update_customer_dropdown(event):
                """
                Dynamically update the dropdown as the user types in the customer field.
                """
                search_term = customer_entry.get().strip().lower()
                
                if not search_term:
                    customers = fetch_customers(limit=20)  # Fetch the first 20 customers if the field is empty
                else:
                    customers = fetch_customers(search_term=search_term)  # Fetch based on the search term

                listbox_customer.delete(0, tk.END)  # Clear previous results
                for customer in customers:
                    listbox_customer.insert(tk.END, customer)

                if customers:
                    # Place the listbox just below the customer_entry field
                    listbox_frame_customer.place(x=customer_entry.winfo_x(), y=customer_entry.winfo_y() + customer_entry.winfo_height(), width=customer_entry.winfo_width())
                    listbox_frame_customer.lift()  # Ensure the listbox appears above other widgets
                else:
                    listbox_frame_customer.place_forget()  # Hide the listbox if no matches

            customer_entry.bind("<FocusIn>", show_default_customers)
            customer_entry.bind("<Button-1>", show_default_customers)

            customer_entry.bind("<KeyRelease>", update_customer_dropdown)

            def select_customer(event):
                try:
                    selected_customer = listbox_customer.get(listbox_customer.curselection())
                    # print(f"Selected Customer: {selected_customer}")
                    customer_entry.delete(0, tk.END)
                    customer_entry.insert(0, selected_customer)
                    listbox_frame_customer.place_forget()  # Hide the listbox after selection
                except tk.TclError:  # Handle case where no item is selected
                    pass

            listbox_customer.bind("<ButtonRelease-1>", select_customer)
            # listbox_customer.bind("<Button-1>", select_customer)
            # hide_listbox_on_outside_click(customer_entry, listbox_frame_customer, create_window)

            # def hide_listbox_cust(event):
            #     if event.widget not in (customer_entry, listbox_customer, listbox_frame_customer):
            #         listbox_frame_customer.place_forget()  # Hide the listbox if clicked outside

            # def hide_listbox(event):
            #     # Get global (screen) coordinates of the mouse click
            #     x, y = event.x_root, event.y_root

            #     # If the click is NOT inside customer_entry AND NOT inside listbox frame or its children
            #     if not customer_entry.winfo_containing(x, y) and not listbox_frame_customer.winfo_containing(x, y):
            #         listbox_frame_customer.place_forget()

            # create_window.bind("<Button-1>", hide_listbox_cust)
        elif field == "Icris Number":  # Create search box for Icris Number using Combobox
            icris_entry = Entry(create_window, width=field_width)  # Use Entry instead of Combobox
            icris_entry.grid(row=idx, column=1, padx=10, pady=5, sticky="w")
            entries[field] = icris_entry

            # Listbox for customer suggestions
            listbox_frame = tk.Frame(create_window, bd=1, relief=tk.RAISED)
            listbox = tk.Listbox(listbox_frame, height=8, selectmode=tk.SINGLE, font=("Arial", 11), activestyle="none")
            listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=listbox.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            listbox.config(yscrollcommand=scrollbar.set)

            # Initially hide the listbox frame
            listbox_frame.place_forget()

            def show_default_icris_numbers(event=None):
                """
                Show the default 20 customers when the icris_entry is clicked and no text is typed.
                """
                if not icris_entry.get().strip():  # If the entry field is empty
                    icris_numbers = fetch_icris_numbers(limit=20)  # Fetch the first 20 customers
                    # print("Fetched Icris Numbers (default):", icris_numbers)  # Debugging

                    listbox.delete(0, tk.END)  # Clear previous results
                    for icris_number in icris_numbers:
                        listbox.insert(tk.END, icris_number)

                    if icris_numbers:
                        # Correctly position the listbox relative to the entry field
                        # Place the listbox just below the icris_entry, using its absolute position
                        listbox_frame.place(
                            x=icris_entry.winfo_x(),  # X coordinate of the customer entry
                            y=icris_entry.winfo_y() + icris_entry.winfo_height(),  # Y coordinate just below the entry field
                            width=icris_entry.winfo_width()  # Align the listbox width with the customer entry field
                        )
                        listbox_frame.lift()  # Ensure the listbox appears above other widgets
                        # print("Listbox frame placed.")
                    else:
                        listbox_frame.place_forget()  # Hide the listbox if no customers
                        # print("No Icirs Numbers to show, listbox hidden.")

            def update_icris_numbers_dropdown(event):
                """
                Dynamically update the dropdown as the user types in the customer field.
                """
                search_term = icris_entry.get().strip().lower()
                
                if not search_term:
                    icris_numbers = fetch_icris_numbers(limit=20)  # Fetch the first 20 customers if the field is empty
                else:
                    icris_numbers = fetch_icris_numbers(search_term=search_term)  # Fetch based on the search term

                listbox.delete(0, tk.END)  # Clear previous results
                for icris_number in icris_numbers:
                    listbox.insert(tk.END, icris_number)

                if icris_numbers:
                    # Place the listbox just below the icris_entry field
                    listbox_frame.place(x=icris_entry.winfo_x(), y=icris_entry.winfo_y() + icris_entry.winfo_height(), width=icris_entry.winfo_width())
                    listbox_frame.lift()  # Ensure the listbox appears above other widgets
                else:
                    listbox_frame.place_forget()  # Hide the listbox if no matchesButton-1

            icris_entry.bind("<FocusIn>", show_default_icris_numbers)
            icris_entry.bind("<Button-1>", show_default_icris_numbers)
            icris_entry.bind("<KeyRelease>", update_icris_numbers_dropdown)

            def select_icris_number(event):
                try:
                    selected_icris_number = listbox.get(listbox.curselection())
                    # print(f"Selected Icris Number: {selected_icris_number}")
                    icris_entry.delete(0, tk.END)
                    icris_entry.insert(0, selected_icris_number)
                    listbox_frame.place_forget()  # Hide the listbox after selection
                except tk.TclError:  # Handle case where no item is selected
                    pass
            
            listbox.bind("<ButtonRelease-1>", select_icris_number)
            # listbox.bind("<Button-1>", select_icris_number)
            # hide_listbox_on_outside_click(icris_entry, listbox_frame, create_window)

            # def hide_listbox_icris(event):
            #     if event.widget not in (icris_entry, listbox, listbox_frame):
            #         listbox_frame.place_forget()  # Hide the listbox if clicked outside

            # create_window.bind("<Button-1>", hide_listbox_icris)

        elif field == "Manifest File Type" :
            entry = ttk.Combobox(create_window, width=field_width)
            entry['values'] = ["","OPSYS", "ISPS"]  # Only "Export" and "Import" options
            entry.set("")  # Set default value to "Export"
            entry.grid(row=idx, column=1, padx=10, pady=5, sticky="w")
            entries[field] = entry
        elif field ==  "Date Type" :
            entry = ttk.Combobox(create_window, width=field_width)
            entry['values'] = ["Shipped Date", "Import Date"]  # Only "Export" and "Import" options
            entry.set("Shipped Date")  # Set default value to "Export"
            entry.grid(row=idx, column=1, padx=10, pady=5, sticky="w")
            entries[field] = entry


        elif field == "Gateway":  # Change this to an Entry field
            gateway_entry = Entry(create_window, width=field_width)  # Use Entry instead of Combobox
            gateway_entry.grid(row=idx, column=1, padx=10, pady=5, sticky="w")
            entries[field] = gateway_entry

            # Listbox for gateway suggestions
            listbox_frame_gateway = tk.Frame(create_window, bd=1, relief=tk.RAISED)
            listbox_gateway = tk.Listbox(listbox_frame_gateway, height=8, selectmode=tk.SINGLE, font=("Arial", 11), activestyle="none")
            listbox_gateway.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar = ttk.Scrollbar(listbox_frame_gateway, orient=tk.VERTICAL, command=listbox_gateway.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            listbox_gateway.config(yscrollcommand=scrollbar.set)

            # Initially hide the listbox frame
            listbox_frame_gateway.place_forget()

            def show_default_gateway(event=None):
                """
                Show the default 20 gateways when the gateway_entry is clicked and no text is typed.
                """
                if not gateway_entry.get().strip():  # If the entry field is empty
                    gateways = fetch_gateways(limit=20)  # Fetch the first 20 gateways
                    # print("Fetched Gateway (default):", gateways)  # Debugging

                    listbox_gateway.delete(0, tk.END)  # Clear previous results
                    for gateway in gateways:
                        listbox_gateway.insert(tk.END, gateway)

                    if gateways:
                        # Correctly position the listbox relative to the entry field
                        # Place the listbox just below the gateway_entry, using its absolute position
                        listbox_frame_gateway.place(
                            x=gateway_entry.winfo_x(),  # X coordinate of the gateway entry
                            y=gateway_entry.winfo_y() + gateway_entry.winfo_height(),  # Y coordinate just below the entry field
                            width=gateway_entry.winfo_width()  # Align the listbox width with the gateway entry field
                        )
                        listbox_frame_gateway.lift()  # Ensure the listbox appears above other widgets
                        # print("Listbox frame placed.")
                    else:
                        listbox_frame_gateway.place_forget()  # Hide the listbox if no gateways
                        # print("No gateways to show, listbox hidden.")

            def update_gateway_dropdown(event):
                """
                Dynamically update the dropdown as the user types in the gateway field.
                """
                search_term = gateway_entry.get().strip().lower()
                
                if not search_term:
                    gateways = fetch_gateways(limit=20)  # Fetch the first 20 gateways if the field is empty
                else:
                    gateways = fetch_gateways(search_term=search_term)  # Fetch based on the search term

                listbox_gateway.delete(0, tk.END)  # Clear previous results
                for gateway in gateways:
                    listbox_gateway.insert(tk.END, gateway)

                if gateways:
                    # Place the listbox just below the gateway_entry field
                    listbox_frame_gateway.place(x=gateway_entry.winfo_x(), y=gateway_entry.winfo_y() + gateway_entry.winfo_height(), width=gateway_entry.winfo_width())
                    listbox_frame_gateway.lift()  # Ensure the listbox appears above other widgets
                else:
                    listbox_frame_gateway.place_forget()  # Hide the listbox if no matches

            gateway_entry.bind("<FocusIn>", show_default_gateway)
            gateway_entry.bind("<Button-1>", show_default_gateway)
            gateway_entry.bind("<KeyRelease>", update_gateway_dropdown)

            def select_gateway(event):
                try:
                    selected_gateway = listbox_gateway.get(listbox_gateway.curselection())
                    # print(f"Selected Gateway: {selected_gateway}")
                    gateway_entry.delete(0, tk.END)
                    gateway_entry.insert(0, selected_gateway)
                    listbox_frame_gateway.place_forget()  # Hide the listbox after selection
                except tk.TclError:  # Handle case where no item is selected
                    pass

            listbox_gateway.bind("<ButtonRelease-1>", select_gateway)
            # listbox_gateway.bind("<Button-1>", select_gateway)
            # hide_listbox_on_outside_click(gateway_entry, listbox_frame_gateway, create_window)

            # def hide_listbox_gateway(event):
            #     if event.widget not in (gateway_entry, listbox_gateway, listbox_frame_gateway):
            #         listbox_frame_gateway.place_forget()

            # create_window.bind("<Button-1>", hide_listbox_gateway)

        # else:
        #     entry = Entry(create_window)
        #     entry.grid(row=idx, column=1, padx=10, pady=5, sticky="w")
        #     entries[field] = entry
    searchable_pairs = [
        (customer_entry, listbox_frame_customer),
        (icris_entry, listbox_frame),
        (gateway_entry, listbox_frame_gateway)
    ]

    def hide_all_listboxes(event):
        for entry_widget, listbox_frame in searchable_pairs:
            widget = event.widget
            # If clicked widget is not the entry, not the listbox, and not inside listbox
            if widget not in (entry_widget, listbox_frame) and not str(widget).startswith(str(listbox_frame)):
                listbox_frame.place_forget()

    create_window.bind_all("<Button-1>", hide_all_listboxes, add="+")
    sales_invoice_combobox = ttk.Combobox(create_window, width=field_width)
    sales_invoice_combobox.grid(row=idx, column=1, padx=10, pady=5, sticky="w")

    # Populate the dropdown with Sales Invoice Definitions
    invoice_definitions = fetch_sales_invoice_definitions()  # This function fetches the available invoice definitions
    sales_invoice_combobox['values'] = invoice_definitions
    if invoice_definitions:
        sales_invoice_combobox.current(0)  # Set default to the first item

    # Add the Posting Date field
    posting_date_label = Label(create_window, text="Posting Date")
    posting_date_label.grid(row=len(fields)-1, column=0, padx=10, pady=5, sticky="w")
    
    posting_date_entry = DateEntry(create_window, width=field_width, date_pattern="yyyy-MM-dd", background="purple", foreground="white", borderwidth=2)
    posting_date_entry.grid(row=len(fields)-1, column=1, padx=10, pady=5, sticky="w")
    entries["Posting Date"] = posting_date_entry


    # Function to save the new record
    def save_new_record():
        # print('showing entries', entries)
        try:
            # Get the values from the entries
            values = []
            for field, entry in entries.items():
                field_value = entry.get()
                # print(field_value)

                # If the field is "Start Date" or "End Date", ensure it's a valid date format (if empty, set to None)
                # if field in ["Start Date", "End Date", "Posting Date"]:
                #     values.append(field_value if field_value else None)  # If empty, append None
                # # # Handle the "Customer" field, set to None if empty
                # elif field == "Customer":
                #     values.append(field_value if field_value else None)  # If empty, append None
                # else:
                #     values.append(field_value if field_value else None)  # If empty, append None for other fields
                values.append(field_value or None)

            # Debugging: Print the collected values
            # print("Values collected:", values)


            # Get the Sales Invoice Definition value
            sales_invoice_definition = sales_invoice_combobox.get()

            # Ensure the Sales Invoice Definition is also handled correctly
            if not sales_invoice_definition:  # If the Sales Invoice Definition is empty, set to None
                sales_invoice_definition = None

            # Append the Sales Invoice Definition to the values list
            values.append(sales_invoice_definition)

            # Debugging: Print the final values list
            # print("Final values including Sales Invoice Definition:", values)

            # Insert the new record with the Sales Invoice Definition field
            cursor.execute("""
            INSERT INTO records (start_date, end_date, billing_type, station, customer, icris_number, export_import, date_type, gateway, manifest_file_type, posting_date, sales_invoice_definition )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, values)  # Using values as the parameter for the query
            # print(values)
            
            
            new_id = cursor.lastrowid
            # print(f"New record created with ID: {new_id}")  # Debugging: Print the new record ID

            conn.commit()
            create_window.destroy()  # Close the "Create New Record" window
            messagebox.showinfo("Success", "Record created successfully.")
            # load_parent_records()  # Refresh the records view if applicable
            load_parent_records(selected_id=new_id)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save record: {str(e)}")

    Button(create_window, text="Save Record", command=save_new_record).grid(row=len(fields), column=0, columnspan=2, pady=10)
    # Optional: Configure the grid to make it more spacious and organized
    create_window.grid_rowconfigure(len(fields), weight=1)  # Add spacing between the last input field and the save button
    create_window.grid_columnconfigure(0, weight=1)
    create_window.grid_columnconfigure(1, weight=3)


def fetch_counts_from_db():
    """
    Fetch total counts of customers and Icris numbers from the database.
    Returns:
        tuple: (customer_count, icris_number_count)
    """
    try:
        # Fetch the count of customers
        cursor.execute("SELECT COUNT(*) FROM Customer")  # Replace with your actual table and column names
        customer_count = cursor.fetchone()[0]

        # Fetch the count of Icris numbers
        cursor.execute("SELECT COUNT(*) FROM IcrisNumber")  # Replace with your actual table and column names
        icris_number_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM Gateway")  # Replace with your actual table and column names
        gateway_count = cursor.fetchone()[0]

        return customer_count, icris_number_count, gateway_count
    except Exception as e:
        print(f"An error occurred while fetching counts: {str(e)}")
        return 0, 0  # Return 0 if there is an error

def show_count_popup():
    """
    Create and display a popup window with the total customer and Icris number counts.
    """
    # Create a new pop-up window
    popup_window = tk.Toplevel()
    popup_window.title("Settings")
    
    # Set the size of the pop-up window
    popup_window.geometry("700x250")
    
    # Create a frame to organize the labels and buttons
    frame = tk.Frame(popup_window)
    frame.pack(fill="both", expand=True, padx=20, pady=20)

    # Create a frame for the labels (left side)
    label_frame = tk.Frame(frame)
    label_frame.pack(side="left", fill="both", expand=True)

    # Create labels to show the counts
    customer_label = tk.Label(label_frame, 
                              text="Total Customers (Local): 0", 
                              font=("Arial", 12), 
                              anchor="w")  # Left-align the text
    customer_label.pack(pady=10, padx=10, fill="x")  # Add padding on the left and ensure it fills horizontally

    icris_number_label = tk.Label(label_frame, 
                                  text="Total Icris Numbers (Local): 0", 
                                  font=("Arial", 12), 
                                  anchor="w")  # Left-align the text
    icris_number_label.pack(pady=10, padx=10, fill="x") 

    gateway_label = tk.Label(label_frame, 
                              text="Total Gateway (Local): 0", 
                              font=("Arial", 12), 
                              anchor="w")  # Left-align the text
    gateway_label.pack(pady=10, padx=10, fill="x")  # Add padding on the left and ensure it fills horizontally

    # Create a frame for the buttons (right side)
    button_frame = tk.Frame(frame)
    button_frame.pack(side="right", fill="y", padx=20)

    # Function to update the counts dynamically
    def update_counts():
        customer_count, icris_number_count, gateway_count = fetch_counts_from_db()
        customer_label.config(text=f"Total Customers (Local): {customer_count}")
        icris_number_label.config(text=f"Total Icris Numbers (Local): {icris_number_count}")
        gateway_label.config(text=f"Total Gateway Numbers (Local): {gateway_count}")

    # Create Sync buttons
    sync_customers_button = tk.Button(button_frame, text="Sync Customers", width=20, command=lambda: (fetch_and_store_customers(), update_counts()))
    sync_customers_button.pack(pady=10)

    sync_icris_button = tk.Button(button_frame, text="Sync Icris Numbers", width=20, command=lambda: (fetch_and_store_icris_numbers(), update_counts()))
    sync_icris_button.pack(pady=10)

    sync_gateway_button = tk.Button(button_frame, text="Sync Gateway", width=20, command=lambda: (fetch_and_store_gateway(), update_counts()))
    sync_gateway_button.pack(pady=10)
    
    # Add a Close button to close the pop-up
    close_button = tk.Button(popup_window, text="Close", width=10, command=popup_window.destroy)
    close_button.pack(pady=10)

    # Initial count update
    update_counts()



def load_parent_records(selected_id=None):
    table.delete(*table.get_children())
    cursor.execute("SELECT * FROM records ORDER BY id DESC")
    for record in cursor.fetchall():
        # Insert the record into the Treeview
        tree_item = table.insert("", "end", values=record)
        # Auto-select the newly inserted record (assumes record[0] is ID)
        # print(f"Loaded record: {record}")
        if selected_id and record[0] == selected_id:
            table.selection_set(tree_item)
            table.focus(tree_item)
            table.see(tree_item)
            load_shipment_numbers(selected_id)


def on_generate_invoice_button_click():
    # Get the selected parent record ID
    selected_item = table.selection()
    if not selected_item:
        messagebox.showerror("Error", "No parent record selected!")
        return
    # print(selected_item)
    
    parent_id = table.item(selected_item)["values"][0]

    # Check if the operating system is Windows
    if os.name == 'nt':
        command = f"python Generate_sales_invoice.py --parent_id={parent_id} --login_username={logged_in_username}"
        subprocess.run(f'start cmd /k {command}', shell=True)
    else:
        command = f"xterm -geometry 120x40 -hold -e 'python3 Generate_sales_invoice.py --parent_id={parent_id} --login_username={logged_in_username}'"
        subprocess.Popen(command, shell=True)
    load_shipment_numbers(parent_id)


def show_completion_message(message):
    """
    Callback function to update the Tkinter GUI once the task is complete.
    """
    # Show success message in the main thread
    messagebox.showinfo("Success", message)
    # Re-enable the button so it can be clicked again
    generate_invoice_button.config(state="normal")


def on_table_hover(event):
    # Get the row and column under the mouse
    region = shipment_table.identify_region(event.x, event.y)
    if region == "cell":
        row_id = shipment_table.identify_row(event.y)  # Get the row ID
        col_id = shipment_table.identify_column(event.x)  # Get the column ID

        if col_id == "#4":  # Assuming logs are in the 4th column
            cell_value = shipment_table.item(row_id)["values"][3]  # Index is 3 (0-based)
            
            if cell_value:  # Ensure the cell has a value
                x, y, width, height = shipment_table.bbox(row_id, col_id)  # Get bounding box of the cell
                tooltip.showtip(cell_value, x + shipment_table.winfo_rootx(), y + shipment_table.winfo_rooty())
            else:
                tooltip.hidetip()
        else:
            tooltip.hidetip()
    else:
        tooltip.hidetip()



def on_table_scroll_or_configure(event):
    # Manually trigger hover logic using current mouse pointer position
    x = shipment_table.winfo_pointerx() - shipment_table.winfo_rootx()
    y = shipment_table.winfo_pointery() - shipment_table.winfo_rooty()

    # Create a fake event to pass to your existing handler
    fake_event = type("FakeEvent", (object,), {"x": x, "y": y})
    on_table_hover(fake_event)


fetch_and_store_customers()
fetch_and_store_icris_numbers()
fetch_and_store_gateway()


# # Function to populate the dropdown (ComboBox) with Sales Invoice Definitions
# def populate_sales_invoice_dropdown(parent_id):
#     """
#     Populate the dropdown with the Sales Invoice Definition associated with the given parent_id.
#     """
#     # Fetch the Sales Invoice Definition from the 'records' table using parent_id
#     cursor.execute("""
#         SELECT sales_invoice_definition
#         FROM records
#         WHERE id = ?
#     """, (parent_id,))
#     result = cursor.fetchone()

#     if result and result[0]:  # Check if a definition exists
#         sales_invoice_definition = result[0]
#         # Set the dropdown value to the one from the parent record
#         sales_invoice_combobox['values'] = [sales_invoice_definition]
#         sales_invoice_combobox.current(0)  # Set the first value as selected
#     else:
#         # Fetch all available definitions if none are associated with the parent
#         available_definitions = fetch_sales_invoice_definitions()
#         sales_invoice_combobox['values'] = available_definitions
#         if available_definitions:
#             sales_invoice_combobox.current(0)  # Set the first available definition as default

#     # Refresh the UI to ensure updates are displayed
#     root.update_idletasks()


# Initialize the main GUI
root = Tk()
root.title("Sales Invoice Generator")
root.geometry("900x600")
root.minsize(600, 400)  # Set a minimum size to prevent extreme shrinking

style = ttk.Style()

# Set the theme to 'clam' (a lightweight theme that works well for customizations)
style.theme_use('clam')

# Modify general background and foreground colors
style.configure("TButton", background="#5D3A78", foreground="black", font=("Arial", 10, "bold"))
# style.configure("TLabel", background="#5D3A78", foreground="black", font=("Arial", 10, "bold"))
style.configure("TCombobox", background="purple", foreground="black", font=("Arial", 10, "bold"))
style.configure("TTreeview", background="white", foreground="black", fieldbackground="purple", font=("Arial", 10, "bold"))
style.configure("TTreeview.Heading", background="#5D3A78", foreground="black", font=("Arial", 12, "bold"))
style.configure("TEntry", background="purple", foreground="black", font=("Arial", 10, "bold"))

# Set the background color for the root window
root.configure(bg="#5D3A78")




# print('helo')
# Configure the grid layout for responsiveness
root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=3)  # Table column
root.grid_columnconfigure(0, weight=1)

# Parent table
columns = ("id", "export_import", "start_date", "end_date", "billing_type", "station", "customer", "icris_number", "date_type", "gateway", "manifest_file_type", "sales_invoice_definition", "posting_date")
table = ttk.Treeview(root, columns=columns, show="headings", height=10)  # Adjust table height
for col in columns:
    table.heading(col, text=col.replace("_", " ").capitalize())
    table.column(col, anchor="center", width=100)  # Adjust column width

scrollbar = Scrollbar(root, orient="vertical", command=table.yview)
table.configure(yscroll=scrollbar.set)
table.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)
scrollbar.grid(row=0, column=1, sticky="ns")

# Child table
shipment_columns = ("shipment_index", "shipment_number", "sales_invoice", "logs")
shipment_table = ttk.Treeview(root, columns=shipment_columns, show="headings", height=5)  # Adjust table height
for col in shipment_columns:
    shipment_table.heading(col, text=col.replace("_", " ").capitalize())
    shipment_table.column(col, anchor="center", width=100)  # Adjust column width
table.bind("<ButtonRelease-1>", on_parent_record_click)
table.bind("<Double-Button-1>", copy_cell_value_parent)
shipment_scrollbar = Scrollbar(root, orient="vertical", command=shipment_table.yview)
shipment_table.configure(yscroll=shipment_scrollbar.set)
shipment_table.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
shipment_scrollbar.grid(row=1, column=1, sticky="ns")



# Buttons
# Frame for refresh button at the top right
refresh_frame = Frame(root, bg="#5D3A78")
refresh_frame.grid(row=0, column=2, sticky="new", padx=3, pady=(3, 0))

if logged_in_username:
    user_label = tk.Label(refresh_frame, text=f"{logged_in_username}", width=33)
    user_label.pack(pady=5)





refresh_button = Button(refresh_frame, text="⟳ Refresh", command=refresh_shipment_table, width=20)
refresh_button.pack(fill="x")


button_frame = Frame(root, bg="#5D3A78")
button_frame.grid(row=1, column=2, rowspan=2, sticky="ns", padx=3, pady=1)  # Position to the right of both tables
button_frame.grid_rowconfigure(0, weight=1)
button_frame.grid_rowconfigure(0, weight=1)
button_frame.grid_rowconfigure(0, weight=1)
button_frame.grid_rowconfigure(0, weight=1)


button_width = 30  # Set a consistent width for buttons

create_button = Button(button_frame, text="Create New Record", command=create_new_record, width=button_width)
create_button.grid(row=2, column=0, padx=0, pady=0, sticky="ew")

delete_button = Button(button_frame, text="Delete Record", command=delete_parent_record, width=button_width)
delete_button.grid(row=3, column=0, padx=0, pady=0, sticky="ew")

get_shipment_button = Button(button_frame, text="Get Shipment Numbers", command=fetch_shipment_numbers_via_script, width=button_width)
get_shipment_button.grid(row=4, column=0, padx=0, pady=0, sticky="ew")

generate_invoice_button = Button(button_frame, text="Generate Sales Invoice", command=on_generate_invoice_button_click, width=button_width)
generate_invoice_button.grid(row=5, column=0, padx=0, pady=0, sticky="ew")

create_button = tk.Button(button_frame, text="Settings", command=show_count_popup, width=button_width)
create_button.grid(row=6, column=0, padx=0, pady=0, sticky="ew")

download_button = ttk.Button(button_frame, text="Download Shipment Numbers", command=download_selected_shipment_numbers)
download_button.grid(row=7, column=0, padx=0, pady=0, sticky="ew")


class Tooltip:
    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.last_text = ""
        self.last_pos = (None, None)

    def showtip(self, text, x, y):
        # If tooltip is showing and text & position are unchanged, skip
        if self.tipwindow and text == self.last_text and (x, y) == self.last_pos:
            return

        self.hidetip()
        if not text:
            return

        self.last_text = text
        self.last_pos = (x, y)


        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x+20}+{y+20}")
        label = tk.Label(tw, text=text, justify=tk.LEFT,
                        background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                        font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None
        self.last_text = ""
        self.last_pos = (None, None)



# Tooltip for the table
tooltip = Tooltip(shipment_table)

# Bind mouse movement to show tooltip
shipment_table.bind("<Motion>", on_table_hover)
shipment_table.bind("<Leave>", lambda e: tooltip.hidetip())


if system == "Windows" or system == "Darwin":  # Windows or macOS
    shipment_table.bind("<MouseWheel>", on_table_scroll_or_configure)
elif system == "Linux":
    shipment_table.bind("<Button-4>", on_table_scroll_or_configure)  # scroll up
    shipment_table.bind("<Button-5>", on_table_scroll_or_configure)  # scroll down
else:
    shipment_table.bind("<MouseWheel>", on_table_scroll_or_configure)
    shipment_table.bind("<Button-4>", on_table_scroll_or_configure)
    shipment_table.bind("<Button-5>", on_table_scroll_or_configure)

shipment_table.bind("<Configure>", on_table_scroll_or_configure)
shipment_table.bind("<Double-Button-1>", copy_cell_value_child)
        
# Load parent records initially
load_parent_records()

# Start the main loop
root.mainloop()




