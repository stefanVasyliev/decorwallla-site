"""Reads the content data files as plain literals (ast.literal_eval), without executing them."""
import ast, os

HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

def load(filename):
    tree = ast.parse(open(os.path.join(HERE, filename)).read())
    out = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            out[node.targets[0].id] = ast.literal_eval(node.value)
    return out

CITIES = load("data_cities.py")["CITIES"]
SERVICES = load("data_services.py")["SERVICES"]
STYLES = load("data_styles.py")["STYLES"]
_dv = load("detail_variants.py")
DETAIL_ALT, STEPS_B = _dv["DETAIL_ALT"], _dv["STEPS_B"]
FAQ_ALT = load("faq_variants.py")["FAQ_ALT"]
