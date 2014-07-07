import pysocketio_parser as parser
import logging

log = logging.getLogger(__name__)


class Adapter(object):
    def __init__(self, nsp):
        """Memory adapter constructor.

        :param nsp: Adapter namespace
        :type nsp: pysocketio.namespace.Namespace
        """
        self.nsp = nsp

        self.rooms = {}
        self.sids = {}

        self.encoder = parser.Encoder()

    def add(self, sid, room, callback=None):
        """Adds a socket from a room.

        :param sid: socket id
        :type sid: str

        :param room: room name
        :type room: str

        :param callback: Callback
        :type callback: function
        """
        self.sids[sid] = self.sids.get(sid) or {}
        self.rooms[room] = self.rooms.get(room) or {}

        self.sids[sid][room] = True
        self.rooms[room][sid] = True

        if callback:
            callback()

    def remove(self, sid, room, callback=None):
        """Removes a socket from a room.

        :param sid: socket id
        :type sid: str

        :param room: room name
        :type room: str

        :param callback: Callback
        :type callback: function
        """
        self.sids[sid] = self.sids.get(sid) or {}
        self.rooms[room] = self.rooms.get(room) or {}

        del self.sids[sid][room]
        del self.rooms[room][sid]

        if callback:
            callback()

    def remove_all(self, sid):
        """Removes a socket from all rooms it's joined.

        :param sid: socket id
        :type sid: str
        """
        if sid not in self.sids:
            return

        for room in self.sids[sid].keys():
            if sid in self.rooms[room]:
                del self.rooms[room][sid]

        del self.sids[sid]

    def broadcast(self, packet, options=None):
        """Broadcasts a packet.

        Options
         - `flags` {dict} flags for this packet
         - `except` {list} sids that should be excluded
         - `rooms` {list} rooms that this packet should broadcast to

        :param packet: Packet
        :type packet: dict

        :param options: Packet options
        :type options: dict
        """
        log.debug('broadcast - packet: %s, options: %s', packet, options)

        if options is None:
            options = {}

        flags = options.get('flags') or {}
        excluded = options.get('except') or []
        rooms = options.get('rooms') or []

        packet['nsp'] = self.nsp.name

        def on_encoded(encoded_packets):
            if not rooms:
                # Send to all clients
                return self.broadcast_clients(flags, excluded, encoded_packets)

            # Send to clients in specified rooms
            return self.broadcast_rooms(flags, excluded, encoded_packets, rooms)

        # Encode packets, handle decoded packets
        self.encoder.encode(packet, on_encoded)

    def broadcast_clients(self, flags, excluded, encoded_packets):
        for sid in list(self.sids):
            if sid in excluded:
                continue

            socket = self.nsp.connected.get(sid)

            if socket is None:
                continue

            socket.packet(encoded_packets, True, flags.get('volatile'))

    def broadcast_rooms(self, flags, excluded, encoded_packets, rooms):
        sids = {}

        for room in list(rooms):
            if room not in self.rooms:
                continue

            for sid in list(self.rooms[room]):
                if sid in sids or sid in excluded:
                    continue

                socket = self.nsp.connected.get(sid)

                if socket is None:
                    continue

                socket.packet(encoded_packets, True, flags.get('volatile'))
                sids[sid] = True
