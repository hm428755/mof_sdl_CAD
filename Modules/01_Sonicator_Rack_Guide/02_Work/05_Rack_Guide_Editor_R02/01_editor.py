"""Local-only CAD editor. Standard library UI server; CAD runs in a child process."""
from pathlib import Path
import argparse,json,math,os,subprocess,sys,threading,time,webbrowser,secrets,tempfile
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from urllib.parse import urlparse,unquote
from datetime import datetime
HERE=Path(__file__).resolve().parent
MODULE=HERE.parents[1]
PROJECT=HERE.parents[3]
WINDOWS_STORAGE=r'C:\Users\yeonseo kim\Desktop\MOF_SDL\Hardware\CAD'
OUTPUT_PREF=HERE/'06_Output_Location_R02.json'
OUTPUT_SUBDIR=Path('Modules')/'01_Sonicator_Rack_Guide'/'03_Preview'/'05_Rack_Guide_Editor_R02'
def default_storage(windows=None):
 return WINDOWS_STORAGE if (os.name=='nt' if windows is None else windows) else str(PROJECT)
def load_storage():
 try:
  p=Path(json.loads(OUTPUT_PREF.read_text(encoding='utf-8'))['directory'])
  if p.is_absolute():return p
 except (OSError,ValueError,KeyError,TypeError):pass
 return Path(default_storage())
STORAGE=load_storage()
RESULTS=STORAGE/OUTPUT_SUBDIR
def validate_storage(raw):
 if not isinstance(raw,str) or not raw.strip():raise ValueError('저장할 폴더의 전체 경로를 입력하세요.')
 p=Path(raw.strip()).expanduser()
 if not p.is_absolute():raise ValueError('상대 경로 대신 C:\\Users\\... 같은 전체 경로를 입력하세요.')
 if p.exists() and not p.is_dir():raise ValueError('파일이 아닌 폴더 경로를 선택하세요.')
 return p.resolve()
def open_local_path(p):
 if os.name=='nt':os.startfile(str(p))
 elif sys.platform=='darwin':subprocess.Popen(['open',str(p)])
 else:raise ValueError('이 PC에서는 자동 열기를 지원하지 않습니다. 화면의 경로로 폴더를 여세요.')
LAST=HERE/'05_Last_Settings_R02.json'
# name,label,default,min,max,group; all dimensional entries mm.
FIELDS=[
 ('rack_width','랙 폭 X',85.48,70,115,'랙·상판'),('rack_length','랙 길이 Z',127.76,100,195,'랙·상판'),
 ('rack_height','랙 높이',45,12,60,'랙·상판'),('rack_gap','두 랙 사이 간격',24,14,80,'랙·상판'),
 ('opening_clearance','상판 통과 여유 / 한쪽',2,1,4,'랙·상판'),('frame_thickness','상판 두께',3,2,8,'랙·상판'),
 ('rod_diameter','봉 지름',10,6,12,'봉'),('rod_gap','랙–봉 틈새',1,.5,3,'봉'),
 ('bottom_gap','봉–바닥 높이',2,1,8,'봉'),('rod_chamfer','봉 양끝 모따기',1,.5,2,'봉'),
 ('side_offset','장변 봉: 중앙에서 이동',40,0,75,'봉'),('end_offset','단변 봉: 중앙에서 이동',30,0,45,'봉'),
 ('water_height','목표 수위 / 바닥 기준',11,2,30,'수위·바이알'),('finger_height','그리퍼 하단 / 바닥 기준',18,5,60,'수위·바이알'),
 ('sample_height','시료 액면 / 바닥 기준',10,1,30,'수위·바이알'),('vial_diameter','바이알 몸통 지름',16.6,10,19,'수위·바이알'),
 ('vial_height','바이알 높이',60,30,90,'수위·바이알')]
