"""Standalone R02 generator. Preserves R01. No original project router available."""
from pathlib import Path
import os,math,json,hashlib
import tempfile
os.environ.setdefault('MPLCONFIGDIR',str(Path(tempfile.gettempdir())/'mof_sdl_matplotlib'))
import cadquery as cq
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Circle,FancyBboxPatch
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from parameters import *
import runpy
editor=runpy.run_path(str(Path(__file__).with_name('01_editor.py')))
config=editor['validate_config'](json.loads(Path(os.environ['MOF_CAD_CONFIG']).read_text(encoding='utf-8')))
globals().update(editor['derive_parameters'](config))
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(os.environ['MOF_CAD_OUTPUT'])
OUT.mkdir(parents=True,exist_ok=True)
parts=[]
rod_shapes=[]
rack_shapes=[]
plate_shapes=[]
checks={}
EPS=.1 # boolean operation overrun only, not a design dimension
STEEL=(.18,.48,.70)
ORANGE=(.92,.55,.12)
GREEN=(.30,.65,.44)
def box(x,y,z,center):return cq.Workplane('XY').box(x,y,z).translate(center).val()
def cyl(radius,y0,y1,x,z):return cq.Solid.makeCylinder(radius,y1-y0,cq.Vector(x,y0,z),cq.Vector(0,1,0))
def add(name,shape,color):
 assert shape.isValid(),name
 parts.append((name,shape,color))
def local_rods(cx):
 dx=RACK_WIDTH_X/2+ROD_RACK_GAP+ROD_DIAMETER/2
 dz=RACK_LENGTH_Z/2+ROD_RACK_GAP+ROD_DIAMETER/2
 if GUIDE_LAYOUT=='eight':
  return [(cx+x,z,'x') for x in (-dx,dx) for z in (-GUIDE_LONG_SIDE_Z,GUIDE_LONG_SIDE_Z)]+[(cx+x,z,'z') for x in (-GUIDE_END_X,GUIDE_END_X) for z in (-dz,dz)]
 return [(cx-dx,GUIDE_LONG_SIDE_Z,'x'),(cx+dx,-GUIDE_LONG_SIDE_Z,'x'),(cx-GUIDE_END_X,dz,'z'),(cx+GUIDE_END_X,-dz,'z')]

def capsule(x,z,axis):
 d=SLOT_TOTAL_TRAVEL/2
 a=cyl(SLOT_DIAMETER/2,RIM_Y-EPS,RIM_Y+FRAME_THICKNESS+EPS,x-(d if axis=='x' else 0),z-(d if axis=='z' else 0))
 b=cyl(SLOT_DIAMETER/2,RIM_Y-EPS,RIM_Y+FRAME_THICKNESS+EPS,x+(d if axis=='x' else 0),z+(d if axis=='z' else 0))
 bridge=box(SLOT_TOTAL_TRAVEL if axis=='x' else SLOT_DIAMETER,FRAME_THICKNESS+2*EPS,SLOT_DIAMETER if axis=='x' else SLOT_TOTAL_TRAVEL,(x,RIM_Y+FRAME_THICKNESS/2,z))
 return a.fuse(b).fuse(bridge)
