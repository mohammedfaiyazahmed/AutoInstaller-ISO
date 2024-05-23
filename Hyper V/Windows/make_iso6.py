import requests
import os


autoattend_url = "https://wiki.ith.intel.com/download/attachments/2518244265/autounattend.xml?version=1&modificationDate=1659385714323&api=v2"
windows_iso_url = "https://ubit-artifactory-ba.intel.com/artifactory/dcg-dea-srvplat-local/Kits/BHS-GNR-SP-WIN2022/BHS-GNR-SP-WIN2022-24.21.2.4/Images/20348.2322_13feb2024_server_eval_x64fre_en-us_gnr_bkc_FRE_IA-64_BHS-GNR-SP-WIN2022-24.21.2.4.iso"

download_directory = os.path.join(os.getcwd(), "../../downloads")
if not os.path.exists(download_directory):
    os.makedirs(download_directory)

autoattend_file = os.path.join(download_directory, "autounattend.xml")
windows_iso_file = os.path.join(download_directory, "windows.iso")

def download(url, download_path):
    req_obj = requests.get(url, stream=True, timeout=120)
    with open(download_path, "wb") as file_obj:
        for chunk in req_obj.iter_content(chunk_size=8192):
            file_obj.write(chunk)

download(autoattend_url, autoattend_file)

download(windows_iso_url, windows_iso_file)