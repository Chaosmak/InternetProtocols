import requests
import json
import socket
import re
import sys
import time
from subprocess import Popen, PIPE


def tracert(ip):
    p = Popen(['tracert', ip], stdout=PIPE)
    pairs, bad_lines = [], 0
    r = re.compile(r'[0-9]+(?:\.[0-9]+){3}')
    while True:
        line = p.stdout.readline().decode('cp866')
        if not line:
            break
        current_ip = re.findall(r, line)
        if current_ip:
            pairs.append(current_ip[0])
        else:
            if '*' in line:
                bad_lines += 1
                if bad_lines > 3:
                    return pairs[1:]
    return pairs[1:]


def get_info(ip):
    url = 'https://stat.ripe.net/data/prefix-overview/data.json?resource=' + ip
    try:
        r = requests.get(url).json()
        AS = r['data']['asns'][0]['asn']
        holder = r['data']['asns'][0]['holder']
    except IndexError:  # ip не белый
        return

    url = 'https://stat.ripe.net/data/geoloc/data.json?resource=' + ip
    try:
        country = requests.get(url).json()['data']['locations'][0]['country']
    except IndexError:  # ip не белый
        return

    return AS, country, holder


def print_res(res):
    for x in res:
        print(' | '.join(x))


if __name__ == '__main__':
    start = time.time()
    ip_list = tracert(socket.gethostbyname(sys.argv[1]))
    result = []
    for idx, current_ip in enumerate(ip_list):
        res = get_info(current_ip)
        if res:
            AS, country, holder = res
        else:
            AS, country, holder = '-' * 3
        result.append((str(idx + 1), current_ip, str(AS), country, holder))
    print_res(result)
    end = time.time()
    print('\nВремя работы: {}'.format(end - start))