ref_path=ROOT/'01_References'/'01_ST_510_H_manufacturer_CAD.step'
ref=cq.importers.importStep(str(ref_path)).val()
bb=ref.BoundingBox()
checks['manufacturer_bbox_mm']=[bb.xlen,bb.ylen,bb.zlen]
checks['manufacturer_solid_count']=len(ref.Solids())
checks['manufacturer_sha256']=hashlib.sha256(ref_path.read_bytes()).hexdigest()
parts.append(('Manufacturer_REFERENCE_shells',ref,(.64,.66,.69)))
for index,cx in enumerate(RACK_CENTERS_X):
 label='Left' if cx<0 else 'Right'
 xmin,xmax=(-FRAME_WIDTH_X/2,-PLATE_SPLIT_GAP/2) if cx<0 else (PLATE_SPLIT_GAP/2,FRAME_WIDTH_X/2)
 plate=box(xmax-xmin,FRAME_THICKNESS,FRAME_LENGTH_Z,((xmin+xmax)/2,RIM_Y+FRAME_THICKNESS/2,0))
 plate=plate.cut(box(OPENING_WIDTH_X,FRAME_THICKNESS+2*EPS,OPENING_LENGTH_Z,(cx,RIM_Y+FRAME_THICKNESS/2,0)))
 for x,z,axis in local_rods(cx):plate=plate.cut(capsule(x,z,axis))
 add(label+'_independent_top_plate',plate,STEEL if cx<0 else (.16,.60,.68))
 plate_shapes.append(plate)
 for j,(x,z,axis) in enumerate(local_rods(cx)):
  name=label+'_Guide_%02d'%(j+1)
  rod=cyl(ROD_DIAMETER/2,FLOOR_Y+ROD_BOTTOM_GAP,RIM_Y,x,z)
  rod=cq.Workplane(obj=rod).edges('%CIRCLE').chamfer(ROD_CHAMFER).val()
  rod=rod.cut(cyl(TAP_MINOR_DIAMETER/2,RIM_Y-TAP_DEPTH,RIM_Y+EPS,x,z))
  add(name,rod,ORANGE)
  rod_shapes.append((name,rod))
  yhead=RIM_Y+FRAME_THICKNESS+WASHER_THICKNESS
  screw=cyl(SCREW_HEAD_DIAMETER/2,yhead,yhead+SCREW_HEAD_HEIGHT,x,z).fuse(cyl(SCREW_DIAMETER/2,RIM_Y-SCREW_ENGAGEMENT,yhead,x,z))
  add(label+'_M3_screw_envelope_%02d'%j,screw,(.28,.28,.30))
  washer=cyl(WASHER_DIAMETER/2,RIM_Y+FRAME_THICKNESS,yhead,x,z).cut(cyl(WASHER_INNER_DIAMETER/2,RIM_Y+FRAME_THICKNESS-EPS,yhead+EPS,x,z))
  add(label+'_washer_envelope_%02d'%j,washer,(.55,.55,.56))
 if RACK_MODEL=='uploaded_r20':
  tray_path=ROOT/'01_References'/'05_VialTray_Grip24x20_Preview_R20.step'
  tray_original=cq.importers.importStep(str(tray_path)).val()
  assert hashlib.sha256(tray_path.read_bytes()).hexdigest()==editor['REFERENCE_TRAY']['source_sha256']
  rack=tray_original.rotate((0,0,0),(1,1,1),-120).translate((cx,FLOOR_Y,0))
  assert abs(rack.Volume()-tray_original.Volume())<1.e-5
 else:
  rack=box(RACK_WIDTH_X,RACK_HEIGHT,RACK_LENGTH_Z,(cx,FLOOR_Y+RACK_HEIGHT/2,0))
  for x,z in VIAL_POSITIONS:rack=rack.cut(cyl(VIAL_HOLE_DIAMETER/2,FLOOR_Y-EPS,FLOOR_Y+RACK_HEIGHT+EPS,cx+x,z))
  rack=rack.cut(box(GRIP_HOLE_X,RACK_HEIGHT+2*EPS,GRIP_HOLE_Z,(cx,FLOOR_Y+RACK_HEIGHT/2,0)))
 if SHOW_VIALS:
  for i,(x,z) in enumerate(VIAL_POSITIONS):
   vial=cyl(VIAL_DIAMETER/2,FLOOR_Y+VIAL_BASE_ABOVE_FLOOR,FLOOR_Y+VIAL_BASE_ABOVE_FLOOR+VIAL_HEIGHT,cx+x,z)
   assert vial.intersect(rack).Volume()<1.e-5
   add(label+'_Vial_REFERENCE_%02d'%i,vial,(.60,.80,.87))
 rack_shapes.append(rack)
 add(label+'_Rack_REFERENCE_'+RACK_MODEL,rack,(.88,.33,.21) if cx<0 else (.58,.36,.77))
 # External locator tabs belong to this independent half, not to the neighboring half.
 sx=-1 if cx<0 else 1
 x_outer=sx*(FRAME_WIDTH_X/2+LOCATOR_RIM_GAP+LOCATOR_THICKNESS/2)
 for sz in (-1,1):
  z1=sz*(FRAME_LENGTH_Z/2+LOCATOR_RIM_GAP+LOCATOR_THICKNESS-LOCATOR_ARM_LENGTH/2)
  x2=sx*(FRAME_WIDTH_X/2+LOCATOR_RIM_GAP+LOCATOR_THICKNESS-LOCATOR_ARM_LENGTH/2)
  z_outer=sz*(FRAME_LENGTH_Z/2+LOCATOR_RIM_GAP+LOCATOR_THICKNESS/2)
  tab=box(LOCATOR_THICKNESS,LOCATOR_DEPTH,LOCATOR_ARM_LENGTH,(x_outer,RIM_Y-LOCATOR_DEPTH/2,z1)).fuse(box(LOCATOR_ARM_LENGTH,LOCATOR_DEPTH,LOCATOR_THICKNESS,(x2,RIM_Y-LOCATOR_DEPTH/2,z_outer)))
  capx=x_outer-sx*(LOCATOR_CAP_WIDTH-LOCATOR_THICKNESS)/2
  capz=z_outer-sz*(LOCATOR_CAP_WIDTH-LOCATOR_THICKNESS)/2
  tab=tab.fuse(box(LOCATOR_CAP_WIDTH,FRAME_THICKNESS,LOCATOR_ARM_LENGTH,(capx,RIM_Y+FRAME_THICKNESS/2,z1))).fuse(box(LOCATOR_ARM_LENGTH,FRAME_THICKNESS,LOCATOR_CAP_WIDTH,(x2,RIM_Y+FRAME_THICKNESS/2,capz)))
  assert len(tab.Solids())==1
  add(label+'_locator_%s'%sz,tab,GREEN)
 pad_x=sx*(BODY_WIDTH_X/2+CLAMP_PAD_THICKNESS/2)
 tab_x=sx*(BODY_WIDTH_X/2+CLAMP_PAD_THICKNESS+CLAMP_TAB_THICKNESS+LOCATOR_RIM_GAP)
 add(label+'_clamp_pad_CONCEPT',box(CLAMP_PAD_THICKNESS,CLAMP_PAD_HEIGHT,CLAMP_PAD_WIDTH,(pad_x,RIM_Y-CLAMP_PAD_HEIGHT/2,0)),(.7,.3,.5))
 add(label+'_clamp_tab_CONCEPT',box(CLAMP_TAB_THICKNESS,CLAMP_TAB_HEIGHT,CLAMP_TAB_WIDTH,(tab_x,RIM_Y-CLAMP_TAB_HEIGHT/2,0)),GREEN)
 screw=cq.Solid.makeCylinder(CLAMP_SCREW_DIAMETER/2,CLAMP_SCREW_LENGTH,cq.Vector(sx*(BODY_WIDTH_X/2-CLAMP_SCREW_DIAMETER/2),RIM_Y-CLAMP_PAD_HEIGHT/2,0),cq.Vector(sx,0,0))
 add(label+'_clamp_screw_CONCEPT',screw,(.3,.3,.3))
