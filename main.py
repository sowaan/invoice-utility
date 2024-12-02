# Import necessary modules
import os
import sqlite3
import subprocess
import requests
import tkinter as tk
from tkinter import *
from tkinter import messagebox, ttk,filedialog
from tkcalendar import DateEntry
import threading
import time
import config as config
from tkinter import Tk, Toplevel, messagebox, Scrollbar, Button, Label, Entry, Frame
from tkinter.simpledialog import askstring
from tkinter import Listbox
# from get_shipment_numbers import load_shipment_numbers
import csv
import json
# Create a connection that is thread-safe
conn = sqlite3.connect(config.DATABASE_CONFIG['DB_PATH'], check_same_thread=config.DATABASE_CONFIG['CHECK_SAME_THREAD'])
cursor = conn.cursor()
selected_parent_id = None
# Create the 'records' table if it doesn't exist
# cursor.execute("""
# ALTER TABLE records
# ADD COLUMN posting_date TEXT
# """)
conn.commit()
cursor.execute("""
CREATE TABLE IF NOT EXISTS records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    start_date TEXT,
    end_date TEXT,
    billing_type TEXT,
    station TEXT,
    customer TEXT,
    icris_number TEXT,
    export_import TEXT,  
    sales_invoice_definition TEXT,
    posting_date TEXT  -- New column added
)
""")
conn.commit()

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





# Your ERPNext API details (replace with actual credentials)
site_url = config.ERP_CONFIG['SITE_URL']
shipment_api_url = f"{site_url}{config.ERP_CONFIG['SHIPMENT_API_URL']}"
generate_invoice_api_url = f"{site_url}{config.ERP_CONFIG['GENERATE_SALES_INVOICE_API_URL']}"
headers = config.ERP_CONFIG['HEADERS']
api_key = config.ERP_CONFIG['API_KEY']
api_secret = config.ERP_CONFIG['API_SECRET']




# # Function to fetch shipment numbers
# def get_shipment_numbers(start_date, end_date, billing_type, station, customer, icris_number, export_import):
#     params = {
#         'start_date': start_date,
#         'end_date': end_date,
#         'billing_type': billing_type,
#         'station': station,
#         'customer': customer,
#         'icris_number': icris_number,
#         'import__export': export_import  # Added Export/Import to the parameters
#     }

#     # Use the site URL and API path from config.py
#     shipment_api_url = f"{config.ERP_CONFIG['SITE_URL']}{config.ERP_CONFIG['SHIPMENT_API_URL']}"

#     # Send the request using the shipment_api_url
#     response = requests.get(shipment_api_url, headers=config.ERP_CONFIG['HEADERS'], params=params)

    
#     if response.status_code == 200:
#         data = response.json()  # Parse the JSON response
#         return data.get('message', [])
#     else:
#         messagebox.showerror("Error", f"Failed to fetch shipment numbers. Status code: {response.status_code}")
#         return []





# Load shipment numbers in the child table
def load_shipment_numbers(parent_id):
    # Clear any existing data in the child table
    shipment_table.delete(*shipment_table.get_children())

    if parent_id is None:
        return

    cursor.execute("SELECT shipment_index, shipment_number, sales_invoice, logs FROM shipment_numbers WHERE parent_id = ?", (parent_id,))
    records = cursor.fetchall()

    if records:
        for record in records:
            shipment_table.insert("", "end", values=record)
    else:
        # Show a message when no child records are available for the selected parent
        shipment_table.insert("", "end", values=("No shipment records", "", "", ""))




def fetch_shipment_numbers_via_script():

    selected_item = table.selection()
    parent_id = table.item(selected_item)["values"][0]
    command = f"xterm -hold -e 'python3 get_shipment_numbers.py --parent_id={parent_id}'"
    # command = f"xterm -hold -e 'python3 Generate_sales_invoice.py --parent_id={parent_id}'"
    process = subprocess.Popen(command, shell=True)    # Use subprocess to execute the command
    
    # print(process)
    # return process
    
# # Function to fetch and insert shipment numbers
# def fetch_and_insert_shipment_numbers(parent_id):
#     cursor.execute("DELETE FROM shipment_numbers WHERE parent_id = ?", (parent_id,))
#     conn.commit()

