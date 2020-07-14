#!/usr/bin/env python3
#
import binascii

from iroha import IrohaCrypto, ed25519_sha2
from iroha import Iroha, IrohaGrpc
from extension import enviroment
from extension import extension

account_name = 'mst_account5@test'
account_private_keys = [
    'aa6369985c4decf7f81d2ff8d44663a3175e68bd35b9ee810bba6763ee4c562e53abb2f4c98a20379f74f1f3af055abf9d6f5d105d416af5a470007592a44718',
    '718e89b7847018aa269541f2b8492fd983324ff5de590cd966cdda37c6998a7f'
]
account_pk = ed25519_sha2.SigningKey(binascii.unhexlify(account_private_keys[0]))
account_pk2 = ed25519_sha2.SigningKey(binascii.unhexlify(account_private_keys[1]))
net = IrohaGrpc('{}:{}'.format(enviroment.IROHA_HOST_ADDR, enviroment.IROHA_PORT))

@extension.trace
def transfer_asset():
    tx = enviroment.iroha.transaction([
        enviroment.iroha.command('RemovePeer', public_key='b78cc625609d0ac6759173b794421d81ab73593194b6d596a6d04627a59e13ba')
    ], creator_account=account_name, quorum=1)

    IrohaCrypto.sign_transaction(tx, account_private_keys[1])
    extension.send_transaction_and_print_status(tx)


transfer_asset()
