import os
import binascii

from iroha import IrohaCrypto, primitive_pb2
from iroha import Iroha, IrohaGrpc
from iroha.primitive_pb2 import can_set_my_account_detail, Peer
import sys

if sys.version_info[0] < 3:
    raise Exception('Python 3 or a more recent version is required.')

IROHA_HOST_ADDR = os.getenv('IROHA_HOST_ADDR', '127.0.0.1')
IROHA_PORT = os.getenv('IROHA_PORT', '50052')
ADMIN_ACCOUNT_ID = os.getenv('ADMIN_ACCOUNT_ID', 'admin@test')
ADMIN_PRIVATE_KEY = os.getenv(
    'ADMIN_PRIVATE_KEY', 'f101537e319568c765b2cc89698325604991dca57b9716b58016b253506cab70')

user_private_key = IrohaCrypto.private_key()
user_public_key = IrohaCrypto.derive_public_key(user_private_key)
iroha = Iroha(ADMIN_ACCOUNT_ID)
net = IrohaGrpc('{}:{}'.format(IROHA_HOST_ADDR, IROHA_PORT))
peer1 = primitive_pb2.Peer()
peer1.address = '127.0.0.1:10001'
peer1.peer_key = 'bddd58404d1315e0eb27902c5d7c8eb0602c16238f005773df406bc191308929'
peer2 = primitive_pb2.Peer()
peer2.address = '127.0.0.1:10002'
peer2.peer_key = '313a07e6384776ed95447710d15e59148473ccfc052a681317a72a69f2a49910'
peer3 = primitive_pb2.Peer()
peer3.address = '127.0.0.1:10003'
peer3.peer_key = '716fe505f69f18511a1b083915aa9ff73ef36e6688199f3959750db38b8f4bfc'

alice_private_keys = [
    'f101537e319568c765b2cc89698325604991dca57b9716b58016b253506caba1',
    'f101537e319568c765b2cc89698325604991dca57b9716b58016b253506caba2'
]
alice_public_keys = [IrohaCrypto.derive_public_key(x) for x in alice_private_keys]

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
def add_peer():
    """
    add peer in iroha
    """
    tx = iroha.transaction([
        iroha.command('AddPeer', peer=peer1)
    ], creator_account=ADMIN_ACCOUNT_ID, quorum=1)

    IrohaCrypto.sign_transaction(tx, ADMIN_PRIVATE_KEY)
    send_transaction_and_print_status(tx)

@trace
def alice_accepts_add_peer_request():
    global net
    q = IrohaCrypto.sign_query(
        Iroha('alice@test').query('GetPendingTransactions'),
        alice_private_keys[0]
    )
    pending_transactions = net.send_query(q)
    for tx in pending_transactions.transactions_response.transactions:
        IrohaCrypto.sign_transaction(tx, *alice_private_keys)
    send_batch_and_print_status(
        pending_transactions.transactions_response.transactions)

add_peer()
alice_accepts_add_peer_request()
