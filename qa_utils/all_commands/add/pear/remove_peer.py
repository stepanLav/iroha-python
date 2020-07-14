#!/usr/bin/env python3
#

from iroha import IrohaCrypto
from extension import enviroment
from extension import extension

@extension.trace
def remove_peer():

    tx = enviroment.iroha.transaction([
        enviroment.iroha.command('RemovePeer', public_key='18310750cb28a63fd24bb0967ecd66aaa47a219df7a0b7308307d2053ce99d4a')
    ], creator_account=enviroment.ADMIN_ACCOUNT_ID, quorum=1)

    IrohaCrypto.sign_transaction(tx, enviroment.ADMIN_PRIVATE_KEY)
    extension.send_transaction_and_print_status(tx)

remove_peer()