REFERENCE_TRAY=json.loads((HERE/'07_R20_reference_metadata.json').read_text(encoding='utf-8'))
RACK_MODELS={'uploaded_r20':'업로드 트레이 R20 · 원본 STEP','parametric':'간이 트레이 · 치수 직접 변경'}
DEFAULT={f[0]:float(f[2]) for f in FIELDS};DEFAULT.update(layout='centered',rack_model='uploaded_r20',show_vials=False)
LAYOUTS={'centered':'4봉 · 각 변 중앙','offset':'4봉 · 엇갈린 배치','eight':'8봉 · 회전 여유 감소'}
def validate_config(raw):
 if not isinstance(raw,dict):raise ValueError('설정 파일은 JSON 객체여야 합니다.')
 unknown=set(raw)-set(DEFAULT)
 if unknown:raise ValueError('알 수 없는 설정 항목: '+', '.join(sorted(unknown)))
 c={**DEFAULT,**raw}
 if 'rack_model' not in raw and any(k in raw for k in ('rack_width','rack_length','rack_height')):c['rack_model']='parametric'
 if c['rack_model']=='parametric':
  for k,v in {'rack_width':100.,'rack_length':190.,'rack_height':20.,'side_offset':60.,'end_offset':45.}.items():
   if k not in raw:c[k]=v
 if c['rack_model'] not in RACK_MODELS:raise ValueError('트레이 모델을 선택하세요.')
 if not isinstance(c['show_vials'],bool):raise ValueError('바이알 표시 설정은 참/거짓이어야 합니다.')
 if c['rack_model']=='uploaded_r20':
  c.update(rack_width=REFERENCE_TRAY['width_x'],rack_length=REFERENCE_TRAY['length_z'],rack_height=round(REFERENCE_TRAY['height'],6))
 if c['layout'] not in LAYOUTS:raise ValueError('봉 배치를 선택하세요.')
 for key,label,default,lo,hi,group in FIELDS:
  if isinstance(c[key],bool):raise ValueError(label+': 숫자를 입력하세요.')
  try:v=float(c[key])
  except (TypeError,ValueError):raise ValueError(label+': 숫자를 입력하세요.') from None
  if not math.isfinite(v) or not lo<=v<=hi:raise ValueError(f'{label}: {lo}~{hi} mm 범위로 입력하세요.')
  c[key]=v
 w,l,g=c['rack_width'],c['rack_length'],c['rack_gap'];d=c['rod_diameter'];gap=c['rod_gap']
 if g<2*(d+gap)+2:raise ValueError(f'중앙 봉 간격 확보를 위해 랙 사이를 {2*(d+gap)+2:g} mm 이상으로 늘리세요.')
 if d/2+gap-c['opening_clearance']-1.7-.25<1.5:raise ValueError('상판 체결홀 가장자리 살이 1.5 mm 미만입니다. 봉 지름/틈새를 늘리거나 통과 여유를 줄이세요.')
 if c['rod_chamfer']>=d/2-1.25:raise ValueError('모따기가 봉 탭 주변을 과도하게 깎습니다. 모따기를 줄이세요.')
 cx=(w+g)/2
 # Exact reference floor outer rounded rectangle, measured from manufacturer STEP.
 for x in (cx-w/2,cx+w/2):
  if math.hypot(max(abs(x)-98.5,0),max(l/2-68.5,0))>33.821:raise ValueError('랙 모서리가 수조 바닥 평탄부를 벗어납니다. 랙 크기/간격을 줄이세요.')
 if cx-(w/2+c['opening_clearance'])<1+3:raise ValueError('상판 중앙 레일 폭이 부족합니다. 랙 간격을 늘리세요.')
 if c['layout']!='centered':
  if c['side_offset']>l/2-6 or c['end_offset']>w/2-5:raise ValueError('봉 이동량이 랙 변을 벗어납니다. 이동량을 줄이세요.')
  if min(c['side_offset'],c['end_offset'])<5:raise ValueError('엇갈림/8봉 배치는 각 이동량을 5 mm 이상으로 설정하세요.')
 if c['rack_model']=='parametric':
  if 2*.11*w<c['vial_diameter']+.6+1:raise ValueError('바이알 홀 사이에 1 mm 여유가 없습니다. 랙 폭을 늘리거나 바이알 지름을 줄이세요.')
  if .236842*l<c['vial_diameter']+.6+1:raise ValueError('바이알 길이 방향 피치가 부족합니다.')
  if math.hypot(max(.11*w-5,0),max((22.5/190)*l-12,0))<c['vial_diameter']/2+.3+1:raise ValueError('중앙 그립 구멍과 바이알 홀 간격이 부족합니다. 랙 폭/길이를 늘리거나 바이알 지름을 줄이세요.')
 elif c['show_vials'] and c['vial_diameter']>REFERENCE_TRAY['vial_hole_diameter']-.2:raise ValueError('원본 트레이 홀은 Ø17.6 mm입니다. 참고 바이알 지름을 17.4 mm 이하로 설정하세요.')
 if not c['sample_height']<=c['water_height']<=c['finger_height']-5:raise ValueError('시료 액면 ≤ 수위 ≤ 그리퍼 하단−5 mm 조건을 맞추세요.')
 if c['water_height']>=c['rack_height']:raise ValueError('수위가 랙 윗면보다 낮아야 합니다.')
 return c

