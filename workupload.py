import logging
import sys
import re
import requests
import json

from tqdm import tqdm

if len(sys.argv) < 2:
    print("Usage: workupload.py '>>workupload link<<'")
    sys.exit(1)
logging.root.setLevel(logging.NOTSET)


link = sys.argv[1]

# Extract the type and id from the link
id_string = re.sub(r'.*workupload.com/', '', link)
type = id_string.split('/')[0]
id = id_string.split('/')[1]

# Check if the link is a valid WorkUpload link
if type not in ['file', 'archive']:
    logging.critical('Invalid WorkUpload-Link, check your link and try again')
    sys.exit(1)

# Set the start URL based on the link type
if type == 'file':
    start_url = f'https://workupload.com/start/{id}'
elif type == 'archive':
    start_url = f'https://workupload.com/archive/{id}/start'

# Log a message indicating that we are getting the token
logging.info('Getting token...')

# Make a request to the link to get the token cookie
response = requests.get(link, cookies=dict(token=''))
cookies = response.cookies
token = cookies['token']

# Log a message indicating that we have the token
logging.info(f'Token : {token}, getting DownloadURL....')

# Set the URL for the API call to get the download server
api_url = f'https://workupload.com/api/{type}/getDownloadServer/{id}'
headers = {'Cookie': f'token={token}'}

# Make a request to the API to get the download server
response = requests.get(api_url, headers=headers)
data = json.loads(response.text)
dl_url = data['data']['url']

# Make a request to the download server to get the file
response = requests.get(dl_url, headers=headers, stream=True)
response.raise_for_status()

# Get the filename from the response headers
filename = response.headers.get("Content-Disposition")

# If the filename was not found, use a default value
if filename:
    filename = re.search(r'filename="(.+)"', filename).group(1)
    logging.info(f'Downloading {filename}')
else:
    filename = "default"
    logging.warning(f'Could not find any filename, using default as filename..')

# Get file's size
total_size = int(response.headers.get('Content-Length', 0))

# Initialize progress bar
progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True)

# Save the file to the current directory
with open(filename, "wb") as f:
    for chunk in response.iter_content(chunk_size=1024):
        if chunk:  # filter out keep-alive new chunks
            f.write(chunk)

# Close stream
progress_bar.close()

# Send message if downloaded size doesn't match file's size
if total_size != 0 and progress_bar.n != total_size:
    logging.error(f'Download incomplete!')
    