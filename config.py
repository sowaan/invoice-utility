# import os

# DATABASE_CONFIG = {
#     'DB_PATH': os.path.join(os.path.expanduser("~"), ".my_app_credentials.db"),
#     'CHECK_SAME_THREAD': False
# }


DATABASE_CONFIG = {
    'DB_PATH': 'data.db',  # Path to SQLite database
    'CHECK_SAME_THREAD': False,  # Ensure thread safety
}

# ERPNext API Configuration
ERP_CONFIG = {
    # 'SITE_URL': 'https://ups-uat.sowaanerp.com/',  # URL of your ERPNext instance
    # 'API_KEY': 'ed092d973544561',  # Your ERPNext API key
    # 'API_SECRET': 'a959503ba7ec7b8',  # Your ERPNext API secret
    # 'HEADERS': {
    #     'Authorization': 'token ed092d973544561:a959503ba7ec7b8',  # Authorization header for API requests
    #     'Content-Type': 'application/json',  # The content type for API requests
    # },
    
    'SITE_URL': 'http://127.0.0.1:8003/', #local
    'API_KEY': 'eaddb52294d113e', #local
    'API_SECRET': '11924cb7830a5f8', # local
    'HEADERS': {
        'Authorization': 'token eaddb52294d113e:11924cb7830a5f8',  # Authorization header for API requests
        'Content-Type': 'application/json',  # The content type for API requests
    },

    # 'SITE_URL': 'https://ups-dev.sowaanerp.com/', #local
    # 'API_KEY': 'a45a4fe9effad75', #local
    # 'API_SECRET': '26201c03c8ff537', # local
    # 'HEADERS': {
    #     'Authorization': 'token a45a4fe9effad75:26201c03c8ff537',  # Authorization header for API requests
    #     'Content-Type': 'application/json',  # The content type for API requests
    # },



    'SHIPMENT_API_URL':'api/method/uls_booking.uls_booking.api.sales_invoice_script.get_shipment_numbers_and_sales_invoices',
    'GENERATE_SALES_INVOICE_API_URL': 'api/method/uls_booking.uls_booking.api.sales_invoice_script.generate_single_invoice',
    'FETCH_LOGS_API_URL': 'api/method/uls_booking.uls_booking.api.sales_invoice_script.get_sales_invoice_logs' ,
    'DEFINITION_URL': 'api/resource/Sales Invoice Definition?fields=[\"name\"]',
    'CUSTOMER_URL':'api/resource/Customer?fields=[\"name\"]&&limit_page_length=None',
    'GATEWAY_URL':'api/resource/Gateway?fields=[\"name\"]&&limit_page_length=None',
    'ICRIS_NUMBER_URL':'api/resource/ICRIS List?fields=[\"shipper_no\"]&&limit_page_length=None',
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




