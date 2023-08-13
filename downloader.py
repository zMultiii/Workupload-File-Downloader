import log
from requests import get
from re import search
from tqdm import tqdm
from pathlib import Path
from shutil import move


tempf = Path('./downloads')


class File:
    def __init__(self, server: str, token: str):
        headers = {'Cookie': f'token={token}'}
        self.content = get(url=server, headers=headers, stream=True)

        name = self.content.headers.get('Content-Disposition')
        self.name = search(r'filename="(.+)"', name).group(1)
        size = self.content.headers.get('Content-Length', 0)
        self.size = int(size)

        self.tempf = Path(f'{tempf.absolute()}/{self.name}.tmp')

        log.info(f'File\'s original name: {self.name}')
        log.info(f'File\'s size: {self.size}')
        log.deb(f'Downloading to: {self.tempf}')

    def move(self, destination: Path):
        if destination.exists():
            if destination.is_dir():
                destination = destination.joinpath(self.name)
            else:
                log.warn(f'{destination} is already exist!')
                return
        elif not destination.parent.exists():
            destination.parent.mkdir()

        log.info('Moving downloaded file to destination')
        move(self.tempf, destination)
        log.info('Done!')


def start(file: File):
    _prepare()

    log.info("Starting download process...")

    progress_bar = tqdm(total=file.size, unit='iB', unit_scale=True)
    with open(file.tempf, 'wb') as temp:
        for chunk in file.content.iter_content(chunk_size=1024):
            if chunk:
                progress_bar.update(len(chunk))
                temp.write(chunk)
    progress_bar.close()

    if progress_bar.n != file.size:
        log.warn('Download is NOT complete, check log or report bug')


def _prepare():
    if not tempf.exists():
        tempf.mkdir()
    if not tempf.is_dir():
        raise FileExistsError("Could not create temps folder to store file, temp is not a directory")