import binascii
import pickle
import socket

from PacketCreator import *


def format_hex(msg):
    return ''.join('%02x' % i for i in msg)


class CacheServer:
    cache = {}

    def __init__(self, dns_addr):
        self.dns_addr = dns_addr
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def start_server(self, port):
        self.load_cache()
        self.bindedsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.bindedsock.bind(('localhost', port))
        print('Server started at port {}'.format(port))
        while True:
            try:
                print('-' * 20)
                print('Cache length: {}'.format(len(self.cache)))
                data, addr = self.bindedsock.recvfrom(8096)
                p = DNSEntry(data)
                print('Ask about {}. Type is {}'
                      .format(p.name.decode(),
                              p.questions[0].type))
                print('Received from {}'.format(addr))
                answ = self.get_answer(data)
                self.bindedsock.sendto(answ, addr)
            except (KeyboardInterrupt, SystemExit):
                self.shutdown()
                self.sock.close()
                break
            except socket.error:
                self.bindedsock.close()
                self.bindedsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.bindedsock.bind(('localhost', port))

    def get_packet_from_dns(self, msg):
        try:
            msg = binascii.unhexlify(msg)
        except Exception:
            pass
        self.sock.sendto(msg, (self.dns_addr, 53))
        self.sock.settimeout(5)
        try:
            return self.sock.recv(2048)
        except Exception:
            return PacketCreator.get_error_answer(msg)

    def get_answer(self, msg):
        current_time = datetime.datetime.now()
        request_entry = DNSEntry(msg)
        name = request_entry.name
        type = request_entry.questions[0].type
        key = (name, type)
        value = self.cache.get(key)
        response = None
        if value:
            packet = value[0]
            end_of_life = value[1]
            if end_of_life > current_time:
                response = PacketCreator.set_ttl(packet, (end_of_life - current_time).seconds)
            else:
                self.cache.pop(key)
        if not response:
            response = self.get_packet_from_dns(msg)
            ttl = PacketCreator.get_min_ttl(response)
            self.cache[key] = (response, current_time + datetime.timedelta(seconds=ttl))
        return PacketCreator.copy_id(msg, response)

    def shutdown(self):
        with open('cache', 'wb') as f:
            pickle.dump(self.cache, f)

    def load_cache(self):
        current_time = datetime.datetime.now()
        try:
            with open('cache', 'rb') as f:
                cache = pickle.load(f)
                for key in cache:
                    end_of_life = cache[key][1]
                    if end_of_life > current_time:
                        self.cache[key] = cache[key]
        except Exception:
            self.cache = {}

    def close(self):
        self.sock.close()
        self.bindedsock.close()


def start_it(addr, port):
    print('Server: {}\nPort: {}'.format(addr, port))
    cacheServer = CacheServer(addr)
    cacheServer.start_server(port)


def get_settings():
    try:
        with open('settings.txt', 'rb') as f:
            addr = f.readline().decode().strip()
            port = int(f.readline())
            return addr, port
    except Exception:
        return None, None


if __name__ == '__main__':
    addr, port = get_settings()
    if addr:
        start_it(addr, port)
    else:
        start_it('8.8.8.8', 53)
