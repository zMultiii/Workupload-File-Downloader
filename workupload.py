import sys
import log
from pathlib import PurePath, Path
import scout
import downloader

url = ""
destination = Path('./downloads')


def parse_argv(argv: list[str]):
    global url
    global destination

    for i, arg in enumerate(argv):
        if arg.startswith("https://workupload.com/") and not url:
            url = arg
        if arg == '-o':
            if argv[i + 1]:
                destination = Path(argv[i + 1]).expanduser()


def validate_args() -> bool:
    global url
    global destination

    if not url.startswith('https://workupload.com/'):
        log.err(f'{url} is not a valid WorkUpload URL')
        return False
    try:
        PurePath(destination)
    except (TypeError, ValueError):
        log.warn(f'{destination} is not a valid path. ')
        return False

    return True


def print_man():
    print("Download files from WorkUpload.com at faster speed")
    print("\tUsage: workupload.py <url> [-o output]")
    print("\t\t-o\t- File's destination (Default at location of workupload.py)")


if __name__ == "__main__":
    try:
        if len(sys.argv) < 2:
            log.err("Missing argument")
            print_man()
            log.end_of_line()
            sys.exit(1)

        parse_argv(sys.argv)
        if not validate_args():
            log.end_of_line()
            sys.exit(1)

        log.deb(f'Target URL: {url}')
        log.deb(f'Save to: {destination}')

        scout = scout.Scout(url)
        if not scout.isValid:
            log.end_of_line()
            sys.exit(1)

        file = downloader.File(scout.server, scout.token)
        downloader.start(file)
        file.move(destination)
        log.end_of_line()
    except Exception as e:
        log.ex(e)
        log.end_of_line()

