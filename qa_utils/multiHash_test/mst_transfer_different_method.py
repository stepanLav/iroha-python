#!/usr/bin/env python3
#
import binascii
import os

from iroha import IrohaCrypto, ed25519_sha2
from iroha import Iroha, IrohaGrpc

account_name = 'mst_account@test'
IROHA_HOST_ADDR = os.getenv('IROHA_HOST_ADDR', 'localhost')
IROHA_PORT = os.getenv('IROHA_PORT', '50051')
ADMIN_ACCOUNT_ID = os.getenv('ADMIN_ACCOUNT_ID', account_name)
ADMIN_PRIVATE_KEY = '51cec58ded55857ff908d4f205abe940aa5f20786753ec60ad56ed0db3d27048'
ADMIN_PRIVATE_BIN = binascii.unhexlify(ADMIN_PRIVATE_KEY)
account_private_keys = [
    'aa6369985c4decf7f81d2ff8d44663a3175e68bd35b9ee810bba6763ee4c562e',
    '7bab70e95cb585ea052c3aeb27de0afa9897ba5746276aa1c25310383216ceb8'
]
account_pk = ed25519_sha2.SigningKey(binascii.unhexlify(account_private_keys[0]))
account_pk2 = ed25519_sha2.SigningKey(binascii.unhexlify(account_private_keys[1]))
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
def transfer_asset():
    tx = iroha.transaction([
        iroha.command('TransferAsset', src_account_id=account_name, dest_account_id='alice@test',
                                 asset_id='coin#test', description='init top up', amount='10')
    ], creator_account=account_name, quorum=2)

    IrohaCrypto.sign_transaction(tx, account_pk)
    send_transaction_and_print_status(tx)


@trace
def bob_accepts_exchange_request():
    global net
    q = IrohaCrypto.sign_query(
        Iroha(account_name).query('GetPendingTransactions'),
        account_pk
    )
    pending_transactions = net.send_query(q)
    for tx in pending_transactions.transactions_response.transactions:
        if tx.payload.reduced_payload.creator_account_id == account_name:
            IrohaCrypto.sign_transaction(tx, account_pk2)
        else:
            del tx.signatures[:]
    send_batch_and_print_status(
        pending_transactions.transactions_response.transactions)


transfer_asset()
bob_accepts_exchange_request()
