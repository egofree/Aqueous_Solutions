# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""Byte-stable STEP export for the manufacturing models (AQS-PLAN-006; F-20261110-12).

The Open CASCADE STEP writer names an unnamed product 'Open CASCADE STEP translator
<version> <n>', where <n> counts the exports made so far in the writing process, and
it stamps the file header FILE_NAME with the wall-clock export time. The same model
therefore exported different bytes depending on how many exports ran before it in that
process and on the day the lane ran, and the committed files needed a separate
normalize pass (lib/step_normalize.py) that a check cannot gate.

export_step carries the whole export instead: it builds the same XCAF document and
uses the same writer settings cadquery's own exporters use, sets every product name as
a document label before the transfer, and fixes the header name and time stamp from
lib/stamp_date.py before the write. A rebuild is byte-identical on any day and in any
export order, with no post-pass. lib/step_normalize.py stays for legacy one-off use.

    from lib import step_export
    step_export.export_step(shape, "export/unit.step")            # name from the path stem
    step_export.export_step(assembly, path)                       # product names from the labels
    step_export.export_step(solid, path, write_pcurves=False)     # BAGHOUSE convention
"""
import pathlib

import cadquery as cq
from OCP.APIHeaderSection import APIHeaderSection_MakeHeader
from OCP.IFSelect import IFSelect_ReturnStatus
from OCP.Interface import Interface_Static
from OCP.STEPCAFControl import STEPCAFControl_Writer
from OCP.STEPControl import STEPControl_StepModelType
from OCP.TCollection import TCollection_HAsciiString, TCollection_ExtendedString
from OCP.TDataStd import TDataStd_Name
from OCP.TDocStd import TDocStd_Document
from OCP.XCAFApp import XCAFApp_Application
from OCP.XCAFDoc import XCAFDoc_DocumentTool
from OCP.XSControl import XSControl_WorkSession

import os, pathlib, re, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib.stamp_date import deterministic_date          # noqa: E402

_UUID_RE = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")


def export_step(obj, path, name=None, write_pcurves=True, precision_mode=0):
    """Write `obj` (Assembly, Shape or Workplane) to `path` as STEP, byte-stable.

    The product name is `name` (default: the path stem) for a Shape or Workplane, and
    the assembly's own labels for an Assembly. `write_pcurves` and `precision_mode`
    are the same options the cadquery exporters take. Returns True on success.
    """
    name = name or pathlib.Path(path).stem
    if isinstance(obj, cq.Assembly):
        from cadquery.occ_impl.assembly import toCAF
        top, doc = toCAF(obj, True)        # the same document build cq's exporter uses
        if _UUID_RE.fullmatch(str(obj.name or "")):
            # cq.Assembly() without a name carries a random UUID; the root product must
            # not depend on it, so the top label takes the file stem's fixed name.
            TDataStd_Name.Set_s(top, TCollection_ExtendedString(name))
    else:
        shape = obj if isinstance(obj, cq.Shape) else _compound(obj)
        doc = TDocStd_Document(TCollection_ExtendedString("XmlXCAF Document"))
        XCAFApp_Application.GetApplication_s().NewDocument(
            TCollection_ExtendedString("MDTV-XCAF"), doc)
        tool = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
        label = tool.AddShape(shape.wrapped, False, False)   # one named product
        TDataStd_Name.Set_s(label, TCollection_ExtendedString(name))

    session = XSControl_WorkSession()
    writer = STEPCAFControl_Writer(session, False)
    writer.SetColorMode(True)
    writer.SetLayerMode(True)
    writer.SetNameMode(True)
    Interface_Static.SetIVal_s("write.surfacecurve.mode", 1 if write_pcurves else 0)
    Interface_Static.SetIVal_s("write.precision.mode", precision_mode)
    Interface_Static.SetIVal_s("write.stepcaf.subshapes.name", 1)
    Interface_Static.SetCVal_s("xstep.cascade.unit", "MM")
    Interface_Static.SetCVal_s("write.step.unit", "MM")
    writer.Transfer(doc, STEPControl_StepModelType.STEPControl_AsIs)

    model = writer.ChangeWriter().Model()
    header = APIHeaderSection_MakeHeader(model)
    header.SetName(TCollection_HAsciiString(name))
    header.SetTimeStamp(TCollection_HAsciiString(deterministic_date() + "T00:00:00"))
    header.Apply(model)
    return writer.Write(path) == IFSelect_ReturnStatus.IFSelect_RetDone


def _compound(workplane):
    """The same shape cq.exporters.export builds from a Workplane (its stack items)."""
    from cadquery.occ_impl.shapes import compound
    return compound(*workplane)
