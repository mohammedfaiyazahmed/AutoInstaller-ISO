import os
import requests
import shutil
import subprocess
from requests.auth import HTTPBasicAuth
from tqdm import tqdm


print("*******", requests.certs.where())


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


def ensure_oscdimg_installed():
    oscdimg_path = shutil.which("oscdimg")
    if oscdimg_path:
        print(f"oscdimg is already installed at {oscdimg_path}")
        return oscdimg_path

    print("oscdimg not found. Installing oscdimg...")

    oscdimg_url = "https://software-download.microsoft.com/download/pr/OSCDIMG.exe"
    oscdimg_dest = os.path.join(download_directory, "OSCDIMG.exe")
    download_file(oscdimg_url, oscdimg_dest)


    oscdimg_install_dir = os.path.join(os.environ["SYSTEMROOT"], "System32")
    shutil.move(oscdimg_dest, os.path.join(oscdimg_install_dir, "OSCDIMG.exe"))

    run_powershell_script(
        f'[System.Environment]::SetEnvironmentVariable("Path", $env:Path + ";{oscdimg_install_dir}", "Machine")',
        as_admin=True)
    return os.path.join(oscdimg_install_dir, "OSCDIMG.exe")


def run_powershell_script(script, as_admin=False):
    if as_admin:
        script = f'Start-Process powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -Command \\"{script}\\"" -Verb RunAs'
    else:
        script = f'powershell -NoProfile -ExecutionPolicy Bypass -Command "{script}"'
    completed = subprocess.run(script, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return completed.stdout.decode().strip()


def add_autounattend_to_iso(iso_path, answer_file_path, new_iso_path):
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    if not os.path.exists(mount_dir):
        os.makedirs(mount_dir)

    run_powershell_script(f'Mount-DiskImage -ImagePath "{iso_path}"', as_admin=True)


    drive_letter = run_powershell_script('(Get-Volume -FileSystemLabel "CD-ROM").DriveLetter', as_admin=True) + ":\\"


    run_powershell_script(f'Copy-Item -Path "{drive_letter}*" -Destination "{temp_dir}" -Recurse', as_admin=True)


    run_powershell_script(f'Dismount-DiskImage -ImagePath "{iso_path}"', as_admin=True)


    shutil.copy(answer_file_path, os.path.join(temp_dir, 'autounattend.xml'))


    oscdimg_path = ensure_oscdimg_installed()


    run_powershell_script(
        f'& "{oscdimg_path}" -m -o -u2 -udfver102 -bootdata:2#p0,e,b"{temp_dir}boot\\etfsboot.com"#pEF,e,b"{temp_dir}efi\\microsoft\\boot\\efisys.bin" "{temp_dir}" "{new_iso_path}"',
        as_admin=True)


    shutil.rmtree(temp_dir)
    shutil.rmtree(mount_dir)



try:
    download_file(autoattend_url, autoattend_file)
    download_file(windows_iso_url, windows_iso_file)
except requests.exceptions.RequestException as e:
    print(f"Download failed: {e}")


add_autounattend_to_iso(windows_iso_file, autoattend_file, modified_iso_file)

print(f"New ISO created at {modified_iso_file}")
