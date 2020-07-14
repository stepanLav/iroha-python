#!/usr/bin/env python3
#

from iroha import IrohaCrypto
from extension import enviroment
from extension import extension

@extension.trace
def revoke_permission():

    tx = enviroment.iroha.transaction([
        enviroment.iroha.command('RevokePermission', account_id='user@test', permission=enviroment.permission)
    ], creator_account=enviroment.ADMIN_ACCOUNT_ID, quorum=1)

    IrohaCrypto.sign_transaction(tx, enviroment.ADMIN_PRIVATE_KEY)
    extension.send_transaction_and_print_status(tx)

revoke_permission()