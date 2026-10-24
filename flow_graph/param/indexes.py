# SPDX-License-Identifier: MIT
# Copyright 2026 Mike Matthews.
"""Files written by index stages (regen_manifest.json stages with "index": true).

An index stage scans the whole repository and lists what it finds: assumptions, cited standards, document numbers.
Index scanners skip each other's outputs. An index records its sources, not other indexes; scanning one another
would make the pipeline chase its own tail, each index growing a row for the other's latest row."""
import fnmatch, json, os, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def index_globs():
    m = json.load(open(os.path.join(ROOT, 'flow_graph', 'param', 'regen_manifest.json')))
    return [g for s in m['stages'] if s.get('index') for g in s.get('outputs', [])]


def is_index_output(path):
    rel = os.path.relpath(os.path.join(ROOT, path), ROOT) if not os.path.isabs(path) else os.path.relpath(path, ROOT)
    return any(fnmatch.fnmatch(rel, g) for g in index_globs())
