"""Run with Python; no CAD packages required for these configuration checks."""
import unittest,runpy,tempfile
from pathlib import Path
app=runpy.run_path(str(Path(__file__).with_name('01_editor.py')))
validate=app['validate_config'];derive=app['derive_parameters']
class ConfigurationTests(unittest.TestCase):
 def test_defaults_match_delivered_centered_model(self):
  p=derive({});self.assertEqual(p['RACK_CENTERS_X'],(-62,62));self.assertEqual(p['GUIDE_LONG_SIDE_Z'],0);self.assertEqual(p['OPENING_WIDTH_X'],104)
 def test_alternate_layout_and_coupled_dimensions(self):
  p=derive({'layout':'offset','rack_gap':25,'opening_clearance':2.5,'side_offset':50,'end_offset':40,'frame_thickness':4})
  self.assertEqual(p['RACK_CENTERS_X'],(-62.5,62.5));self.assertEqual(p['OPENING_WIDTH_X'],105);self.assertEqual(p['GUIDE_END_X'],40);self.assertEqual(p['FRAME_THICKNESS'],4)
 def test_invalid_values_are_rejected(self):
  bad=[{'rod_diameter':6},{'rack_gap':15},{'rod_gap':float('nan')},{'rack_width':True},{'layout':'other'},{'finger_height':12},{'rack_length':130},{'unexpected':'not allowed'},{'side_offset':75,'layout':'offset','rack_length':150}]
  for c in bad:
   with self.subTest(config=c),self.assertRaises(ValueError):validate(c)
 def test_inputs_do_not_modify_defaults(self):
  derive({'layout':'eight','end_offset':30});self.assertEqual(derive({})['GUIDE_LAYOUT'],'centered')
 def test_runs_never_overwrite_previous_files_or_numbers(self):
  fn=app['allocate_run'];g=fn.__globals__;old=g['RESULTS']
  try:
   with tempfile.TemporaryDirectory() as tmp:
    root=Path(tmp);g['RESULTS']=root
    (root/'01_Editor_R02').mkdir();(root/'02_Interface.png').write_bytes(b'keep')
    self.assertEqual(fn().name,'03_Editor_R02');self.assertEqual(fn().name,'04_Editor_R02')
    self.assertEqual((root/'02_Interface.png').read_bytes(),b'keep')
  finally:g['RESULTS']=old
if __name__=='__main__':unittest.main()
