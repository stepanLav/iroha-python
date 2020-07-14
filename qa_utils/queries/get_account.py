#!/usr/bin/env python3
#

from iroha import IrohaCrypto
from extension import enviroment
from extension import extension

@extension.trace
def get_account():
    q = IrohaCrypto.sign_query(
        enviroment.Iroha('bob@test').query('GetPendingTransactions'),
        enviroment.ADMIN_PRIVATE_KEY
    )
    pending_transactions = extension.net.send_query(q)
    for tx in pending_transactions.transactions_response.transactions:
        if tx.payload.reduced_payload.creator_account_id == 'alice@test':
            # we need do this temporarily, otherwise accept will not reach MST engine
            del tx.signatures[:]
        else:
            # intentionally alice keys were used to fail bob's txs
            IrohaCrypto.sign_transaction(tx, *enviroment.ADMIN_PRIVATE_KEY)
            # zeroes as private keys are also acceptable
    extension.send_batch_and_print_status(
        pending_transactions.transactions_response.transactions)

get_account()