for sx in (-1,1):
 for sz in (-1,1):
  x=sx*(BODY_WIDTH_X/2+LOCATOR_RIM_GAP+STOP_WIDTH/4)
  z=sz*(BODY_LENGTH_Z/2+LOCATOR_RIM_GAP+STOP_WIDTH/4)
  wallx=sx*(BODY_WIDTH_X/2+LOCATOR_RIM_GAP+STOP_WALL_THICKNESS/2)
  stop=box(STOP_WIDTH,STOP_BASE_THICKNESS,STOP_LENGTH,(x,TABLE_Y+STOP_BASE_THICKNESS/2,z)).fuse(box(STOP_WALL_THICKNESS,STOP_WALL_HEIGHT,STOP_WIDTH,(wallx,TABLE_Y+STOP_WALL_HEIGHT/2,z)))
  stop=stop.cut(cyl(STOP_HOLE_DIAMETER/2,TABLE_Y-EPS,TABLE_Y+STOP_BASE_THICKNESS+EPS,x,z+sz*STOP_HOLE_OUTWARD_OFFSET))
  add('Table_stop_CONCEPT_%s_%s'%(sx,sz),stop,(.55,.35,.72))
# STEP output: reference assembly and two independent modules separately.
def export_assembly(items,path,name):
 a=cq.Assembly(name=name)
 for n,s,c in items:a.add(s,name=n,color=cq.Color(*c))
 a.save(str(path))
