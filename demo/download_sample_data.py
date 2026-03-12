import os
import requests
import zipfile

from pathlib import Path

def main():

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

if __name__ == "__main__":
    main()
