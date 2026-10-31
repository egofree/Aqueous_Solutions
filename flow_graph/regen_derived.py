"""X-GOV-06: regenerate the graph-derived layer views (flow_graph/views/*) that sit outside the
balance pipeline. Run after balance; _rev_stamp.py then reports them current. The matplotlib PFD
renders, the FreeCAD phase frames and the plant_phase_d.mp4 were retired from the pipeline
(2026-10-27, AQS-UI-001 Rev D demotes matplotlib; the 3D presentation bias is FreeCAD) - the
exporters remain on-demand tools under flow_graph/exporters/matplotlib/ and models/freecad/."""
import os, subprocess, hashlib, json, sys
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); env = dict(os.environ, PYTHONPATH=R)
def main():
    subprocess.run([sys.executable, 'flow_graph/render_layer_views.py'], cwd=R, env=env, check=True,
                   stdout=subprocess.DEVNULL)
    json.dump({'graph_sha256': hashlib.sha256(open(os.path.join(R, 'flow_graph/plant_flow_graph.json'), 'rb').read()).hexdigest(),
               'patterns': ['flow_graph/views/*']}, open(os.path.join(R, 'media/_generated.json'), 'w'), indent=1)
    print('layer views regenerated')
if __name__ == '__main__': main()
