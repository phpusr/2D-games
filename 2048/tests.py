from unittest import TestCase

from main import Game2048


class Test2048(TestCase):

    def setUp(self):
        self.game = Game2048()

    def test_is_zero_in_array(self):
        self.assertTrue(self.game._is_zero_in_array())

        self.game._array[2][2] = 1
        self.assertTrue(self.game._is_zero_in_array())

        for row in self.game._array:
            for cell_index in range(self.game._array_size):
                row[cell_index] = 1
        self.assertFalse(self.game._is_zero_in_array())

    def test_get_empty_cells(self):
        game = Game2048()
        for row in game._array:
            for cell_index in range(game._array_size):
                if cell_index != 2:
                    row[cell_index] = 1
        expected_result = [(0, 2), (1, 2), (2, 2), (3, 2)]
        self.assertEqual(game._get_empty_cells(), expected_result)

    def test_run_filled(self):
        init_array = [
            [2, 32, 512, 100000],
            [4, 64, 1024, 0],
            [8, 128, 2048, 0],
            [16, 256, 10000, 0],
        ]
        self.game.start(init_array)
