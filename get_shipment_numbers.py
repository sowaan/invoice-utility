import sqlite3
import requests
import argparse
import config
from tkinter import messagebox
import sys
from tqdm import tqdm
import os
conn = sqlite3.connect(config.DATABASE_CONFIG['DB_PATH'], check_same_thread=config.DATABASE_CONFIG['CHECK_SAME_THREAD'])
cursor = conn.cursor()



def get_shipment_numbers(export_import="", start_date ="", end_date ="", billing_type="", station="", customer="", icris_number="", manifest_file_type = "", date_type="", gateway=""):
    """
    Fetch shipment numbers based on the given filters.
    """
    params = {
        'import__export': export_import ,
        'start_date': start_date,
        'end_date': end_date,
        'billing_type': billing_type,
        'station': station,
        'customer': customer,
        'icris_number': icris_number,
        'manifest_file_type':manifest_file_type,
        'date_type':date_type,
        'gateway':gateway
    }
    print("Getting Shipment Numbers.........")

    shipment_api_url = f"{config.ERP_CONFIG['SITE_URL']}{config.ERP_CONFIG['SHIPMENT_API_URL']}"
    

    try:
        # Make the GET request
        # print(f"Fetching shipment numbers from {shipment_api_url} with params: {params}")
         # Use the requests library to make the API call
        response = requests.get(shipment_api_url, headers=config.ERP_CONFIG['HEADERS'], params=params)
        if response.status_code == 200:
            data = response.json()
            shipment_numbers = data.get('message', [])
            return shipment_numbers  # Return shipment numbers
            
        else:
            print(f"Failed to fetch shipment numbers. Status code: {response.status_code}")
            return []

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return []



# Function to fetch and insert shipment numbers
def fetch_and_insert_shipment_numbers(parent_id):
    cursor.execute("DELETE FROM shipment_numbers WHERE parent_id = ?", (parent_id,))
    conn.commit()


    # print('parent_id',parent_id)
    # parent_record = cursor.execute("""
    #     SELECT export_import, start_date, end_date, billing_type, station, customer, icris_number, date_type, manifest_file_type, gateway
    #     FROM records WHERE id = ?
    # """, (parent_id,)).fetchone()

    # print('parent_record',parent_record)



    parent_record = cursor.execute("SELECT * FROM records WHERE id = ?", (parent_id,)).fetchone()
    
    
    if not parent_record:
        messagebox.showerror("Error", "Parent record not found!")
        return

    idx, export_import, start_date, end_date, billing_type, station, customer, icris_number, date_type, gateway, manifest_file_type, sid, pd = parent_record
    shipment_numbers = get_shipment_numbers(
    export_import="" if export_import== None else export_import,
    start_date="" if start_date== None else start_date,
    end_date="" if end_date== None else end_date,
    billing_type="" if billing_type== None else billing_type,
    station="" if station== None else station,
    customer="" if customer== None else customer,
    icris_number="" if icris_number== None else icris_number,
    manifest_file_type="" if manifest_file_type== None else manifest_file_type,
    date_type="" if date_type== None else date_type,
    gateway="" if gateway== None else gateway

    )

    
    if not shipment_numbers:
        messagebox.showinfo("Info", "No shipment data found.")
        return

    records_to_insert = [
    (parent_id, shipment_number, '', '', idx)
    for idx, shipment_number in enumerate(shipment_numbers, start=1)
        ]
    # Perform a single batch insert
    cursor.executemany("""
    INSERT INTO shipment_numbers (parent_id, shipment_number, sales_invoice, logs, shipment_index)
    VALUES (?, ?, ?, ?, ?)
    """, records_to_insert)
    conn.commit()
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"Successfully inserted {len(shipment_numbers)} shipment numbers.")
    messagebox.showinfo("Success", f"Fetched {len(shipment_numbers)} shipment numbers successfully.")







parser = argparse.ArgumentParser(description="Fetch and insert shipment numbers for a given parent record.")
parser.add_argument("--parent_id", required=True, help="Parent Id")

args = parser.parse_args()

# Call the function with the arguments from the command line
# print(f"Fetching and inserting shipment numbers for parent_id: {args}")
fetch_and_insert_shipment_numbers(args.parent_id)
