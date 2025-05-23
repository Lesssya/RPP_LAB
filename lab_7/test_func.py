import unittest
from triangle_func import get_triangle_type, IncorrectTriangleSides


class TestTriangleFunction(unittest.TestCase):
    def test_equilateral(self):
        self.assertEqual(get_triangle_type(5, 5, 5), 'equilateral')
    
    def test_isosceles(self):
        self.assertEqual(get_triangle_type(5, 5, 6), 'isosceles')
        self.assertEqual(get_triangle_type(5, 6, 5), 'isosceles')
        self.assertEqual(get_triangle_type(6, 5, 5), 'isosceles')
    
    def test_nonequilateral(self):
        self.assertEqual(get_triangle_type(3, 4, 5), 'nonequilateral')
    
    def test_invalid_sides_negative(self):
        with self.assertRaises(IncorrectTriangleSides):
            get_triangle_type(-1, 2, 3)
    
    def test_invalid_sides_zero(self):
        with self.assertRaises(IncorrectTriangleSides):
            get_triangle_type(0, 0, 0)
    
    def test_invalid_triangle_inequality(self):
        with self.assertRaises(IncorrectTriangleSides):
            get_triangle_type(1, 2, 3)

if __name__ == '__main__':
    unittest.main()