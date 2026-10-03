from pathlib import Path
import json,math
p=Path(__file__).parent
v=json.loads((p/'validity_results.json').read_text());g=json.loads((p/'goil_matrix.json').read_text());r=json.loads((p/'rayoptics_summary.json').read_text())
# Compare actual extracted GOIL predictions with independent matrix values.
assert g['source_sha256']=='74c32acdda997b35bc2be62fe54884c36ed68af68c53575ee94ab702ce79c5b8'
assert len(v['grid'])==40 and sum(x['rays'] for x in v['grid'])==4040
assert r['passed'] and r['ray_comparisons']==4040
assert r['max_abs_image_intercept_difference_cm']<1e-9
for row in g['rows']:
 o=row['outputs']
 assert abs(o['q']-v['paraxial_q_cm'])<1e-10
 assert abs(o['f']-v['efl_cm'])<1e-10
 assert abs(o['m']-v['magnification'])<1e-10
 assert abs(o['yI']-v['magnification']*45*math.tan(math.radians(row['field'])))<1e-12
print('Reference grid, independent-library tolerance, tested source hash and GOIL matrix agree.')
