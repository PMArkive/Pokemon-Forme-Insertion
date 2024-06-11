import unittest

from utilities import max_of_column, entire_of_column, find_rows_with_column_matching


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

    def test_entire_of_column(self):
        example_table = [
            [
                1, "a", 2
            ],
            [
                3, 4, "b"
            ]
        ]
        self.assertEqual(entire_of_column(example_table, 0, allow_multiple=False), [1, 3])
        self.assertEqual(entire_of_column(example_table, 1, allow_multiple=False), ["a", 4])
        self.assertEqual(entire_of_column(example_table, 2, allow_multiple=False), [2, "b"])

    def test_find_rows_with_column_matching(self):
        example_table = [
            [
                1, "a", 2,
            ],
            [
                3, 4, "b",
            ],
            [
                1, "a", 2,
            ],
        ]
        self.assertEqual(find_rows_with_column_matching(example_table, 0, 3), [1])
        self.assertEqual(find_rows_with_column_matching(example_table, 1, "a"), [0,2])



if __name__ == '__main__':
    unittest.main()
