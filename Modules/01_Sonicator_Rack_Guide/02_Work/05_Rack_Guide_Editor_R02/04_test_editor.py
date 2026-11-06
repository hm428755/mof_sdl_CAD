"""Run with Python; no CAD packages required for these configuration checks."""
import unittest,runpy,tempfile
from pathlib import Path
app=runpy.run_path(str(Path(__file__).with_name('01_editor.py')))
validate=app['validate_config'];derive=app['derive_parameters']
class ConfigurationTests(unittest.TestCase):
 def test_defaults_match_delivered_centered_model(self):
  p=derive({});self.assertEqual(p['RACK_CENTERS_X'],(-54.74,54.74));self.assertEqual(p['GUIDE_LONG_SIDE_Z'],0);self.assertEqual(p['OPENING_WIDTH_X'],89.48);self.assertEqual(p['RACK_MODEL'],'uploaded_r20')
 def test_alternate_layout_and_coupled_dimensions(self):
  p=derive({'rack_model':'parametric','layout':'offset','rack_gap':25,'opening_clearance':2.5,'side_offset':50,'end_offset':40,'frame_thickness':4})
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
 def test_windows_default_matches_requested_folder(self):
  self.assertEqual(app['default_storage'](True),r'C:\Users\yeonseo kim\Desktop\MOF_SDL\Hardware\CAD')
 def test_output_change_persists_and_rejects_relative_path(self):
  manager=app['JobManager']();g=app['validate_storage'].__globals__
  saved={k:g[k] for k in ['STORAGE','RESULTS','OUTPUT_PREF']}
  try:
   with tempfile.TemporaryDirectory() as tmp:
    g['OUTPUT_PREF']=Path(tmp)/'preferences.json'
    target=Path(tmp)/'Path With Spaces'/'CAD'
    d=manager.set_storage(str(target))
    self.assertEqual(g['STORAGE'],target)
    self.assertEqual(app['load_storage'](),target)
    self.assertTrue(Path(d['results']).is_relative_to(target))
    with self.assertRaises(ValueError):manager.set_storage('relative/folder')
    manager.job={'status':'running'}
    with self.assertRaises(ValueError):manager.set_storage(str(Path(tmp)/'other'))
  finally:g.update(saved)
 def test_uploaded_tray_cannot_be_silently_scaled(self):
  p=derive({'rack_model':'uploaded_r20','rack_width':110,'rack_length':190,'rack_height':20})
  self.assertEqual((p['RACK_WIDTH_X'],p['RACK_LENGTH_Z'],p['RACK_HEIGHT']),(85.48,127.76,45))
  self.assertEqual(len(p['VIAL_POSITIONS']),16);self.assertFalse(p['SHOW_VIALS'])
 def test_old_dimension_settings_remain_parametric(self):
  p=derive({'rack_width':100,'rack_length':190,'rack_height':20});self.assertEqual(p['RACK_MODEL'],'parametric')
 def test_wider_gap_moves_both_racks_and_opens_same_tray(self):
  p=derive({'rack_gap':44})
  self.assertAlmostEqual(p['RACK_CENTERS_X'][0],-64.74);self.assertAlmostEqual(p['RACK_CENTERS_X'][1],64.74);self.assertEqual(p['RACK_WIDTH_X'],85.48)
  self.assertAlmostEqual(derive({'rack_gap':60})['RACK_CENTERS_X'][1],72.74)
 def test_startup_reports_missing_extracted_files(self):
  start=runpy.run_path(str(Path(__file__).with_name('08_start_editor.py')))
  with tempfile.TemporaryDirectory() as tmp:
   with self.assertRaisesRegex(FileNotFoundError,'Extract the full editor ZIP'):start['check_files'](Path(tmp),Path(tmp)/'editor')
if __name__=='__main__':unittest.main()
