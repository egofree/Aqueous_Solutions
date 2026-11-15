"""engine v2: the grid — integer quantities on a declared, parametric physical grid.

Every model quantity is an integer count of a grid unit (a Qty). The grid scales
per dimension are data (grid.json), never code: changing a scale is a data edit.
Quantities computed by the solve cannot wobble below the grid, so byte-identical
regeneration is true by construction rather than policed after the fact.

Arithmetic rules:
- same-dimension add/subtract: exact integers.
- multiply/divide by an integer scalar: exact / round-half-up at the grid
  (div.round_half_up() says it explicitly at the call site).
- no floats exist in the model. Display conversion (grid unit -> display unit)
  happens only at serialization/render, as an exact decimal string built from
  the integer count.
"""
import json, os
from decimal import Decimal, ROUND_HALF_UP

_GRID_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'grid.json')


class Grid:
    """The declared grid: dimension -> (grid unit, display unit, per-display count)."""

    def __init__(self, spec):
        self.spec = {}
        for dim, d in spec.items():
            if dim.startswith('_'):
                continue
            self.spec[dim] = (d['grid_unit'], d['display_unit'], int(d['per_display']))

    @classmethod
    def load(cls, path=_GRID_PATH):
        with open(path, encoding='utf-8') as f:
            return cls(json.load(f))

    def check(self, dim):
        if dim not in self.spec:
            raise KeyError(f'dimension {dim!r} is not declared in the grid; declare it in grid.json')

    def display(self, dim, count):
        """Exact decimal string of count grid units in the display unit (integer math only)."""
        g, disp, per = self.spec[dim]
        if per == 1:
            return f'{count} {disp}'
        d = (Decimal(count) / Decimal(per)).quantize(Decimal(1).scaleb(-_decimals(per)), rounding=ROUND_HALF_UP)
        return f'{d.normalize():f} {disp}'


def _decimals(per):
    """Decimal places needed to express 1/per exactly (per is a power-of-ten-friendly int)."""
    n, places = per, 0
    while n % 10 == 0 and n > 1:
        n //= 10
        places += 1
    if n != 1:                                  # e.g. per = 500: 2 places + trailing zeros
        places += len(str(n)) - 1
    return max(places, 0)


class Qty:
    """An integer count of grid units of one dimension. Immutable."""

    __slots__ = ('count', 'dim', '_grid')

    def __init__(self, count, dim, grid=None):
        if not isinstance(count, int) or isinstance(count, bool):
            raise TypeError(f'Qty holds an integer count of grid units, got {count!r}')
        self.count, self.dim, self._grid = count, dim, grid or _default_grid
        self._grid.check(dim)

    def __add__(self, other):
        self._same(other)
        return Qty(self.count + other.count, self.dim, self._grid)

    def __sub__(self, other):
        self._same(other)
        return Qty(self.count - other.count, self.dim, self._grid)

    def __mul__(self, scalar):
        if not isinstance(scalar, int) or isinstance(scalar, bool):
            raise TypeError('multiply a Qty by an integer scalar (declare scaling factors as integers on the grid)')
        return Qty(self.count * scalar, self.dim, self._grid)

    __rmul__ = __mul__

    def round_half_up(self, per):
        """Divide by the integer `per`, rounding half up at the grid — the division rule,
        named explicitly at the call site."""
        if not isinstance(per, int) or per <= 0:
            raise TypeError('divide by a positive integer per')
        q, r = divmod(self.count, per)
        if r * 2 >= per:
            q += 1
        return Qty(q, self.dim, self._grid)

    def display(self):
        return self._grid.display(self.dim, self.count)

    def _same(self, other):
        if not isinstance(other, Qty) or other.dim != self.dim:
            raise TypeError(f'dimension mismatch: {self.dim} vs {getattr(other, "dim", other)!r}')

    def __eq__(self, other):
        return isinstance(other, Qty) and other.count == self.count and other.dim == self.dim

    def __hash__(self):
        return hash((self.count, self.dim))

    def __repr__(self):
        return f'Qty({self.count}, {self.dim!r})'


_default_grid = Grid.load()
