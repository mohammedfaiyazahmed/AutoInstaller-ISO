import os
import requests
import shutil
import subprocess
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
mount_dir = os.path.join(download_directory, "mount_iso")


def download_file(url, filename):
    if os.path.exists(filename):
        print(f"{filename} already exists, skipping download.")
        return

    proxies = {
        "http": "",
        "https": "",
    }
    print("Current file path:", filename)
    with requests.get(url, stream=True, proxies=proxies, verify=False,
                      auth=HTTPBasicAuth('sys_degsi1', 'zaq1@wsxcde34rfvbgt5')) as r:
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
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    if not os.path.exists(mount_dir):
        os.makedirs(mount_dir)

    # Mount the ISO file
    subprocess.run(['PowerShell', 'Mount-DiskImage', '-ImagePath', iso_path])

    # Get the drive letter of the mounted ISO
    drive_letter = subprocess.check_output(
        ['PowerShell', '(Get-DiskImage', f'-ImagePath "{iso_path}").DevicePath']).decode().strip()
    drive_letter = drive_letter.replace('\\', '').replace('.', '') + '\\'

    # Copy the contents of the ISO to a temporary directory
    subprocess.run(['xcopy', drive_letter, temp_dir, '/e', '/h', '/k'])

    # Dismount the ISO
    subprocess.run(['PowerShell', 'Dismount-DiskImage', '-ImagePath', iso_path])

    # Copy the autounattend.xml to the root of the extracted ISO
    shutil.copy(answer_file_path, os.path.join(temp_dir, 'autounattend.xml'))

    # Create a new ISO with the answer file
    subprocess.run(['oscdimg', '-m', '-o', '-u2', temp_dir, new_iso_path])

    # Clean up
    shutil.rmtree(temp_dir)
    shutil.rmtree(mount_dir)


# Download files
try:
    download_file(autoattend_url, autoattend_file)
    download_file(windows_iso_url, windows_iso_file)
except requests.exceptions.RequestException as e:
    print(f"Download failed: {e}")

# Add autounattend.xml to the downloaded ISO
add_autounattend_to_iso(windows_iso_file, autoattend_file, modified_iso_file)

print(f"New ISO created at {modified_iso_file}")
