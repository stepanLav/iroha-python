from iroha import IrohaCrypto as ic, Iroha, IrohaGrpc
from google.protobuf.json_format import MessageToJson
import requests, sys

if len(sys.argv) != 3:
	print("Wrong argument numbers. Usage example: python3 sora_xor.py <accountId> <amount>")
	sys.exit(0)

accountId = sys.argv[1]
amount = sys.argv[2]

# xor@sora(Sora's backend as signatory)
key1priv = "34ca2f53c5a2ac9e6fad3e45a3a18bf26fbb053ed316620ce41684f94c672e18"
key1pub = "483666d8466927c5f14e6ac6a7fe62d549bf77260df0a62d404b02996eea5bf9"

# xor@sora(signatory 1)
key2priv = "e97d5792158fc339048e0057683b8f31d2fbb383179edee906dbf6f19ce426b1"
key2pub = "95fde424b9c12befd4f36219ca1d8c4ea39691c98a2cbcd88869c313d8e8fba0"

# xor@sora(signatory 2)
key3priv = "3a2ffadd4db9d5562b1767b702e6838e119c284de824066ea4a2e44da8357a53"
key3pub = "34733ddf85e053bb0e130b0f7d42447576403d31c4d9b8981b7d92e857a3764d"

# xor@sora(signatory 3)
key4priv = "c61dfcaa6d466661d5f4e0f7c5bd02b7e78cc670a6c220e7516a6f383773f441"
key4pub = "4c01249d5a4773a990f38792c46f6636bd0b371c33be1c7f55204a00f42a4112"

adminAccountId = "xor@sora"
assetId = "xor#sora"
brvsUrl = "https://brvs.s1.dev.soranet.soramitsu.co.jp/brvs/rest/transaction/send"  # TODO:found new possible way to send

iroha = Iroha(adminAccountId)

tx = iroha.transaction(
    [iroha.command(
        'TransferAsset',
        src_account_id=adminAccountId,
        dest_account_id=accountId,
        asset_id=assetId,
        description='Sended from python script',
        amount=amount
    )]
)

ic.sign_transaction(tx, key1priv)
ic.sign_transaction(tx, key2priv)
ic.sign_transaction(tx, key3priv)
ic.sign_transaction(tx, key4priv)

r = requests.post(brvsUrl, data=MessageToJson(tx))
print(r.status_code, r.reason)
print(r.text)