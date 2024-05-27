import os
import shutil
import subprocess
import requests
import urllib.parse

downloads_folder = os.path.expanduser('C:\\Users\\General\\PycharmProjects\\AutoInstaller-ISO\\downloads')
iso_path = os.path.join(downloads_folder, 'windows.iso')
autoattend_path = os.path.join(downloads_folder, 'autounattend.xml')
extracted_iso_folder = os.path.join(downloads_folder, 'extracted_iso')
new_iso_path = os.path.join(downloads_folder, 'new_windows_vm.iso')
imgburn_installer_path = os.path.join(downloads_folder, 'SetupImgBurn.exe')
imgburn_path = 'C:\\Program Files (x86)\\ImgBurn\\ImgBurn.exe'
seven_zip_installer_path = os.path.join(downloads_folder, '7z1900-x64.exe')
seven_zip_executable = 'C:\\Program Files\\7-Zip\\7z.exe'
boot_image_path = os.path.join(downloads_folder, 'BootImage.ima')

url_7zip = 'https://www.7-zip.org/a/7z1900-x64.exe'
url_imgburn = 'https://ubit-artifactory-ba.intel.com/artifactory/dcg-dea-srvplat-local/Automation_Tools/PAIV_DevOps/Faiyaz/SetupImgBurn_2.5.8.0.exe'

proxies = {
    "http": "",
    "https": "",
}

def download_and_install_7zip():
    response = requests.get(url_7zip)
    with open(seven_zip_installer_path, 'wb') as file:
        file.write(response.content)
    subprocess.run([seven_zip_installer_path, '/S'], check=True)

def extract_iso(iso_path, extract_to):
    subprocess.run([seven_zip_executable, 'x', iso_path, f'-o{extract_to}'], check=True)

def add_autoattend(extracted_folder, autoattend_file):
    destination = os.path.join(extracted_folder, 'autounattend.xml')
    shutil.copyfile(autoattend_file, destination)

def download_and_install_imgburn():
    response = requests.get(url_imgburn, proxies=proxies)
    with open(imgburn_installer_path, 'wb') as file:
        file.write(response.content)
    subprocess.run([imgburn_installer_path, '/S'], check=True)

def mount_iso(iso_path):
    mount_command = ['PowerShell', '-Command', f'Mount-DiskImage -ImagePath "{iso_path}"']
    subprocess.run(mount_command, check=True)

def get_mounted_drive_letter():
    command = ['PowerShell', '-Command', '(Get-DiskImage -ImagePath "{}" | Get-Volume).DriveLetter'.format(iso_path)]
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    return result.stdout.strip()

def extract_boot_image(mounted_drive_letter):
    save_boot_command = [
        imgburn_path,
        '/MODE', 'BUILD',
        '/BUILDINPUTMODE', 'DEVICE',
        '/SRC', f'{mounted_drive_letter}:',
        '/DEST', boot_image_path,
        '/BOOTIMAGE', f'{mounted_drive_letter}:/boot/etfsboot.com',
        '/MAKEIMAGEBOOTABLE', 'YES',
        '/START',
        '/NOIMAGEDETAILS',
        '/NOLOG',
        '/CLOSESUCCESS'
    ]
    subprocess.run(save_boot_command, check=True)

def create_iso_with_imgburn(source_folder, iso_path):
    build_mode_command = [
        imgburn_path,
        '/MODE', 'BUILD',
        '/BUILDINPUTMODE', 'FOLDER',
        '/SRC', source_folder,
        '/DEST', iso_path,
        '/FILESYSTEM', 'ISO9660+UDF',
        '/UDFREVISION', '1.02',
        '/VOLUMELABEL', 'WinISO',
        '/BOOTIMAGE', boot_image_path,
        '/MAKEIMAGEBOOTABLE', 'YES',
        '/OVERWRITE', 'YES',
        '/START',
        '/NOIMAGEDETAILS',
        '/ROOTFOLDER', 'YES',
        '/NOLOG',
        '/CLOSESUCCESS'
    ]
    subprocess.run(build_mode_command, check=True)

def main():
    download_and_install_7zip()
    extract_iso(iso_path, extracted_iso_folder)
    add_autoattend(extracted_iso_folder, autoattend_path)
    download_and_install_imgburn()
    mount_iso(iso_path)
    mounted_drive_letter = get_mounted_drive_letter()
    extract_boot_image(mounted_drive_letter)
    create_iso_with_imgburn(extracted_iso_folder, new_iso_path)
    shutil.rmtree(extracted_iso_folder)

if __name__ == "__main__":
    main()