def derive_parameters(raw):
 c=validate_config(raw);w,l=c['rack_width'],c['rack_length'];cx=(w+c['rack_gap'])/2
 return dict(RACK_MODEL=c['rack_model'],SHOW_VIALS=c['show_vials'],VIAL_BASE_ABOVE_FLOOR=6 if c['rack_model']=='uploaded_r20' else 2,
 VIAL_POSITIONS=[(y,x) for x,y in REFERENCE_TRAY['native_hole_centers_xy']] if c['rack_model']=='uploaded_r20' else [(w*x,l*z) for x in (-.33,-.11,.11,.33) for z in (-67.5/190,-22.5/190,22.5/190,67.5/190)],
 RACK_WIDTH_X=w,RACK_LENGTH_Z=l,RACK_HEIGHT=c['rack_height'],RACK_CENTERS_X=(-cx,cx),
 OPENING_WIDTH_X=w+2*c['opening_clearance'],OPENING_LENGTH_Z=l+2*c['opening_clearance'],FRAME_THICKNESS=c['frame_thickness'],
 ROD_DIAMETER=c['rod_diameter'],ROD_RACK_GAP=c['rod_gap'],ROD_BOTTOM_GAP=c['bottom_gap'],ROD_CHAMFER=c['rod_chamfer'],
 GUIDE_LAYOUT=c['layout'],GUIDE_LONG_SIDE_Z=0 if c['layout']=='centered' else c['side_offset'],GUIDE_END_X=0 if c['layout']=='centered' else c['end_offset'],
 WATER_HEIGHT=c['water_height'],GRIPPER_FINGER_HEIGHT=c['finger_height'],SAMPLE_LIQUID_HEIGHT=c['sample_height'],
 VIAL_DIAMETER=c['vial_diameter'],VIAL_HEIGHT=c['vial_height'],VIAL_HOLE_DIAMETER=c['vial_diameter']+.6,
 VIAL_X_POSITIONS=tuple(w*v for v in (-.33,-.11,.11,.33)),VIAL_Z_POSITIONS=tuple(l*v for v in (-67.5/190,-22.5/190,22.5/190,67.5/190)))

def allocate_run():
 RESULTS.mkdir(parents=True,exist_ok=True)
 # Atomic mkdir, never reuse a completed or failed output folder.
 start=1+max((int(p.name.split('_',1)[0]) for p in RESULTS.iterdir() if p.name.split('_',1)[0].isdigit()),default=0)
 for i in range(start,100000):
  p=RESULTS/f'{i:02d}_Editor_R02'
  try:p.mkdir();return p
  except FileExistsError:continue
 raise RuntimeError('생성 폴더가 너무 많습니다.')

