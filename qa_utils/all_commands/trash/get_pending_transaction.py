import os
import binascii

from iroha import IrohaCrypto
from iroha import Iroha, IrohaGrpc
import sys

if sys.version_info[0] < 3:
    raise Exception('Python 3 or a more recent version is required.')

IROHA_HOST_ADDR = os.getenv('IROHA_HOST_ADDR', '127.0.0.1')
IROHA_PORT = os.getenv('IROHA_PORT', '2345')
ADMIN_ACCOUNT_ID = os.getenv('ADMIN_ACCOUNT_ID', 'alice@test')
ADMIN_PRIVATE_KEY = os.getenv(
    'ADMIN_PRIVATE_KEY', '51cec58ded55857ff908d4f205abe940aa5f20786753ec60ad56ed0db3d27048')
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
def get_info_pending_block():
    q = IrohaCrypto.sign_query(Iroha(ADMIN_ACCOUNT_ID).query('GetPendingTransactions'),
                               ADMIN_PRIVATE_KEY)

    response = net.send_query(q)
    for tx in response.transactions_response.transactions:
        if tx.payload.reduced_payload.creator_account_id == 'alice@test':
            print(tx)
        else:
            del tx.signatures[:]

i = 0
while i < 10000:
    get_info_pending_block()
    i += 1
