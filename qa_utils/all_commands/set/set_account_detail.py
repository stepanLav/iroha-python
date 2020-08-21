#!/usr/bin/env python3
#

import os
import binascii
from iroha import IrohaCrypto
from iroha import Iroha, IrohaGrpc
from iroha.primitive_pb2 import can_set_my_account_detail
import sys

if sys.version_info[0] < 3:
    raise Exception('Python 3 or a more recent version is required.')


IROHA_HOST_ADDR = os.getenv('IROHA_HOST_ADDR', 'localhost')
IROHA_PORT = os.getenv('IROHA_PORT', '2345')
ADMIN_ACCOUNT_ID = 'superuser@sora'
ADMIN_PRIVATE_KEY = '3B102A3F22A24EA1F3C9CCB0A237EC268955F099154F92CEC20B0474690AC58C'
iroha = Iroha(ADMIN_ACCOUNT_ID)
net = IrohaGrpc('{}:{}'.format(IROHA_HOST_ADDR, IROHA_PORT))
hex_hash = ''

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
    global hex_hash
    hex_hash = binascii.hexlify(IrohaCrypto.hash(transaction))
    print('Transaction hash = {}, creator = {}'.format(
        hex_hash, transaction.payload.reduced_payload.creator_account_id))
    net.send_tx(transaction)
    for status in net.tx_status_stream(transaction):
        print(status)


@trace
def set_account_detail():

    tx = iroha.transaction([
        iroha.command('SetAccountDetail', account_id='sora_projects@notary', key="project__sora", value="First dist project.2")
    ])
    IrohaCrypto.sign_transaction(tx, ADMIN_PRIVATE_KEY)

    send_transaction_and_print_status(tx)

set_account_detail()
