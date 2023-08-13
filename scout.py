import log
from re import sub, match
from requests import get
from json import loads


url_pattern = r'.*workupload.com'


class Scout:
    def __init__(self, url: str):
        self.url = url
        self.token = ''
        self.server = ''
        self.isValid = match(url_pattern, url)
        if not self.isValid:
            log.err(f'Invalid URL structure!')
            return

        log.info('Requesting download token from WorkUpload')
        self.get_token()
        if not self.token:
            self.isValid = False
            log.warn('Failed to retrieve token, please check download URL')
            return
        log.info('Token generated!')

        log.info("Requesting download server")
        if self.get_download_server():
            log.info("Download server acquired!")
        else:
            self.isValid = False
            log.err("Request failed, check log or report bug")
            return

        log.deb(f'Downloadable URL: {self.server}')

    def get_token(self):
        self.token = get(self.url, cookies=dict(token='')).cookies['token']
        log.deb(f'Token: {self.token}')

    def get_download_server(self) -> bool:
        headers = {'Cookie': f'token={self.token}'}
        uris = self._split_url()
        address = f'https://workupload.com/api/{uris[0]}/getDownloadServer/{uris[1]}'

        log.deb(f'Request link: {address}')
        log.deb(f'Request headers: {headers}')

        response = get(address, headers=headers).text
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
