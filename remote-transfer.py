import paramiko
import logging
import os
from config import dbValorant
logging.basicConfig(level=logging.ERROR)
import dotenv

dotenv.load_dotenv()


server_ip = os.getenv("SERVER_IP")
port = 22  # Default port for SSH
username = 'admin'
private_key_path = 'key.pem'

# Create SSH client
client = paramiko.SSHClient()

# Automatically add the server's host key to the known_hosts file
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# Specify the path to your private key

# Load the private key
pkey = paramiko.RSAKey.from_private_key_file(private_key_path)

# Connect to the server using the private key
client.connect(server_ip, port=port, username=username, pkey=pkey)

# Perform file transfer
sftp = client.open_sftp()

def upload_dir(local_path, remote_path, type):
    local_path = local_path + "/" +type 
    totalDirs = 5308
    current = 0
    try:
        sftp.chdir(remote_path)
    except IOError:
        print(f"Base remote path {remote_path} does not exist. Creating...")
        sftp.mkdir(remote_path)
        sftp.chdir(remote_path)

    type_path = f"{remote_path}/{type}"
    
    try:
        sftp.mkdir(type_path)
        print(f"Remote directory {type_path} created.")
    except IOError as e:
        print(f"Error creating directory {type_path}: {e}")
    

    for root, dirs, files in os.walk(local_path):
        current +=1
        crosshair_id = os.path.basename(root)
        crosshair_remote_path = f"{type_path}/{crosshair_id}"
        print(f"Transferring crosshair {crosshair_id} ({current}/{totalDirs})")

        try:
            sftp.stat(crosshair_remote_path)
            print(f"Crosshair {crosshair_id} already exists. Skipping...")
            continue
        except IOError:
            pass
        
        try:
            sftp.mkdir(crosshair_remote_path)
            # print(f"Created directory {crosshair_remote_path}")
        except IOError as e:
            print(f"Error creating directory {crosshair_remote_path}: {e}")
            continue

        for file in files:
            local_file_path = os.path.join(root, file)
            remote_file_path = f"{crosshair_remote_path}/{file}"
            sftp.put(local_file_path, remote_file_path)
            # print(f"Transferring {local_file_path} to {remote_file_path}")
            dbValorant.crosshairs.update_one({"id": crosshair_id}, {"$set": {"uploaded": True, "remote_path": crosshair_remote_path}})

    nested_top_path = f"{type_path}/{type}"
    try:
        sftp.rmdir(nested_top_path)
        print(f"Nested 'top' directory removed: {nested_top_path}")
    except IOError:
        pass

    print("Transfer completed.")

# Call the upload_dir function
upload_dir('crosshairs/', '/home/admin/Looking-For-Teammates-Discord-Bot/crosshairs', "user")

# Close the SFTP and SSH connections
sftp.close()
client.close()
