# Sonicator Rack Guide — Preview R02

最新/최신: R02, two racks / two independently removable top plate modules. Not approved for manufacture or operation. R01 remains unchanged in the earlier revision folders.

USER_CONFIRMED: maximum two racks in the tank, split top into two parts (current correction). Rack per task190×100×20,16 vials each.
ASSUMED: rotate each rack90° fromR01; centersX±62,Z0; footprint224×190; rackgap24; plate157.75×257.5×3 each, splitgap2;8 Ø10 guides perplate/16total. Actual water, gripper, cap/vial support, clamp retention and table fastening unresolved. See R02 design_basis and verification.

References in01_References remain unchanged. Source:02_Work/02_Rack_Guide_R02. Exports:03_Preview/02_Rack_Guide_R02. Colored full assembly STEP and individual left/right module STEP plus PNGs. No Output/Release.

Original Zn-BDC project/routing tools not supplied: original prepare/check not run. Standalone workspace index only. HEO repo untouched.

Next: inspect two-rack arrangement with user; confirm rack/gripper/water and retention details before detailed manufacture release. Robot payload is for one carried rack at a time unless user specifies otherwise.

## Latest R02 4-rod variant
Current user requested R02 and fewer rods. Added Rack_Guide_4Rod family:4guides perrack/8total, preserved originalR02. Source02_Work/03_Rack_Guide_4Rod_R02; Preview03_Preview/03_Rack_Guide_4Rod_R02. Windowsroot C:\Users\yeonseo kim\Desktop\MOF_SDL\Hardware\CAD. Localgeneration/reimportverified; Windowslaunchersnotexecuted. Fixed-centeryaw-1.243/+0.948deg, minimumguide-tankdistance1.464mm. Seevariantdesignbasisforlimitations. GitHub upload succeeded; R02 four-guide Windows ZIP is available under Downloads.

## Latest user-selected layout: Centered4 / R02
Oneguideateachsidecenter,4perrack/8total. Source02_Work/04_Rack_Guide_Centered4_R02,Preview03_Preview/04_Rack_Guide_Centered4_R02. Prioroffset4and8guidevariantsretained. Centeredlayoutfixed-centeryaw±8.0693deg;repeatablepickuporientationnotestablished. Windowslauncher05_Build_CAD_Centered4_R02.bat.

## R02 CAD Editor
Portable local browser editor added under02_Work/05_Rack_Guide_Editor_R02; launch06_Open_CAD_Editor_R02.bat. Central4/offset4/eightlayouts and dimensioncontrols with validation; settingsround-trip; immutable per-run outputs under03_Preview/05_Rack_Guide_Editor_R02. SourceandpreviousCADvariantsremainunchanged. RuntimeislocalPC,notremotecloudAPI. WindowslauncheruntestedonactualWindows;LinuxChromiumandactualgenerationtested. Originalroutingtoolstillunavailable,prepare/checknotclaimed.
