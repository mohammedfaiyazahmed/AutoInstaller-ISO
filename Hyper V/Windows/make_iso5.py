import os
import requests
import subprocess
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
    proxies = {
        "http": "http://proxy-dmz.intel.com:912",
        "https": "https://proxy-dmz.intel.com:912",
    }
    with requests.get(url, stream=True, proxies=proxies, verify=False) as r:
        r.raise_for_status()
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

try:
    download_file(autoattend_url, autoattend_file)
    download_file(windows_iso_url, windows_iso_file)
except requests.exceptions.RequestException as e:
    print(f"Download failed: {e}")


print("Modifying ISO to include autounattend.xml...")
if os.path.exists(windows_iso_file):
    iso = PyCdlib()
    iso.open(windows_iso_file)
    iso.add_file(autoattend_file, '/AUTOUNATTEND.XML')
    iso.write(modified_iso_file)
    iso.close()
    print(f"Modified ISO has been created as {modified_iso_file}")
else:
    print(f"File not found: {windows_iso_file}. Unable to modify ISO.")