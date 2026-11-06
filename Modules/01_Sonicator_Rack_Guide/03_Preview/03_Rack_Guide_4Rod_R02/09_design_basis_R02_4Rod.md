# R02 / Rack_Guide_4Rod — Preview only

Current request: keep R02, reduce guides to4ifpossible, use newWindowsprojectroot. Interpretation:4perrack,8total; two racks and split independent topplates retained. Original8guides-per-rackR02 is preserved as a separate variant. Four TOTAL for two racks is not the design made here.

Guide layout per rack, relative to its own center X/Z (mm):
- (-56,+60), (+56,-60): opposite long sides, offset from center
- (-45,+101), (+45,-101): opposite ends, offset in the opposite rotational sense

One guide per side; not four guides at the side midpoints. Ideal contact-normal matrix has rank3 and a positive balancing combination (12JSON), supporting local bounded X/Z/yaw at zero clearance. At actual1mm gaps the rack has play, not rigid/form-fit zero-play location. Fixed-center yaw firstcontact +0.947658/-1.243073deg. A simultaneous-translation/yaw global maximum, tolerance/vibration/friction/dynamics is NOT established by that calculation.

Dimensions inherited: rack100X×190Z×20Y each; centersX±62; totalfootprint224×190; rackgap24; two157.75×257.5×3 plates, seamgap2; openings104×194; Ø10rods×148; bottom2abovefloor; rackguidegap1; 3.4×3.9M3slots, ligament2.05. Top/bottomC1. All new dimensions ASSUMED unless stated elsewhere. Rack envelope/count and two-rack/split-top requirement task/userconfirmed. Reference manufacturer unchanged.

Fewer holes:4perplate; tap/fastener/washer4setsperplate. Pin-to-rack1, closestpinpair32.449971, closestpin-to-reference1.463868mm. Surface minimum is not the2mmvertical floor gap. Pin centers near rounded tank bottom require tolerance review. All8rackbottomcorners lie on the exact imported planar floorface (distance0), improving on bbox-only inference. Floor in-plane rounded corner is measuredR33.821; the quotedR15 is the vertical fillet, not the floor outline corner. Updated top drawing uses the measured in-plane radius.

Actual STEP output reimport valid with74newsolids plus original manufacturer reference shells. 2racks/32vials/2topplates/8guides. Manufacturer is a surface reference,0solids/86shells. Left/right module files each18solids. NoSTL. Reference geometry is never used as a valid volumetric boolean tank model.

ASSUMED water11/finger18/sample10mm abovefloor retained; operatingwater minimum, actualgripper/vial support/caps, clampretention/tableanchors/rail stiffness andvibration remainunresolved. Illustrative one-rack carriedpayload2.02125kg uses assumedmaterials/masses, not operationapproval. Stationaryuniformsteelestimate1.93275kg.

Windowsroot:
C:\Users\yeonseo kim\Desktop\MOF_SDL\Hardware\CAD

Paths inside Python are portable and relative to source, rather than hardcoded to the old PC or /workspace. Requirements and setup/buildbatchfiles are provided at projectroot. Windows scripts were not run on an actualWindowsmachine; Linuxgenerationisverified. Windows path is a target on user'sPC, not mounted/accessed from this server. AttachedAGENTS/harness are unchanged references; original projectroutingtools remain unavailable, prepare/checknotrun. NoOutput/Release.
