#!/usr/bin/env python3
#

import os
import binascii
from time import sleep

from iroha import IrohaCrypto
from iroha import Iroha, IrohaGrpc
from iroha import primitive_pb2
import sys

if sys.version_info[0] < 3:
    raise Exception('Python 3 or a more recent version is required.')


IROHA_HOST_ADDR = os.getenv('IROHA_HOST_ADDR', '127.0.0.1')
IROHA_PORT = os.getenv('IROHA_PORT', '50051')
ADMIN_ACCOUNT_ID = 'admin@test'
ADMIN_PRIVATE_KEY = 'f101537e319568c765b2cc89698325604991dca57b9716b58016b253506cab70'
iroha = Iroha(ADMIN_ACCOUNT_ID)
net = IrohaGrpc('{}:{}'.format(IROHA_HOST_ADDR, IROHA_PORT))


def trace(func):
    """
    A decorator for tracing methods' begin/end execution points
    """

    def tracer(*args, **kwargs):
        name = func.__name__
        print('\tEntering "{}"'.format(name))
        result = func(*args, **kwargs)
        print('\tLeaving "{}"'.format(name))
        return result

    return tracer


@trace
def send_transaction_and_print_status(transaction):
    hex_hash = binascii.hexlify(IrohaCrypto.hash(transaction))
    print('Transaction hash = {}, creator = {}'.format(
        hex_hash, transaction.payload.reduced_payload.creator_account_id))
    net.send_tx(transaction)
    for status in net.tx_status_stream(transaction):
        print(status)


@trace
def add_peer():
    peer4 = primitive_pb2.Peer()
    peer4.address = '127.0.0.1:10004'
    peer4.peer_key = '4b66488f8d745930334efe15ed4879642cfd493bae302f7833d6564ba3edaea9'
    tx = iroha.transaction([
        iroha.command('AddPeer', peer=peer4)
    ], creator_account=ADMIN_ACCOUNT_ID, quorum=1)

    IrohaCrypto.sign_transaction(tx, ADMIN_PRIVATE_KEY)
    send_transaction_and_print_status(tx)


add_peer()
