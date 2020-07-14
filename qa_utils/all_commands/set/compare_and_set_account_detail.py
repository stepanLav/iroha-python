#!/usr/bin/env python3
#

from iroha import IrohaCrypto
from extension import enviroment
from extension import extension

@extension.trace
def compare_and_set_account_detail():

    tx = enviroment.iroha.transaction([
        enviroment.iroha.command('CompareAndSetAccountDetail', account_id='user@test', key='One', value='Two',
                                 old_value='five')
    ], creator_account=enviroment.ADMIN_ACCOUNT_ID, quorum=1)

    IrohaCrypto.sign_transaction(tx, enviroment.ADMIN_PRIVATE_KEY)
    extension.send_transaction_and_print_status(tx)

compare_and_set_account_detail()