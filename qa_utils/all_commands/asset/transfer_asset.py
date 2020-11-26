#!/usr/bin/env python3
#
# Copyright Soramitsu Co., Ltd. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#

import os
import binascii
from time import sleep

from iroha import IrohaCrypto
from iroha import Iroha, IrohaGrpc
from iroha.primitive_pb2 import can_set_my_account_detail
import sys

if sys.version_info[0] < 3:
    raise Exception('Python 3 or a more recent version is required.')


IROHA_HOST_ADDR = os.getenv('IROHA_HOST_ADDR', '127.0.0.1')
IROHA_PORT = os.getenv('IROHA_PORT', '50051')
ADMIN_ACCOUNT_ID = 'alice@test'
ADMIN_PRIVATE_KEY = '51cec58ded55857ff908d4f205abe940aa5f20786753ec60ad56ed0db3d27048'
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
def transfer_coin_from_admin_to_userone():
    tx = iroha.transaction([
        iroha.command('TransferAsset', src_account_id=ADMIN_ACCOUNT_ID,
                      dest_account_id='bob@test',
                      asset_id='coin#test', description='Are you have 100 symbols?Are you have 100 symbols?Are you have 100 symbols?', amount='1')
    ])
    IrohaCrypto.sign_transaction(tx, ADMIN_PRIVATE_KEY)
    send_transaction_and_print_status(tx)



@trace
def get_account_assets():

        query = iroha.query('GetAccountAssets', account_id=ADMIN_ACCOUNT_ID)
        IrohaCrypto.sign_query(query, ADMIN_PRIVATE_KEY)

        response = net.send_query(query)
        data = response.account_assets_response.account_assets
        for asset in data:
            print('Asset id = {}, balance = {}'.format(
                asset.asset_id, asset.balance))

i=0
while i < 100:
    transfer_coin_from_admin_to_userone()
    get_account_assets()
    i += 1
    sleep(1)

