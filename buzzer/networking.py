# -*- coding: utf-8 -*-

import socket
import asyncore
import asynchat


TERMINATOR = '\r\n'
BUFFER_SIZE = 256


class Server(asyncore.dispatcher):

    def __init__(self, host, port, delegate, max_conn):
        asyncore.dispatcher.__init__(self)
        self._channels = {}
        self._buzzed = False
        self._max_conn = max_conn
        self._delegate = delegate
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(1)
        self.log('Server started.')

    def __del__(self):
        self.handle_close()

    def writable(self):
        return False

    def handle_close(self):
        for channel in self._channels.values():
            channel.handle_close()
        self.close()
        self.log('Server closed.')

    def handle_accept(self):
        conn, addr = self.accept()
        if len(self._channels) < self._max_conn:
            self.log('Connection accepted: %s' % (addr, ))
            # Dispatch connection to a _Channel
            _Channel(self, conn)
        else:
            self.log('Max number of connections reached, rejected: %s' % (addr, ))
            conn.close()

    def reset(self):
        self._buzzed = False
        for channel in self._channels.values():
            channel.reset()


class _Channel(asynchat.async_chat):
    """Handler for Client connections"""

    ac_in_buffer_size = BUFFER_SIZE
    ac_out_buffer_size = BUFFER_SIZE

    def __init__(self, server, conn):
        asynchat.async_chat.__init__(self, conn)
        self.add_channel(server._channels)
        self.log = server.log
        self.set_terminator(TERMINATOR)
        self._buffer = []
        self.server = server
        self._client_id = ''

    def handle_close(self):
        del self.server._channels[self._fileno]
        self.close()
        self.log('Connection closed: %s' % (self.addr, ))
        self.server._delegate.close(self._client_id)

    def handle_error(self):
        self.handle_close()

    def collect_incoming_data(self, data):
        self._buffer.append(data)

    def found_terminator(self):
        data = ''.join(self._buffer)
        self._buffer = []
        self.handle_data(data)

    def reset(self):
        self.push('<reset>' + TERMINATOR)

    def handle_data(self, data):
        self.log(data)
        if data == '<buzz>:' + self._client_id and not self.server._buzzed:
            self.server._buzzed = True
            self.push('<ack>' + TERMINATOR)
            self.server._delegate.ack(self._client_id)
        elif data.startswith('<id>:'):
            self._client_id = data.split(':')[1]
            self.server._delegate.accept(self._client_id, self.addr[0])


class Client(asynchat.async_chat):

    ac_in_buffer_size = BUFFER_SIZE
    ac_out_buffer_size = BUFFER_SIZE

    def __init__(self, host, port, delegate, id):
        asynchat.async_chat.__init__(self)
        self._id = id
        self._delegate = delegate
        self._buffer = []
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_terminator(TERMINATOR)
        self.connect((host, port))

    def handle_connect(self):
        self.log('connected')
        self.push('<id>:' + self._id + TERMINATOR)

    def handle_error(self):
        self.handle_close()

    def collect_incoming_data(self, data):
        self._buffer.append(data)

    def found_terminator(self):
        data = ''.join(self._buffer)
        self._buffer = []
        self.handle_data(data)

    def handle_data(self, data):
        self.log(data)
        if data == '<ack>':
            self._delegate.reply()
        elif data == '<reset>':
            self._delegate.reset()

    def buzz(self):
        self.push('<buzz>:' + self._id + TERMINATOR)
