import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from datetime import datetime
from google.auth import default
from google.oauth2 import service_account
from google.auth.transport.requests import Request
import gspread
import json

def main():
    # Step 1: Load Google Sheets credentials from the JSON key file
    with open("/tmp/service_account.json") as f:
        creds_dict = json.load(f)

    creds = service_account.credentials.Credentials.from_service_account_info(creds_dict)

    # Refresh the credentials if expired
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())

    # Step 2: Authorize gspread with the credentials
    gc = gspread.authorize(creds)

    # Step 3: Open Google Sheets by name
    spreadsheet = gc.open('testposh')  # Replace with your sheet name
    worksheet = spreadsheet.worksheet('MENS_JacketsCoats100_500_JustInSold')

    # Step 4: Setup Chrome WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in background
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Set the binary location to where Chromium is installed in Colab
    options.binary_location = '/usr/bin/chromium-browser'

    # Initialize the WebDriver using SeleniumManager
    driver = webdriver.Chrome(options=options)

    # Step 5: Target URL
    url = "https://poshmark.com/category/Men-Jackets_&_Coats?sort_by=added_desc&price%5B%5D=100-250&price%5B%5D=250-500&availability=sold_out"
    driver.get(url)

    # Step 6: Allow Time for JavaScript to Load
    time.sleep(5)

    # Step 7: Extract Brand Names and Prices
    try:
        # Extract brands
        brand_elements = driver.find_elements(By.CLASS_NAME, "tile__title")
        brands = [brand.text for brand in brand_elements]

        # Extract prices (if available)
        price_elements = driver.find_elements(By.CLASS_NAME, "price")
        prices = [price.text for price in price_elements]

        # Fill missing prices with 'N/A' in case some listings don't have prices
        if len(prices) < len(brands):
            prices.extend(['N/A'] * (len(brands) - len(prices)))

        # Step 8: Ensure Data is Collected Correctly
        if brands:
            # Get today's date
            today_date = datetime.today().strftime('%m-%d-%Y')

            # Create DataFrame with Brand and Price
            data = {'Brand': brands, 'Price': prices, 'Date': [today_date] * len(brands)}

            # Create DataFrame
            df = pd.DataFrame(data)

            # Step 9: Convert DataFrame to list and append to Google Sheets
            data_to_append = df.values.tolist()
            worksheet.append_rows(data_to_append)  # Append data to Google Sheets

            # Print DataFrame for verification
            print(df)
        else:
            print("⚠️ No brands found.")
    except Exception as e:
        print(f"⚠️ An error occurred: {e}")

    # Step 10: Quit the WebDriver
    driver.quit()

if __name__ == "__main__":
    main()
