"""Solve functions, family by family. Each module registers its pure functions
with the registry decorator; solve.py imports modules in the declared order
(the reference manifest's topo order). No module here may do I/O, use
wall-clock or RNG, or hold floats — the lint holds this.
"""
