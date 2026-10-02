"""Run unchanged installed validator; redirect only output logs/prep/latest paths."""
import hashlib,json,pathlib,runpy,sys
root=pathlib.Path('/workspace/atom-mlmm-g04-v2'); out=pathlib.Path(__file__).resolve().parent
validator=root/'validate.py'
assert validator.read_bytes()==pathlib.Path('environment/cloud-cpu/validate.py').read_bytes()
def prior():
 files=[root/'latest-validation.json',*(root/'logs').rglob('*')]
 return {str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files if p.is_file()}
before=prior()
with (out/'strict-original-outputs-before.json').open('x') as f:json.dump(before,f,indent=2)
original=pathlib.Path.__truediv__
def redirected(self,key):
 if self==root and str(key)=='logs':return original(out,'strict-logs')
 if self==root and str(key)=='latest-validation.json':return original(out,'strict-latest-validation.json')
 return original(self,key)
sys.argv=[str(validator),'--repository',str(pathlib.Path.cwd())]
print('Unchanged validator sha256',hashlib.sha256(validator.read_bytes()).hexdigest())
print('Output redirects:',str(root/'logs'),'->',str(out/'strict-logs'),'; latest ->',str(out/'strict-latest-validation.json'))
pathlib.Path.__truediv__=redirected
try:
 runpy.run_path(str(validator),run_name='__main__')
finally:
 pathlib.Path.__truediv__=original
 after=prior()
 with (out/'strict-original-outputs-after.json').open('x') as f:json.dump(after,f,indent=2)
 assert before==after,'external prior outputs changed'
