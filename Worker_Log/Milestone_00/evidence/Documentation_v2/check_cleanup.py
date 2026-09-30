#!/usr/bin/env python3
"""Snapshot-specific cleanup regression evidence; not molecular qualification."""
from pathlib import Path
import argparse, collections, hashlib, json, re, sys, zipfile

def section(text, name):
    m = re.search(r'^## '+re.escape(name)+r'\n(.*?)(?=^## |\Z)', text, re.M|re.S)
    return m.group(1).strip() if m else ''

def check(root, original):
    errors=[]
    def require(ok, msg):
        if not ok: errors.append(msg)
    def old(rel): return original[rel].decode('utf-8')
    def new(rel): return (root/rel).read_text()
    require((root/'README.md').is_file(),'one root README is required')
    require(not (root/'docs/project-0/plan-index.json').exists(),'retire the duplicate live JSON index')
    require(not (root/'docs/project-0/TEST_CATALOG.md').exists(),'retire the duplicate planned-test catalog')
    require(not list(root.glob('Worker_Log/Milestone_*/README.md')),'remove placeholder milestone READMEs')
    require('Project_0_ATM_MLMM_environment.yml' not in new('ATM_MLMM_Environment.md'),'environment commands must name the actual YAML')
    require('ENVIRONMENT.md' not in new('ATM_MLMM_environment.yml'),'YAML must point to the actual environment guide')
    def substantive_yaml(s): return '\n'.join(x for x in s.splitlines() if x.strip() and not x.lstrip().startswith('#'))
    require(substantive_yaml(old('ATM_MLMM_environment.yml'))==substantive_yaml(new('ATM_MLMM_environment.yml')),'do not change environment dependency values')
    counts={'gates':0,'tasks':0,'planned_tests':0,'requirements':0}
    for rel in original:
        if re.fullmatch(r'docs/project-0/gates/G\d\d-.*\.md',rel):
            counts['gates']+=1
            require((root/rel).exists(),f'keep {rel}')
            if not (root/rel).exists(): continue
            a,b=old(rel),new(rel)
            rows=lambda s: re.findall(r'^\| P0-TEST-.*$',s,re.M)
            require(rows(a)==rows(b),f'preserve exact assertions/nodes/requirement links in {rel}')
            counts['planned_tests']+=len(rows(b))
            tasks=lambda s: re.findall(r'^### (G\d\d-T\d+):',s,re.M)
            require(tasks(a)==tasks(b),f'preserve task IDs in {rel}')
            counts['tasks']+=len(tasks(b))
            for tid in tasks(a):
                pat=r'^### '+re.escape(tid)+r':.*?\n(.*?)(?=^### |^## |\Z)'
                ta=re.search(pat,a,re.M|re.S).group(1)
                tb=re.search(pat,b,re.M|re.S).group(1)
                for para in ta.strip().split('\n\n'):
                    if para.startswith('**Finish this part with:'): continue
                    norm=lambda text: re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', text)
                    require(norm(para) in norm(tb),f'preserve task-specific text for {tid}')
    r='docs/project-0/REQUIREMENTS.md'
    reqrows=lambda s: [x.split('|')[1:5] for x in s.splitlines() if x.startswith('| P0-REQ-')]
    require(reqrows(old(r))==reqrows(new(r)),'preserve all requirement IDs, behavior, owner and specification')
    counts['requirements']=len(reqrows(new(r)))
    active='\n'.join(p.read_text() for p in root.glob('docs/project-0/specs/S*.md'))+'\n'+'\n'.join(p.read_text() for p in root.glob('docs/project-0/gates/G*.md'))
    math=lambda s: re.findall(r'\$\$.*?\$\$|(?<!\$)\$(?!\$)[^\n$]+\$',s,re.S)
    scientific=[r for r in original if re.fullmatch(r'docs/project-0/specs/S\d\d-.*\.md',r)]
    scientific+=['docs/project-0/reference/scientific-notes.md','docs/project-0/guides/spec-and-test-workflow.md']
    required=set(x for r in scientific for x in math(old(r)))
    require(required<=set(math(active)),'preserve every scientific expression from specs and merged notes')
    counts['distinct_preserved_math_expressions']=len(required)
    for rel in original:
        if rel.startswith('Worker_Log/Milestone_00/evidence/Documentation_v1/') or rel=='Worker_Log/Milestone_00/Documentation_v1_worker.md' or rel.startswith('Original_planning_docs/') or rel.endswith('/original-brainstorming-plan.md'):
            require((root/rel).is_file() and (root/rel).read_bytes()==original[rel],f'preserve historical bytes: {rel}')
    closers={'M01':'G01','M02':'G03','M03':'G07','M04':'G08','M05':'G10','M06':'G11','M07':'G12','M08':'G13'}
    for mid,gid in closers.items():
        src=next(r for r in original if r.startswith('docs/project-0/milestones/'+mid+'-'))
        dest=next(root.glob('docs/project-0/gates/'+gid+'-*.md'))
        require(section(old(src),'Combined review: what to check and why') in dest.read_text(),f'preserve combined review for {mid}')
    for p in root.rglob('*'):
        require(p.name not in ('.DS_Store','__MACOSX','.git') and not p.name.startswith('._'),f'no metadata in clean tree: {p.relative_to(root)}')
    if (root/'README.md').is_file():
        roadmap=new('README.md')
        baseline=json.loads(old('docs/project-0/plan-index.json'))
        prereq=section(roadmap,'Roadmap').split('### Gate prerequisites',1)[-1]
        for g in baseline['gates']:
            row=next((line for line in prereq.splitlines() if line.startswith('| ['+g['id']+'](')), '')
            cells=row.split('|')
            actual=re.findall(r'\[(G\d\d)\]',cells[2]) if len(cells)>2 else []
            require(actual==g['depends_on'],f'preserve direct dependencies for {g["id"]}')
        for m in baseline['milestones']:
            row=next((line for line in roadmap.splitlines() if line.startswith('| ['+m['id']+'](')), '')
            cells=row.split('|')
            actual=re.findall(r'\[(M\d\d)\]',cells[4]) if len(cells)>4 else []
            require(actual==m['depends_on'],f'preserve earlier milestone reviews for {m["id"]}')
    return {'errors':errors,'counts':counts,'scope':'cleanup preservation only; not scientific implementation or installation'}

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('--root',type=Path,default=Path.cwd()); ap.add_argument('--original',type=Path); ap.add_argument('--output',type=Path); args=ap.parse_args()
    if args.original:
        original={p.relative_to(args.original).as_posix():p.read_bytes() for p in args.original.rglob('*') if p.is_file() and '.git' not in p.parts and p.name!='.DS_Store' and not p.name.startswith('._')}
    else:
        snapshot=args.root/'Worker_Log/Milestone_00/evidence/Documentation_v2/snapshot_before_cleanup.zip'
        with zipfile.ZipFile(snapshot) as z:
            original={i.filename[len('AToM_MLMM/'):]:z.read(i) for i in z.infolist() if not i.is_dir() and i.filename.startswith('AToM_MLMM/')}
    result=check(args.root.resolve(),original); output=json.dumps(result,indent=2)+'\n'; print(output)
    if args.output: args.output.write_text(output)
    sys.exit(bool(result['errors']))
