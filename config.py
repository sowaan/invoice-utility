import os

DATABASE_CONFIG = {
    'DB_PATH': 'data.db',  # Path to SQLite database
    'CHECK_SAME_THREAD': False,  # Ensure thread safety
}

# ERPNext API Configuration
ERP_CONFIG = {
    "SITE_URL": "http://127.0.0.1:8000/",
    'API_KEY': 'XXXXXXXX',  # Your local API Key
    'API_SECRET': 'YYYYYYYY',  # Your Local API Secret
    'HEADERS': {
        'Authorization': 'token XXXXXXXX:YYYYYYYY',  # Updated Authorization header
        'Content-Type': 'application/json',
    },

    'SHIPMENT_API_URL':'api/method/uls_booking.uls_booking.api.sales_invoice_script.get_shipment_numbers_and_sales_invoices',
    'GENERATE_SALES_INVOICE_API_URL': 'api/method/uls_booking.uls_booking.api.sales_invoice_script.generate_single_invoice',
    'FETCH_LOGS_API_URL': 'api/method/uls_booking.uls_booking.api.sales_invoice_script.get_sales_invoice_logs',
    'DEFINITION_URL': 'api/resource/Sales Invoice Definition?fields=["name"]',
    'CUSTOMER_URL':'api/resource/Customer?fields=["name"]&limit_page_length=None',
    'GATEWAY_URL':'api/resource/Gateway?fields=["name"]&limit_page_length=None',
    'ICRIS_NUMBER_URL':'api/resource/ICRIS List?fields=["shipper_no"]&limit_page_length=None',

    "STATIONS": [
        "",
        "Faisalabad",
        "Gujranwala",
        "Islamabad",
        "Karachi",
        "Lahore",
        "Peshawar",
        "Sialkot",
        "Wazirabad"
    ]
}

