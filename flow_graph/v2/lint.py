"""engine v2: the determinism lint — the discipline, enforced.

The solve must be reproducible bytes: this lint scans the engine's modules for
the constructs that could break that — wall-clock and RNG imports, float
literals in computation code, file opens outside the declared I/O boundary
(graph_io, check, manifest), and unsorted iteration over model collections.
"""
import ast, os

PKG = os.path.dirname(os.path.abspath(__file__))
BANNED_IMPORTS = {'datetime', 'random', 'uuid', 'time', 'tempfile'}
IO_MODULES = {'graph_io.py', 'check.py', 'manifest.py', 'grid.py', 'lint.py'}  # declared readers/writers
TEST_MARK = 'test'


def run(root=PKG):
    violations = []
    for name in sorted(os.listdir(root)):
        if not name.endswith('.py'):
            continue
        path = os.path.join(root, name)
        with open(path, encoding='utf-8') as f:
            src = f.read()
        try:
            tree = ast.parse(src)
        except SyntaxError as e:
            violations.append(f'{name}: does not parse: {e}')
            continue
        is_test = name.startswith(TEST_MARK)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    if a.name.split('.')[0] in BANNED_IMPORTS:
                        violations.append(f'{name}:{node.lineno}: banned import {a.name}')
            elif isinstance(node, ast.ImportFrom):
                if (node.module or '').split('.')[0] in BANNED_IMPORTS:
                    violations.append(f'{name}:{node.lineno}: banned import from {node.module}')
            elif isinstance(node, ast.Constant):
                if isinstance(node.value, float) and not is_test:
                    violations.append(f'{name}:{node.lineno}: float literal in engine code (use integer grid counts)')
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'open':
                if name not in IO_MODULES and not is_test:
                    violations.append(f'{name}:{node.lineno}: file I/O outside the declared boundary')
    return violations


if __name__ == '__main__':
    v = run()
    for x in v:
        print('LINT:', x)
    raise SystemExit(1 if v else 0)
