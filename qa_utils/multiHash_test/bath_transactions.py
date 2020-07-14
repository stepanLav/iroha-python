#!/usr/bin/env python3
#
import binascii

from iroha import IrohaCrypto, ed25519_sha2
from iroha import Iroha, IrohaGrpc
from extension import enviroment
from extension import extension

account_name = 'mst_account@test'
account_private_keys = [
    'aa6369985c4decf7f81d2ff8d44663a3175e68bd35b9ee810bba6763ee4c562e53abb2f4c98a20379f74f1f3af055abf9d6f5d105d416af5a470007592a44718',
]
account_pk = ed25519_sha2.SigningKey(binascii.unhexlify(account_private_keys[0]))
net = IrohaGrpc('{}:{}'.format(enviroment.IROHA_HOST_ADDR, enviroment.IROHA_PORT))
iroha = Iroha(account_name)

@extension.trace
def transfer_asset():
    commands = [
        iroha.command('TransferAsset', src_account_id=account_name, dest_account_id='admin@test',
                asset_id='coin#test', description='init top up', amount='10'),
        iroha.command('TransferAsset', src_account_id=account_name, dest_account_id='admin@test',
                asset_id='coin#test', description='init top up', amount='0.10'),
        iroha.command('TransferAsset', src_account_id=account_name, dest_account_id='admin@test',
                      asset_id='coin#test', description='init top up', amount='10')
    ]
    tx = IrohaCrypto.sign_transaction(
        iroha.transaction(commands, quorum=1), account_pk)
    extension.send_transaction_and_print_status(tx)


transfer_asset()
