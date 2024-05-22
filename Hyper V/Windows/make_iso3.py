import os
import requests
from pycdlib import PyCdlib
import subprocess

download_directory = os.path.join(os.getcwd(), "downloads")
if not os.path.exists(download_directory):
    os.makedirs(download_directory)

autoattend_url = "https://wiki.ith.intel.com/download/attachments/2518244265/autounattend.xml?version=1&modificationDate=1659385714323&api=v2"
windows_iso_url = "https://ubit-artifactory-ba.intel.com/artifactory/dcg-dea-srvplat-local/Kits/BHS-GNR-SP-WIN2022/BHS-GNR-SP-WIN2022-24.21.2.4/Images/20348.2322_13feb2024_server_eval_x64fre_en-us_gnr_bkc_FRE_IA-64_BHS-GNR-SP-WIN2022-24.21.2.4.iso"

autoattend_file = os.path.join(download_directory, "autounattend.xml")
windows_iso_file = os.path.join(download_directory, "windows.iso")
modified_iso_file = os.path.join(download_directory, "modified_windows.iso")

print("windows ISO file:", windows_iso_file)

proxies = {
    "http": "https://proxy-dmz.intel.com:912",
    "https": "https://proxy-dmz.intel.com:912",
}

def download_file(url, filename):

    try:
        cmd = f"curl -u 'sys_degsi1':'zaq1@wsxcde34rfvbgt5' -X GET {url} --output {filename}"
        process = subprocess.check_output(cmd, shell=True)

        print(process)

    except Exception as e:
        print("some issue occured during download:", e)

download_file(autoattend_url, autoattend_file)

download_file(windows_iso_url, windows_iso_file)

# print("Modifying ISO to include autounattend.xml...")
# iso = PyCdlib()
# if os.path.exists(windows_iso_file):
#     iso.open(windows_iso_file)
# else:
#     print(f"File not found: {windows_iso_file}")
#
# iso.add_file(autoattend_file, '/AUTOUNATTEND.XML')
#
# iso.write(modified_iso_file)
# iso.close()
#
# print(f"Modified ISO has been created as {modified_iso_file}")