export_assembly(parts,OUT/'01_Sonicator_Two_Racks_Split_Top_Preview_R02_Editor.step','Sonicator_Two_Racks_Preview_R02')
for label,num in [('Left','02'),('Right','03')]:
 export_assembly([p for p in parts if p[0].startswith(label+'_') and not any(t in p[0] for t in ('Rack_REFERENCE','Vial_REFERENCE'))],OUT/f'{num}_{label}_Guide_Module_Preview_R02_Editor.step',label+'_Guide_Module_R02')
loaded=cq.importers.importStep(str(OUT/'01_Sonicator_Two_Racks_Split_Top_Preview_R02_Editor.step')).val()
expected_solids=sum(len(shape.Solids()) for name,shape,color in parts if not name.startswith('Manufacturer'))
print('STEP solids:',len(loaded.Solids()),'expected:',expected_solids,flush=True)
assert len(loaded.Solids())==expected_solids
assert loaded.isValid()
checks['reimport_solid_count']=len(loaded.Solids())
bb=loaded.BoundingBox();checks['assembly_bbox_mm']=[bb.xlen,bb.ylen,bb.zlen]
checks['rack_count']=len(rack_shapes)
checks['vial_count']=sum('Vial_REFERENCE' in n for n,s,c in parts)
checks['top_plate_count']=len(plate_shapes)
checks['guide_count']=len(rod_shapes)
checks['per_module_guides']=len(local_rods(0))
checks['locator_to_reference_min_distance_mm']=min(s.distance(ref) for n,s,c in parts if '_locator_' in n)
checks['rack_centers_X_mm']=RACK_CENTERS_X
checks['rack_footprint_XZ_mm']=[RACK_CENTERS_X[1]-RACK_CENTERS_X[0]+RACK_WIDTH_X,RACK_LENGTH_Z]
checks['rack_to_rack_gap_mm']=rack_shapes[0].distance(rack_shapes[1])
checks['plate_to_plate_gap_mm']=plate_shapes[0].distance(plate_shapes[1])
checks['minimum_rod_to_reference_surface_distance_mm']=min(s.distance(ref) for n,s in rod_shapes)
checks['minimum_guide_pair_distance_mm']=min(a.distance(b) for i,(n,a) in enumerate(rod_shapes) for m,b in rod_shapes[i+1:])
checks['minimum_rod_to_any_rack_distance_mm']=min(s.distance(r) for n,s in rod_shapes for r in rack_shapes)
checks['per_rack_reference_surface_distance_mm']=[r.distance(ref) for r in rack_shapes]
floor_face=next(f for f in ref.Faces() if f.geomType()=='PLANE' and abs(f.BoundingBox().ymin-FLOOR_Y)<1.e-5 and abs(f.BoundingBox().ymax-FLOOR_Y)<1.e-5)
checks['rack_bottom_corner_to_floor_face_max_mm']=max(cq.Vertex.makeVertex(cx+x,FLOOR_Y,z).distance(floor_face) for cx in RACK_CENTERS_X for x in (-RACK_WIDTH_X/2,RACK_WIDTH_X/2) for z in (-RACK_LENGTH_Z/2,RACK_LENGTH_Z/2))
assert checks['rack_bottom_corner_to_floor_face_max_mm']<1.e-5
checks['rod_floor_vertical_gap_mm']=ROD_BOTTOM_GAP
checks['rod_length_mm']=RIM_Y-FLOOR_Y-ROD_BOTTOM_GAP
checks['rod_coordinates_XZ_mm']=[(x,z) for cx in RACK_CENTERS_X for x,z,a in local_rods(cx)]
checks['rack_nominal_guide_clearance_mm']=ROD_RACK_GAP
checks['nominal_slot_opening_ligament_mm']=(RACK_WIDTH_X/2+ROD_RACK_GAP+ROD_DIAMETER/2-OPENING_WIDTH_X/2)-SLOT_DIAMETER/2-SLOT_TOTAL_TRAVEL/2
checks['slot_adjusted_rack_clearance_range_mm']=[ROD_RACK_GAP-SLOT_TOTAL_TRAVEL/2,ROD_RACK_GAP+SLOT_TOTAL_TRAVEL/2]
checks['ring_placement_XZ_each_side_mm']=[(OPENING_WIDTH_X-RACK_WIDTH_X)/2,(OPENING_LENGTH_Z-RACK_LENGTH_Z)/2]
# Fixed-center yaw at first rectangular rack/cylindrical guide contact.
def yaw_clears(angle):
 c,s=math.cos(angle),math.sin(angle)
 for x,z,axis in local_rods(0):
  xx,zz=c*x+s*z,-s*x+c*z
  if math.hypot(max(abs(xx)-RACK_WIDTH_X/2,0),max(abs(zz)-RACK_LENGTH_Z/2,0))<ROD_DIAMETER/2:return False
 return True
