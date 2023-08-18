import requests
import log
from bs4 import BeautifulSoup
from hashlib import sha256


def web(response: requests.Response) -> str:
    soup = BeautifulSoup(response.text, 'html.parser')
    checksum_td = soup.find('td', string=lambda t: t and t.endswith('(SHA256)'))
    checksum = checksum_td.text.split(' ')

    log.deb(f'Extracted checksum: {checksum[0]}')

    return checksum[0]


def file(file: str, buffer: int = 8192) -> str:
    computed = sha256()
    with open(file, 'rb') as f:
        log.info(f'Calculating SHA256 of: {f.name}')

        for block in iter(lambda: f.read(buffer), b''):
            computed.update(block)

    fileHash = computed.hexdigest()
    log.info(f'SHA256: {fileHash}')

    return fileHash


def compare(hash0: str, hash1: str) -> bool:
    log.deb(f'Comparing {hash0} to {hash1}')
    if hash0 == hash1:
        log.info('Provided hashes matched!')
    else:
        log.warn('Provided hashes do NOT match')
    return hash0 == hash1
