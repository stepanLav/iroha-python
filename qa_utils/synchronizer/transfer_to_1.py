#!/usr/bin/env python3
#
# Copyright Soramitsu Co., Ltd. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#

import os
import binascii
from iroha import IrohaCrypto
from iroha import Iroha, IrohaGrpc
import time
from iroha.primitive_pb2 import can_set_my_account_detail
import sys

if sys.version_info[0] < 3:
    raise Exception('Python 3 or a more recent version is required.')

IROHA_HOST_ADDR = os.getenv('IROHA_HOST_ADDR', '127.0.0.1')
IROHA_PORT = os.getenv('IROHA_PORT', '50051')
ADMIN_ACCOUNT_ID = os.getenv('ADMIN_ACCOUNT_ID', 'admin@test')
ADMIN_PRIVATE_KEY = os.getenv(
    'ADMIN_PRIVATE_KEY', 'f101537e319568c765b2cc89698325604991dca57b9716b58016b253506cab70')

user_private_key = IrohaCrypto.private_key()
user_public_key = IrohaCrypto.derive_public_key(user_private_key)
iroha = Iroha(ADMIN_ACCOUNT_ID)
net = IrohaGrpc('{}:{}'.format(IROHA_HOST_ADDR, IROHA_PORT))

f=0

def trace(func):
    def tracer(*args, **kwargs):
        count = 100

        while count:
            try:
                name = func.__name__
                print('\tEntering "{}"'.format(name))
                result = func(*args, **kwargs)
                print('\tLeaving "{}"'.format(name))
                return result
            except Exception as e:
                print('Error:', e)
                count -= 1
                time.sleep(1)
                transfer_coin_from_admin_to_userone()

    return tracer

@trace
def send_transaction_and_print_status(transaction):
    hex_hash = binascii.hexlify(IrohaCrypto.hash(transaction))
    print('Transaction hash = {}, creator = {}'.format(
        hex_hash, transaction.payload.reduced_payload.creator_account_id))
    net.send_tx(transaction)
    for status in net.tx_status_stream(transaction):
        print(status)


@trace
def transfer_coin_from_admin_to_userone():
    """
    Transfer 2.00 'coin#domain' from 'admin@test' to 'userone@domain'
    """
    tx = iroha.transaction([
        iroha.command('TransferAsset', src_account_id='admin@test', dest_account_id='test@test',
                asset_id='coin#test', description='init top up', amount='1.1'),
    ], creator_account=ADMIN_ACCOUNT_ID, quorum=1)

    IrohaCrypto.sign_transaction(tx, ADMIN_PRIVATE_KEY)
    send_transaction_and_print_status(tx)

@trace
def asset_transfer():
    global iroha
    init_cmds = [
        iroha.command('AddAssetQuantity',
                      asset_id='coin#test', amount='3.10'),
        iroha.command('TransferAsset', src_account_id='admin@test', dest_account_id='test@test',
                      asset_id='coin#test', description='init top up', amount='2'),
    ]
    init_tx = iroha.transaction(init_cmds)
    IrohaCrypto.sign_transaction(init_tx, ADMIN_PRIVATE_KEY)
    send_transaction_and_print_status(init_tx)