#     parent_record = cursor.execute("""
#         SELECT start_date, end_date, billing_type, station, customer, icris_number, export_import
#         FROM records WHERE id = ?
#     """, (parent_id,)).fetchone()
    
#     if not parent_record:
#         messagebox.showerror("Error", "Parent record not found!")
#         return

#     start_date, end_date, billing_type, station, customer, icris_number, export_import = parent_record
#     shipment_numbers = fetch_shipment_numbers_via_script(
#     start_date="" if start_date== None else start_date,
#     end_date="" if end_date== None else end_date,
#     billing_type="" if billing_type== None else billing_type,
#     station="" if station== None else station,
#     customer="" if customer== None else customer,
#     icris_number="" if icris_number== None else icris_number,
#     export_import="" if export_import== None else export_import
# )


#     if not shipment_numbers:
#         messagebox.showinfo("Info", "No shipment data found.")
#         return

#     for idx, shipment_number in enumerate(shipment_numbers, start=1):
#         # Ensure all five values are provided: parent_id, shipment_number, empty sales_invoice, empty logs, and shipment_index
#         cursor.execute("""
#         INSERT INTO shipment_numbers (parent_id, shipment_number, sales_invoice, logs, shipment_index) 
#         VALUES (?, ?, '', '', ?)
#         """, (parent_id, shipment_number, idx))  # We're passing 5 values: parent_id, shipment_number, '', '', idx
#         conn.commit()

#     messagebox.showinfo("Success", "Shipment numbers updated successfully.")
    




# Function to handle "Get Shipment Numbers" button click
def get_shipment_numbers_for_selected_parent():
    selected_item = table.selection()
    if not selected_item:
        messagebox.showerror("Error", "No parent record selected!")
        return

    parent_id = table.item(selected_item)["values"][0]  # Get the parent record ID
    load_shipment_numbers(parent_id)
    
    # process = subprocess.Popen(command, shell=True)










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






def on_parent_record_click(event):
    global selected_parent_id
    selected_item = table.selection()  # Get the selected row
    if not selected_item:
        return

    selected_parent_id = table.item(selected_item)["values"][0]  # Store the selected parent record ID
    load_shipment_numbers(selected_parent_id)

def download_selected_shipment_numbers():
    global selected_parent_id
    if not selected_parent_id:
        messagebox.showerror("Error", "No parent record selected!")
        return

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


def on_generate_invoice_button_click():
      
    # # Get the selected parent record ID
    selected_item = table.selection()
    
    parent_id = table.item(selected_item)["values"][0]

    
    command = f"xterm -hold -e 'python3 Generate_sales_invoice.py --parent_id={parent_id}'"
    process = subprocess.Popen(command, shell=True)


def show_completion_message(message):
    """
    Callback function to update the Tkinter GUI once the task is complete.
    """
    # Show success message in the main thread
    messagebox.showinfo("Success", message)
    # Re-enable the button so it can be clicked again
    generate_invoice_button.config(state="normal")




# Configure the grid layout for responsiveness
root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=3)  # Table column
root.grid_columnconfigure(0, weight=1)

# Parent table
columns = ("id", "start_date", "end_date", "billing_type", "station", "customer", "icris_number", "export_import", "sales_invoice_definition","posting_date")
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
shipment_scrollbar = Scrollbar(root, orient="vertical", command=shipment_table.yview)
shipment_table.configure(yscroll=shipment_scrollbar.set)
shipment_table.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
shipment_scrollbar.grid(row=1, column=1, sticky="ns")





# Buttons
button_frame = Frame(root, bg="#5D3A78")
button_frame.grid(row=1, column=2, rowspan=2, sticky="ns", padx=3, pady=1)  # Position to the right of both tables
button_frame.grid_rowconfigure(0, weight=1)
button_frame.grid_rowconfigure(0, weight=1)
button_frame.grid_rowconfigure(0, weight=1)
button_frame.grid_rowconfigure(0, weight=1)

button_width = 20  # Set a consistent width for buttons




