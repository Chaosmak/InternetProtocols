import base64
import configparser
import os
import socket
import ssl

CRLF = '\r\n'

MIME_TYPES = {'.mp4': 'audio/mp4',
              '.pdf': 'application/pdf',
              '.ogg': 'application/ogg',
              '.zip': 'application/zip',
              '.mp3': 'audio/mpeg',
              '.mpeg': 'audio/mpeg',
              '.jpeg': 'image/jpeg',
              '.png': 'image/png',
              '.txt': 'text/plain',
              '.doc': 'application/msword'
              }

FROM = 'stest54@yandex.ru'
PASSWORD = 'QwertY01'


def sendto(sock, msg):
    sock.send((msg + CRLF).encode())
    if len(msg) < 1000:
        print(msg)


def load_letter():
    filename = os.path.join('.', 'Attachments', 'Letter.txt')
    with open(filename, 'r') as f:
        return f.read()


def get_file_and_extension(filepath):
    filename = os.path.basename(filepath)
    extension = os.path.splitext(filename)[1]
    with open(filepath, 'rb') as f:
        file = f.read()
    return file, extension


def format_smtp_message(addressees, theme, files):
    messages = []
    for addressee in addressees:
        list = ['EHLO stest54', 'AUTH LOGIN',
                base64.b64encode('{}'.format(FROM).encode()).decode(),
                base64.b64encode('{}'.format(PASSWORD).encode()).decode(),
                'MAIL FROM: {}'.format(FROM),
                'RCPT TO: {}'.format(addressee),
                'DATA']
        stop_symbol = '--?+?'
        message = ['From: Me(SMTP) {}'.format(FROM),
                   'To: You <{}>'.format(addressee), 'Subject: {}'.format(theme),
                   'Content-Type: multipart/mixed; boundary=?+?;', '', stop_symbol,
                   'Content-Type: text/plain', '\n', '{}'.format(load_letter()), '{}'.format(stop_symbol)]
        for filepath in files:
            filename = os.path.basename(filepath)
            file, ext = get_file_and_extension(filepath)
            message += ['Content-Type:{}; name={}'.format(MIME_TYPES[ext], filename),
                        'Content-Transfer-Encoding:base64',
                        'Content-Disposition:attachment; filename={}'.format(filename),
                        '\n', base64.b64encode(file).decode(),
                        '{}'.format(stop_symbol)]
        message[-1] += '--'
        message += ['.']
        messages.append((list, message))
    return messages


def load_config(path):
    if not os.path.exists(path):
        raise ValueError('WHERE IS CONFIG.INI????')

    config = configparser.ConfigParser()
    config.read(path)
    addressees = []
    to_items = config.items('To')
    for key, to in to_items:
        addressees.append(to)

    theme = config.get('Subject', 'theme')
    files = []
    file_items = config.items('Files')
    for k, file in file_items:
        files.append(os.path.join('.', 'Attachments', file))
    return addressees, theme, files


def send_smtp_msg(list, message):
    sock = socket.socket()
    sock.settimeout(10)
    sock.connect(('smtp.yandex.ru', 465))
    sslSock = ssl.wrap_socket(sock)
    data = sslSock.recv(1024)
    for header_line in list:
        sendto(sslSock, header_line)
        data = sslSock.recv(1024)
        print(data)
    for line in message:
        print(len(body))
        sendto(sslSock, line)
    print(sslSock.recv(1024))


if __name__ == '__main__':
    addressees, theme, files = load_config(os.path.join('.', 'Attachments', 'config.ini'))
    res = format_smtp_message(addressees, theme, files)
    for msg in res:
        header, body = msg
        send_smtp_msg(header, body)
