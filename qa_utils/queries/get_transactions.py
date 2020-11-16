
import os
import binascii
from iroha import IrohaCrypto
from iroha import Iroha, IrohaGrpc
from iroha.primitive_pb2 import can_set_my_account_detail
import sys

if sys.version_info[0] < 3:
    raise Exception('Python 3 or a more recent version is required.')


IROHA_HOST_ADDR = os.getenv('IROHA_HOST_ADDR', 'localhost')
IROHA_PORT = os.getenv('IROHA_PORT', '2346')
ADMIN_ACCOUNT_ID = 'admin@nbc'
ADMIN_PRIVATE_KEY = '72a9eb49c0cd469ed64f653e33ffc6dde475a6b9fd8be615086bce7c44b5a8f8'
iroha = Iroha(ADMIN_ACCOUNT_ID)
net = IrohaGrpc('{}:{}'.format(IROHA_HOST_ADDR, IROHA_PORT))
txs = ['e209af307d44ccef03f52538ab23c56d493e215bbc3d8593aeffe9beb5fa2ad7']

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
def get_account():
    query = IrohaCrypto.sign_query(
        Iroha(ADMIN_ACCOUNT_ID).query('GetTransactions', tx_hashes=txs),
        ADMIN_PRIVATE_KEY
    )
    IrohaCrypto.sign_query(query, ADMIN_PRIVATE_KEY)
    response = net.send_query(query)
    print(response)


get_account()