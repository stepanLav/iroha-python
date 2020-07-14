#!/usr/bin/env python3
#
# Copyright Soramitsu Co., Ltd. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#
import hashlib
import re
from this import s

from iroha import IrohaCrypto, ed25519_sha2
from iroha import Iroha, IrohaGrpc


import binascii
import time
import os

IROHA_HOST_ADDR = os.getenv('IROHA_HOST_ADDR', 's1.tst2.iroha.tech')
IROHA_PORT = os.getenv('IROHA_PORT', '50051')
ADMIN_ACCOUNT_ID = os.getenv('ADMIN_ACCOUNT_ID', 'ursama1@test')
ADMIN_PRIVATE_KEY = os.getenv(
     'ADMIN_PRIVATE_KEY', 'a9b588e7b07ee23d96b9e2480cefefde1b9274ffff01d91cfaea543a3b834a14e26d0543942dd602c95e0d98926c25b0089d7c39f08a40ab58f2d33431393c40')
iroha = Iroha(ADMIN_ACCOUNT_ID)
ADMIN_PRIVATE_KEY_1 = ed25519_sha2.SigningKey(binascii.unhexlify(ADMIN_PRIVATE_KEY))
net = IrohaGrpc('{}:{}'.format(IROHA_HOST_ADDR, IROHA_PORT))

f=0

def trace(func):
    def tracer(*args, **kwargs):
        count = 1

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
        iroha.command('TransferAsset', src_account_id='ursama1@test', dest_account_id='ursama@test',
                asset_id='coin#test', description='init top up', amount='10'),
    ], creator_account=ADMIN_ACCOUNT_ID, quorum=1)

    IrohaCrypto.sign_transaction(tx, ADMIN_PRIVATE_KEY_1)
    send_transaction_and_print_status(tx)
    print(tx)


@trace
def get_coin_info():
    """
    Get asset info for coin#domain
    :return:
    """
    query = iroha.query('GetAssetInfo', asset_id='coin#test')
    IrohaCrypto.sign_query(query, ADMIN_PRIVATE_KEY_1)

    response = net.send_query(query)
    data = response.asset_response.asset
    print('Asset id = {}, precision = {}'.format(data.asset_id, data.precision))

transfer_coin_from_admin_to_userone()
get_coin_info()
print('done')
