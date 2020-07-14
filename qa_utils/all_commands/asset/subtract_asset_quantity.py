#!/usr/bin/env python3
#

from iroha import IrohaCrypto
from extension import enviroment
from extension import extension

@extension.trace
def subtract_asset_quantity():

    tx = enviroment.iroha.transaction([
        enviroment.iroha.command('SubtractAssetQuantity', asset_id='coin#test', amount='2')
    ], creator_account=enviroment.ADMIN_ACCOUNT_ID, quorum=1)

    IrohaCrypto.sign_transaction(tx, enviroment.ADMIN_KEY)
    extension.send_transaction_and_print_status(tx)

subtract_asset_quantity()