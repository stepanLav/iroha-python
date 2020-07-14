#!/usr/bin/env python3
#
import os
from iroha import IrohaCrypto, primitive_pb2
from extension import enviroment
from extension import extension

ADMIN_ACCOUNT_ID = os.getenv('ADMIN_ACCOUNT_ID', 'admin@test')
ADMIN_PRIVATE_KEY = 'f101537e319568c765b2cc89698325604991dca57b9716b58016b253506cab70'


@extension.trace
def add_peer():
    peer4 = primitive_pb2.Peer()
    peer4.address = '127.0.0.1:10004'
    peer4.peer_key = '4b66488f8d745930334efe15ed4879642cfd493bae302f7833d6564ba3edaea9'
    tx = enviroment.iroha.transaction([
        enviroment.iroha.command('AddPeer', peer=peer4)
    ], creator_account=ADMIN_ACCOUNT_ID, quorum=1)

    IrohaCrypto.sign_transaction(tx, ADMIN_PRIVATE_KEY)
    extension.send_transaction_and_print_status(tx)


add_peer()
