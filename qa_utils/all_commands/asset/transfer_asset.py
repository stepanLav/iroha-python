#!/usr/bin/env python3
#
# Copyright Soramitsu Co., Ltd. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#

import os
import binascii
from iroha import IrohaCrypto
from iroha import Iroha, IrohaGrpc
from iroha.primitive_pb2 import can_set_my_account_detail
import sys

if sys.version_info[0] < 3:
    raise Exception('Python 3 or a more recent version is required.')


IROHA_HOST_ADDR = os.getenv('IROHA_HOST_ADDR', '127.0.0.1')
IROHA_PORT = os.getenv('IROHA_PORT', '55551')
ADMIN_ACCOUNT_ID = 'admin@root'
ADMIN_PRIVATE_KEY = 'de9d622f92efe4a6e9a3926024b2a4543462233db0bfabcaf8eb6933e6c81466'
iroha = Iroha(ADMIN_ACCOUNT_ID)
in_file = open("/Users/stepanlavrentev/irohaSetting/tls/server.crt", "rb")
sert = in_file.read()
in_file.close()
in_file = open("/Users/stepanlavrentev/irohaSetting/tls/server.key", "rb")
key = in_file.read()
in_file.close()
net = IrohaGrpc('{}:{}'.format(IROHA_HOST_ADDR, IROHA_PORT), secure=True, cert=sert, priv=key, chain=sert)


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
                      dest_account_id='admin@root',
                      asset_id='coin#test', description='ansfdlkbahkebfjhkbewajfjwevbdfjkaevwkgjfvkghaevwghfvhkgawevfghaevwjhfgawkfvgkhavwehfvaehjkwvfgevwkjfvgjkwaev', amount='10.00')
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


transfer_coin_from_admin_to_userone()
get_account_assets()
print('done')
