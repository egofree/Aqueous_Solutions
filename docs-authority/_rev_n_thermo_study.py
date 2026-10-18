"""AQS-DUTY-012 Rev A, WP-THERMO-DB (screening): leach-outlet speciation across the ORP range with PHREEQC.

Tool    : IPhreeqc 3.7.3 through phreeqpy 0.6.0 (Parkhurst & Appelo 2013, USGS TM 6-A43, https://pubs.usgs.gov/tm/06/a43/).
Database: llnl.dat and pitzer.dat from the USGS PHREEQC distribution (https://github.com/usgs-coupled/phreeqc3/tree/master/database),
          copied to data/ with their sha256 recorded in the output.
Step 1  : species coverage check of each database for Fe(III), Cu(I), Zn, Sn, Pb and Au chloro-complexes (WP-THERMO-DB item 1).
Step 3  : E-pH point checks of protective-oxide stability for Fe, Cu, Ni, Cr, Ti, Sn, Pb, Zn at leach and EW conditions, and\n          corrosion-domain maps (screening Pourbaix form) over Eh -0.6..1.6 V vs SHE and pH 0..7 at 77.5 C.
Step 2  : speciation of the Rev N EW feed (leach outlet) at 77.5 C over Eh 0.40-1.20 V vs SHE with llnl.dat.
          llnl.dat uses the B-dot (extended Debye-Hueckel) activity model, intended for ionic strength up to about 1 mol/kg;
          the liquor is above that, so the result is a screening of the Fe(III)/Fe(II) and Cu(II)/Cu(I) split, not a design value.
Input   : composition from the Rev N report (--rep, default data/rev_n_report.json; compositions.feed in mol/d over the EW feed volume);
          concentrations taken as molalities (screening).
Output  : data/thermo_screen.json
Run     : python3 _rev_n_thermo_study.py --rep repN.json   (requires phreeqpy)
"""
import hashlib
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
T_C = 77.5
EH = [round(0.40 + 0.05 * i, 2) for i in range(17)]
NEED = {"Fe(III) chloro": ["FeCl+2", "FeCl2+"], "Cu(I) chloro": ["CuCl2-", "CuCl3-2"], "Zn chloro": ["ZnCl+", "ZnCl2"],
        "Sn chloro": ["SnCl+"], "Pb chloro": ["PbCl+", "PbCl2"], "Au chloro": ["AuCl4-", "AuCl2-"], "Al": ["Al+3"]}


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def coverage(db):
    txt = open(db, encoding="latin-1").read()
    toks = set()
    for line in txt.splitlines():
        s = line.split("#")[0].strip()
        if "=" in s:
            toks.update(t for t in s.replace("=", " ").split())
    return {k: {sp: sp in toks for sp in v} for k, v in NEED.items()}


OXIDES = dict(Fe="Hematite", Cu="Tenorite", Ni="Bunsenite", Cr="Eskolaite", Ti="Rutile", Sn="Cassiterite", Pb="Plattnerite", Zn="Zincite")
SERVICES = [("leach (LEACH_CSTR_1)", 77.5, 1.0, 1.05), ("leach, pH 0 bound", 77.5, 0.0, 1.05),
            ("EW anode region (Cl2 evolution above 1.3 V; checked at the 1.20 V convergence limit)", 55.0, 1.0, 1.20), ("EW_7 catholyte, pH 2.5 option", 55.0, 2.5, 0.0)]


def passivity(ph):
    """E-pH point checks (WP-THERMO-DB item 3, partial): saturation index of the protective oxide at 1e-6 mol/kgw dissolved metal
    in 2 mol/kgw NaCl background. SI >= 0: oxide thermodynamically stable (passive film possible); SI < 0: active dissolution expected.
    Pourbaix (1974) convention of 1e-6 activity for the corrosion boundary. Thermodynamics only; no kinetics or film breakdown by Cl-."""
    res = []
    for name, t, phv, eh in SERVICES:
        pe = eh / (math.log(10) * 8.314462 * (t + 273.15) / 96485.0)
        row = dict(service=name, T_C=t, pH=phv, Eh_V_SHE=eh, SI={})
        for m, oxide in OXIDES.items():
            s = f"""SOLUTION 1
 temp {t}
 units mol/kgw
 pH {phv}
 pe {pe:.4f}
 redox pe
 Na 2.0
 Cl 2.0 charge
 {m} 1e-6
SELECTED_OUTPUT
 -reset false
 -saturation_indices {oxide}
END
"""
            try:
                ph.run_string(s)
                arr = ph.get_selected_output_array()
                si = dict(zip(arr[0], arr[1])).get(f"si_{oxide}")
            except Exception:
                si = None
            row["SI"][f"{m} ({oxide})"] = None if si is None or si < -900 else round(si, 2)
        res.append(row)
    return res


