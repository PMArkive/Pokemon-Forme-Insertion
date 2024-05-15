import unittest

from file_handling import max_of_column


class TestUtilities(unittest.TestCase):
    def test_max_of_column(self):
        example_table = [
            [
                1, "a", 2
            ],
            [
                3, 4, "b"
            ]
        ]

        self.assertEqual(max_of_column(example_table, 0), 3)
        self.assertEqual(max_of_column(example_table, 1), 4)
        self.assertEqual(max_of_column(example_table, 2), 2)


if __name__ == '__main__':
    unittest.main()
