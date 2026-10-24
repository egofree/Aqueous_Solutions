"""X-PAR-04 / X-GOV-06: regenerate the graph-derived views and drawings that sit outside the balance pipeline:
layer views (render_layer_views.py), the seven media/pfd PNGs (matplotlib exporters), the Phase D frames (models/freecad/render_frames.py)
and media/plant_phase_d.mp4 (ffmpeg, 12 fps, 1280x720). Run after balance; _rev_stamp.py then reports them current."""
import os, shutil, subprocess, sys, glob
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); env = dict(os.environ, PYTHONPATH=R)
def run(*a, cwd=R): subprocess.run([sys.executable, *a], cwd=cwd, env=env, check=True, stdout=subprocess.DEVNULL)
def main():
    run('flow_graph/render_layer_views.py')
    E = os.path.join(R, 'flow_graph/exporters/matplotlib')
    for f in ['completion', 'continuous_recycling', 'glass_ceramic', 'master_disassembly', 'oil_line', 'polish_bank', 'wet_line_factory']:
        run(os.path.join(E, f + '_pfd.py')); shutil.move(os.path.join(E, f + '_pfd.png'), os.path.join(R, 'media/pfd', f + '_pfd.png'))
    run('render_frames.py', cwd=os.path.join(R, 'models/freecad')); A = os.path.join(R, 'models/animation')
    for p in glob.glob(os.path.join(A, '*.png')): shutil.move(p, os.path.join(R, 'media', os.path.basename(p)))
    shutil.rmtree(A, ignore_errors=True)
    if shutil.which('ffmpeg'):
        fr = ['F0_campus', 'D0_overview', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6']; lst = os.path.join(R, 'media/.frames.txt')
        open(lst, 'w').write(''.join(f"file '{os.path.join(R, 'media', f + '.png')}'\nduration 4.625\n" for f in fr) + f"file '{os.path.join(R, 'media/D6.png')}'\n")
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-vf', 'scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2:color=f3efe6,fps=12,format=yuv420p',
                        '-c:v', 'libx264', os.path.join(R, 'media/plant_phase_d.mp4')], check=True); os.remove(lst)
    import hashlib, json   # manifest read by docs-authority/_rev_stamp.py: these outputs were derived again from this exact graph
    json.dump({'graph_sha256': hashlib.sha256(open(os.path.join(R, 'flow_graph/plant_flow_graph.json'), 'rb').read()).hexdigest(),
               'patterns': ['flow_graph/views/*', 'media/pfd/*', 'media/D*.png', 'media/F0_campus.png', 'media/plant_phase_d.mp4']}, open(os.path.join(R, 'media/_generated.json'), 'w'), indent=1)
    print('derived views, PFDs, frames and video regenerated')
if __name__ == '__main__': main()
