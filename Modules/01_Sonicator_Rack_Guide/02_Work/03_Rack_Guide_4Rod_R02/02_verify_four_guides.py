"""Independent planar contact-layout check; zero-clearance local approximation."""
import json
from pathlib import Path
import numpy as np
from parameters import GUIDE_LONG_SIDE_Z,GUIDE_END_X
# [translation X, translation Z, yaw radians] -> outward contact displacement
A=np.array([[-1,0,GUIDE_LONG_SIDE_Z],[1,0,GUIDE_LONG_SIDE_Z],[0,1,-GUIDE_END_X],[0,-1,-GUIDE_END_X]],dtype=float)
w=np.array([GUIDE_END_X,GUIDE_END_X,GUIDE_LONG_SIDE_Z,GUIDE_LONG_SIDE_Z],dtype=float)
w/=w.sum()
assert np.linalg.matrix_rank(A)==3
assert np.all(w>0) and np.linalg.norm(w@A)<1.e-10
out=Path(__file__).resolve().parents[2]/'03_Preview/03_Rack_Guide_4Rod_R02/12_Planar_contact_check_R02_4Rod.json'
d={'rank':3,'constraint_rows':A.tolist(),'positive_balancing_weights':w.tolist(),'meaning':'Offset four-side contacts locally bound X, Z and both yaw directions in zero-clearance approximation. This is not preload, vibration, tolerance or full-motion validation.'}
out.write_text(json.dumps(d,indent=2));print(json.dumps(d,indent=2))
