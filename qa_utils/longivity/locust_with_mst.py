import os
import time
import binascii

from locust import Locust, TaskSet, events, task

import grpc.experimental.gevent as grpc_gevent

grpc_gevent.init_gevent()

import grpc, random
from iroha import Iroha, IrohaGrpc
from iroha import IrohaCrypto as ic
import iroha
import write

import random
import gevent
import threading
import _thread

HOSTNAME = os.environ['HOSTNAME']
ADMIN_PRIVATE_KEY = '4985f7499aa8e9841100fe41499a4e8f44c501b20afcf29be62ef5053ed89a1c'
MST_PRIVATE_KEYS = [
    '28271e1149882ad4a625357c650723791e9cdcc908c828ffac468f3d88aa2ed3',
    '6dc3ae1062f650498ff2104b522de3f98105bdaa82c3546cc5c039d1b84be4cd',
    '948ed3e42c1776b2c2da3a4eaf5167df6bc31ade3061bf3a47f72efde7a48173'
]

TXS = dict()  # hash -> sent time
COMMITTED = set()
SENT = set()
BLOCKS = set()
SENT_AM = dict()  # hash -> desc

MST_TXS = dict()
MST_COMMITTED = set()
MST_SENT = set()
MST_BLOCKS = set()
MST_SENT_AM = dict()  # hash -> desc

LISTENING = False
DEPOSITED = False

MST_LISTENING = False
MST_DEPOSITED = False

DEPOSIT_AMOUNT = 100000000000.00
TRANSFER_AMOUNT = 0.01
TRANSACTION_COUNTER = 0
MST_TRANSACTION_COUNTER = 0

def ascii_hash(tx):
    return binascii.hexlify(ic.hash(tx)).decode('ascii')


class IrohaClient(IrohaGrpc):
    """
    Simple, sample Iroha gRPC client implementation that wraps IrohaGrpc and
    fires locust events on request_success and request_failure, so that all requests
    gets tracked in locust's statistics.
    """

    def await_status(self, transaction, start_time):
        """
        Wait for the final status to be reported in status stream
        :param transaction: protobuf Transaction
        :param start_time: time when transaction was sent
        :return: None
        """
        hex_hash = binascii.hexlify(ic.hash(transaction))
        try:
            tx_status = 'NOT_RECEIVED'
            while tx_status not in ['COMMITTED', 'REJECTED']:
                for status in self.tx_status_stream(transaction):
                    tx_status = status[0]
        except grpc.RpcError as e:
            total_time = int((time.time() - start_time) * 1000)
            events.request_failure.fire(request_type="grpc", name='send_tx_await', response_time=total_time,
                                        tx_hash=hex_hash, exception=e)
        else:
            total_time = int((time.time() - start_time) * 1000)
            events.request_success.fire(request_type="grpc", name='send_tx_await', response_time=total_time,
                                        tx_hash=hex_hash, response_length=0)
            # In this example, I've hardcoded response_length=0. If we would want the response length to be
            # reported correctly in the statistics, we would probably need to hook in at a lower level

    def send_tx_await(self, transaction):
        """
        Send a transaction to Iroha and wait for the final status to be reported in status stream
        :param transaction: protobuf Transaction
        :return: None
        """
        while len(SENT) - len(COMMITTED) > 100:
            time.sleep(0.01)

        hex_hash = ascii_hash(transaction)
        start_time = time.time()

        try:
            self.send_tx(transaction)
            # tx_future = self._command_service_stub.Torii.future(transaction)
            SENT.add(hex_hash)
            TXS[hex_hash] = start_time
        except grpc.RpcError as e:
            total_time = int((time.time() - start_time) * 1000)
            events.request_failure.fire(request_type="grpc", name='send_tx_await', response_time=total_time,
                                        tx_hash=hex_hash, exception=e)
        # else:
        #     pool.spawn(IrohaClient.await_status, self, transaction, start_time)


# def fire(hash, response_time):
#     events.request_success.fire(request_type="grpc", name='send_tx_await', response_time=response_time, tx_hash=hash, response_length=0)

def block_listener(host):
    iroha_api = iroha.Iroha("alice@test")
    net = IrohaGrpc(host)
    query = iroha_api.blocks_query()
    ic.sign_query(query, ADMIN_PRIVATE_KEY)
    print("Listeting blocks")
    for block in net.send_blocks_stream_query(query):
        BLOCKS.add(block.block_response.block.block_v1.payload.height)
        hashes = block.block_response.block.block_v1.payload.rejected_transactions_hashes
        txs = block.block_response.block.block_v1.payload.transactions
        for tx in txs:
            hashes.append(ascii_hash(tx))

        # print(hashes)
        for hash in hashes:
            if hash not in TXS.keys():
                continue
            start_time = TXS[hash]
            COMMITTED.add(hash)
            del TXS[hash]
            total_time = int((time.time() - start_time) * 1000)
            # pool.spawn(fire, hash, total_time)
            try:
                events.request_success.fire(request_type="grpc", name='send_tx_await', response_time=total_time,
                                            tx_hash=hash, sent=start_time, committed=time.time(), response_length=0)
            except Exception as e:
                print(e)


