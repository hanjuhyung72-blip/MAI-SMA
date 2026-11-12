"""Recompute public scalar metrics from local, non-public evaluator JSONL files."""
from pathlib import Path
import sys,json,csv,importlib.util
root=Path(__file__).resolve().parent.parent
raw=root/'evaluation_3b/private_raw'
out=root/'results/llama32_3b';out.mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location('student_eval',root/'eval/run_eval.py')
ev=importlib.util.module_from_spec(spec);spec.loader.exec_module(ev)
tags={'agg':'llama32_3b_20261112_agg_F_NL','proc':'llama32_3b_20261112_proc_en'}
records={t:[json.loads(s) for s in (raw/(tag+'.jsonl')).read_text('utf-8').splitlines() if s.strip()] for t,tag in tags.items()}
assert all(len(v)==100 and len({r['qid'] for r in v})==100 for v in records.values())
stats={'aggregate':ev.agg_stats(records['agg']),'procedural':ev.proc_stats(records['proc'])}
(out/'recomputed_metrics.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2),'utf-8')
fields=['task','qid','strict','norm','answer_type','difficulty','abstained','json_valid','cls','n_steps','n_exact','n_misrec','n_halluc','sec','total_sec','completion_tokens','finish_reason']
with (out/'item_metrics.csv').open('w',encoding='utf-8-sig',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
    for rows in records.values():
        for record in rows:writer.writerow({k:record.get(k,'') for k in fields})
print('Public metrics recomputed. Questions, records and response text were omitted.')
