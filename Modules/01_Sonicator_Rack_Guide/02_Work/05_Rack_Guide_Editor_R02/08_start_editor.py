"""Visible, logged editor startup. No third-party dependency needed to report failure."""
from pathlib import Path
import argparse,importlib.metadata,json,os,subprocess,sys,traceback
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
def check_files(root=ROOT,here=HERE):
 required=[here/'01_editor.py',here/'02_interface.html',here/'03_generate.py',here/'parameters.py',here/'07_R20_reference_metadata.json',root/'Modules/01_Sonicator_Rack_Guide/01_References/01_ST_510_H_manufacturer_CAD.step',root/'Modules/01_Sonicator_Rack_Guide/01_References/05_VialTray_Grip24x20_Preview_R20.step']
 missing=[str(p) for p in required if not p.is_file()]
 if missing:raise FileNotFoundError('Extract the full editor ZIP; required files missing:\n'+'\n'.join(missing))
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--check-only',action='store_true');args=parser.parse_args()
 log_path=ROOT/'CAD_Editor_Start.log'
 with log_path.open('w',encoding='utf-8') as log:
  def emit(message):
   print(message,flush=True);log.write(str(message)+'\n');log.flush()
  try:
   emit('MOF CAD Editor startup');emit('Python: '+sys.version.split()[0]);emit('Program folder: '+str(ROOT));emit('Startup log: '+str(log_path))
   check_files()
   for package in ('cadquery','numpy','matplotlib'):emit(package+': '+importlib.metadata.version(package))
   emit('Files and installed packages checked.')
   if args.check_only:return 0
   env=os.environ.copy();env.update(PYTHONUTF8='1',PYTHONUNBUFFERED='1')
   with subprocess.Popen([sys.executable,'-u',str(HERE/'01_editor.py')],cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding='utf-8',errors='replace') as process:
    try:
     for line in process.stdout:emit(line.rstrip('\n'))
     code=process.wait()
    except KeyboardInterrupt:
     process.terminate();process.wait();emit('Editor stopped.');return 0
   if code:emit(f'Editor failed (exit {code}). Read this log for the traceback.')
   return code
  except Exception:
   emit(traceback.format_exc());return 1
if __name__=='__main__':raise SystemExit(main())
