# -*- coding: utf-8 -*-

import sys
import os.path
import signal
import socket
import asyncore

from buzzer.asyncqt import ServerDelegate, ClientDelegate
from buzzer.networking import Server, Client

from PyQt4 import QtCore, QtGui, uic


class _AsyncoreThread(QtCore.QThread):

    def run(self):
        asyncore.loop()


def server_main():
    app = QtGui.QApplication(sys.argv)
    # server config
    config = uic.loadUi(os.path.join('resources', 'server-config.ui'))
    validator = QtGui.QIntValidator(1, 65535, config)
    config.numClients.setValidator(validator)
    config.port.setValidator(validator)
    if not config.exec_():
        sys.exit()

    port = int(config.port.text())
    num_clients = int(config.numClients.text())
    obj = ServerDelegate()

    try:
        server = Server('', port, obj, num_clients)
    except socket.error, msg:
        server.handle_close()
        sys.exit(msg)

    # actual UI
    ui = uic.loadUi(os.path.join('resources', 'server.ui'))

    def accept(uid, ip):
        row_count = ui.clients.rowCount()
        ui.clients.setRowCount(row_count + 1)
        item = QtGui.QTableWidgetItem(uid)
        ui.clients.setItem(row_count, 0, item)
        item = QtGui.QTableWidgetItem(ip)
        ui.clients.setItem(row_count, 1, item)

    def close(client_id):
        row = ui.clients.findItems(client_id, QtCore.Qt.MatchExactly)[0].row()
        ui.clients.removeRow(row)

    def ack(client_id):
        QtGui.QMessageBox.information(ui, 'First', client_id)
        server.reset()

    # start asyncore loop
    t = _AsyncoreThread()
    t.start()
    # Setup signal-slot connections
    app.lastWindowClosed.connect(server.handle_close)
    obj.clientAdded.connect(accept)
    obj.clientRemoved.connect(close)
    obj.ackSent.connect(ack)
    # show UI
    ui.show()
    # Setup signal handlers
    signal.signal(signal.SIGTERM, lambda s, f: ui.close())
    signal.signal(signal.SIGINT, lambda s, f: ui.close())
    # Start event loop
    sys.exit(app.exec_())


def client_main():
    app = QtGui.QApplication(sys.argv)
    # client config
    config = uic.loadUi(os.path.join('resources', 'client-config.ui'))
    validator = QtGui.QIntValidator(1, 65535, config)
    config.port.setValidator(validator)
    if not config.exec_():
        sys.exit()

    host = str(config.host.text())
    port = int(config.port.text())
    client_id = str(config.clientId.text())
    obj = ClientDelegate()

    try:
        client = Client(host, port, obj, client_id)
    except socket.gaierror, error:
        client.handle_close()
        sys.exit(msg)

    ui = uic.loadUi(os.path.join('resources', 'client.ui'))
    ui.setWindowTitle('Buzzer - ' + client_id)

    css = 'background: #FFFFFF url(resources/%s) no-repeat center middle;'
    ui.buzzButton.setStyleSheet(css % ('push-button-normal.jpg', ))

    def clicked():
        ui.buzzButton.setEnabled(False)
        client.buzz()

    def pressed():
        ui.buzzButton.setStyleSheet(css % ('push-button-pressed.jpg', ))

    def released():
        ui.buzzButton.setStyleSheet(css % ('push-button-normal.jpg', ))

    def ack():
        QtGui.QSound.play(os.path.join('resources', 'buzzerheavy.wav'))

    def reset():
        ui.buzzButton.setEnabled(True)

    # start asyncore loop
    t = _AsyncoreThread()
    t.start()
    # Setup signal-slot connections
    app.lastWindowClosed.connect(client.handle_close)
    ui.buzzButton.clicked.connect(clicked)
    ui.buzzButton.pressed.connect(pressed)
    ui.buzzButton.released.connect(released)
    obj.ackReceived.connect(ack)
    obj.resetReceived.connect(reset)
    # show UI
    ui.show()
    # Setup signal handlers
    signal.signal(signal.SIGTERM, lambda s, f: ui.close())
    signal.signal(signal.SIGINT, lambda s, f: ui.close())
    # Start event loop
    sys.exit(app.exec_())
