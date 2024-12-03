# Sales Invoice Utility

A Tkinter-based desktop application designed to streamline the process of fetching shipment data, managing it, and generating sales invoices through ERPNext APIs. The application is responsive, efficient, and supports multitasking.

---

## Table of Contents
1. [Overview](#overview)
2. [Features](#features)
3. [Prerequisites](#prerequisites)
4. [Installation and Setup](#installation-and-setup)
5. [User Guide](#user-guide)
   - [Setting Filters](#setting-filters)
   - [Fetching Shipment Numbers](#fetching-shipment-numbers)
   - [Viewing and Managing Shipments in the Child Table](#viewing-and-managing-shipments-in-the-child-table)
   - [Generating Sales Invoices](#generating-sales-invoices)
   - [Downloading Sales Invoice Logs](#downloading-sales-invoice-logs)
   - [Using the Settings Page](#using-the-settings-page)
6. [Technical Details](#technical-details)
   - [API Integration](#api-integration)
   - [Database Overview](#database-overview)
   - [Multitasking and Responsiveness](#multitasking-and-responsiveness)


---

## Overview
The **Shipment-to-Sales Invoice Utility** simplifies the workflow for managing shipments and generating sales invoices. It integrates with ERPNext APIs to fetch shipment data and ICRIS numbers, manage customers, and handle invoice creation seamlessly.

---

## Features
- **Dynamic Filtering:** Retrieve shipment numbers based on user-defined filters.
- **Child Table Management:** Display and manage fetched shipment data.
- **Sales Invoice Generation:** Generate invoices for selected shipments.
- **Download Logs:** Export logs of generated invoices in CSV format.
- **Settings Page:**
  - Sync customer data and ICRIS numbers from ERPNext.
  - Store and manage these locally for quick access.
- **Responsive Design:** Optimized for multitasking.

---

## Prerequisites
- Python 3.x installed.
- ERPNext instance with API access enabled.
- API keys and permissions for:
  - Fetching shipments, customers, and ICRIS numbers.
  - Creating invoices.
- Database configured for local storage.

---
## Installation and Setup

### Step 1: Clone the Repository
```bash
### Step 1: Clone the Repository
``` 
- pip install -r requirements.txt
- python main.py
---
## User Guide

### Setting Filters
- Use the filter section to specify criteria, such as:
  - Shipment Date
  - Shipment Status
  - Customer
- Apply filters to retrieve shipment numbers matching the criteria.

### Fetching Shipment Numbers
- After setting filters, fetch shipment numbers using the **Fetch** button.
- The fetched shipment numbers are displayed in the child table.

### Viewing and Managing Shipments in the Child Table
- Use the child table to view fetched shipment details.
- Select or deselect shipments for further processing.
- Update entries in the table as needed.

### Generating Sales Invoices
- Select shipments from the child table.
- Click the **Generate Invoices** button to create invoices via ERPNext.
- A success or error message will confirm the operation.

### Downloading Sales Invoice Logs
- Go to the **Logs** section in the application.
- Click the **Download Logs** button to save a CSV file of sales invoice logs.

### Using the Settings Page
- Navigate to the **Settings Page** from the main menu.
- **Sync Customers:**
  - Fetch customer data from ERPNext and store it in the local database.
- **Sync ICRIS Numbers:**
  - Retrieve ICRIS numbers from ERPNext and save them locally for quick access.
 
## Technical Details

### API Integration
The application integrates with ERPNext APIs to perform key tasks:
- **Fetch Shipments:** `GET /api/resource/Shipment`
- **Create Invoices:** `POST /api/resource/Sales Invoice`
- **Sync Customers:** `GET /api/resource/Customer`
- **Sync ICRIS Numbers:** `GET /api/resource/ICRIS`

### Database Overview
- **Customer Table:** Stores customer details such as names, IDs, and contact information.
- **ICRIS Table:** Stores synced ICRIS numbers and any associated metadata.
- **Records Table:** Stores general records related to shipments and invoices, such as timestamps and statuses.
- **Shipment Numbers Table:** Stores shipment numbers fetched from ERPNext, associated with relevant records and customer data.
  
### Multitasking and Responsiveness
- The application supports multitasking for smooth, uninterrupted workflows.
- Designed with responsiveness to handle simultaneous tasks efficiently.   
