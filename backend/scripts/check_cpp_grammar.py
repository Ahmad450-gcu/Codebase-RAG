import tree_sitter_cpp as tscpp
from tree_sitter import Language, Parser

CPP_LANGUAGE = Language(tscpp.language())
parser = Parser(CPP_LANGUAGE)

def dump(node, source_bytes, depth=0, max_depth=6):
    if depth > max_depth:
        return
    if node.is_named:
        text_preview = source_bytes[node.start_byte:node.end_byte].decode("utf8").split("\n")[0][:50]
        print("  " * depth + f"{node.type}   -> {text_preview!r}")
    for child in node.children:
        dump(child, source_bytes, depth + 1, max_depth)

sample = b"""
int add(int a, int b) {
    return a + b;
}
class Shape {
public:
    Shape(double area);
    double getArea() const {
        return area_;
    }
private:
    double area_;
};
double Shape::getArea2() const {
    return area_ * 2;
}
struct Point {
    int x;
    int y;
};

namespace geometry {
    double square(double x) {
        return x * x;
    }
    class Circle {
    public:
        double radius;
    };
}

template<typename T>
class Container {
public:
    T get() { return value; }
private:
    T value;
};
"""

tree = parser.parse(sample)
dump(tree.root_node, sample)