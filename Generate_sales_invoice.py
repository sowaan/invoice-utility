import argparse
import requests
import sqlite3
from tkinter import messagebox
import config  # Importing the config file
import sys
from array import array
from tqdm import tqdm
import time
import json
from requests.exceptions import ConnectionError, RequestException, Timeout

# print('generate')
conn = sqlite3.connect(config.DATABASE_CONFIG['DB_PATH'])  # Use DB_PATH from config
cursor = conn.cursor()

create = 0
duplicate = 0

def generate_sales_invoices(parent_id, login_username):
    """
    Generate sales invoices for the selected parent record.
    This function runs in a separate thread to avoid blocking the main GUI.
    """
    global create, duplicate
    try:
        conn = sqlite3.connect(config.DATABASE_CONFIG['DB_PATH'])
        cursor = conn.cursor()

        shipment_numbers, sales_invoice_definition, end_date = fetch_parent_record_details(parent_id, conn, cursor)
        shipment_numbers_count = len(shipment_numbers)
        generate_invoice_api_url = f"{config.ERP_CONFIG['SITE_URL']}{config.ERP_CONFIG['GENERATE_SALES_INVOICE_API_URL']}"
        # fetch_logs_api_url = f"{config.ERP_CONFIG['SITE_URL']}{config.ERP_CONFIG['FETCH_LOGS_API_URL']}"  # Add in config

        with tqdm(total=shipment_numbers_count, desc="Processing Shipments") as pbar:
            for i in range(shipment_numbers_count):
                item = shipment_numbers[i]

                shipment_number = item["shipment_number"]
                manifest_input_date = item["manifest_input_date"]
                existing_invoice = item["sales_invoice"]

                if existing_invoice:
                    duplicate += 1
                    pbar.set_postfix(Created=create, Duplicate=duplicate)
                    pbar.update(1)
                    time.sleep(0.1)
                    continue

                payload = {
                    'parent_id': parent_id,
                    'login_username': login_username,
                    'shipment_number': shipment_number,
                    'sales_invoice_definition': sales_invoice_definition,
                    'end_date': end_date,
                    'manifest_input_date': manifest_input_date
                }
                response = requests.post(generate_invoice_api_url, headers=config.ERP_CONFIG['HEADERS'], json=payload)
                if response.status_code == 200:
                    try:
                        logs_data = response.json()
                        if isinstance(logs_data, str):
                            logs_data = json.loads(logs_data)
                        
                        message_data = logs_data.get("message", {})

                        if not isinstance(message_data, dict):
                            message_data = {}

                        sales_invoice_name = message_data.get("sales_invoice_name", "")
                        logs = message_data.get("logs", "")
                        if message_data.get("sales_invoice_status") == "Already Created":
                            duplicate += 1
                        elif message_data.get("sales_invoice_status") == "Created":
                            create += 1
                        
                        update_sales_invoice_column(conn, cursor, shipment_number, sales_invoice_name, logs)
                    except Exception as e:
                        print(f"Error parsing JSON response: {str(e)}")
                else:
                    print(f"Error generating invoice for shipment {shipment_number}: {response.status_code} - {response.text}")
                    continue
                pbar.set_postfix(Created=create, Duplicate=duplicate)
                pbar.update(1)
            tqdm.write("All invoices processed successfully!")
    finally:
        conn.close()



def fetch_parent_record_details(parent_id, conn, cursor):
    """
    Fetch shipment numbers (with manifest_input_date)
    and sales invoice definition for the parent record ID.
    """
    try:
        cursor.execute("""
            SELECT
                shipment_number,
                sales_invoice,
                logs,
                manifest_input_date
            FROM shipment_numbers
            WHERE parent_id = ?
        """, (parent_id,))

        rows = cursor.fetchall()
        if not rows:
            messagebox.showinfo("Error", "No shipment numbers found for this record.")
            return None, None, None

        shipment_numbers = [
            {
                "shipment_number": row[0],
                "sales_invoice": row[1],
                "logs": row[2],
                "manifest_input_date": row[3]
            }
            for row in rows
        ]

        cursor.execute("""
            SELECT sales_invoice_definition, end_date
            FROM records
            WHERE id = ?
        """, (parent_id,))
        record_details = cursor.fetchone()

        if not record_details:
            messagebox.showinfo("Error", "Parent record not found!")
            return None, None, None

        sales_invoice_definition, end_date = record_details
        return shipment_numbers, sales_invoice_definition, end_date

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")
        return None, None, None


def update_sales_invoice_column(conn, cursor, shipment_number, sales_invoice_name,logs):
    """
    Update the `sales_invoice` column for the corresponding shipment number.
    """
    try:
        if isinstance(logs, (list, array)):  # Check if logs is a list or an array.array
            logs = "; ".join(map(str, logs))  # Convert each element to string and join
        elif logs is None:
            logs = ""
        cursor.execute(
            "UPDATE shipment_numbers SET sales_invoice = ?, logs = ? WHERE shipment_number = ?",
            (sales_invoice_name, logs, shipment_number)
        )
        conn.commit()
        # print(f"Shipment number {shipment_number} updated with sales invoice {sales_invoice_name}.")
    except Exception as e:
        print(f"Error updating sales invoice for shipment number {shipment_number}: {str(e)}")





# Hardcoded parameters to start invoice generation
parser = argparse.ArgumentParser(description="Generate Sales Invoices.")
# Define the named argument
parser.add_argument("--parent_id", required=True, help="Parent Id")
parser.add_argument("--login_username", required=True, help="Login Username")
# Parse the arguments
args = parser.parse_args()
generate_sales_invoices(args.parent_id, args.login_username)



