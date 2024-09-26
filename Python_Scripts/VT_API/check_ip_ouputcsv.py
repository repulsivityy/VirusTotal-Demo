#####################################
# DISCLAIMER - THIS CODE WAS HEAVILY GENERATED BY GEMINI WITH SOME TWEAKS AS PART OF TESTING. USE AT YOUR OWN RISK.
#
# Takes inputs from a CSV file and gets results from GTI if they are malicious or not
# Outputs to a CSV file that you specify with the columns: IP, Detection, Country

# requirements:
# - Google Threat Intelligence (or VT) API Key

# Usage
# 1. put all IPs into a csv file
# 2. run the script, specify input csv file and output csv file

# Notes
# 1. malware_family comes from Google Threat Intelligence. If using VT API Key, the malware_family column will be empty
#####################################


import requests
import csv
import os
import time
from tqdm import tqdm  # Import tqdm for progress bar

# Get API key from environment variable
GTI_APIKEY = os.getenv("GTI_APIKEY")
if not GTI_APIKEY:
    raise ValueError("GTI_APIKEY environment variable not set.")

def check_ip_virustotal(ip_address):
    try:
        url = f"https://www.virustotal.com/api/v3/ip_addresses/{ip_address}"
        headers = {
            "x-apikey": GTI_APIKEY,
        }
        response = requests.get(url, headers=headers, timeout=10)  # Timeout added for robustness

        response.raise_for_status()  # Raise exception for bad HTTP status codes

        data = response.json()
        detections = data["data"]["attributes"]["last_analysis_stats"]["malicious"]
        total_engines = sum(data["data"]["attributes"]["last_analysis_stats"].values())
        detection_ratio = detections #/ total_engines if total_engines else 0  # Handle division by zero
        country = data["data"]["attributes"]["country"]
        malware_family = ""  # Initialize as empty string

        # Check if malware_families exists in the response
        if "attribution" in data["data"]["attributes"] and "malware_families" in data["data"]["attributes"]["attribution"]:
            malware_families = data["data"]["attributes"]["attribution"]["malware_families"]
            if malware_families:
                malware_family = malware_families[0].get("family", "")

        return detection_ratio, country, malware_family
    
    except requests.exceptions.RequestException as e:
        print(f"Error checking IP: {ip_address} - {e}")
        return None, None, None
    
    except KeyError as e:
        print(f"Unexpected API response format for IP: {ip_address} - {e}")
        return None, None, None

def main():
    while True:
        csv_file = input("Enter the path to your CSV file: ")
        if os.path.exists(csv_file):
            break
        else:
            print("File not found. Please try again.")

    output_file = input("Enter the name for the output CSV file: ")

    # Get threshold from user
    while True:
        try:
            threshold = int(input("Enter the detection ratio threshold (e.g., 5): "))
            if threshold >= 0:
                break
            else:
                print("Please enter a non-negative integer.")
        except ValueError:
            print("Invalid input. Please enter an integer.")

    try:
        with open(csv_file, "r", newline="") as csvfile, open(output_file, "w", newline="") as outfile:
            reader = csv.reader(csvfile)
            writer = csv.writer(outfile)
            # Skip header if present
            next(reader, None)  

            # Get total number of rows for progress bar
            total_rows = sum(1 for row in reader)
            csvfile.seek(0)  # Reset file pointer
            next(reader, None)  # Skip header again

            # Create progress bar
            with tqdm(total=total_rows, unit="IP", desc="Processing IPs") as pbar:
                # Process the first line (header)
                first_row = next(reader)
                ip_address = first_row[0].strip()
                if "[" in ip_address and "]" in ip_address:
                    ip_address = ip_address.replace("[", "").replace("]", "")
                detection_ratio, country, malware_family = check_ip_virustotal(ip_address)
                if detection_ratio is not None:
                    malicious_status = "Malicious" if detection_ratio > threshold else ""
                    writer.writerow([ip_address, detection_ratio, country, malware_family, malicious_status])
                pbar.update(1)  # Update progress bar

                # Process the remaining lines
                for row in reader:
                    ip_address = row[0].strip()
                    if "[" in ip_address and "]" in ip_address:
                        ip_address = ip_address.replace("[", "").replace("]", "")
                    detection_ratio, country, malware_family = check_ip_virustotal(ip_address)
                    if detection_ratio is not None:
                        malicious_status = "Malicious" if detection_ratio > threshold else ""
                        writer.writerow([ip_address, detection_ratio, country, malware_family, malicious_status])
                    pbar.update(1)  # Update progress bar

                    # Update progress percentage every 5 seconds
                    time.sleep(5)
                    pbar.set_description(f"Processing IPs - {pbar.n}/{pbar.total} ({pbar.n/pbar.total:.1%})")

        print(f"IP detection results saved to '{output_file}'.")

    except FileNotFoundError:
        print(f"Error: CSV file '{csv_file}' not found.")

if __name__ == "__main__":
    main()