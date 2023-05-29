import subprocess
import datetime as dt
import socket
import sched
import time


STORE_DIR: str = './'
STORE_FILE: str = 'requirements.txt'
STORE_PATH: str = STORE_DIR + STORE_FILE

NETSTAT_COMMAND: list[str] = ['netstat', '-nutw']
AWK_COMMAND: list[str] = ['awk', 'FNR > 6 {print $5}']  # gets all the foreign IPs

NON_PUBLIC_IP_START = ['10.', '172.', '192.', '127.']


class Connection:
    __ip: str
    __to: str
    __time: str
    __sec: float

    @staticmethod
    def __get_now() -> str:
        return str(dt.datetime.now())

    @staticmethod
    def __get_time() -> float:
        return time.time()

    def __init__(self, ip: str) -> None:
        self.__ip = ip
        self.__resolve()
        self.__time = Connection.__get_now()
        self.__sec = Connection.__get_time()

    def __resolve(self) -> None:
        try:
            self.__to, *_ = socket.gethostbyaddr(self.__ip)
        except socket.herror:
            self.__to = self.__ip

    def is_same(self, ip: str, to: str = '') -> bool:
        return self.get_ip() == ip or self.get_to() == to

    def is_in_time(self) -> bool:
        return Connection.__get_time() - self.__sec < 120

    def get_info(self) -> str:
        return f'DOMAIN: {self.__to: <64} | TIME: {self.__time}\n'

    def get_ip(self) -> str:
        return self.__ip

    def get_to(self) -> str:
        return self.__to


class Log:
    __old_scanned: list[Connection]
    __scan_connections: list[Connection]
    __scheduler: sched.scheduler

    @staticmethod
    def __is_public_ip(ip: str) -> bool:
        return all([not ip.startswith(x) for x in NON_PUBLIC_IP_START])

    @staticmethod
    def __get_active_ips() -> list[str]:
        netstat: subprocess.Popen = subprocess.Popen(NETSTAT_COMMAND, stdout=subprocess.PIPE)
        awk: bytes = subprocess.check_output(AWK_COMMAND, stdin=netstat.stdout)
        return [ip[:ip.find(':')] for ip in awk.decode('utf-8').split('\n') if ip != '' and Log.__is_public_ip(ip)]

    def __init__(self) -> None:
        self.__old_scanned = []
        self.__scan_connections = []
        self.__scheduler = sched.scheduler(time.time, time.sleep)

    def start_logging(self) -> None:
        self.__scheduler.enter(10, 1, self.__scan)
        self.__scheduler.run()

    def __scan(self) -> None:
        self.__old_scanned += self.__scan_connections
        self.__scan_connections.clear()

        for ip in Log.__get_active_ips():
            self.__add_scanned(Connection(ip))

        self.__store_scan()

        self.__scheduler.enter(10, 1, self.__scan)

    def __add_scanned(self, connection: Connection) -> None:
        for scanned in self.__scan_connections:
            if connection.is_same(scanned.get_ip()):
                return

        for old_scanned in self.__old_scanned:
            if connection.is_same(old_scanned.get_ip()) and old_scanned.is_in_time():
                return

        self.__scan_connections.append(connection)

    def __store_scan(self) -> None:
        with open(STORE_PATH, 'a') as f:
            for connection in self.__scan_connections:
                f.write(connection.get_info())


if __name__ == '__main__':
    ip_logger = Log()
    ip_logger.start_logging()
