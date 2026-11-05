"""STEP exports are byte-stable: the Open CASCADE per-process product counter is removed
(models/mfg/lib/step_normalize.py), so rebuilding one unit cannot rewrite another unit's STEP file."""
import importlib.util, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_spec = importlib.util.spec_from_file_location('step_normalize', os.path.join(ROOT, 'models', 'mfg', 'lib', 'step_normalize.py'))
SN = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(SN)

HEAD = (b"#7 = PRODUCT('Open CASCADE STEP translator 7.9 %d',\n"
        b"  'Open CASCADE STEP translator 7.9 %d','',(#8));\n#8 = PRODUCT_CONTEXT('',#2,'mechanical');\n")


def test_counter_removed_and_export_order_irrelevant():
    a = SN.normalize_bytes(HEAD % (41, 41))
    b = SN.normalize_bytes(HEAD % (42, 42))
    assert a == b
    assert b"translator 7.9'" in a


def test_normalize_is_idempotent(tmp_path):
    p = tmp_path / 'x.step'
    p.write_bytes(HEAD % (3, 3))
    assert SN.normalize(str(p)) is True
    first = p.read_bytes()
    assert SN.normalize(str(p)) is False
    assert p.read_bytes() == first
