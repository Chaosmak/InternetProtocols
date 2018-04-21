import datetime
import struct


class Question:
    def __init__(self, qname, qtype, qclass):
        self.qname = qname
        self.type = qtype
        self.qclass = qclass

    def __repr__(self):
        return 'name: {}, type: {}, class: {}'.format(self.qname, self.type, self.qclass)


class Answer:
    def __init__(self, name, antype, anclass, ttl, rdata, raw_name):
        self.name = name
        self.type = antype
        self.anclass = anclass
        self.ttl = ttl
        self.end_of_life = datetime.datetime.now() + datetime.timedelta(seconds=self.ttl)
        self.data = rdata
        self.raw_name = raw_name

    def __repr__(self):
        return 'name: {}, type: {}, class: {}, ttl: {}\ndata: {}\n'.format(
            self.name, self.type, self.anclass, self.ttl, self.data)


DNS_QUERY_MESSAGE_HEADER = struct.Struct("!6H")

DNS_QUERY_SECTION_FORMAT = struct.Struct("!2H")


class DNSEntry:
    def __init__(self, dns_packet):
        self.packet = dns_packet
        self.id = None
        self.qdcount = 0
        self.ancount = 0
        self.nscount = 0
        self.arcount = 0
        self.qr = None
        self.opcode = None
        self.aa = None
        self.tc = None
        self.rd = None
        self.ra = None
        self.z = None
        self.rcode = None
        self.name = None
        self.questions = []
        self.answers = []
        self.authoritativeRR = []
        self.additionalRR = []
        self.initialize_by_msg(dns_packet)

    def convert_to_response(self):
        self.qr = False

    @staticmethod
    def get_packet_with_changed_ttl(message, ttl):
        id, flags, qdcount, ancount, nscount, arcount = DNS_QUERY_MESSAGE_HEADER.unpack_from(
            message)

        offset = DNS_QUERY_MESSAGE_HEADER.size
        questions, offset, name = DNSEntry.decode_question_section(message, offset, qdcount, None)
        packet, offset = DNSEntry.decode_RR_section(message, offset, ancount, ttl)
        packet, offset = DNSEntry.decode_RR_section(packet, offset, nscount, ttl)
        packet, offset = DNSEntry.decode_RR_section(packet, offset, arcount, ttl)
        return packet

    def initialize_by_msg(self, message):
        self.id, flags, self.qdcount, self.ancount, self.nscount, self.arcount = DNS_QUERY_MESSAGE_HEADER.unpack_from(
            message)

        self.qr = (flags & 0x8000) != 0  # тип сообщения
        self.opcode = (flags & 0x7800) >> 11  # код операции
        self.aa = (flags & 0x0400) != 0  # авторитетный ответ
        self.tc = (flags & 0x200) != 0  # обрезано
        self.rd = (flags & 0x100) != 0  # рекурсивно?
        self.ra = (flags & 0x80) != 0  # рекурсия возможна
        self.z = (flags & 0x70) >> 4  # зарезервировано ( 3 ноля)
        self.rcode = flags & 0xF  # код возврата

        offset = DNS_QUERY_MESSAGE_HEADER.size
        self.questions, offset, self.name = DNSEntry.decode_question_section(message, offset, self.qdcount, self.name)
        self.answers, offset = DNSEntry.decode_RR_section(message, offset, self.ancount)
        self.authoritativeRR, offset = DNSEntry.decode_RR_section(message, offset, self.nscount)
        self.additionalRR, offset = DNSEntry.decode_RR_section(message, offset, self.arcount)

    def append_answer(self, answer):
        self.ancount += 1
        self.answers.append(answer)

    @staticmethod
    def decode_question_labels(message, offset):
        labels = []
        while True:
            length, = struct.unpack_from("!B", message, offset)
            if (length & 0xC0) == 0xC0:
                pointer, = struct.unpack_from("!H", message, offset)
                offset += 2
                res = DNSEntry.decode_question_labels(message, pointer & 0x3FFF)
                try:
                    return labels + res, offset
                except TypeError:
                    try:
                        return labels + res[0]
                    except TypeError:
                        return labels + [res[0]]
                except Exception:
                    print(res)
                    return labels + [b'Error']

            if (length & 0xC0) != 0x00:
                raise ValueError("unknown label encoding")
            offset += 1
            if length == 0:
                return labels, offset
            labels.append(*struct.unpack_from("!%ds" % length, message, offset))
            offset += length

    @staticmethod
    def decode_question_section(message, offset, qdcount, name):
        questions = []
        for _ in range(qdcount):
            qname, offset = DNSEntry.decode_question_labels(message, offset)
            if not name:
                name = b'.'.join(qname)
            qtype, qclass = DNS_QUERY_SECTION_FORMAT.unpack_from(message, offset)
            offset += DNS_QUERY_SECTION_FORMAT.size
            question = Question(qname, qtype, qclass)
            questions.append(question)
        return questions, offset, name

    @staticmethod
    def decode_cname_labels(message, offset):
        labels = []
        while True:
            length, = struct.unpack_from("!B", message, offset)
            if (length & 0xC0) == 0xC0:
                pointer, = struct.unpack_from("!H", message, offset)
                offset += 2
                res = DNSEntry.decode_question_labels(message, pointer & 0x3FFF)[0]
                try:
                    return labels + DNSEntry.decode_question_labels(message, pointer & 0x3FFF)[0]
                except TypeError:
                    return labels + [res[0]]
            if (length & 0xC0) != 0x00:
                raise ValueError("unknown label encoding")
            offset += 1
            if length == 0:
                return labels
            labels.append(*struct.unpack_from("!%ds" % length, message, offset))
            offset += length

    @staticmethod
    def decode_RR_section(message, offset, ancount, new_ttl = None):
        answers = []
        for _ in range(ancount):
            pointer, = struct.unpack_from("!H", message, offset)
            raw_name = message[offset:offset + 2]
            anname = DNSEntry.decode_cname_labels(message, pointer & 0x3FFF)
            offset += 2
            antype, anclass = DNS_QUERY_SECTION_FORMAT.unpack_from(message, offset)
            offset += 4
            ttl, = struct.unpack_from('!i', message, offset)
            if new_ttl:
                ttl_in_bytes = struct.pack('!i',new_ttl)
                message = message[:offset] + ttl_in_bytes + message[offset+4:]
            offset += 4
            rdlength, = struct.unpack_from('!H', message, offset)
            offset += 2
            rdata = message[offset:offset + rdlength]
            answer = Answer(anname, antype, anclass, ttl, rdata, raw_name)
            answers.append(answer)
            offset += rdlength
        if new_ttl:
            return message, offset
        return answers, offset

    def __repr__(self):
        return '{} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {}'.format(
            self.name, self.id, self.qdcount, self.ancount,
            self.nscount, self.arcount, self.qr, self.opcode, self.aa,
            self.tc, self.rd, self.ra, self.z, self.rcode, self.questions,
            self.answers, self.authoritativeRR, self.additionalRR)
