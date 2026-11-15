"""engine v2: the solve-function registry.

`fn(name, basis)` decorates a pure solve function and registers it. Family
modules live in flow_graph/v2/functions/ and import the decorator from here;
solve.py imports the family modules in the declared composition order (the
manifest's topo order, family by family as migration lands).
"""
FNS = []


def fn(name, basis):
    """Register a solve function under a name and its engineering basis citation."""
    def deco(f):
        f.stage_name, f.stage_basis = name, basis
        FNS.append(f)
        return f
    return deco