MAP_PHASES = dict(Fe=(["Hematite", "Magnetite", "Goethite"], "Fe", []), Cu=(["Tenorite", "Cuprite"], "Cu", ["Nantokite", "Atacamite"]),
                  Ni=(["Bunsenite", "Ni(OH)2"], "Ni", []), Cr=(["Eskolaite"], "Cr", []), Ti=(["Rutile", "Anatase", "Ti2O3"], "Ti", []),
                  Sn=(["Cassiterite", "Romarchite"], "Sn", []), Pb=(["Plattnerite", "Litharge", "Massicot", "Minium"], "Pb", ["Cotunnite"]),
                  Zn=(["Zincite"], "Zn", []))
MAP_EH = [round(-0.6 + 0.1 * i, 1) for i in range(23)]
MAP_PH = [round(0.5 * i, 1) for i in range(15)]


def passivity_map(ph, t=T_C, cl=2.0):
    """Corrosion-domain maps in E-pH space (WP-THERMO-DB item 3, screening form of a Pourbaix diagram): for each metal at 1e-6 mol/kgw
    dissolved total in a 2 mol/kgw NaCl background at 77.5 C, each grid point is classed I (immunity: metal phase SI >= 0),
    P (passivation: an oxide or hydroxide SI >= 0), S (chloride salt film only), C (corrosion: no solid stable) or ? (no convergence; PHREEQC does not solve beyond the water stability limits).
    Thermodynamics only (llnl.dat, B-dot); no kinetics and no film breakdown by chloride (pitting), which favours the metal."""
    out = {}
    for m, (oxides, metal, salts) in MAP_PHASES.items():
        phases = oxides + [metal] + salts
        grid = []
        for eh in reversed(MAP_EH):
            row = ""
            pe = eh / (math.log(10) * 8.314462 * (t + 273.15) / 96485.0)
            for phv in MAP_PH:
                s = f"""SOLUTION 1
 temp {t}
 units mol/kgw
 pH {phv}
 pe {pe:.4f}
 redox pe
 Na {cl}
 Cl {cl} charge
 {m} 1e-6
SELECTED_OUTPUT
 -reset false
 -saturation_indices {' '.join(phases)}
END
"""
                try:
                    ph.run_string(s)
                    arr = ph.get_selected_output_array()
                    si = {k[3:]: v for k, v in zip(arr[0], arr[1]) if k.startswith("si_")}
                    ok = lambda names: any(si.get(n, -999) is not None and -900 < si.get(n, -999) and si.get(n, -999) >= 0 for n in names)
                    row += "I" if ok([metal]) else "P" if ok(oxides) else "S" if ok(salts) else "C"
                except Exception:
                    row += "?"
            grid.append(row)
        out[m] = dict(phases=dict(passive=oxides, immune=metal, salt=salts), rows_Eh_V_SHE_desc=list(reversed(MAP_EH)), cols_pH=MAP_PH, grid=grid)
    return out


