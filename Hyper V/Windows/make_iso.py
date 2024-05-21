import os
import requests
from pycdlib import PyCdlib

download_directory = os.path.join(os.getcwd(), "downloads")
if not os.path.exists(download_directory):
    os.makedirs(download_directory)

autoattend_url = "https://wiki.ith.intel.com/download/attachments/2518244265/autounattend.xml?version=1&modificationDate=1659385714323&api=v2"
windows_iso_url = "https://ubit-artifactory-ba.intel.com/artifactory/dcg-dea-srvplat-local/Kits/BHS-GNR-SP-WIN2022/BHS-GNR-SP-WIN2022-24.21.2.4/Images/20348.2322_13feb2024_server_eval_x64fre_en-us_gnr_bkc_FRE_IA-64_BHS-GNR-SP-WIN2022-24.21.2.4.iso"

autoattend_file = os.path.join(download_directory, "autounattend.xml")
windows_iso_file = os.path.join(download_directory, "windows.iso")
modified_iso_file = os.path.join(download_directory, "modified_windows.iso")

def download_file(url, filename):
    print(f"Downloading file from {url} to {filename}...")
    response = requests.get(url)
    with open(filename, 'wb') as file:
        file.write(response.content)
    print(f"Download completed: {filename}")

download_file(autoattend_url, autoattend_file)

download_file(windows_iso_url, windows_iso_file)

print("Modifying ISO to include autounattend.xml...")
iso = PyCdlib()
iso.open(windows_iso_file)

iso.add_file(autoattend_file, '/AUTOUNATTEND.XML')

iso.write(modified_iso_file)
iso.close()

print(f"Modified ISO has been created as {modified_iso_file}")