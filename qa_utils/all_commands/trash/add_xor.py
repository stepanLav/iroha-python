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


IROHA_HOST_ADDR = os.getenv('IROHA_HOST_ADDR', 'localhost')
IROHA_PORT = os.getenv('IROHA_PORT', '2345')
ADMIN_ACCOUNT_ID = 'superuser@sora'
ADMIN_PRIVATE_KEY = "3B102A3F22A24EA1F3C9CCB0A237EC268955F099154F92CEC20B0474690AC58C"

user_private_key = IrohaCrypto.private_key()
user_public_key = IrohaCrypto.derive_public_key(user_private_key)
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
def send_batch_and_print_status(transactions):
    global net
    net.send_txs(transactions)
    for tx in transactions:
        hex_hash = binascii.hexlify(IrohaCrypto.hash(tx))
        print('\t' + '-' * 20)
        print('Transaction hash = {}, creator = {}'.format(
            hex_hash, tx.payload.reduced_payload.creator_account_id))
        for status in net.tx_status_stream(tx):
            print(status)


@trace
def transfer_coin_from_admin_to_userone():
    """
    Need set quorum 2
    """
    tx = iroha.transaction([
        iroha.command('TransferAsset', src_account_id='superuser@sora',
                      dest_account_id='did_sora_b1e53fe1b6d0ef49b877@sora',
                      asset_id='xor#sora', description='', amount='1000000.00')
    ])
    IrohaCrypto.sign_transaction(tx, ADMIN_PRIVATE_KEY)
    send_transaction_and_print_status(tx)

@trace
def get_account_assets():
        """
        List all the assets of userone@domain
        """
        query = iroha.query('GetAccountAssets', account_id='did_sora_f03f140f5174dc19d8f9@sora')
        IrohaCrypto.sign_query(query, ADMIN_PRIVATE_KEY)

        response = net.send_query(query)
        data = response.account_assets_response.account_assets
        for asset in data:
            print('Asset id = {}, balance = {}'.format(
                asset.asset_id, asset.balance))


transfer_coin_from_admin_to_userone()
get_account_assets()
print('done')