lo,hi=0.,.7
for i in range(55):
 m=(lo+hi)/2
 if yaw_clears(m):lo=m
 else:hi=m
checks['fixed_center_positive_yaw_contact_deg']=math.degrees(lo)
lo,hi=0.,.7
for i in range(55):
 m=(lo+hi)/2
 if yaw_clears(-m):lo=m
 else:hi=m
checks['fixed_center_negative_yaw_contact_deg']=-math.degrees(lo)
checks['assumed_water_height_mm']=WATER_HEIGHT
checks['assumed_water_constraints_satisfied']=SAMPLE_LIQUID_HEIGHT<=WATER_HEIGHT<=GRIPPER_FINGER_HEIGHT-SPLASH_MARGIN and WATER_HEIGHT<RACK_HEIGHT
checks['assumed_finger_water_clearance_mm']=GRIPPER_FINGER_HEIGHT-WATER_HEIGHT
checks['rack_reference_volume_each_mm3']=[r.Volume() for r in rack_shapes]
vial_n=len(VIAL_POSITIONS)
checks['assumed_robot_carried_mass_one_rack_kg']=rack_shapes[0].Volume()*ASSUMED_RACK_DENSITY_KG_MM3+vial_n*(ASSUMED_EMPTY_VIAL_MASS_KG+ASSUMED_CAP_MASS_KG+ASSUMED_LIQUID_MASS_PER_VIAL_KG)+ASSUMED_GRIPPER_MASS_KG+ASSUMED_ADAPTER_MASS_KG
checks['stationary_solids_volume_mm3']=sum(s.Volume() for n,s,c in parts if not any(k in n for k in ['Manufacturer','Rack_REFERENCE','Vial_REFERENCE']))
checks['assumed_stationary_steel_mass_kg']=checks['stationary_solids_volume_mm3']*ASSUMED_STEEL_DENSITY_KG_MM3
checks['original_project_routing_check']='NOT RUN - original router not supplied'
checks['stage']='EDITOR PREVIEW: assumptions only; not a manufacturing or robot-operation approval.'
checks['editor_config']=config
checks['rack_model']=RACK_MODEL
if RACK_MODEL=='uploaded_r20':checks['tray_source_metadata']=editor['REFERENCE_TRAY']
assert checks['rack_count']==2 and checks['top_plate_count']==2 and checks['vial_count']==(32 if SHOW_VIALS else 0) and checks['guide_count']==2*len(local_rods(0))
assert abs(checks['rack_to_rack_gap_mm']-config['rack_gap'])<1e-5
assert checks['minimum_guide_pair_distance_mm']>.1
assert checks['minimum_rod_to_reference_surface_distance_mm']>.05
assert checks['minimum_rod_to_any_rack_distance_mm']>=ROD_RACK_GAP-1.e-5
(OUT/'07_Geometry_checks_R02_Editor.json').write_text(json.dumps(checks,indent=2))
# Draw actual CAD tessellation; overview includes transparent original manufacturer surfaces.
def render_iso(include_ref,path,limits,title):
 fig=plt.figure(figsize=(12,10));ax=fig.add_subplot(111,projection='3d')
 for n,s,c in parts:
  if not include_ref and (n.startswith('Manufacturer') or n.startswith('Table_stop')):continue
  verts,tris=s.tessellate(.8)
  v=np.array([[p.x,p.z,p.y] for p in verts])
  ax.add_collection3d(Poly3DCollection(v[np.array(tris)],facecolors=c,edgecolor='none',shade=True,alpha=.10 if n.startswith('Manufacturer') else 1.))
 ax.set(xlim=limits[0],ylim=limits[1],zlim=limits[2],xlabel='X mm',ylabel='Z mm',zlabel='Y mm (vertical)')
 ax.set_box_aspect(tuple(b-a for a,b in limits));ax.view_init(38,-58);ax.set_title(title)
 fig.savefig(path,dpi=150);plt.close(fig)
