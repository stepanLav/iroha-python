#!/usr/bin/env python3
#

import os
import binascii

from iroha import IrohaCrypto
from iroha import Iroha, IrohaGrpc
from iroha import primitive_pb2
import sys

if sys.version_info[0] < 3:
    raise Exception('Python 3 or a more recent version is required.')


IROHA_HOST_ADDR = os.getenv('IROHA_HOST_ADDR', '127.0.0.1')
IROHA_PORT = os.getenv('IROHA_PORT', '50051')
ADMIN_ACCOUNT_ID = 'root@root'
ADMIN_PRIVATE_KEY = '7a1cb487ed17a60efbf4aa21df74bb391fcc2260f87c83eb7de9c120d2112ec7'
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
    peer1 = primitive_pb2.Peer()
    peer1.address = '10.211.12.6:10002'
    peer1.peer_key = '313a07e6384776ed95447710d15e59148473ccfc052a681317a72a69f2a49910'
    tx = iroha.transaction([
        iroha.command('AddPeer', peer=peer1)
    ], creator_account=ADMIN_ACCOUNT_ID, quorum=1)

    IrohaCrypto.sign_transaction(tx, ADMIN_PRIVATE_KEY)
    send_transaction_and_print_status(tx)


add_peer()
