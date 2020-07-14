#!/usr/bin/env python3
#
from time import sleep
import os
import binascii
from iroha import IrohaCrypto
from iroha import Iroha, IrohaGrpc
import sys

if sys.version_info[0] < 3:
    raise Exception('Python 3 or a more recent version is required.')

f=0
IROHA_HOST_ADDR = os.getenv('IROHA_HOST_ADDR', 'localhost')
IROHA_PORT = os.getenv('IROHA_PORT', '2345')
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
def send_transaction(transaction):
    hex_hash = binascii.hexlify(IrohaCrypto.hash(transaction))
    print('Transaction hash = {}, creator = {}'.format(
        hex_hash, transaction.payload.reduced_payload.creator_account_id))
    net.send_tx(transaction)


@trace
def transfer_asset():
    tx = iroha.transaction([
        iroha.command('TransferAsset', src_account_id='admin@test', dest_account_id='userone@domain',
                                 asset_id='coin#test', description='init top up', amount='2')
    ], creator_account=ADMIN_ACCOUNT_ID, quorum=1)

    IrohaCrypto.sign_transaction(tx, ADMIN_PRIVATE_KEY)
    send_transaction(tx)

while f<=99990:
    transfer_asset()
    f+=1
    sleep(0.5)
    print(f)
    print('=============================================================')

