import requests
import os


API_URL = 'http://ipwho.is/'
IP_FILES_PATH = 'ip_files'
RESOLVED_FILES_PATH = 'resolved_files'


class Entry:
    __ip: str
    __resolve: str
    __time: str

    def __init__(self, entry_str: str) -> None:
        _, *tmp_time, _, self.__ip = entry_str.strip().split(' ')
        self.__time = ' '.join(tmp_time)

    def resolve(self) -> None:
        tmp_response = requests.get(API_URL + self.__ip)
        self.__resolve = tmp_response.json()['connection']['org']

    def to_str(self) -> str:
        return f'TIME: {self.__time} IP: {self.__ip: <15} DOMAIN: {self.__resolve}\n'


class Resolver:
    __ip_file: str
    __resolved_file: str
    __entries: list[Entry]

    def __init__(self, ip_file: str, resolved_file: str) -> None:
        self.__ip_file = ip_file
        self.__resolved_file = resolved_file
        self.__entries = []

    def load_entries(self) -> None:
        with open(self.__ip_file, 'r') as ip_file:
            for line in ip_file.readlines():
                self.__entries.append(Entry(line))

    def resolve(self) -> None:
        for e in self.__entries:
            e.resolve()

    def store_resolved(self) -> None:
        with open(self.__resolved_file, 'w') as resolved_file:
            for res in self.__entries:
                resolved_file.write(res.to_str())


if __name__ == '__main__':
    ip_files = os.listdir(IP_FILES_PATH)
    for file in ip_files:
        resolver = Resolver(os.path.join(IP_FILES_PATH, file), os.path.join(RESOLVED_FILES_PATH, file))
        resolver.load_entries()
        resolver.resolve()
        resolver.store_resolved()