@trace
def get_coin_info():
    """
    Get asset info for coin#domain
    :return:
    """
    query = iroha.query('GetAssetInfo', asset_id='coin#test')
    IrohaCrypto.sign_query(query, ADMIN_PRIVATE_KEY)

    response = net.send_query(query)
    data = response.asset_response.asset
    print('Asset id = {}, precision = {}'.format(data.asset_id, data.precision))
    bytes = ('\n\x0e\x63ommands.proto\x12\x0eiroha.protocol\x1a\x0fprimitive.proto\"4\n\x10\x41\x64\x64\x41ssetQuantity\x12\x10\n\x08\x61sset_id\x18\x01 \x01(\t\x12\x0e\n\x06\x61mount\x18\x02 \x01(\t\"-\n\x07\x41\x64\x64Peer\x12\"\n\x04peer\x18\x01 \x01(\x0b\x32\x14.iroha.protocol.Peer\"6\n\x0c\x41\x64\x64Signatory\x12\x12\n\naccount_id\x18\x01 \x01(\t\x12\x12\n\npublic_key\x18\x02 \x01(\t\"G\n\x0b\x43reateAsset\x12\x12\n\nasset_name\x18\x01 \x01(\t\x12\x11\n\tdomain_id\x18\x02 \x01(\t\x12\x11\n\tprecision\x18\x03 \x01(\r\"L\n\rCreateAccount\x12\x14\n\x0c\x61\x63\x63ount_name\x18\x01 \x01(\t\x12\x11\n\tdomain_id\x18\x02 \x01(\t\x12\x12\n\npublic_key\x18\x03 \x01(\t\"B\n\x10SetAccountDetail\x12\x12\n\naccount_id\x18\x01 \x01(\t\x12\x0b\n\x03key\x18\x02 \x01(\t\x12\r\n\x05value\x18\x03 \x01(\t\"7\n\x0c\x43reateDomain\x12\x11\n\tdomain_id\x18\x01 \x01(\t\x12\x14\n\x0c\x64\x65\x66\x61ult_role\x18\x02 \x01(\t\"9\n\x0fRemoveSignatory\x12\x12\n\naccount_id\x18\x01 \x01(\t\x12\x12\n\npublic_key\x18\x02 \x01(\t\"6\n\x10SetAccountQuorum\x12\x12\n\naccount_id\x18\x01 \x01(\t\x12\x0e\n\x06quorum\x18\x02 \x01(\r\"w\n\rTransferAsset\x12\x16\n\x0esrc_account_id\x18\x01 \x01(\t\x12\x17\n\x0f\x64\x65st_account_id\x18\x02 \x01(\t\x12\x10\n\x08\x61sset_id\x18\x03 \x01(\t\x12\x13\n\x0b\x64\x65scription\x18\x04 \x01(\t\x12\x0e\n\x06\x61mount\x18\x05 \x01(\t\"3\n\nAppendRole\x12\x12\n\naccount_id\x18\x01 \x01(\t\x12\x11\n\trole_name\x18\x02 \x01(\t\"3\n\nDetachRole\x12\x12\n\naccount_id\x18\x01 \x01(\t\x12\x11\n\trole_name\x18\x02 \x01(\t\"T\n\nCreateRole\x12\x11\n\trole_name\x18\x01 \x01(\t\x12\x33\n\x0bpermissions\x18\x02 \x03(\x0e\x32\x1e.iroha.protocol.RolePermission\"^\n\x0fGrantPermission\x12\x12\n\naccount_id\x18\x01 \x01(\t\x12\x37\n\npermission\x18\x02 \x01(\x0e\x32#.iroha.protocol.GrantablePermission\"_\n\x10RevokePermission\x12\x12\n\naccount_id\x18\x01 \x01(\t\x12\x37\n\npermission\x18\x02 \x01(\x0e\x32#.iroha.protocol.GrantablePermission\"9\n\x15SubtractAssetQuantity\x12\x10\n\x08\x61sset_id\x18\x01 \x01(\t\x12\x0e\n\x06\x61mount\x18\x02 \x01(\t\"\xb2\x07\n\x07\x43ommand\x12>\n\x12\x61\x64\x64_asset_quantity\x18\x01 \x01(\x0b\x32 .iroha.protocol.AddAssetQuantityH\x00\x12+\n\x08\x61\x64\x64_peer\x18\x02 \x01(\x0b\x32\x17.iroha.protocol.AddPeerH\x00\x12\x35\n\radd_signatory\x18\x03 \x01(\x0b\x32\x1c.iroha.protocol.AddSignatoryH\x00\x12\x31\n\x0b\x61ppend_role\x18\x04 \x01(\x0b\x32\x1a.iroha.protocol.AppendRoleH\x00\x12\x37\n\x0e\x63reate_account\x18\x05 \x01(\x0b\x32\x1d.iroha.protocol.CreateAccountH\x00\x12\x33\n\x0c\x63reate_asset\x18\x06 \x01(\x0b\x32\x1b.iroha.protocol.CreateAssetH\x00\x12\x35\n\rcreate_domain\x18\x07 \x01(\x0b\x32\x1c.iroha.protocol.CreateDomainH\x00\x12\x31\n\x0b\x63reate_role\x18\x08 \x01(\x0b\x32\x1a.iroha.protocol.CreateRoleH\x00\x12\x31\n\x0b\x64\x65tach_role\x18\t \x01(\x0b\x32\x1a.iroha.protocol.DetachRoleH\x00\x12;\n\x10grant_permission\x18\n \x01(\x0b\x32\x1f.iroha.protocol.GrantPermissionH\x00\x12;\n\x10remove_signatory\x18\x0b \x01(\x0b\x32\x1f.iroha.protocol.RemoveSignatoryH\x00\x12=\n\x11revoke_permission\x18\x0c \x01(\x0b\x32 .iroha.protocol.RevokePermissionH\x00\x12>\n\x12set_account_detail\x18\r \x01(\x0b\x32 .iroha.protocol.SetAccountDetailH\x00\x12>\n\x12set_account_quorum\x18\x0e \x01(\x0b\x32 .iroha.protocol.SetAccountQuorumH\x00\x12H\n\x17subtract_asset_quantity\x18\x0f \x01(\x0b\x32%.iroha.protocol.SubtractAssetQuantityH\x00\x12\x37\n\x0etransfer_asset\x18\x10 \x01(\x0b\x32\x1d.iroha.protocol.TransferAssetH\x00\x42\t\n\x07\x63ommandb\x06proto3')
    hexty = binascii.unhexlify(bytes)
    print(hexty)


while f<=990:
    transfer_coin_from_admin_to_userone()
    asset_transfer()
    get_coin_info()
    f+=1
    print(f)
    print('=============================================================')

print('done')