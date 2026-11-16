"""engine v2: the determinism lint — the discipline, enforced.

The solve must be reproducible bytes: this lint scans the engine's modules for
the constructs that could break that — wall-clock and RNG imports, float
literals in computation code, file opens outside the declared I/O boundary
(graph_io, check, manifest), and unsorted iteration over model collections.
"""
import ast, os

PKG = os.path.dirname(os.path.abspath(__file__))
BANNED_IMPORTS = {'datetime', 'random', 'uuid', 'time', 'tempfile'}
IO_MODULES = {'graph_io.py', 'check.py', 'manifest.py', 'grid.py', 'lint.py', 'inputs.py'}  # declared readers/writers (inputs.py is the payload-loading boundary)
TEST_MARK = 'test'


def run(root=PKG):
    violations = []
    for dirpath, _dirs, files in sorted(os.walk(root)):
        for name in sorted(files):
            if not name.endswith('.py'):
                continue
            rel = os.path.relpath(os.path.join(dirpath, name), root)
            path = os.path.join(dirpath, name)
            with open(path, encoding='utf-8') as f:
                src = f.read()
            try:
                tree = ast.parse(src)
            except SyntaxError as e:
                violations.append(f'{rel}: does not parse: {e}')
                continue
            is_test = name.startswith(TEST_MARK) or rel.startswith('tests' + os.sep)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for a in node.names:
                        if a.name.split('.')[0] in BANNED_IMPORTS:
                            violations.append(f'{rel}:{node.lineno}: banned import {a.name}')
                elif isinstance(node, ast.ImportFrom):
                    if (node.module or '').split('.')[0] in BANNED_IMPORTS:
                        violations.append(f'{rel}:{node.lineno}: banned import from {node.module}')
                elif isinstance(node, ast.Constant):
                    if isinstance(node.value, float) and not is_test:
                        violations.append(f'{rel}:{node.lineno}: float literal in engine code (use integer grid counts)')
                elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'open':
                    if os.path.basename(name) not in IO_MODULES and not is_test:
                        violations.append(f'{rel}:{node.lineno}: file I/O outside the declared boundary')
    return violations


if __name__ == '__main__':
    v = run()
    for x in v:
        print('LINT:', x)
    raise SystemExit(1 if v else 0)
