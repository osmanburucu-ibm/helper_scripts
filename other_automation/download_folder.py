import os
import requests

def download_files(url, save_directory):
    response = requests.get(url)
    content = response.text
    lines = content.split("\n")

    for line in lines:
        print (f"line={line}")
        if line.startswith("<a href="):
            filename = line.split('"')[1]
            file_url = url + "/" + filename

            if filename.endswith("/"):
                new_directory = save_directory + "/" + filename.rstrip("/")
                os.makedirs(new_directory, exist_ok=True)
                download_files(file_url, new_directory)
            else:
                save_path = save_directory + "/" + filename
                print("Downloading:", save_path)
                download_file(file_url, save_path)

def download_file(url, save_path):
    response = requests.get(url, stream=True)
    with open(save_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

# Usage example

def main():

    folder_url = "https://download.boulder.ibm.com/ibmdl/pub/software/rationalsdp/documentation/multimedia/Web_Based_Training/rational_RD205"
    save_directory = "/Users/ozzy/temp/RSAD"
    download_files(folder_url, save_directory)

if __name__ == '__main__':
    main()
