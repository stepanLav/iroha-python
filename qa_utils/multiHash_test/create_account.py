import os
import binascii

from iroha import IrohaCrypto
from iroha import Iroha, IrohaGrpc
from iroha.primitive_pb2 import can_set_my_account_detail, Peer
import sys

if sys.version_info[0] < 3:
    raise Exception('Python 3 or a more recent version is required.')

IROHA_HOST_ADDR = os.getenv('IROHA_HOST_ADDR', 'localhost')
IROHA_PORT = os.getenv('IROHA_PORT', '50051')
ADMIN_ACCOUNT_ID = os.getenv('ADMIN_ACCOUNT_ID', 'alice@test')
ADMIN_PRIVATE_KEY = os.getenv(
    'ADMIN_PRIVATE_KEY', '51cec58ded55857ff908d4f205abe940aa5f20786753ec60ad56ed0db3d27048')

user_private_key = IrohaCrypto.private_key()
user_public_key = IrohaCrypto.derive_public_key(user_private_key)
iroha = Iroha(ADMIN_ACCOUNT_ID)
net = IrohaGrpc('{}:{}'.format(IROHA_HOST_ADDR, IROHA_PORT))
alice_private_keys = [
    'a9b588e7b07ee23d96b9e2480cefefde1b9274ffff01d91cfaea543a3b834a14e26d0543942dd602c95e0d98926c25b0089d7c39f08a40ab58f2d33431393c40'
]
alice_public_key = '12209f6f97df18cb5512a0f5f62d15670d32e48b46d1066b947bba20ceffe430b3d2'

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
def create_account():

    tx = iroha.transaction([
        iroha.command('CreateAccount', account_name='generatepub2', domain_id='test',
                      public_key=alice_public_key),
        iroha.command('TransferAsset', src_account_id='alice@test', dest_account_id='generatepub2@test',
                asset_id='coin#test', description='init top up', amount='10000')])
    IrohaCrypto.sign_transaction(tx, ADMIN_PRIVATE_KEY)
    send_transaction_and_print_status(tx)


print(alice_public_key)
create_account()
