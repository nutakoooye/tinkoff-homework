import unittest
from multiprocessing import cpu_count
from blockchain import Block, Blockchain


class BlockChainTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.blockchain = Blockchain("0")

    def test_genesis_block_create_success(self):
        self.assertEqual(len(self.blockchain.chain), 1)
        self.assertEqual(self.blockchain.complex, "0")
        self.assertIsInstance(self.blockchain.chain[0], Block)

    def test_create_block(self):
        block = self.blockchain.init_block(0,"0", False)
        self.assertEqual(len(self.blockchain.chain), 2)
        self.assertEqual(block.proof, 0)
        self.assertEqual(block.in_progress, False)

    def test_get_previous(self):
        for _ in range(5):
            self.blockchain.new_block(wait=True)
        self.assertEqual(self.blockchain.get_previous_block(),
                         self.blockchain.chain[-1])

    def test_get_previous_with_one_block(self):
        self.assertEqual(self.blockchain.get_previous_block(),
                         self.blockchain.chain[0])

    def test_valid_blockchain(self):
        for _ in range(5):
            self.blockchain.new_block(wait=True)
        self.assertEqual(len(self.blockchain.chain), 6)
        self.assertTrue(self.blockchain.chain_valid())

    def test_invalid_if_change_proof(self):
        for _ in range(5):
            self.blockchain.new_block(wait=True)
        broken_block = self.blockchain.chain[3]
        broken_block.proof = 0
        self.assertFalse(self.blockchain.chain_valid())

    def test_invalid_if_change_last_proof(self):
        self.blockchain.new_block(wait=True)
        last_block = self.blockchain.get_previous_block()
        last_block.proof = 0
        self.assertFalse(self.blockchain.chain_valid())

    def test_valid_if_change_first_proof(self):
        self.blockchain.new_block(wait=True)
        first_block = self.blockchain.chain[0]
        first_block.proof = 1212
        self.assertFalse(self.blockchain.chain_valid())

    def test_proof_of_work_none_if_not_find(self):
        self.assertIsNone(self.blockchain.proof_of_work(0, 1, 2))

    @unittest.skipIf(cpu_count() != 4,
                     "supported only with 4 processor cores")
    def test_range_gen(self):
        patch = self.blockchain.range_gen(0, 100)
        self.assertEqual(
            next(patch),
            [(0, 0, 25), (0, 25, 50), (0, 50, 75), (0, 75, 100)]
        )
        self.assertEqual(
            next(patch),
            [(0, 100, 125), (0, 125, 150), (0, 150, 175), (0, 175, 200)]
        )
