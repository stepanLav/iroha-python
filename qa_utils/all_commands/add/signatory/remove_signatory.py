#!/usr/bin/env python3
#

from iroha import IrohaCrypto
from extension import enviroment
from extension import extension

@extension.trace
def remove_signatory():

    tx = enviroment.iroha.transaction([
        enviroment.iroha.command('RemoveSignatory', account_id='user@test', public_key="716fe505f69f18511a1b083915aa9ff73ef36e6688199f3959750db38b8f4bfc")
    ], creator_account=enviroment.ADMIN_ACCOUNT_ID, quorum=1)

    IrohaCrypto.sign_transaction(tx, enviroment.ADMIN_PRIVATE_KEY)
    extension.send_transaction_and_print_status(tx)

remove_signatory()