import datetime, hashlib, json, pathlib, subprocess
R=pathlib.Path.cwd(); O=R/'Worker_Log/Milestone_02/evidence/M02_v2_independent'
def git(*a): return subprocess.check_output(['git',*a],text=True).strip()
head=git('rev-parse','HEAD'); base='a8098a43d46df76b981861aa8dec0522d31be966'; source='33daa6bebd91c49ad87f822d48cfa87e600deb6d'; predecessor='87146b4cc7fbd0b58d6688903a5ba081b813ac13'
m=json.loads((R/'Worker_Log/Milestone_02/evidence/M02_v2/source-input-manifest.json').read_text())
rows={p:dict(expected=h,working=hashlib.sha256((R/p).read_bytes()).hexdigest(),source_commit=hashlib.sha256(subprocess.check_output(['git','show',source+':'+p])).hexdigest()) for p,h in m['sha256'].items()}
assert len(rows)==127 and all(len(set(r.values()))==1 for r in rows.values())
old=[p for p in git('ls-tree','-r','--name-only',base,'Worker_Log/Milestone_02').splitlines() if '_v1' in p or '/M02_v1/' in p or '/M02_v1_independent/' in p]
oldrows={p:hashlib.sha256((R/p).read_bytes()).hexdigest() for p in old}
assert all((R/p).read_bytes()==subprocess.check_output(['git','show',base+':'+p]) for p in old)
protected=['docs/project-0/specs','environment','models','examples','fixtures']
assert not git('diff','--name-only',base,'HEAD','--',*protected)
assert not git('diff','--name-only',source,'HEAD','--','src','tests','fixtures','environment')
assert head=='6015a652c4a9a9c968ab7933c07ac7bbb4573e12'
assert subprocess.run(['git','merge-base','--is-ancestor',predecessor,head]).returncode==0
record=dict(head=head,source_commit=source,handoff_base=base,predecessor=predecessor,checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),source_input_count=len(rows),source_inputs=rows,unchanged_v1_count=len(oldrows),unchanged_v1_sha256=oldrows,unchanged_protected_paths=protected,repair_changed_files=git('diff','--name-only',base,source,'--','src','tests').splitlines(),source_to_head_diff=git('diff','--name-only',source,'HEAD','--','src','tests','fixtures','environment'),working_status=git('status','--short'),main=git('rev-parse','refs/remotes/origin/main'),development_predecessor_object=git('rev-parse',predecessor),development_remote_ref='not present locally; no network fetch performed')
(O/'snapshot-check.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({k:v for k,v in record.items() if k not in ('source_inputs','unchanged_v1_sha256')},indent=2))
