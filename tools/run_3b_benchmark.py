from pathlib import Path
import subprocess,sys,os,json,time,hashlib,http.client
from datetime import datetime,timezone,timedelta

ROOT=Path(__file__).resolve().parent.parent
PKG=ROOT
OUT=ROOT/'evaluation_3b';OUT.mkdir(exist_ok=True)
RESULTS=OUT/'private_raw';RESULTS.mkdir(exist_ok=True)
PREFIX='llama32_3b_20261112'
phases=[('agg',PREFIX+'_agg_F_NL'),('proc',PREFIX+'_proc_en')]
env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1';env['PYTHONIOENCODING']='utf-8'
cfg=json.loads((PKG/'config.json').read_text('utf-8-sig'))
assert cfg['model']=='mai-sma-llama3.2-8k:3b'
assert cfg['base_url']=='http://127.0.0.1:11964/v1'
record={'started_at':datetime.now(timezone(timedelta(hours=9))).isoformat(),'base_model':'llama3.2:3b','alias_model':cfg['model'],'config':cfg,'python':sys.version.split()[0],'tasks':{},'evaluation_overrides':{'timeout_sec':180,'retries':0,'agg_condition':'F','agg_phrasing':'NL','proc_language':'en','output_tokens':{'agg':400,'proc':2200}},'source_sha256':{str(p.relative_to(PKG)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [PKG/'eval/run_eval.py',PKG/'eval/eval_from_config.py',PKG/'app/build_prompt100.py']}}
try:
    con=http.client.HTTPConnection('127.0.0.1',11964,timeout=5);con.request('GET','/api/tags');models=json.load(con.getresponse());con.close()
    model=next(m for m in models['models'] if m['name']==cfg['model'])
    record['model_identity']={k:model.get(k) for k in ['name','digest','size','details']}
except Exception as e:record['identity_error']=str(e)
def save(): (OUT/'run_manifest.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),'utf-8')
save()
for task,tag in phases:
    command=[sys.executable,'-B','eval/eval_from_config.py','--task',task,'--ids','all','--tag',tag,'--out-dir',str(RESULTS),'--timeout','180','--retries','0','--resume']
    if task=='agg':command+=['--cond','F','--phrasing','NL']
    else:command+=['--lang','en']
    logpath=OUT/(task+'_execution.log')
    print(json.dumps({'event':'start','task':task,'items':100,'tag':tag}),flush=True)
    began=time.time();record['tasks'][task]={'command':command[2:],'state':'running','started_at':datetime.now(timezone(timedelta(hours=9))).isoformat()};save()
    with logpath.open('w',encoding='utf-8') as log:
        process=subprocess.Popen(command,cwd=str(PKG),env=env,stdout=log,stderr=subprocess.STDOUT)
        last=-1
        while process.poll() is None:
            journal=RESULTS/(tag+'.jsonl')
            n=0
            if journal.exists():
                with journal.open(encoding='utf-8') as f:
                    for line in f:
                        try:json.loads(line);n+=1
                        except json.JSONDecodeError:pass
            if n!=last:
                print(json.dumps({'event':'progress','task':task,'completed':n,'total':100,'elapsed_sec':round(time.time()-began)}),flush=True);last=n
            time.sleep(3)
    record['tasks'][task].update(state='complete' if process.returncode==0 else 'failed',exit_code=process.returncode,elapsed_sec=round(time.time()-began,2));save()
    print(json.dumps({'event':'phase_finished','task':task,'exit_code':process.returncode,'elapsed_sec':round(time.time()-began)}),flush=True)
    if process.returncode:break
record['ended_at']=datetime.now(timezone(timedelta(hours=9))).isoformat();save()
print(json.dumps({'event':'run_finished','states':{t:v['state'] for t,v in record['tasks'].items()}}),flush=True)
