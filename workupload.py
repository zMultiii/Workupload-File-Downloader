import logging
from tqdm import tqdm
from sys import argv, exit
from re import sub, search
from json import loads
from requests import get, Response

logging.root.name = "downloader"
logging.root.setLevel(logging.NOTSET)

valid_url = r'.*workupload.com/'
report_url = "https://github.com/knighthat/WorkuploadDownloader/issues"


def extract(url: str) -> dict:
    uri = sub(valid_url, '', url).split('/')

    logging.info(f"Download type: {uri[0]}")
    logging.info(f"File's id: {uri[1]}")

    return {
        'type': uri[0],
        'id': uri[1]
    }


def get_token(url: str) -> str:
    print(" ")
    logging.info("Getting token...")
    token = get(url, cookies=dict(token='')).cookies['token']
    logging.info(f"Your temporary token: {token}")
    return token


def get_download_url(parts: dict, headers: dict) -> str:
    print(" ")
    logging.info(f"Requesting download URL...")
    api_url = f"https://workupload.com/api/{parts['type']}/getDownloadServer/{parts['id']}"

    data_response = get(api_url, headers=headers)
    dl_url = loads(data_response.text)['data']['url']

    logging.info(f"Downloading from {dl_url}")
    return dl_url


def get_file_information(url: str, headers: dict) -> dict:
    print(" ")
    logging.info("Searching file...")
    file_response = get(url, headers=headers, stream=True)

    name = file_response.headers.get('Content-Disposition')
    name = search(r'filename="(.+)"', name).group(1)

    size = file_response.headers.get('Content-Length', 0)

    logging.info(f"File's name: {name}")
    logging.info(f"File's size: {size}")
    return {
        'name': name,
        'size': int(size),
        'response': file_response
    }


def download(name: str, size: int, response: Response) -> None:
    print(f"Downloading {name}...")
    progress_bar = tqdm(total=size, unit='iB', unit_scale=True)

    with open(name, 'wb') as file:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                progress_bar.update(len(chunk))
                file.write(chunk)

    progress_bar.close()
    if size != 0 and progress_bar.n != size:
        logging.error(f"Error occurs during download. Report at \n {report_url}")


if __name__ == '__main__':
    if len(argv) < 2:
        logging.fatal("Usage: python main.py <url>")
        exit(1)

    link = argv[1]
    parts = extract(link)
    token = get_token(link)

    headers = {'Cookie': f'token={token}'}
    dl_url = get_download_url(parts, headers)

    content = get_file_information(dl_url, headers)

    download(content['name'], content['size'], content['response'])
