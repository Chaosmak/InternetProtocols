import socket
from multiprocessing.dummy import Pool
from functools import partial
import time

def connect(ip, delay, output, port_number):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(delay)
    try:
        sock.connect((ip, port_number))
        output.append(port_number)
    except:
        pass
    sock.close()


def scan_ports(host_ip, delay, start_port, finish_port):

    threads = []
    output = []

    partial_connect = partial(connect, host_ip, delay, output)
    pool = Pool(200)
    ports = list(range(start_port, finish_port + 1))
    pool.map(partial_connect, ports)
 
    print('Open ports:')
    for i in range(len(output)):
        print(output[i])


def main():
    host_ip = input('Host: ')
    start_port = int(input('Start: '))
    finish_port = int(input('Finish: '))
    s = time.time()
    scan_ports(host_ip, 0.3, start_port, finish_port)
    f = time.time()
    print('Time: {}'.format(f-s))

if __name__ == '__main__':
    main()