def fetch_and_store_icris_numbers():
    icris_numbers_url = f"{config.ERP_CONFIG['SITE_URL']}{config.ERP_CONFIG['ICRIS_NUMBER_URL']}"
    
    try:
        response = requests.get(icris_numbers_url, headers=config.ERP_CONFIG['HEADERS'])
        
        # Debug: print response details
        print(f"Status Code: {response.status_code}")
        print(f"Response Content: {response.content}")  # Print raw content

        if response.status_code == 200:
            data = response.json()  # Parse the JSON response
            
            # Debug: print the response data structure
            print(f"Response JSON: {data}")

            # Extract Icris Numbers from the 'data' field
            icris_numbers = data.get('data', [])
            print(f"Extracted Icris Numbers: {icris_numbers}")  # Check if the data is extracted correctly
            
            if icris_numbers:
                cursor.execute("DELETE FROM IcrisNumber")
                conn.commit()
                for icris_number in icris_numbers:
                    shipper_no = icris_number.get('shipper_no')
                    print(f"Added shipper_no: {shipper_no}")  # Debug: print each shipper_no

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
        print("Fetched customers:", customers)  # Debugging output
        return customers
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while fetching customers from the database: {str(e)}")
        return []

def create_new_record():
    create_window = Toplevel(root)
    create_window.title("Create New Record")
    field_width = 25
    # Set the size of the window
    create_window.geometry("600x400")  # Adjust window size (width x height)

    fields = ["Start Date", "End Date", "Billing Type", "Station", "Customer", "Icris Number", "Export/Import", "Sales Invoice Definition","Posting Date"]
    entries = {}

    # Fetch Icris numbers from the database
    icris_numbers_list = fetch_icris_numbers()  # Fetch Icris Numbers from the database

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
            entry.set("")  # Set default value to "Monthly"
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
            entry.set("")  # Set default value to "Export"
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
                    print("Fetched Customers (default):", customers)  # Debugging

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
                        print("Listbox frame placed.")
                    else:
                        listbox_frame_customer.place_forget()  # Hide the listbox if no customers
                        print("No customers to show, listbox hidden.")

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
            customer_entry.bind("<KeyRelease>", update_customer_dropdown)

            def select_customer(event):
                try:
                    selected_customer = listbox_customer.get(listbox_customer.curselection())
                    print(f"Selected Customer: {selected_customer}")
                    customer_entry.delete(0, tk.END)
                    customer_entry.insert(0, selected_customer)
                    listbox_frame_customer.place_forget()  # Hide the listbox after selection
                except tk.TclError:  # Handle case where no item is selected
                    pass

            listbox_customer.bind("<Button-1>", select_customer)

            def hide_listbox(event):
                if event.widget not in (customer_entry, listbox_customer, listbox_frame_customer):
                    listbox_frame_customer.place_forget()  # Hide the listbox if clicked outside

            create_window.bind("<Button-1>", hide_listbox)

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
                    print("Fetched Icris Numbers (default):", icris_numbers)  # Debugging

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
                        print("Listbox frame placed.")
                    else:
                        listbox_frame.place_forget()  # Hide the listbox if no customers
                        print("No Icirs Numbers to show, listbox hidden.")

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
                    listbox_frame.place_forget()  # Hide the listbox if no matches

            icris_entry.bind("<FocusIn>", show_default_icris_numbers)
            icris_entry.bind("<KeyRelease>", update_icris_numbers_dropdown)

            def select_icris_number(event):
                try:
                    selected_icris_number = listbox.get(listbox.curselection())
                    print(f"Selected Icris Number: {selected_icris_number}")
                    icris_entry.delete(0, tk.END)
                    icris_entry.insert(0, selected_icris_number)
                    listbox_frame.place_forget()  # Hide the listbox after selection
                except tk.TclError:  # Handle case where no item is selected
                    pass

            listbox.bind("<Button-1>", select_icris_number)

            def hide_listbox(event):
                if event.widget not in (icris_entry, listbox, listbox_frame):
                    listbox_frame.place_forget()  # Hide the listbox if clicked outside

            create_window.bind("<Button-1>", hide_listbox)

        # else:
        #     entry = Entry(create_window)
        #     entry.grid(row=idx, column=1, padx=10, pady=5, sticky="w")
        #     entries[field] = entry

    
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
        try:
            # Get the values from the entries
            values = []
            for field, entry in entries.items():
                field_value = entry.get()

                # If the field is "Start Date" or "End Date", ensure it's a valid date format (if empty, set to None)
                if field in ["Start Date", "End Date", "Posting Date"]:
                    values.append(field_value if field_value else "")  # If empty, append None
                # Handle the "Customer" field, set to None if empty
                elif field == "Customer":
                    values.append(field_value if field_value else "")  # If empty, append None
                else:
                    values.append(field_value if field_value else "")  # If empty, append None for other fields

            # Debugging: Print the collected values
            print("Values collected:", values)


            # Get the Sales Invoice Definition value
            sales_invoice_definition = sales_invoice_combobox.get()

            # Ensure the Sales Invoice Definition is also handled correctly
            if not sales_invoice_definition:  # If the Sales Invoice Definition is empty, set to None
                sales_invoice_definition = None

            # Append the Sales Invoice Definition to the values list
            values.append(sales_invoice_definition)

            # Debugging: Print the final values list
            print("Final values including Sales Invoice Definition:", values)

            # Insert the new record with the Sales Invoice Definition field
            cursor.execute("""
            INSERT INTO records (start_date, end_date, billing_type, station, customer, icris_number, export_import, posting_date, sales_invoice_definition)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?,?)
        """, values)  # Using values as the parameter for the query

            conn.commit()
            create_window.destroy()  # Close the "Create New Record" window
            messagebox.showinfo("Success", "Record created successfully.")
            load_parent_records()  # Refresh the records view if applicable

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save record: {str(e)}")

    Button(create_window, text="Save Record", command=save_new_record).grid(row=len(fields)+1, column=0, columnspan=2, pady=10)
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

        return customer_count, icris_number_count
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
    popup_window.geometry("600x200")
    
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

    # Create a frame for the buttons (right side)
    button_frame = tk.Frame(frame)
    button_frame.pack(side="right", fill="y", padx=20)

    # Function to update the counts dynamically
    def update_counts():
        customer_count, icris_number_count = fetch_counts_from_db()
        customer_label.config(text=f"Total Customers (Local): {customer_count}")
        icris_number_label.config(text=f"Total Icris Numbers (Local): {icris_number_count}")

    # Create Sync buttons
    sync_customers_button = tk.Button(button_frame, text="Sync Customers", width=20, command=lambda: (fetch_and_store_customers(), update_counts()))
    sync_customers_button.pack(pady=10)

    sync_icris_button = tk.Button(button_frame, text="Sync Icris Numbers", width=20, command=lambda: (fetch_and_store_icris_numbers(), update_counts()))
    sync_icris_button.pack(pady=10)
    
    # Add a Close button to close the pop-up
    close_button = tk.Button(popup_window, text="Close", command=popup_window.destroy)
    close_button.pack(pady=20)

    # Initial count update
    update_counts()






