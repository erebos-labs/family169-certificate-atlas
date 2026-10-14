"""External CLI corruption probes; originals remain untouched."""
from pathlib import Path
from collections import Counter
from copy import deepcopy
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import time

import argparse
ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('package',type=Path)
ap.add_argument('--output',type=Path,required=True)
a=ap.parse_args()
package=a.package.resolve()
root=a.output.resolve()
root.mkdir(parents=True,exist_ok=False)
(root/'logs').mkdir()
catalog=json.loads((package/'atlas/atlas.json').read_text())
entry=next(x for x in catalog['graphs'] if x['h']==[2,3,3])
original=json.loads((package/'atlas'/entry['path']).read_text())
rows=[]
start=time.perf_counter()

def summary(obj):
    c=Counter((tuple(x['partition']),x['degree']) for x in obj['witness'])
    obj['elementary']=[{'partition':list(p),'q_coefficients':[c[p,d] for d in range(3)]}
                      for p in sorted({p for p,d in c})]

def run_case(name, mutate, expected, optimized=False, basis=False, accepted=False):
    with tempfile.TemporaryDirectory(prefix='probe-',dir=root) as d:
        p=Path(d)
        shutil.copytree(package/'atlas',p/'atlas')
        cat=deepcopy(catalog)
        obj=deepcopy(original)
        if basis:
            bp=p/'atlas/basis/n03.json'
            data=json.loads(bp.read_text()); mutate(data)
            bp.write_text(json.dumps(data))
        else:
            mutate(obj)
            fp=p/'atlas'/entry['path']
            fp.write_text(json.dumps(obj))
            for x in cat['graphs']:
                if x['path']==entry['path']:
                    x['sha256']=hashlib.sha256(fp.read_bytes()).hexdigest()
            (p/'atlas/atlas.json').write_text(json.dumps(cat))
        command=[sys.executable]+(['-O'] if optimized else [])+[str(package/'src/verify.py'),'--atlas',str(p/'atlas'),'--min-n','3','--max-n','3']
        if accepted:
            command.append('--skip-basis')
        result=subprocess.run(command,capture_output=True,text=True,timeout=30)
        output=result.stdout+result.stderr
        assert (result.returncode==0)==accepted,(name,optimized,output)
        assert expected in output,(name,optimized,output)
        rows.append({'case':name,'optimized':optimized,'return_code':result.returncode,'expected':expected,'accepted_as_intended':accepted})
        (root/'logs'/f'probe-{name}-{int(optimized)}.log').write_text(output)

def wrong_partition(o):
    next(x for x in o['witness'] if x['permutation']==[1,3,2])['partition']=[3]
    summary(o)

def swapped_degrees(o):
    o['witness'][0]['degree'],o['witness'][-1]['degree']=o['witness'][-1]['degree'],o['witness'][0]['degree']
    summary(o)

def forbidden(o):
    o['witness'][1]['permutation']=[3,1,2]

def bool_degree(o):
    o['witness'][0]['degree']=False

def raw_missing(o):
    o['monomials'].pop()

def inverse(o):
    o['inverse_rows_lambda_columns_mu'][0][0]+=1

def matrix(o):
    o['matrix_rows_mu_columns_lambda'][0][0]+=1

def determinant(o):
    o['determinant']=-o['determinant']

for optimized in (False,True):
    for name,mutation,error in [('consistent_wrong_partition',wrong_partition,'coefficient_identity'),('inverted_degree_convention',swapped_degrees,'wrong_graph_inversion_degree'),('forbidden_nonedge_descent',forbidden,'nonpermitted_permutation'),('boolean_degree',bool_degree,'degree_bound'),('missing_raw_term',raw_missing,'colouring_table_mismatch')]:
        run_case(name,mutation,error,optimized)
    for name,mutation,error in [('basis_inverse',inverse,'basis_inverse_product'),('basis_matrix',matrix,'basis_matrix'),('basis_determinant',determinant,'basis_determinant')]:
        run_case(name,mutation,error,optimized,basis=True)
    run_case('core_ignores_basis',matrix,'verification_pass',optimized,basis=True,accepted=True)

# Independently recompute the RHS after the consistent wrong-partition mutation.
import independent_audit as I
bad=deepcopy(original); wrong_partition(bad)
bins=Counter((tuple(x['partition']),x['degree']) for x in bad['witness'])
raw,_=I.polynomial(3,[(0,1),(1,2)],3)
rhs={(a,d):sum(c*I.elementary_coefficient(p,a) for (p,degree),c in bins.items() if degree==d)
     for a in I.compositions(3,3) for d in range(3)}
rhs={k:c for k,c in rhs.items() if c}
assert rhs!=dict(raw)
rows.append({'case':'independent_wrong_partition','rejected':True})

result={'event':'additional_probes_pass','probes':rows,'rejections':17,'intentional_acceptances':2,'seconds':time.perf_counter()-start}
(root/'additional-probes.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result),flush=True)
