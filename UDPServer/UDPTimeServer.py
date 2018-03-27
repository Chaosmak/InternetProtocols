import socket
import time
import datetime
import struct

def get_settings():
    with open('settings.txt', 'r') as f:
        try:
            offset = int(f.readline())
            time_server = f.readline()
            if not time_server:
                raise ValueError
        except ValueError:
            print('Please set the correct configuration\nNow offset is 0 and time server is OS :)')
            return 0, None
    return offset, time_server


def gettime_ntp(addr):
    TIME1970 = 2208988800
    s = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
    data = '\x1b' + 47 * '\0'
    s.sendto( data.encode(), (addr, 123))
    s.settimeout(10)
    try:
        data, address = s.recvfrom(1024)
    except socket.error:
        return 'cant connect to server'

    if data:
        t = struct.unpack( '!12I', data )[10]
        t -= TIME1970
        return datetime.datetime.strptime(time.ctime(t), "%a %b %d %H:%M:%S %Y")

def get_time(time_server=None):
    if time_server:
        return gettime_ntp(time_server)
    else:
        return datetime.datetime.now()


# def get_my_ip():
#     ip = socket.gethostbyname(socket.gethostname())
#     if ip.startswith("127."):
#         s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#         s.connect(("8.8.8.8", 53))
#         ip = s.getsockname()[0]
#         s.close()
#     return ip


def start_server():
    host = socket.gethostbyname(socket.gethostname())
    port = 123
    offset, time_server = get_settings()

    print('Current ip: {}'.format(host))
    print('Current offset: {} seconds'.format(offset))
    print('Current server: {}'.format(time_server))
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.bind((host, port))
    except (OSError, socket.error):
        return 'Please open 123 port'  # вырубить службу времени (w32tm)
    while True:
        try:
            data, addr = s.recvfrom(1024)
        except socket.error:
            print('Just another socket error')
            continue
        print('Request from {}:{}: "{}"'.format(addr[0], addr[1], data.decode('utf-8')))
        msg = str(get_wrong_time(offset, time_server))
        print('Answer to {}:{}: "{}"\n'.format(addr[0], addr[1], msg))
        s.sendto(msg.encode('utf-8'), addr)



def get_wrong_time(offset, time_server):
    return get_time(time_server=time_server) + datetime.timedelta(seconds=offset)
    # cur_time = datetime.datetime.now()
    # wrong_time = cur_time + datetime.timedelta(seconds=offset)
    # return '{:02d}:{:02d}:{:02d}'.format(wrong_time.hour, wrong_time.minute, wrong_time.second)


if __name__ == '__main__':
    res = start_server()
    if res:
        print(res)