create_button = Button(button_frame, text="Create New Record", command=create_new_record, width=button_width)
create_button.grid(row=1, column=0, padx=0, pady=0, sticky="ew")

delete_button = Button(button_frame, text="Delete Record", command=delete_parent_record, width=button_width)
delete_button.grid(row=2, column=0, padx=0, pady=0, sticky="ew")

get_shipment_button = Button(button_frame, text="Get Shipment Numbers", command=fetch_shipment_numbers_via_script, width=button_width)
get_shipment_button.grid(row=3, column=0, padx=0, pady=0, sticky="ew")

generate_invoice_button = Button(button_frame, text="Generate Sales Invoice", command=on_generate_invoice_button_click, width=button_width)
generate_invoice_button.grid(row=4, column=0, padx=0, pady=0, sticky="ew")

create_button = tk.Button(button_frame, text="Settings", command=show_count_popup, width=button_width)
create_button.grid(row=5, column=0, padx=0, pady=0, sticky="ew")

download_button = ttk.Button(button_frame, text="Download Shipment Numbers", command=download_selected_shipment_numbers)
download_button.grid(row=6, column=0, padx=0, pady=0, sticky="ew")



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


class Tooltip:
    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None

    def showtip(self, text, x, y):
        """Show a tooltip near the given coordinates."""
        if self.tipwindow or not text:
            return
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x+20}+{y+20}")  # Position slightly offset from the pointer
        label = tk.Label(tw, text=text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None

# Tooltip for the table
tooltip = Tooltip(shipment_table)

# Bind mouse movement to show tooltip
shipment_table.bind("<Motion>", on_table_hover)




def load_parent_records():
    table.delete(*table.get_children())
    cursor.execute("SELECT * FROM records")
    for record in cursor.fetchall():
        table.insert("", "end", values=record)
# Load parent records initially
load_parent_records()

# Start the main loop
root.mainloop()
