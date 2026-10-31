# Parcel selection interface

Document number: AQS-SITE-014  
Revision: A  
Date: 2026-10-30  
Authority: AQS-PLAN-007 X-BAS-03; AQS-SITE-002 Rev C (the location-neutral bounding basis); open questions Q-033 and Q-026 closures (2026-10-30). The interface contract for a parcel-selection application (details with the application owner; this page fixes our side of the contract). Style: AQS-DOC-002.

| Rev | Description | Date |
|---|---|---|
| A | First issue: the contract, the schema extension and the ingestion path | 2026-10-30 |

## 1. Purpose and scope

The baseline design is location-neutral (AQS-SITE-002 Rev C): every site value is a bounding value, and a specific site design replaces each bounding value with the location's own published value. The location enters through the **site design tool** as a *parcel profile*. This page is the contract a parcel-selection application must satisfy to feed that tool: what the application exports, how it validates, and how the model re-solves. The application itself is a separate deliverable; nothing here constrains its user interface, only its output.

## 2. The contract in one paragraph

The application exports one **parcel profile**: a JSON document that carries the parcel's identity and boundary, the code-mandated site loads, and the field data. It validates against the site-profile schema (`flow_graph/schema/site_profile.schema.json`) extended by the parcel group of section 4, and is consumed exactly as any other locale profile in `flow_graph/param/sites/`: `drivers.load('parcel')` resolves the site-bound drivers from it, every bounding value is replaced, and the model re-solves (AQS-SITE-002 section 1). The application does not write the model; it writes the profile.

## 3. What the application must supply

Table 3.1. Parcel profile inputs, by the driver each feeds

| Parcel fact | Feeds | Baseline it replaces |
| --- | --- | --- |
| Boundary polygon, coordinates, elevation | identity group | the bounding-class site description |
| ASCE 7-22 wind (Risk II), ground snow, seismic Ss/S1 and site class | wind, snow, seismic groups | the bounding 70 m/s, 0.24 kPa, per-site rule |
| ASHRAE design dry bulbs (0.4 % cooling, 99.6 % heating), degree days | thermal group and the season coefficients | the bounding 47.4 / −9.4 °C and the Furnace Creek normals |
| PVWatts (or TMY3) annual yield at the parcel | solar group | the bounding 5.41 kWh/kWp d |
| Geotechnical report: allowable bearing, unit weight, groundwater depth | ground group | the presumptive 72 kPa clay and the study depths |
| Wenner soil-resistivity test | ground group (grounding) | the 50 Ω·m study class |
| Jurisdiction, flag or coastal state, applicable code amendments | identity/compliance notes | the compliance-matrix jurisdiction row |
| Utility interconnection data (if grid-tied) | power-portfolio notes | the self-sustaining portfolio assumption |

Every field carries its own source citation in the profile entry (ref, register id or owner basis - the schema rejects an entry without one), so the site design inherits a provenance-complete basis.

## 4. Schema extension

The parcel profile is a locale profile plus one group. `site_profile.schema.json` gains an optional `parcel` group:

```
parcel: {
  boundary_geojson: string   (GeoJSON polygon, WGS84)
  parcel_id: string          (the application's parcel identifier)
  hazard_tool_run: string    (the ASCE Hazard Tool report identifier or URL)
  geotech_report: string     (the report reference)
  wenner_date: string        (the field test date)
}
```

All fields optional at the schema level; the site design tool warns on any absent field whose driver it would otherwise leave bounding. A bounding value that survives into a built design is a GA-check finding (AQS-SITE-002 section 5).

## 5. Ingestion path

1. The application exports `parcel.json`.
2. The operator drops it in `flow_graph/param/sites/` as the profile `parcel` and runs the regeneration with the profile selected.
3. `drivers.load('parcel')` resolves; every bounding value is replaced; the model re-solves; the site design's documents regenerate.
4. The receipts and the staleness gates prove the tree is current (AQS-PAR-001).

No model file is edited by hand. The application's contract is the exported profile - the schema is the versioned interface, and a schema change is a change to this page and the schema file in the same commit.

## 6. What this page does not do

It does not design the application, name its data sources, or pick a mapping or geotechnical vendor. Those are the application owner's deliverables against the contract above.
