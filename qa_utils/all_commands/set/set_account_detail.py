#!/usr/bin/env python3
#

from iroha import IrohaCrypto
from extension import enviroment
from extension import extension


@extension.trace
def set_account_detail():

    tx = enviroment.iroha.transaction([
        enviroment.iroha.command('SetAccountDetail', account_id='exchange_billing@sora', key="xor__sora", value="FIXED__0.2")
    ])
    IrohaCrypto.sign_transaction(tx, enviroment.ADMIN_PRIVATE_KEY)

    extension.send_transaction_and_print_status(tx)

set_account_detail()
