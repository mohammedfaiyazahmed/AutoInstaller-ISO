import os
import requests
import shutil
from pycdlib import PyCdlib
from requests.auth import HTTPBasicAuth
from tqdm import tqdm

# Print the certs path for debugging purposes
print("*******", requests.certs.where())

# Define paths
download_directory = os.path.join(os.getcwd(), "downloads")
if not os.path.exists(download_directory):
    os.makedirs(download_directory)

autoattend_url = "https://ubit-artifactory-ba.intel.com/artifactory/dcg-dea-srvplat-local/Automation_Tools/PAIV_DevOps/Faiyaz/autounattend.xml"
windows_iso_url = "https://ubit-artifactory-ba.intel.com/artifactory/dcg-dea-srvplat-local/Kits/BHS-GNR-SP-WIN2022/BHS-GNR-SP-WIN2022-24.21.2.4/Images/20348.2322_13feb2024_server_eval_x64fre_en-us_gnr_bkc_FRE_IA-64_BHS-GNR-SP-WIN2022-24.21.2.4.iso"

autoattend_file = os.path.join(download_directory, "autounattend.xml")
windows_iso_file = os.path.join(download_directory, "windows.iso")
modified_iso_file = os.path.join(download_directory, "modified_windows.iso")
temp_dir = os.path.join(download_directory, "temp_iso_extract")


def download_file(url, filename):
    proxies = {
        "http": "",
        "https": "",
    }
    print("Current file path:", filename)
    with requests.get(url, stream=True, proxies=proxies, verify=False, auth=HTTPBasicAuth('sys_degsi1', 'zaq1@wsxcde34rfvbgt5')) as r:
        r.raise_for_status()
        total_size_in_bytes = int(r.headers.get('content-length', 0))
        block_size = 8192
        progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=block_size):
                progress_bar.update(len(chunk))
                f.write(chunk)
        progress_bar.close()


def add_autounattend_to_iso(iso_path, answer_file_path, new_iso_path):
    # Create a temporary directory for ISO extraction
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    # Attempt to open the ISO to verify its validity
    iso = PyCdlib()
    try:
        iso.open(iso_path)
    except Exception as e:
        print(f"Failed to open ISO: {e}")
        return

    # Extract the ISO contents to the temporary directory
    try:
        iso.extract_all(temp_dir)
    except Exception as e:
        print(f"Failed to extract ISO: {e}")
        iso.close()
        return

    # Copy the autounattend.xml to the root of the extracted ISO
    shutil.copy(answer_file_path, os.path.join(temp_dir, 'autounattend.xml'))

    # Create a new ISO with the answer file
    new_iso = PyCdlib()
    new_iso.new(iso_level=3)

    # Walk through the temp directory and add all files to the new ISO
    files_to_add = []
    for root, dirs, files in os.walk(temp_dir):
        for file in files:
            files_to_add.append(os.path.join(root, file))

    progress_bar = tqdm(total=len(files_to_add), unit='file')
    for file_path in files_to_add:
        iso_path = os.path.relpath(file_path, temp_dir)
        with open(file_path, 'rb') as f:
            new_iso.add_file(f, f'/{iso_path.upper().replace(os.sep, "/")}')
        progress_bar.update(1)
    progress_bar.close()

    # Write out the new ISO
    new_iso.write(new_iso_path)

    # Clean up
    iso.close()
    new_iso.close()
    shutil.rmtree(temp_dir)


# Download files
try:
    download_file(autoattend_url, autoattend_file)
    download_file(windows_iso_url, windows_iso_file)
except requests.exceptions.RequestException as e:
    print(f"Download failed: {e}")

# Add autounattend.xml to the downloaded ISO
add_autounattend_to_iso(windows_iso_file, autoattend_file, modified_iso_file)

print(f"New ISO created at {modified_iso_file}")
