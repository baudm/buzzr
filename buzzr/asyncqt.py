# -*- coding: utf-8 -*-
#
# Copyright (C) 2010  Darwin M. Bautista <daruuin@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

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
