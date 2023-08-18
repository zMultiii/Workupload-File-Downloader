import log
from re import sub
from urllib.parse import urlparse
from requests import get, Response
from json import loads


url_pattern = 'https://workupload.com'


class Scout:
    def __init__(self, url: str):
        self.url = url
        self.token = ''
        self.server = ''
        self.isValid = is_url_valid(url)
        if not self.isValid:
            return

        log.info('Retrieving page\'s information...')
        self.response = scout(self.url, {})
        log.deb(f'Status: {self.response.status_code}')
        log.deb(f'Headers: {self.response.headers}')
        log.deb(f'Token: {self.gettoken()}')

        log.info("Requesting download server")
        if self.get_download_server():
            log.info("Download server acquired!")
        else:
            self.isValid = False
            log.err("Request failed, check log or report bug")
            return
        log.deb(f'Downloadable URL: {self.server}')

    def gettoken(self) -> str:
        try:
            return self.response.cookies['token']
        except KeyError:
            return ''

    def get_download_server(self) -> bool:
        headers = {'Cookie': f'token={self.gettoken()}'}
        uris = self._split_url()
        address = f'{url_pattern}/api/{uris[0]}/getDownloadServer/{uris[1]}'

        log.deb(f'Request link: {address}')
        log.deb(f'Request headers: {headers}')

        response = scout(address, headers).text
        log.deb(f'From server: {response}')

        json = loads(response)
        if json['success']:
            self.server = json['data']['url']
        return bool(json['success'])

    def _split_url(self) -> list[str]:
        uris = sub(f'{url_pattern}/', '', self.url).split('/')

        log.deb(f'File\'s type: {uris[0]}')
        log.deb(f'File\'s id: {uris[1]}')

        return uris


def is_url_valid(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme, result.scheme])
    except ValueError:
        log.err(f'Invalid URL structure!')
        return False


def scout(url: str, headers: dict[str, str]) -> Response:
    return get(url, headers=headers)