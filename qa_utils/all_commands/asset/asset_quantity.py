#!/usr/bin/env python3
#

import os
import binascii

from iroha import IrohaCrypto
from iroha import Iroha, IrohaGrpc

IROHA_HOST_ADDR = os.getenv('IROHA_HOST_ADDR', 'localhost')
IROHA_PORT = os.getenv('IROHA_PORT', '5555')
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
def send_transaction(transaction):
    hex_hash = binascii.hexlify(IrohaCrypto.hash(transaction))
    print('Transaction hash = {}, creator = {}'.format(
        hex_hash, transaction.payload.reduced_payload.creator_account_id))
    net.send_tx(transaction)

@trace
def add_asset_quantity():

    tx = iroha.transaction([
        iroha.command('AddAssetQuantity',
                      asset_id='coin#test', amount='100')
    ])

    IrohaCrypto.sign_transaction(tx, ADMIN_PRIVATE_KEY)
    send_transaction(tx)

i=0
while i < 1:
 add_asset_quantity()
 i+=1
