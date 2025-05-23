import pytest
from triangle_class import Triangle, IncorrectTriangleSides


def test_triangle_creation_valid():
    triangle = Triangle(3, 4, 5)
    assert triangle.a == 3
    assert triangle.b == 4
    assert triangle.c == 5


def test_triangle_creation_invalid():
    with pytest.raises(IncorrectTriangleSides):
        Triangle(1, 2, 3)
    with pytest.raises(IncorrectTriangleSides):
        Triangle(0, 1, 1)
    with pytest.raises(IncorrectTriangleSides):
        Triangle(-1, 2, 2)


def test_triangle_type():
    triangle = Triangle(5, 5, 5)
    assert triangle.triangle_type() == 'equilateral'
    triangle = Triangle(5, 5, 6)
    assert triangle.triangle_type() == 'isosceles'
    triangle = Triangle(3, 4, 5)
    assert triangle.triangle_type() == 'nonequilateral'


def test_perimeter():
    triangle = Triangle(3, 4, 5)
    assert triangle.perimeter() == 12