render_iso(True,OUT/'04_Isometric_Two_Racks_Preview_R02_Editor.png',((-205,205),(-180,180),(-305,25)),f'PREVIEW R02 - {GUIDE_LAYOUT} / TWO INDEPENDENT TOP PLATES\nGrey: manufacturer shell reference. Rack and vial details assumed.')
render_iso(False,OUT/'08_Guides_And_Two_Racks_Preview_R02_Editor.png',((-175,175),(-140,140),(-160,20)),f'PREVIEW R02 - fixture isolated from manufacturer for clarity\nLeft and right modules are independently removable; {len(local_rods(0))} guides per module')
fig,ax=plt.subplots(figsize=(12,10))
# Actual ring outline/slots projected schematically; floor/tank rounded rectangles as reference.
for w,h,rad,col,name in [(REFERENCE_TANK_TOP_WIDTH,REFERENCE_TANK_TOP_LENGTH,REFERENCE_TANK_TOP_CORNER_RADIUS,'.6','Tank upper opening (reference approx)'),(REFERENCE_FLOOR_FLAT_WIDTH,REFERENCE_FLOOR_FLAT_LENGTH,REFERENCE_FLOOR_CORNER_RADIUS,'.3','Flat floor outline (reference approx)')]:
 ax.add_patch(FancyBboxPatch((-w/2,-h/2),w,h,boxstyle=f'round,pad=0,rounding_size={rad}',fill=False,ls='--',edgecolor=col,label=name))
for idx,cx in enumerate(RACK_CENTERS_X):
 xmin,xmax=(-FRAME_WIDTH_X/2,-PLATE_SPLIT_GAP/2) if cx<0 else (PLATE_SPLIT_GAP/2,FRAME_WIDTH_X/2)
 color='steelblue' if cx<0 else 'teal'
 ax.add_patch(Rectangle((xmin,-FRAME_LENGTH_Z/2),xmax-xmin,FRAME_LENGTH_Z,fill=False,edgecolor=color,lw=2))
 ax.add_patch(Rectangle((cx-OPENING_WIDTH_X/2,-OPENING_LENGTH_Z/2),OPENING_WIDTH_X,OPENING_LENGTH_Z,fill=False,edgecolor=color,lw=2))
 ax.add_patch(Rectangle((cx-RACK_WIDTH_X/2,-RACK_LENGTH_Z/2),RACK_WIDTH_X,RACK_LENGTH_Z,facecolor='coral' if cx<0 else 'mediumpurple',alpha=.18))
 if RACK_MODEL=='uploaded_r20':
  for vx,vz in VIAL_POSITIONS:ax.add_patch(Circle((cx+vx,vz),editor['REFERENCE_TRAY']['vial_hole_diameter']/2,fill=False,edgecolor='slategray',linewidth=.6))
 ax.text(cx,0,f'{"LEFT" if cx<0 else "RIGHT"}\nRACK {RACK_WIDTH_X:g} x {RACK_LENGTH_Z:g}\n16 SLOTS',ha='center',va='center',fontsize=10)
 for x,z,a in local_rods(cx):
  ax.add_patch(Circle((x,z),ROD_DIAMETER/2,color='goldenrod'))
  ax.text(x,z+7,f'{x:g},{z:g}',ha='center',fontsize=6)
 ax.plot([cx,cx],[-RACK_LENGTH_Z/2-10,RACK_LENGTH_Z/2+10],lw=.6,ls=':',color=color)
