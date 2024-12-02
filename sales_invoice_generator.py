import argparse
import requests
import sqlite3
from tkinter import messagebox
import config  # Importing the config file
import sys
from array import array
from tqdm import tqdm
import time

conn = sqlite3.connect(config.DATABASE_CONFIG['DB_PATH'])  # Use DB_PATH from config
cursor = conn.cursor()



def generate_sales_invoices(parent_id):
    """
    Generate sales invoices for the selected parent record.
    This function runs in a separate thread to avoid blocking the main GUI.
    """
    try:
        # Establish the SQLite connection and cursor (use config for the database path)
        conn = sqlite3.connect(config.DATABASE_CONFIG['DB_PATH'])
        cursor = conn.cursor()

        # Fetch all required details in a single step
        shipment_numbers, sales_invoice_definition,posting_date = fetch_parent_record_details(parent_id, conn, cursor)
        # Total number of shipment numbers for progress tracking
        shipment_numbers_count = len(shipment_numbers)

        # API endpoint for generating invoices (use ERP_CONFIG for API URL)
        generate_invoice_api_url = f"{config.ERP_CONFIG['SITE_URL']}{config.ERP_CONFIG['GENERATE_SALES_INVOICE_API_URL']}"

        # Use tqdm to show progress bar for invoice creation
        for i in tqdm(range(shipment_numbers_count), desc="Creating Invoices"):
            shipment_number = shipment_numbers[i][0]
            existing_invoice = shipment_numbers[i][1]
           
            # Skip the shipment if a sales invoice already exists
            if existing_invoice != "":
                
                time.sleep(0.1)
                continue  # Skip this shipment number if sales invoice is already present

            # Prepare the payload for the API request
            payload = {
                'shipment_number': shipment_number,
                'sales_invoice_definition': sales_invoice_definition,
                'end_date': posting_date
            }

            try:
                # Make the API request to generate the sales invoice
                response = requests.post(generate_invoice_api_url, headers=config.ERP_CONFIG['HEADERS'], json=payload)

                if response.status_code == 200:
                    # Parse the sales invoice name from the response
                    response_data = response.json()
                    message_data = response_data.get('message', {})
                    sales_invoice_name = message_data.get('name', "")
                    logs = "; ".join(message_data.get('message', [])) if len(message_data.get('message', [])) > 0 else ""
                    
                    # Update the database with the generated sales invoice name and logs
                    update_sales_invoice_column(conn, cursor, shipment_number, sales_invoice_name, logs)

                elif response.status_code == 409:
                    # Invoice already exists for this shipment number, no further action needed
                    print(f"Invoice already exists for Shipment {shipment_number}.")
                    pass  # Skip if the invoice already exists

                else:
                    # Handle other HTTP errors
                    print(f"Error for Shipment {shipment_number}: {response.text}")
                    pass  # Log or update based on error if needed

            except Exception as e:
                # Handle any exceptions that occur during the request
                print(f"Error processing Shipment {shipment_number}: {str(e)}")
                pass  # Handle error as needed

        print("All invoices created!")  # Print once all invoices are processed

    finally:
        # Ensure the database connection is closed after processing is done
        conn.close()






def fetch_parent_record_details(parent_id, conn, cursor):
    """
    Fetch shipment numbers and sales invoice definition for the parent record ID.
    """
    try:
        # Fetch shipment number objects for the parent ID
        cursor.execute("SELECT shipment_number, sales_invoice, logs FROM shipment_numbers WHERE parent_id = ?", (parent_id,))
        shipment_numbers = [row for row in cursor.fetchall()]  # List of shipment number object
        
        if len(shipment_numbers) == 0:
            messagebox.showinfo("Error", "No shipment numbers found for this record.")
            return None, None, None
        
        # Fetch sales_invoice_definition and end_date from the parent record
        cursor.execute("SELECT sales_invoice_definition, posting_date FROM records WHERE id = ?", (parent_id,))
        record_details = cursor.fetchone()

        if not record_details:
            messagebox.showinfo("Error", "Parent record not found!")
            return None, None, None
        
        sales_invoice_definition, posting_date = record_details
        return shipment_numbers, sales_invoice_definition, posting_date

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
# Parse the arguments
args = parser.parse_args()
generate_sales_invoices(args.parent_id)



