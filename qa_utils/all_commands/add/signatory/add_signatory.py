#!/usr/bin/env python3
#

from iroha import IrohaCrypto
from extension import enviroment
from extension import extension

@extension.trace
def add_signatory():

    tx = enviroment.iroha.transaction([
        enviroment.iroha.command('AddSignatory', account_id='admin@test', public_key='313a07e6384776ed95447710d15e59148473ccfc052a681317a72a69f2a49910')
    ], creator_account=enviroment.ADMIN_ACCOUNT_ID, quorum=1)

    IrohaCrypto.sign_transaction(tx, enviroment.ADMIN_PRIVATE_KEY)
    extension.send_transaction_and_print_status(tx)

add_signatory()