def main(rep_path):
    from phreeqpy.iphreeqc.phreeqc_dll import IPhreeqc
    rep = json.load(open(rep_path))
    feed = rep["compositions"]["feed"]
    q = rep["ew_summary"]["vol"]["Q_m3_d"]
    c = {k: v / q / 1000 for k, v in feed.items()}      # mol/L -> taken as mol/kgw
    h_in = rep["compositions"]["feed"]["Cl"]
    out = dict(doc="AQS-DUTY-012 WP-THERMO-DB screening", tool="IPhreeqc 3.7.3 (phreeqpy 0.6.0)", T_C=T_C, databases={}, runs=[])
    for db in ("pitzer.dat", "llnl.dat"):
        p = os.path.join(DATA, db)
        out["databases"][db] = dict(sha256=sha(p), coverage=coverage(p))
    comp = dict(Fe=c["Fe"], Cu=c["Cu"], Zn=c["Zn"], Ni=c["Ni"], Pb=c["Pb"], Sn=c["Sn"], Cd=c["Cd"], Al=c["Al"], Na=c["Na"], Cl=c["Cl"])
    out["composition_mol_kgw"] = {k: round(v, 6) for k, v in comp.items()}
    ph = IPhreeqc()
    ph.load_database(os.path.join(DATA, "llnl.dat"))
    for eh in EH:
        pe = eh / (math.log(10) * 8.314462 * (T_C + 273.15) / 96485.0)
        s = f"""SOLUTION 1
 temp {T_C}
 units mol/kgw
 pH 1.0
 pe {pe:.4f}
 redox pe
 Fe {comp['Fe']:.6e}
 Cu {comp['Cu']:.6e}
 Zn {comp['Zn']:.6e}
 Ni {comp['Ni']:.6e}
 Pb {comp['Pb']:.6e}
 Sn {comp['Sn']:.6e}
 Cd {comp['Cd']:.6e}
 Al {comp['Al']:.6e}
 Na {comp['Na']:.6e}
 Cl {comp['Cl']:.6e} charge
SELECTED_OUTPUT
 -reset false
 -ionic_strength true
 -totals Fe(2) Fe(3) Cu(1) Cu(2) Cl
 -molalities Fe+3 FeCl+2 FeCl2+ FeCl4- Fe+2 FeCl+ FeCl2 Cu+2 CuCl+ CuCl2 CuCl4-2 Cu+ CuCl2- CuCl3-2
END
"""
        ph.run_string(s)
        arr = ph.get_selected_output_array()
        row = dict(zip(arr[0], arr[1]))
        fe2, fe3 = row.get("Fe(2)(mol/kgw)", 0.0), row.get("Fe(3)(mol/kgw)", 0.0)
        cu1, cu2 = row.get("Cu(1)(mol/kgw)", 0.0), row.get("Cu(2)(mol/kgw)", 0.0)
        mol = {k.replace("m_", "").replace("(mol/kgw)", ""): v for k, v in row.items() if k.startswith("m_")}
        out["runs"].append(dict(Eh_V_SHE=eh, pe=round(pe, 3), ionic_strength=row.get("mu"), fe3_fraction=fe3 / (fe2 + fe3) if fe2 + fe3 else None,
                                cu2_fraction=cu2 / (cu1 + cu2) if cu1 + cu2 else None, cl_total=row.get("Cl(mol/kgw)"),
                                fe3_dominant=max(("FeCl+2", "FeCl2+", "FeCl4-", "Fe+3"), key=lambda k: mol.get(k, 0.0)),
                                cu1_dominant=max(("Cu+", "CuCl2-", "CuCl3-2"), key=lambda k: mol.get(k, 0.0)), molalities=mol))
    sp = [r for r in out["runs"] if r["fe3_fraction"] is not None]
    half = [r["Eh_V_SHE"] for r in sp if r["fe3_fraction"] >= 0.5]
    out["fe_half_point_V_SHE"] = half[0] if half else None
    fe99 = [r["Eh_V_SHE"] for r in sp if r["fe3_fraction"] >= 0.99]
    out["fe3_99pct_from_V_SHE"] = fe99[0] if fe99 else None
    cu99 = [r["Eh_V_SHE"] for r in out["runs"] if r["cu2_fraction"] is not None and r["cu2_fraction"] >= 0.99]
    out["cu2_99pct_from_V_SHE"] = cu99[0] if cu99 else None
    out["validity"] = ("llnl.dat B-dot activity model; ionic strength above its ~1 mol/kg range: screening only. pitzer.dat lacks Fe(III), Cu, Zn, Pb, Sn, Al and Au species. "
                       "llnl.dat has no Au chloro-complex. A validated concentrated-chloride model is required study RS-THERMO-PITZER.")
    out["passivity_points"] = passivity(ph)
    out["passivity_maps"] = dict(T_C=T_C, background="2 mol/kgw NaCl, 1e-6 mol/kgw metal", legend="I immunity, P passivation, S chloride salt film, C corrosion, ? no PHREEQC convergence (beyond the O2/H2 water stability limits at 1 atm)",
                                 maps=passivity_map(ph))
    json.dump(out, open(os.path.join(DATA, "thermo_screen.json"), "w"), indent=1)
    return out


if __name__ == "__main__":
    rp = sys.argv[sys.argv.index("--rep") + 1] if "--rep" in sys.argv else os.path.join(DATA, "rev_n_report.json")
    o = main(rp)
    print(json.dumps({k: o[k] for k in ("fe_half_point_V_SHE", "fe3_99pct_from_V_SHE", "cu2_99pct_from_V_SHE", "composition_mol_kgw")}, indent=1))
    for r in o["runs"]:
        print(r["Eh_V_SHE"], round(r["ionic_strength"], 3), round(r["fe3_fraction"], 6), round(r["cu2_fraction"], 6), r["fe3_dominant"], r["cu1_dominant"])
    print(json.dumps({k: v["coverage"] for k, v in o["databases"].items()}))
    for r in o["passivity_points"]:
        print(r["service"], r["SI"])
