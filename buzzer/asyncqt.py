# -*- coding: utf-8 -*-

from PyQt4 import QtCore


class ServerDelegate(QtCore.QObject):

    clientAdded = QtCore.pyqtSignal(QtCore.QString, QtCore.QString)

    clientRemoved = QtCore.pyqtSignal(QtCore.QString)

    ackSent = QtCore.pyqtSignal(QtCore.QString)

    def accept(self, client_id, addr):
        self.clientAdded.emit(client_id, addr)

    def close(self, client_id):
        self.clientRemoved.emit(client_id)

    def ack(self, client_id):
        self.ackSent.emit(client_id)


class ClientDelegate(QtCore.QObject):

    ackReceived = QtCore.pyqtSignal()

    resetReceived = QtCore.pyqtSignal()

    def reply(self):
        self.ackReceived.emit()

    def reset(self):
        self.resetReceived.emit()
