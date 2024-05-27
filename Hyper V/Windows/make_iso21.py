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
    response = requests.get(url_imgburn, proxies = proxies)
    with open(imgburn_installer_path, 'wb') as file:
        file.write(response.content)
    subprocess.run([imgburn_installer_path, '/S'], check=True)

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
    create_iso_with_imgburn(extracted_iso_folder, new_iso_path)
    shutil.rmtree(extracted_iso_folder)

if __name__ == "__main__":
    main()
