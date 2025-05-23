class IncorrectTriangleSides(Exception):
    pass


def get_triangle_type(a, b, c):
    if a <= 0 or b <= 0 or c <= 0:
        raise IncorrectTriangleSides("All sides must be positive")
    if (a + b <= c) or (a + c <= b) or (b + c <= a):
        raise IncorrectTriangleSides("The sum of any two sides must be greater than the third")
    
    if a == b == c:
        return "equilateral"
    elif a == b or a == c or b == c:
        return "isosceles"
    else:
        return "nonequilateral"