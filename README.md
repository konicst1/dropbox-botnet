## Dropbox channel based botnet

### Description
This is a Python-based botnet script for controllers and bots, utilizing Dropbox as a communication channel. Each bot is identified by a unique ID, and communication is facilitated through images, with messages embedded using steganography techniques. 


### Installation

#### Requirements
- Python 3.x
- Dropbox API
- schedule
- Stegano

Run the following command to install necessary packages:

`pip install stegano schedule dropbox`

#### Dropbox App Setup
1. Set up permissions for the Dropbox app (`file.content.write/read`).
2. Create folders in Dropbox: `flowers`, `fruits`, `data`, `ID`.

#### Folder Description
- `flowers`: Folder for commands.
- `fruits`: Folder for responses.
- `data`: Folder for transferring files.
- `ID`: Folder for IDs register.

#### Commands
- `w`: List of users currently logged in.
- `ls`: List content of specified directory.
- `id`: ID of current user.
- `copy <filename>`: Copy a file from the bot to the controller.
- `exec <command>`: Execute a binary inside the bot.

#### Note
- Ensure that the clean plumeria image is present in the directory for both client and controller.
- For the controller, `ids.txt` and `command_ids.txt` must also be present.

### Usage

1. **Bot Registration**: After the bot comes alive, it registers a new ID for identification.
2. **Communication**: Communication is held using pictures of plumeria. Messages are transferred in these images using steganography.

### Code Structure
Below is an overview of the main components of the script:

- **Dropbox Initialization**: Setting up Dropbox access and defining folder paths.
- **ID Management**: Functions for handling ID registration and updates.
- **Command Handling**: Functions to upload and download commands and responses.
- **Scheduled Tasks**: Routine tasks are scheduled to check for new commands, process responses, and maintain the bot's "aliveness".

### Running the Script
- **Insert your access token**
- Simply run the controller and the client scripts. Kindly note that the client script runs the best on Linux machines.

### Troubleshooting
I have tried to test on both Windows and Linux machines, in case of any trouble, contact me at: konicst1@fit.cvut.cz
