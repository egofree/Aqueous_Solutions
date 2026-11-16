"""engine v2: the renderer registry — pure functions Model -> document bytes.

Each entry is (repo-relative output path, render function); a render function
takes (model, inputs) and returns the document bytes, reading the model's
fields (the values the physics families stamp, plus the passthrough seed
books) and the input payloads. No I/O, no wall-clock, no RNG: the registry
returns bytes, and file writing stays outside (the declared I/O boundary of
engine v2). The declared order below is the composition order; the acceptance
test renders every entry against the model seeded+computed by the landed
physics families and requires byte-exact equality with the committed file.
"""
from . import duties as _duties
from . import sizing_docs as _sizing
from .electrical import DOCS as _electrical_docs          # the electrical-chain wave (ledger section D), one aggregate import

RENDERS = [
    ('docs-authority/sizing/COLD_BOX.md', _sizing.render_cold_box),
    ('docs-authority/sizing/EVAP_DESIGN.md', _sizing.render_evap_design),
    ('docs-authority/sizing/GAS_RECEIVERS.md', _sizing.render_gas_receivers),
    ('docs-authority/sizing/H2_COMPRESSOR.md', _sizing.render_h2_compressor),
    ('docs-authority/sizing/H2_PURIFIER_BEDS.md', _sizing.render_h2_purifier_beds),
    ('docs-authority/sizing/HOUSE_SCRUBBERS.md', _sizing.render_house_scrubbers),
    ('docs-authority/sizing/UPW_POLISH.md', _sizing.render_upw_polish),
    ('docs-authority/sizing/GEO_LOOP.md', _sizing.render_geo_loop),
] + _electrical_docs + _duties.DOCS

_INDEX = dict(RENDERS)


def render(model, inputs):
    """Run every registered renderer against the model. Returns {path: bytes}
    in the declared order. Pure."""
    return {path: fn(model, inputs) for path, fn in RENDERS}


def render_one(path, model, inputs):
    """One document's bytes by repo-relative output path. Pure."""
    if path not in _INDEX:
        raise KeyError(f'no renderer registered for {path}')
    return _INDEX[path](model, inputs)
