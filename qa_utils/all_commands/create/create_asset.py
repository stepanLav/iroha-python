#!/usr/bin/env python3
#

from iroha import IrohaCrypto
from extension import enviroment
from extension import extension
import sys
from iroha import Iroha, primitive_pb2


if sys.version_info[0] < 3:
    raise Exception('Python 3 or a more recent version is required.')

iroha = Iroha('admin@test')

@extension.trace
def create_asset():
    commands = [
        enviroment.iroha.command('CreateDomain', domain_id='domain', default_role='user'),
        enviroment.iroha.command('CreateAsset', asset_name='coin',
                      domain_id='domain', precision=2)
    ]
    tx = IrohaCrypto.sign_transaction(
        enviroment.iroha.transaction(commands), enviroment.ADMIN_PRIVATE_KEY)
    extension.send_transaction_and_print_status(tx)


create_asset()
