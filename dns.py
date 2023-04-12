"""dns.py: A simple DNS server"""
import glob
import json
import socket

# Using IPV4, UDP
port = 53
ip = '127.0.0.1'
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((ip, port))


def load_zones():
    """Load all the zones from the zones directory"""
    jsonzone = {}

    zonefiles = glob.glob('zones/*.zone')
    for zonefile in zonefiles:
        with open(zonefile, 'r') as zone:
            jsondata = json.load(zone)
            # data["$origin"] contains the domain name
            jsonzone[jsondata["$origin"]] = jsondata

    return jsonzone


zonedata = load_zones()


def getflags(flags):
    """Get the flags from the DNS header"""

    # 2 bytes for Flags
    byte1 = bytes(flags[:1])
    byte2 = bytes(flags[1:2])

    rflags = ''

    QR = '1'

    OPCODE = ''
    for bit in range(1, 5):
        # Get the bit value at the bit position
        OPCODE += str(ord(byte1) & (1 << bit))

    AA = '1'

    TC = '0'

    RD = '0'

    RA = '0'

    Z = '000'

    RCODE = '0000'

    return int(QR + OPCODE + AA + TC + RD, 2) \
        .to_bytes(1, byteorder='big') \
        + int(RA + Z + RCODE, 2) \
            .to_bytes(1, byteorder='big')


def getquestiondomain(data):
    """Get the domain name from the question section"""

    state = 0
    expectedlength = 0
    domainstring = ''
    domainparts = []
    x = 0
    y = 0

    for byte in data:
        if state == 1:
            if byte != 0:
                domainstring += chr(byte)
            x += 1
            if x == expectedlength:
                domainparts.append(domainstring)
                domainstring = ''
                state = 0
                x = 0
            if byte == 0:
                domainparts.append(domainstring)
                break
        else:
            state = 1
            expectedlength = byte
        y += 1

    questiontype = data[y:y + 2]

    return (domainparts, questiontype)


def getzone(domain):
    """Get zone data from the domain name"""

    global zonedata

    zone_name = '.'.join(domain)
    return zonedata[zone_name]


def getrecs(data):
    """Get the records from the zone data"""

    domain, questiontype = getquestiondomain(data)
    qt = ''
    if questiontype == b'\x00\x01':
        qt = 'a'

    zone = getzone(domain)

    return (zone[qt], qt, domain)

def buildquestion(domainname, rectype):
    """Build the question section"""

    qbytes = b''

    for part in domainname:
        length = len(part)
        qbytes += bytes([length])

        for char in part:
            qbytes += ord(char).to_bytes(1, byteorder='big')

    if rectype == 'a':
        qbytes += (1).to_bytes(2, byteorder='big')

    qbytes += (1).to_bytes(2, byteorder='big')

    return qbytes

def rectobytes(domainname, rectype, recttl, recval):
    """Build the resource record section"""

    rbytes = b'\xc0\x0c'

    if rectype == 'a':
        rbytes = rbytes + bytes([0]) + bytes([1])

    rbytes = rbytes + bytes([0]) + bytes([1])

    rbytes += int(recttl).to_bytes(4, byteorder='big')

    if rectype == 'a':
        rbytes = rbytes + bytes([0]) + bytes([4])

        for part in recval.split('.'):
            rbytes += bytes([int(part)])

    return rbytes


def buildresponse(data):
    """Build the response section"""

    # 2 bytes for Transaction ID
    TransactionID = data[:2]

    # 2 bytes for Flags
    Flags = getflags(data[2:4])

    # 2 bytes for Questions
    QDCOUNT = b'\x00\x01'

    # 2 bytes for Answers
    ANCOUNT = len(getrecs(data[12:])[0]).to_bytes(2, byteorder='big')

    # Nameserver Count
    NSCOUNT = (0).to_bytes(2, byteorder='big')

    # Additional Records
    ARCOUNT = (0).to_bytes(2, byteorder='big')

    dnsheader = TransactionID + Flags + QDCOUNT + ANCOUNT + NSCOUNT + ARCOUNT

    dnsbody = b''

    records, rectype, domainname = getrecs(data[12:])

    dnsquestion = buildquestion(domainname, rectype)

    for record in records:
        dnsbody += rectobytes(domainname, rectype, record['ttl'], record[
            'value'])

    return dnsheader + dnsquestion + dnsbody


while 1:
    data, addr = sock.recvfrom(512)
    r = buildresponse(data)
    sock.sendto(r, addr)
