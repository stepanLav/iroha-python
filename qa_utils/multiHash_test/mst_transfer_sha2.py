#!/usr/bin/env python3
#
import binascii

from iroha import IrohaCrypto, ed25519_sha2
from iroha import Iroha, IrohaGrpc
from extension import enviroment
from extension import extension

account_name = 'mst_account4@test'
account_private_keys = [
    'aa6369985c4decf7f81d2ff8d44663a3175e68bd35b9ee810bba6763ee4c562e53abb2f4c98a20379f74f1f3af055abf9d6f5d105d416af5a470007592a44718',
    '7bab70e95cb585ea052c3aeb27de0afa9897ba5746276aa1c25310383216ceb860eb82baacbc940e710a40f21f962a3651013b90c23ece31606752f298c38d90'
]
account_pk = ed25519_sha2.SigningKey(binascii.unhexlify(account_private_keys[0]))
account_pk2 = ed25519_sha2.SigningKey(binascii.unhexlify(account_private_keys[1]))
net = IrohaGrpc('{}:{}'.format(enviroment.IROHA_HOST_ADDR, enviroment.IROHA_PORT))

@extension.trace
def transfer_asset():
    tx = enviroment.iroha.transaction([
        enviroment.iroha.command('TransferAsset', src_account_id=account_name, dest_account_id='admin@test',
                                 asset_id='coin#test', description='init top up', amount='10')
    ], creator_account=account_name, quorum=2)

    IrohaCrypto.sign_transaction(tx, account_pk)
    extension.send_transaction_and_print_status(tx)


@extension.trace
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
    extension.send_batch_and_print_status(
        pending_transactions.transactions_response.transactions)


transfer_asset()
bob_accepts_exchange_request()
