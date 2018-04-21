from DNSClasses import *


class Packet:
    def __init__(self, id, flags):
        self.id = id
        self.flags = flags


class PacketCreator:
    @staticmethod
    def get_min_ttl(packet):
        entry = DNSEntry(packet)
        ttl = float('inf')
        for answer in entry.answers:
            if answer.ttl < ttl:
                ttl = answer.ttl
        for rr in entry.authoritativeRR:
            if rr.ttl < ttl:
                ttl = rr.ttl
        for rr in entry.additionalRR:
            if rr.ttl < ttl:
                ttl = rr.ttl
        if ttl == float('inf'):
            return 600
        return ttl

    @staticmethod
    def set_ttl(packet, ttl):
        return DNSEntry.get_packet_with_changed_ttl(packet, ttl)

    @staticmethod
    def copy_id(question_packet, answer_packet):
        qid = question_packet[:2]
        return qid+answer_packet[2:]

    @staticmethod
    def get_error_answer(packet):
        entry = DNSEntry(packet)
        header = [entry.id, PacketCreator.get_flags_bytes(entry, error=True),
                  entry.qdcount, 0, 0, 0]
        packet = struct.pack('!6H', *header)
        for question in entry.questions:
            for url in question.qname:
                packet += struct.pack("!B", len(url))
                for ch in url.decode():
                    packet += struct.pack("!c", bytes(ch, 'utf-8'))
            packet += struct.pack("!B", 0)  # конец url
            packet += struct.pack("!H", question.type)
            packet += struct.pack("!H", question.qclass)
        return packet

    @staticmethod
    def get_flags_bytes(request_entry, error=False):
        rcode = request_entry.rcode
        if error:
            rcode = 2
        flags = '1' + '{0:04b}'.format(request_entry.opcode)
        for x in (request_entry.aa, request_entry.tc,
                  request_entry.rd, request_entry.ra):
            flags += str(int(x))
        flags += '000' + '{0:04b}'.format(rcode)
        return int(flags, 2)