class JobManager:
 def __init__(self):self.lock=threading.RLock();self.job=None;self.process=None;self.directories={}
 def set_storage(self,raw):
  global STORAGE,RESULTS
  with self.lock:
   if self.job and self.job["status"]=="running":raise ValueError("생성이 끝난 뒤 저장 위치를 변경하세요.")
   p=validate_storage(raw);p.mkdir(parents=True,exist_ok=True)
   with tempfile.TemporaryFile(dir=p):pass
   OUTPUT_PREF.write_text(json.dumps({"directory":str(p)},ensure_ascii=False,indent=2),encoding="utf-8")
   STORAGE=p;RESULTS=p/OUTPUT_SUBDIR
   return {"directory":str(STORAGE),"results":str(RESULTS)}
 def start(self,raw):
  c=validate_config(raw)
  with self.lock:
   if self.job and self.job['status']=='running':raise ValueError('CAD를 생성 중입니다. 완료 후 다시 실행하세요.')
   folder=allocate_run();config=folder/'00_Input_settings_R02.json';config.write_text(json.dumps(c,ensure_ascii=False,indent=2),encoding='utf-8')
   LAST.write_text(json.dumps(c,ensure_ascii=False,indent=2),encoding='utf-8')
   key=secrets.token_hex(8);self.directories[key]=folder
   self.job={'id':key,'status':'running','folder':str(folder),'log':'CAD 형상을 생성하고 있습니다. 잠시 기다려 주세요.','files':[],'checks':None}
   self.process=None
   threading.Thread(target=self.worker,args=(folder,config),daemon=True).start()
   return self.snapshot()
 def worker(self,folder,config):
  proc=None
  try:
   env=os.environ.copy();env.update(MOF_CAD_CONFIG=str(config),MOF_CAD_OUTPUT=str(folder),PYTHONUNBUFFERED='1',PYTHONUTF8='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
   flags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0
   with (folder/'10_Generation_log_R02.txt').open('w',encoding='utf-8') as log:
    with self.lock:
     proc=subprocess.Popen([sys.executable,str(HERE/'03_generate.py')],cwd=HERE,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=flags)
     self.process=proc
    rc=proc.wait()
   summary=folder/'09_Result_summary_R02.json'
   if rc or not summary.exists():raise RuntimeError('CAD 생성 또는 간섭 검사에 실패했습니다. 생성 로그의 마지막 오류를 확인하세요.')
   result=json.loads(summary.read_text(encoding='utf-8'))
   with self.lock:self.job.update(status='done',log='생성과 형상 검사를 마쳤습니다. STEP은 CAD 프로그램에서 열어 확인하세요.',checks=result['checks'],files=sorted(p.name for p in folder.iterdir() if p.is_file()))
  except Exception as e:
   with self.lock:self.job.update(status='failed',log=str(e),files=sorted(p.name for p in folder.iterdir() if p.is_file()))
  finally:
   with self.lock:
    if self.process is proc:self.process=None
 def snapshot(self):
  with self.lock:
   if not self.job:return {'status':'idle'}
   d=dict(self.job);p=Path(d['folder'])/'10_Generation_log_R02.txt'
   d['details']=p.read_text(encoding='utf-8',errors='replace')[-7000:] if p.exists() else ''
   return d

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--no-browser',action='store_true');parser.add_argument('--port',type=int,default=0);args=parser.parse_args()
 jobs=JobManager();token=secrets.token_urlsafe(24)
 class Handler(BaseHTTPRequestHandler):
  def log_message(self,*args):pass
  def send(self,status,data,kind='application/json; charset=utf-8'):
   b=json.dumps(data,ensure_ascii=False).encode() if isinstance(data,(dict,list)) else data
   if isinstance(b,str):b=b.encode('utf-8')
   self.send_response(status);self.send_header('Content-Type',kind);self.send_header('Content-Length',str(len(b)));self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.end_headers();self.wfile.write(b)
  def do_GET(self):
   path=unquote(urlparse(self.path).path)
   if path=='/':
    try:
     saved=json.loads(LAST.read_text(encoding='utf-8'));current=validate_config(saved) if 'rack_model' in saved else DEFAULT
    except (OSError,ValueError):current=DEFAULT
    boot={'config':current,'fields':FIELDS,'layouts':LAYOUTS,'rack_models':RACK_MODELS,'tray_metadata':REFERENCE_TRAY,'token':token,'root':str(PROJECT),'output_root':str(STORAGE),'output_base':str(RESULTS)}
    html=(HERE/'02_interface.html').read_text(encoding='utf-8').replace('__BOOT__',json.dumps(boot,ensure_ascii=False).replace('<','\\u003c'))
    return self.send(200,html,'text/html; charset=utf-8')
   if path=='/api/status':return self.send(200,jobs.snapshot())
   if path.startswith('/result/'):
    bits=path.split('/')
    if len(bits)!=4 or Path(bits[2]).name!=bits[2] or Path(bits[3]).name!=bits[3] or not bits[2] or not bits[3]:return self.send(400,{'error':'잘못된 파일 경로'})
    with jobs.lock:folder=jobs.directories.get(bits[2])
    if folder is None:return self.send(404,{'error':'파일 없음'})
    f=(folder/bits[3]).resolve()
    if f.parent!=folder.resolve() or not f.is_file():return self.send(404,{'error':'파일 없음'})
    kind='image/png' if f.suffix=='.png' else 'application/octet-stream'
    return self.send(200,f.read_bytes(),kind)
   self.send(404,{'error':'찾을 수 없습니다.'})
  def do_POST(self):
   if self.headers.get('X-Editor-Token')!=token:return self.send(403,{'error':'편집기를 새로 열어 주세요.'})
   try:
    size=int(self.headers.get('Content-Length','0'))
    if size<0 or size>20000:raise ValueError('설정 파일이 너무 큽니다.')
    data=json.loads(self.rfile.read(size).decode('utf-8'))
    if self.path=='/api/output':return self.send(200,jobs.set_storage(data.get('directory')))
    if self.path=='/api/output/open':
     STORAGE.mkdir(parents=True,exist_ok=True);open_local_path(STORAGE);return self.send(200,{'ok':True})
    if self.path=='/api/validate':return self.send(200,{'config':validate_config(data)})
    if self.path=='/api/generate':return self.send(200,jobs.start(data))
    if self.path=='/api/open':
     job=jobs.snapshot()
     if job['status']=='idle':raise ValueError('먼저 CAD를 생성하세요.')
     f=Path(job['folder'])
     if data.get('file'):
      name=data['file']
      if name not in job['files']:raise ValueError('생성된 파일만 열 수 있습니다.')
      if job['status']!='done':raise ValueError('완료된 CAD만 열 수 있습니다.')
      f=f/name
     open_local_path(f)
     return self.send(200,{'ok':True})
    if self.path=='/api/quit':
     if jobs.snapshot()['status']=='running':raise ValueError('생성 작업이 끝난 후 종료하세요.')
     self.send(200,{'ok':True});threading.Thread(target=server.shutdown,daemon=True).start();return
    self.send(404,{'error':'찾을 수 없습니다.'})
   except (ValueError,OSError) as e:self.send(400,{'error':str(e)})
 server=ThreadingHTTPServer(('127.0.0.1',args.port),Handler)
 url=f'http://127.0.0.1:{server.server_port}/'
 print('MOF CAD editor:',url,flush=True)
 print('Keep this window open. If the browser does not open, paste the URL above into your browser.',flush=True)
 if not args.no_browser:threading.Timer(.4,lambda:webbrowser.open(url)).start()
 try:server.serve_forever()
 except KeyboardInterrupt:pass
 finally:server.server_close()
if __name__=='__main__':main()