def diff():
    while True:
        print(SENT.difference(COMMITTED))
        print([SENT_AM[x] for x in SENT.difference(COMMITTED)])
        print([SENT_AM[x] for x in SENT])
        time.sleep(5)


class IrohaLocust(Locust):
    """
    This is the abstract Locust class which should be subclassed. It provides an Iroha gRPC client
    that can be used to make gRPC requests that will be tracked in Locust's statistics.
    """

    def __init__(self, *args, **kwargs):
        global LISTENING
        super(IrohaLocust, self).__init__(*args, **kwargs)
        self.client = IrohaClient(self.host)
        if not LISTENING:
            LISTENING = True
            gevent.spawn(block_listener, self.host)
            # gevent.spawn(diff)


class LivingNextDoorToAlice(TaskSet):
    @task
    def send_tx(self):
        global DEPOSITED
        global TRANSACTION_COUNTER

        print("Locust instance (%r) executing my_task" % (self.locust))
        print("""
        \n
            Sent: {}
            Committed: {}
            Diff: {}
            Blocks: {}\n
            """.format(len(SENT), len(COMMITTED), len(SENT) - len(COMMITTED), len(BLOCKS)))
        iroha = Iroha('alice@test')

        desc = str(random.random())
        if not DEPOSITED:
            tx = iroha.transaction([iroha.command(
                'AddAssetQuantity', asset_id='coin#test', amount=str(DEPOSIT_AMOUNT)
            )])
            DEPOSITED = True
        tx = iroha.transaction([iroha.command(
            'TransferAsset', src_account_id='alice@test', dest_account_id='bob@test', asset_id='coin#test',
            amount=str(TRANSFER_AMOUNT), description=HOSTNAME
        )])

        # If the alice account is empty, refill it
        TRANSACTION_COUNTER += 1
        if TRANSACTION_COUNTER >= (DEPOSIT_AMOUNT / TRANSACTION_COUNTER):
            DEPOSITED = False

        ic.sign_transaction(tx, ADMIN_PRIVATE_KEY)
        self.client.send_tx_await(tx)


class LivingNextDoorToMultiAlice(TaskSet):
    @task(1)
    def send_mst_tx(self):
        global MST_DEPOSITED
        global MST_TRANSACTION_COUNTER
        print("Locust instance (%r) executing my_task" % (self.locust))
        print("""
                \n
                    Sent: {}
                    Committed: {}
                    Diff: {}
                    Blocks: {}\n
                    """.format(len(MST_SENT), len(MST_COMMITTED), len(MST_SENT) - len(MST_COMMITTED), len(MST_BLOCKS)))
        iroha = Iroha('rabbit@test')

        if not MST_DEPOSITED:
            tx = iroha.transaction([iroha.command(
                'AddAssetQuantity', asset_id='coin#test', amount=str(DEPOSIT_AMOUNT)
            )])
            MST_DEPOSITED = True
        tx = iroha.transaction([iroha.command(
            'TransferAsset', src_account_id='rabbit@test', dest_account_id='bob@test', asset_id='coin#test',
            amount=str(TRANSFER_AMOUNT), description=HOSTNAME
        )], quorum=2)

        # If the alice account is empty, refill it
        MST_TRANSACTION_COUNTER += 1
        if MST_TRANSACTION_COUNTER >= (DEPOSIT_AMOUNT / MST_TRANSACTION_COUNTER):
            MST_DEPOSITED = False

        ic.sign_transaction(tx, MST_PRIVATE_KEYS)
        self.client.send_tx_await(tx)

    @task(2)
    def accepts_request(self):
        global net
        q = ic.sign_query(
            Iroha('rabbit@test').query('GetPendingTransactions'),
            MST_PRIVATE_KEYS[0]
        )
        pending_transactions = net.send_query(q)
        for tx in pending_transactions.transactions_response.transactions:
            if tx.payload.reduced_payload.creator_account_id == 'rabbit@test':
                ic.sign_transaction(tx, *MST_PRIVATE_KEYS)
            else:
                del tx.signatures[:]
        self.client.send_tx_await(
            pending_transactions.transactions_response.transactions)