ax.annotate('',(-config['rack_gap']/2,0),(config['rack_gap']/2,0),arrowprops={'arrowstyle':'<->','color':'black'})
ax.text(0,14,f"{config['rack_gap']:g} mm\nrack gap",ha='center',fontsize=8)
ax.set(xlim=(-180,180),ylim=(-150,150),xlabel='X mm',ylabel='Z mm',title=f"R02 EDITOR: {GUIDE_LAYOUT}, {2*len(local_rods(0))} guides, diameter {ROD_DIAMETER:g}\nRack {RACK_WIDTH_X:g} x {RACK_LENGTH_Z:g}; openings {OPENING_WIDTH_X:g} x {OPENING_LENGTH_Z:g}; frame thickness {FRAME_THICKNESS:g}")
ax.set_aspect('equal');ax.grid(alpha=.15);ax.legend(loc='upper right',fontsize=7)
fig.savefig(OUT/'05_Top_Two_Plates_Preview_R02_Editor.png',dpi=170);plt.close(fig)
fig,ax=plt.subplots(figsize=(13,8))
ax.plot([-148.483,-147.321,-132.321,132.321,147.321,148.483],[0,-133.131,FLOOR_Y,FLOOR_Y,-133.131,0],color='.5',label='Tank section envelope (schematic)')
for cx in RACK_CENTERS_X:
 xmin,xmax=(-FRAME_WIDTH_X/2,-PLATE_SPLIT_GAP/2) if cx<0 else (PLATE_SPLIT_GAP/2,FRAME_WIDTH_X/2)
 ax.add_patch(Rectangle((xmin,RIM_Y),xmax-xmin,FRAME_THICKNESS,color='steelblue'))
 for x in (cx-RACK_WIDTH_X/2-ROD_RACK_GAP-ROD_DIAMETER/2,cx+RACK_WIDTH_X/2+ROD_RACK_GAP+ROD_DIAMETER/2):
  ax.add_patch(Rectangle((x-ROD_DIAMETER/2,FLOOR_Y+ROD_BOTTOM_GAP),ROD_DIAMETER,RIM_Y-FLOOR_Y-ROD_BOTTOM_GAP,color='goldenrod'))
 ax.add_patch(Rectangle((cx-RACK_WIDTH_X/2,FLOOR_Y),RACK_WIDTH_X,RACK_HEIGHT,fill=False,edgecolor='tomato',lw=2))
 for x in sorted({x for x,z in VIAL_POSITIONS}) if SHOW_VIALS else []:
  ax.add_patch(Rectangle((cx+x-VIAL_DIAMETER/2,FLOOR_Y+VIAL_BASE_ABOVE_FLOOR),VIAL_DIAMETER,VIAL_HEIGHT,fill=False,edgecolor='teal'))
ax.axhline(FLOOR_Y+WATER_HEIGHT,ls='--',color='blue',label=f'ASSUMED water {WATER_HEIGHT:g} mm above floor')
ax.axhline(FLOOR_Y+GRIPPER_FINGER_HEIGHT,ls=':',color='purple',label=f'ASSUMED lowest finger {GRIPPER_FINGER_HEIGHT:g} mm above floor')
ax.text(-150,-172,f'Rack height {RACK_HEIGHT:g}; rod bottom clearance {ROD_BOTTOM_GAP:g}; rack gap {config["rack_gap"]:g} mm.\nFinger-water clearance {GRIPPER_FINGER_HEIGHT-WATER_HEIGHT:g} mm.\nSchematic projection only. Gripper, water level and retention hardware NOT approved.',fontsize=9)
ax.set(xlim=(-180,180),ylim=(-180,20),xlabel='X mm',ylabel='Y mm vertical',title='R02 SIDE SCHEMATIC - BOTH RACKS / INDEPENDENT TOP HALVES')
ax.set_aspect('equal');ax.legend(fontsize=8,loc='upper center');ax.grid(alpha=.15)
fig.savefig(OUT/'06_Section_Two_Racks_Preview_R02_Editor.png',dpi=170);plt.close(fig)
print(json.dumps(checks,indent=2))

# Small dependency-free manifest consumed by the editor.
(OUT/'09_Result_summary_R02.json').write_text(json.dumps({'ok':True,'checks':checks,'files':[p.name for p in OUT.iterdir() if p.is_file()]},indent=2),encoding='utf-8')
