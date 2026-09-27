import unittest
from src.calc import add

class CalcTests(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(7, 5), 12)
        self.assertEqual(add(-2, 2), 0)

if __name__ == "__main__":
    unittest.main()
