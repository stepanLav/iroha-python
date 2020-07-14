import os
import binascii

from iroha import IrohaCrypto, ed25519_sha2
from iroha import Iroha, IrohaGrpc
from iroha.primitive_pb2 import can_set_my_account_detail, Peer
import sys

if sys.version_info[0] < 3:
    raise Exception('Python 3 or a more recent version is required.')

IROHA_HOST_ADDR = os.getenv('IROHA_HOST_ADDR', 's1.tst2.iroha.tech')
IROHA_PORT = os.getenv('IROHA_PORT', '50051')
ADMIN_ACCOUNT_ID = os.getenv('ADMIN_ACCOUNT_ID', 'alice@test')
ADMIN_PRIVATE_KEY = '0a230371f78507d9809a2ba1e349d98cd8022d94fc6f57857f8861c5794f7d39'
ADMIN_PRIVATE_BIN = binascii.unhexlify(ADMIN_PRIVATE_KEY)
iroha = Iroha(ADMIN_ACCOUNT_ID)
net = IrohaGrpc('{}:{}'.format(IROHA_HOST_ADDR, IROHA_PORT))
account_private_keys = [
    'aa6369985c4decf7f81d2ff8d44663a3175e68bd35b9ee810bba6763ee4c562e53abb2f4c98a20379f74f1f3af055abf9d6f5d105d416af5a470007592a44718',
    '7bab70e95cb585ea052c3aeb27de0afa9897ba5746276aa1c25310383216ceb860eb82baacbc940e710a40f21f962a3651013b90c23ece31606752f298c38d90'
]
account_public_key = ['53abb2f4c98a20379f74f1f3af055abf9d6f5d105d416af5a470007592a44718',
                      '60eb82baacbc940e710a40f21f962a3651013b90c23ece31606752f298c38d90']
account_name = 'mst_account4'
domain_id = 'test'
account_with_domain = account_name+'@'+domain_id
account_pk = ed25519_sha2.SigningKey(binascii.unhexlify(account_private_keys[0]))

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
        iroha.command('CreateAccount', account_name=account_name, domain_id=domain_id,
                      public_key="ed0120"+account_public_key[0]),
        iroha.command('TransferAsset', src_account_id='alice@test', dest_account_id=account_with_domain,
                asset_id='coin#test', description='init top up', amount='10000')])
    IrohaCrypto.sign_transaction(tx, ADMIN_PRIVATE_KEY)
    send_transaction_and_print_status(tx)

@trace
def add_keys_and_set_quorum():
    alice_iroha = Iroha(account_with_domain)
    alice_cmds = [
        alice_iroha.command('AddSignatory', account_id=account_with_domain,
                            public_key="ed0120"+account_public_key[1]),
        alice_iroha.command('SetAccountQuorum',
                            account_id=account_with_domain, quorum=2)
    ]
    alice_tx = alice_iroha.transaction(alice_cmds)
    IrohaCrypto.sign_transaction(alice_tx, account_pk)
    send_transaction_and_print_status(alice_tx)


print(account_public_key)
create_account()
add_keys_and_set_quorum()
