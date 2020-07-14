#!/usr/bin/env python3
#

from iroha import IrohaCrypto
from extension import enviroment
from extension import extension

@extension.trace
def set_account_quorum():

    tx = enviroment.iroha.transaction([
        enviroment.iroha.command('CreateRole', role_name='user', default_role=enviroment.permission)
    ], creator_account=enviroment.ADMIN_ACCOUNT_ID, quorum=1)

    IrohaCrypto.sign_transaction(tx, enviroment.ADMIN_PRIVATE_KEY)
    extension.send_transaction_and_print_status(tx)

set_account_quorum()