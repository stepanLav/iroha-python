#!/usr/bin/env python3
#
# Copyright Soramitsu Co., Ltd. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#
import json
import os
import binascii
from time import sleep

from iroha import IrohaCrypto
from iroha import Iroha, IrohaGrpc
import sys

if sys.version_info[0] < 3:
    raise Exception('Python 3 or a more recent version is required.')

IROHA_HOST_ADDR = os.getenv('IROHA_HOST_ADDR', 'localhost')
IROHA_PORT = os.getenv('IROHA_PORT', '50051')
ADMIN_ACCOUNT_ID = 'root@root'
ADMIN_PRIVATE_KEY = '7a1cb487ed17a60efbf4aa21df74bb391fcc2260f87c83eb7de9c120d2112ec7'
iroha = Iroha(ADMIN_ACCOUNT_ID)
net = IrohaGrpc('{}:{}'.format(IROHA_HOST_ADDR, IROHA_PORT))
hex_hash = ''
test_contract = 'BC7209D9E088755AE39F01D0568CDCF2A020B4D5'
query_contract = 'E98FD509BF522680E28CF280CBE1055EF31FEC37'
transfer_contract = '0672C49DF5BC65613B1267B035868A3E2521605B'

transfer_amount = '2cddc411000000000000000000000000000000000000000000000000000000000000008000000000000000000000000000000000000000000000000000000000000000c000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000140000000000000000000000000000000000000000000000000000000000000000a61646d696e40726f6f7400000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000a61646d696e4074657374000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000009636f696e2374657374000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000023130000000000000000000000000000000000000000000000000000000000000'
'''
transfer, func transferAsset(string memory src, string memory dst,
                            string memory asset, string memory amount)
src=admin@root, dst=admin@test, asset=coin#test, amount=10
'''
query_balance = '2c74aaaf00000000000000000000000000000000000000000000000000000000000000400000000000000000000000000000000000000000000000000000000000000080000000000000000000000000000000000000000000000000000000000000000a61646d696e40726f6f74000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000009636f696e23746573740000000000000000000000000000000000000000000000'
'''
query_balance, func queryBalance(string memory _account, string memory _asset) public 
                    returns (bytes memory result)
_account="admin@root, _asset=coin#test
'''

mint_test_contract = '40c10f1900000000000000000000000000000000000000000000000000000002afdde5c50000000000000000000000000000000000000000000000000000000000002710'
'''
mint(admin@root, 10000)
'''

balance_test_contract = '27e235e300000000000000000000000000000000000000000000000000000002afdde5c5'
'''
balance(admin@root)
'''

send_test_contract = 'd0679d3400000000000000000000000000000000000000000000000000000002afdde5c50000000000000000000000000000000000000000000000000000000000000001'
'''
send(admin@test, 10)
'''


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
def call_engine():
    tx = iroha.transaction([
        iroha.command('CallEngine', caller=ADMIN_ACCOUNT_ID,
                      callee=test_contract,
                      input=query_balance)
    ])
    IrohaCrypto.sign_transaction(tx, ADMIN_PRIVATE_KEY)
    send_transaction_and_print_status(tx)


@trace
def getEngineReceipts():
    query = iroha.query('GetEngineReceipts', tx_hash=hex_hash)
    IrohaCrypto.sign_query(query, ADMIN_PRIVATE_KEY)
    response = net.send_query(query)
    print(response)


call_engine()
sleep(4)
getEngineReceipts()
