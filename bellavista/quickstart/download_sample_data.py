import os
import re
import requests
import zipfile

from pathlib import Path
from tqdm import tqdm

def run_quickstart_demo():

    save_folder = os.getcwd()
    folder_name = "KoLab_MERFISH_TAC_single_FOV"

    if not Path(os.path.join(save_folder, folder_name)).exists():
        
        print("Downloading sample dataset...")

        dataset_url = "https://www.dropbox.com/scl/fo/qqvij1593w8m4jrw643cx/ALS0h0e9uvVR9BS4UfW_PjQ?rlkey=wuyqo4qi3eaufbivapsrp5amu&dl=1"

        response = requests.get(dataset_url)
    
        with open(os.path.join(save_folder, f"{folder_name}.zip"), "wb") as f:
            f.write(response.content)
    

        print("Downloaded KoLab_MERFISH_TAC_single_FOV.zip!")
        with zipfile.ZipFile(os.path.join(save_folder, f"{folder_name}.zip"), "r") as zip_ref:
            zip_ref.extractall(os.path.join(save_folder, folder_name))

        print(f"Extracted to: {os.path.join(save_folder, folder_name)}")

    else:
        print("Sample dataset previously downloaded.")

def run_full_dataset(dataset_url):
    save_folder = os.getcwd()
    
    # read dataset folder name
    response = requests.head(dataset_url, allow_redirects=True)
    cd = response.headers.get("Content-Disposition", "")
    response.close()

    filename = re.findall('filename="(.+)"', cd)

    if not filename: 
        return
    
    else: 
        p = Path(filename[0])
        folder_name = p.name.removesuffix("".join(p.suffixes))
        
        zip_path = Path(os.path.join(save_folder, f"{folder_name}.zip"))
        folder_path = Path(os.path.join(save_folder, folder_name))

        if folder_path.exists():
            print(f"{folder_name} dataset previously downloaded.")
            return folder_path

        else:
            if not zip_path.exists():
                response = requests.get(dataset_url, stream=True)
                total_size = int(response.headers.get("content-length", 0))

                with open(zip_path, "wb") as f:
                    with tqdm(total=total_size, unit="B", unit_scale=True, desc=f"Downloading {folder_name} dataset") as bar:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                            bar.update(len(chunk))

            # Validate zip before extracting
            try:
                with zipfile.ZipFile(zip_path, "r") as zip_ref:
                    bad_file = zip_ref.testzip()  # returns None if all good
                    if bad_file:
                        raise zipfile.BadZipFile(f"Corrupted file: {bad_file}")

                    members = zip_ref.infolist()
                    with tqdm(total=len(members), desc=f"Extracting {folder_name}.zip") as bar:
                        for member in members:
                            zip_ref.extract(member, folder_path)
                            bar.update(1)

                zip_path.unlink()  # delete zip only after successful extraction
                # print(f"Data saved at: {folder_path}")

            except zipfile.BadZipFile:
                print(f"Dataset was corrupted during download, please delete and re-download the files.")
                print(f"Corrupted zip file: {zip_path}")
                exit()

            print(f"Data saved at: {folder_path}")

    return folder_path
