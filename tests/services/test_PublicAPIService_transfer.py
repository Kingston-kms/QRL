# coding=utf-8
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.
from unittest import TestCase

from grpc import ServicerContext
from mock import Mock
from pyqrllib.pyqrllib import bin2hstr, QRLHelper

from qrl.core.ChainManager import ChainManager
from qrl.core.State import State
from qrl.core.misc import logger
from qrl.core.node import POW
from qrl.core.p2pfactory import P2PFactory
from qrl.core.qrlnode import QRLNode
from qrl.crypto.misc import sha256
from qrl.generated import qrl_pb2
from qrl.services.PublicAPIService import PublicAPIService
from tests.misc.helper import get_alice_xmss, set_data_dir, set_wallet_dir, get_bob_xmss, set_default_balance_size

logger.initialize_default()


class TestPublicAPI(TestCase):
    def __init__(self, *args, **kwargs):
        super(TestPublicAPI, self).__init__(*args, **kwargs)

    @set_default_balance_size()
    def test_transferCoins_get_unsigned(self):
        with set_data_dir('no_data'):
            with State() as db_state:
                with set_wallet_dir("test_wallet"):
                    p2p_factory = Mock(spec=P2PFactory)
                    p2p_factory.pow = Mock(spec=POW)
                    chain_manager = ChainManager(db_state)

                    qrlnode = QRLNode(db_state, mining_credit_wallet=b'')
                    qrlnode.set_chain_manager(chain_manager)
                    qrlnode._p2pfactory = p2p_factory
                    qrlnode._pow = p2p_factory.pow
                    qrlnode._peer_addresses = ['127.0.0.1', '192.168.1.1']

                    service = PublicAPIService(qrlnode)

                    context = Mock(spec=ServicerContext)

                    alice = get_alice_xmss()
                    bob = get_bob_xmss()

                    request = qrl_pb2.TransferCoinsReq(
                        addresses_to=[bob.address],
                        amounts=[101],
                        fee=12,
                        xmss_pk=alice.pk
                    )

                    response = service.TransferCoins(request=request, context=context)
                    context.set_code.assert_not_called()
                    context.set_details.assert_not_called()

                    self.assertIsNotNone(response)
                    self.assertIsNotNone(response.extended_transaction_unsigned)
                    self.assertEqual('transfer',
                                     response.extended_transaction_unsigned.tx.WhichOneof('transactionType'))

                    self.assertEqual(12, response.extended_transaction_unsigned.tx.fee)
                    self.assertEqual(alice.pk, response.extended_transaction_unsigned.tx.public_key)
                    self.assertEqual(0, response.extended_transaction_unsigned.tx.nonce)

                    self.assertEqual(b'', response.extended_transaction_unsigned.tx.signature)
                    self.assertEqual(b'', response.extended_transaction_unsigned.tx.transaction_hash)

                    self.assertEqual(bob.address, response.extended_transaction_unsigned.tx.transfer.addrs_to[0])
                    self.assertEqual(101, response.extended_transaction_unsigned.tx.transfer.amounts[0])

    @set_default_balance_size()
    def test_transferCoins_push_unsigned(self):
        with set_data_dir('no_data'):
            with State() as db_state:
                with set_wallet_dir("test_wallet"):
                    p2p_factory = Mock(spec=P2PFactory)
                    p2p_factory.pow = Mock(spec=POW)
                    chain_manager = ChainManager(db_state)

                    qrlnode = QRLNode(db_state, mining_credit_wallet=b'')
                    qrlnode.set_chain_manager(chain_manager)
                    qrlnode._p2pfactory = p2p_factory
                    qrlnode._pow = p2p_factory.pow
                    qrlnode._peer_addresses = ['127.0.0.1', '192.168.1.1']

                    service = PublicAPIService(qrlnode)

                    context = Mock(spec=ServicerContext)

                    alice = get_alice_xmss()
                    bob = get_bob_xmss()

                    request = qrl_pb2.TransferCoinsReq(
                        addresses_to=[bob.address],
                        amounts=[101],
                        fee=12,
                        xmss_pk=alice.pk
                    )

                    response = service.TransferCoins(request=request, context=context)
                    context.set_code.assert_not_called()
                    context.set_details.assert_not_called()

                    self.assertIsNotNone(response)
                    self.assertIsNotNone(response.extended_transaction_unsigned)
                    self.assertEqual('transfer', response.extended_transaction_unsigned.tx.WhichOneof('transactionType'))

                    self.assertEqual(12, response.extended_transaction_unsigned.tx.fee)
                    self.assertEqual(alice.pk, response.extended_transaction_unsigned.tx.public_key)
                    self.assertEqual(0, response.extended_transaction_unsigned.tx.nonce)
                    self.assertEqual(b'', response.extended_transaction_unsigned.tx.signature)
                    self.assertEqual(b'', response.extended_transaction_unsigned.tx.transaction_hash)
                    self.assertEqual(bob.address, response.extended_transaction_unsigned.tx.transfer.addrs_to[0])
                    self.assertEqual(101, response.extended_transaction_unsigned.tx.transfer.amounts[0])

                    req_push = qrl_pb2.PushTransactionReq(transaction_signed=response.extended_transaction_unsigned.tx)

                    resp_push = service.PushTransaction(req_push, context=context)
                    context.set_code.assert_not_called()
                    context.set_details.assert_not_called()

                    self.assertIsNotNone(resp_push)
                    self.assertEqual(qrl_pb2.PushTransactionResp.VALIDATION_FAILED,
                                     resp_push.error_code)

    @set_default_balance_size()
    def test_transferCoins_sign(self):
        with set_data_dir('no_data'):
            with State() as db_state:
                with set_wallet_dir("test_wallet"):
                    p2p_factory = Mock(spec=P2PFactory)
                    p2p_factory.pow = Mock(spec=POW)
                    chain_manager = ChainManager(db_state)

                    qrlnode = QRLNode(db_state, mining_credit_wallet=b'')
                    qrlnode.set_chain_manager(chain_manager)
                    qrlnode._p2pfactory = p2p_factory
                    qrlnode._pow = p2p_factory.pow
                    qrlnode._peer_addresses = ['127.0.0.1', '192.168.1.1']

                    service = PublicAPIService(qrlnode)

                    context = Mock(spec=ServicerContext)

                    alice = get_alice_xmss()
                    bob = get_bob_xmss()

                    request = qrl_pb2.TransferCoinsReq(
                        addresses_to=[bob.address],
                        amounts=[101],
                        fee=12,
                        xmss_pk=alice.pk
                    )

                    response = service.TransferCoins(request=request, context=context)
                    context.set_code.assert_not_called()
                    context.set_details.assert_not_called()

                    self.assertIsNotNone(response)
                    self.assertIsNotNone(response.extended_transaction_unsigned.tx)
                    self.assertEqual('transfer', response.extended_transaction_unsigned.tx.WhichOneof('transactionType'))

                    self.assertEqual(12, response.extended_transaction_unsigned.tx.fee)
                    self.assertEqual(alice.pk, response.extended_transaction_unsigned.tx.public_key)
                    self.assertEqual(0, response.extended_transaction_unsigned.tx.nonce)
                    self.assertEqual(b'', response.extended_transaction_unsigned.tx.signature)
                    self.assertEqual(b'', response.extended_transaction_unsigned.tx.transaction_hash)
                    self.assertEqual(bob.address, response.extended_transaction_unsigned.tx.transfer.addrs_to[0])
                    self.assertEqual(101, response.extended_transaction_unsigned.tx.transfer.amounts[0])

                    tmp_hash_pre = bytes(QRLHelper.getAddress(response.extended_transaction_unsigned.tx.public_key))
                    tmp_hash_pre += str(response.extended_transaction_unsigned.tx.fee).encode()
                    tmp_hash_pre += response.extended_transaction_unsigned.tx.transfer.addrs_to[0]
                    tmp_hash_pre += str(response.extended_transaction_unsigned.tx.transfer.amounts[0]).encode()

                    self.assertEqual('010300a1da274e68c88b0ccf448e0b1916fa789b01eb2ed4e9ad565ce264c939078'
                                     '2a9c61ac02f31320103001d65d7e59aed5efbeae64246e0f3184d7c42411421eb38'
                                     '5ba30f2c1c005a85ebc4419cfd313031',
                                     bin2hstr(tmp_hash_pre))

                    tmp_hash = sha256(tmp_hash_pre)

                    self.assertEqual('3645f2819aba65479f9a7fad3f5d7a41a9357410a595fa02fb947bfe3ed96e0f',
                                     bin2hstr(tmp_hash))

                    signed_transaction = response.extended_transaction_unsigned.tx
                    signed_transaction.signature = alice.sign(tmp_hash)

                    req_push = qrl_pb2.PushTransactionReq(transaction_signed=signed_transaction)

                    resp_push = service.PushTransaction(req_push, context=context)
                    context.set_code.assert_not_called()
                    context.set_details.assert_not_called()

                    self.assertIsNotNone(resp_push)
                    self.assertEqual(qrl_pb2.PushTransactionResp.SUBMITTED,
                                     resp_push.error_code)
                    self.assertEqual('30955fdc5e2d9dbe5fb9bf812f2e1b6c4b409a8a7c7a75f1c3e9ba1ffdd8e60e',
                                     bin2hstr(resp_push.tx_hash))