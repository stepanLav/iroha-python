#!/usr/bin/env python3
#
# Copyright Soramitsu Co., Ltd. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#

import os
import binascii
from iroha import IrohaCrypto
from iroha import Iroha, IrohaGrpc
import time
from iroha.primitive_pb2 import can_set_my_account_detail
import sys

if sys.version_info[0] < 3:
    raise Exception('Python 3 or a more recent version is required.')

IROHA_HOST_ADDR = os.getenv('IROHA_HOST_ADDR', '127.0.0.1')
IROHA_PORT = os.getenv('IROHA_PORT', '50051')
ADMIN_ACCOUNT_ID = os.getenv('ADMIN_ACCOUNT_ID', 'admin@test')
ADMIN_PRIVATE_KEY = os.getenv(
    'ADMIN_PRIVATE_KEY', 'f101537e319568c765b2cc89698325604991dca57b9716b58016b253506cab70')

user_private_key = IrohaCrypto.private_key()
user_public_key = IrohaCrypto.derive_public_key(user_private_key)
iroha = Iroha(ADMIN_ACCOUNT_ID)
net = IrohaGrpc('{}:{}'.format(IROHA_HOST_ADDR, IROHA_PORT))

f=0

def trace(func):
    def tracer(*args, **kwargs):
        count = 100

        while count:
            try:
                name = func.__name__
                print('\tEntering "{}"'.format(name))
                result = func(*args, **kwargs)
                print('\tLeaving "{}"'.format(name))
                return result
            except Exception as e:
                print('Error:', e)
                count -= 1
                time.sleep(1)
                transfer_coin_from_admin_to_userone()

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
def transfer_coin_from_admin_to_userone():
    """
    Transfer 2.00 'coin#domain' from 'admin@test' to 'userone@domain'
    """
    tx = iroha.transaction([
        iroha.command('TransferAsset', src_account_id='admin@test', dest_account_id='test@test',
                asset_id='coin#test', description='init top up', amount='1.1'),
    ], creator_account=ADMIN_ACCOUNT_ID, quorum=1)

    IrohaCrypto.sign_transaction(tx, ADMIN_PRIVATE_KEY)
    send_transaction_and_print_status(tx)

@trace
def asset_transfer():
    global iroha
    init_cmds = [
        iroha.command('AddAssetQuantity',
                      asset_id='coin#test', amount='3.10'),
        iroha.command('TransferAsset', src_account_id='admin@test', dest_account_id='test@test',
                      asset_id='coin#test', description='init top up', amount='2'),
    ]
    init_tx = iroha.transaction(init_cmds)
    IrohaCrypto.sign_transaction(init_tx, ADMIN_PRIVATE_KEY)
    send_transaction_and_print_status(init_tx)


@trace
def get_coin_info():
    """
    Get asset info for coin#domain
    :return:
    """
    query = iroha.query('GetAssetInfo', asset_id='coin#test')
    IrohaCrypto.sign_query(query, ADMIN_PRIVATE_KEY)

    response = net.send_query(query)
    data = response.asset_response.asset
    print('Asset id = {}, precision = {}'.format(data.asset_id, data.precision))

while f<=990:
    transfer_coin_from_admin_to_userone()
    asset_transfer()
    f+=1
    print(f)
    print('=============================================================')

print('done')