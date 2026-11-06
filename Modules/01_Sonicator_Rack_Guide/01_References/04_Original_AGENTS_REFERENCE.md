# Zn-BDC Automated Synthesis — CAD agent instructions

This repository is for a robotic synthesis and laboratory-automation platform.
It is not an Ender-3 printing project; the modified Ender-3 is only one motion
module within the platform.

## Required context

At the start of every CAD task:

1. Read `harness.md`.
2. Read `Modules/00_Project_Admin/PROJECT_INDEX.md`.
3. Read the target module's `00_STATUS.md` and only the references needed for
   that module.
4. Keep one Codex task focused on one module or one system-integration question.
5. For every CAD source/export write, follow the mandatory revision routing in
   `Modules/90_Shared_Tools/05_Revision_Folders/06_ROUTING.md`. Run `prepare`
   before adding a version and `check --module <module>` before finishing.

## CAD authority and units

- Base unit: millimetres.
- CadQuery source and native manufacturer STEP are the geometry sources of truth.
- STEP is the editable interchange and assembly-review format.
- DXF/DWG and dimensioned PDF are manufacturing-drawing layers.
- STL/3MF and low-poly models are derived visualization or prototype files;
  never recover production dimensions from them when STEP or drawings exist.
- Record every critical dimension as `REFERENCE`, `USER_CONFIRMED`, `MEASURED`,
  or `ASSUMED`.

## Mandatory stage gate

1. Acquire an exact reference.
2. Extract dimensions and document their provenance.
3. Create a working CAD source.
4. Export preview PNG and preview STEP.
5. Obtain user confirmation.
6. Only then create or update a numbered final output/release.

Do not label inferred dimensions as exact. Do not release manufacturing CAD
before confirmation. Do not delete or overwrite an earlier release; create a
new revision.

## Verification

For every generated release, check at minimum:

- overall X/Y/Z envelope and millimetre units;
- hole count, diameter, pitch, margins and blind/through condition;
- closed-base or wall thicknesses;
- STEP re-import and STL boundary/non-manifold edges;
- assembly fit, collision and service clearances;
- volume and estimated mass when handled by a robot;
- total robot payload including gripper, coupling, adapters, containers and liquid.

## Project organization

- Work only under `Modules/<numbered_module>/` for new tasks.
- Prefix every new CAD file or directory with the next unused two-digit number
  in its containing folder. Reserve `00_STATUS.md` for status, never renumber
  earlier entries, and increment release revisions separately.
- Keep source references immutable.
- Put temporary conversions in `Modules/90_Shared_Tools/03_Temporary_Conversions`.
- Update the target module's `00_STATUS.md` after a meaningful decision or export.
- Update `PROJECT_INDEX.md` when adding, renaming or completing a module.
- Existing links under `Modules` intentionally point to legacy files so old
  scripts and delivered links remain valid.
- Every design module uses numbered revision folders for sources, previews and
  outputs. Existing explicitly versioned folders/legacy links are valid anchors.
  Independent designs with the same revision require distinct `family` names.
  Use shared `revision_dir()` for every exporter, or `04_revision_router.py
  prepare` before authoring files. New revisions create the next numbered folder;
  update revision selection and export filenames together. Do not add flat CAD
  files to module roots or unversioned Work/Preview/Output containers.
- Preserve the immutable reference exceptions and named historical variants in
  `05_Module_Routes.json`. Unidentified historical files use `Unversioned`, common
  tools use `Shared`; do not invent a revision. Never run deployment scripts or
  regenerate old releases merely to reorganize folders.
