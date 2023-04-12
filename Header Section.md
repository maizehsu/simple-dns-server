### Header Section

The header contains the following fields:

                                    1  1  1  1  1  1
      0  1  2  3  4  5  6  7  8  9  0  1  2  3  4  5
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |                      ID                       |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |QR|   Opcode  |AA|TC|RD|RA|   Z    |   RCODE   |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |                    QDCOUNT                    |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |                    ANCOUNT                    |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |                    NSCOUNT                    |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |                    ARCOUNT                    |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+

where:

- **ID**: A 16 bit identifier assigned by the program that generates any kind of query.  This identifier is copied the corresponding reply and can be used by the requester to match up replies to outstanding queries.
- **QR**: A one bit field that specifies whether this message is a query (0), or a response (1).
- **OPCODE**:  A four bit field that specifies kind of query in this message.  This value is set by the originator of a query and copied into the response.  The values are:

                0               a standard query (QUERY)
        
                1               an inverse query (IQUERY)
        
                2               a server status request (STATUS)
        
                3-15            reserved for future use

- **AA**: Authoritative Answer - this bit is valid in responses, and specifies that the responding name server is an authority for the domain name in question section.
- **TC**: TrunCation - specifies that this message was truncated due to length greater than that permitted on the transmission channel.
- **RD**: Desired - this bit may be set in a query and is copied into the response.  If RD is set, it directs the name server to pursue the query recursively. Recursive query support is optional.
- **RA**: Recursion Available - this be is set or cleared in a response, and denotes whether recursive query support is available in the name server.
- **Z**: Reserved for future use.  Must be zero in all queries and responses.
- **RCODE**: Response code - this 4 bit field is set as part of responses.  The values have the following interpretation:

                0               No error condition
        
                1               Format error - The name server was
                                unable to interpret the query.
        
                2               Server failure - The name server was
                                unable to process this query due to a
                                problem with the name server.
        
                3               Name Error - Meaningful only for
                                responses from an authoritative name
                                server, this code signifies that the
                                domain name referenced in the query does
                                not exist.
        
                4               Not Implemented - The name server does
                                not support the requested kind of query.
        
                5               Refused - The name server refuses to
                                perform the specified operation for
                                policy reasons.  For example, a name
                                server may not wish to provide the
                                information to the particular requester,
                                or a name server may not wish to perform
                                a particular operation (e.g., zone transfer) for particular data.
        
                6-15            Reserved for future use.

- **QDCOUNT**: unsigned 16 bit integer specifying the number of entries in the question section.
- **ANCOUNT**: unsigned 16 bit integer specifying the number of resource records in the answer section.
- **NSCOUNT**: an unsigned 16 bit integer specifying the number of name
	                server resource records in the authority records
	                section.
- **ARCOUNT**: an unsigned 16 bit integer specifying the number of
	                resource records in the additional records section.

**Example**

A standard **Domain Name System (query)** might look like this in wireshark:

- Transaction ID: 0x6ee3
- Flags: 0x0120 Standard query
	- 0... .... .... .... = Response: Message is a query
	- .000 0... .... .... = Opcode: Standard query (0)
	- .... ..0. .... .... = Truncated: Message is not truncated
	- .... ...1 .... .... = Recursion desired: Do query recursively
	- .... .... .0.. .... = Z: reserved (0)
	- .... .... ..1. .... = AD bit: Set
	- .... .... ...0 .... = Non-authenticated data: Unacceptable

### DNS Message Compression

**Definition**

In order to reduce the size of messages, the domain system utilizes a compression scheme which eliminates the repetition of domain names in a message.

In this scheme, an entire domain name or a list of labels at
the end of a domain name is replaced with a pointer to a prior occurance
of the same name.

The pointer takes the form of a two octet sequence:

    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    | 1  1|                OFFSET                   |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+

- The first two bits are ones.  This allows a pointer to be distinguished
	from a label, since the label must begin with two zero bits because
	labels are restricted to 63 octets or less. 
- (The 10 and 01 combinations are reserved for future use.) 
- The OFFSET field specifies an offset from the start of the message (i.e., the first octet of the ID field in the domain header).  A zero offset specifies the first byte of the ID field, etc.

The compression scheme allows a domain name in a message to be
represented as either:

   - a sequence of labels ending in a zero octet

   - a pointer

   - a sequence of labels ending with a pointer

