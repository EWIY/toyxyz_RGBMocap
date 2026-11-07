# Fork validation record

This file records the public-source preparation on 2026-11-07. Upstream baseline:
`5aaad4eedf1d1eb388f1f96da123e7c411822594`. Historical upstream and earlier local
measurements remain in [VALIDATION.md](VALIDATION.md); they are not new tests of
this source preparation.

The distribution repository is [EWIY/toyxyz_RGBMocap](https://github.com/EWIY/toyxyz_RGBMocap),
with `custom` as the public feature branch. The source, installation and feature
checks below were completed in isolated local checkouts before publication.

## Export path boundary follow-up — 2026-11-07

After reviewing the overwrite path, final character FBXs now pass backend
validation before preparation and again in Blender before file writing. This
protects bundled/registered source assets, program/runtime folders and internal
caches. Absolute user destinations, valid suffixes and existing parent folders
are required; ordinary project output folders remain available.

All 59 regressions passed. Real background export verified a destination with
Chinese characters and spaces. Attempts to export over a disposable animation
input sentinel or a hardlink of an original-character sentinel failed before
writing and preserved their bytes. An actual Windows runtime-directory junction
was resolved and rejected. The distributed Manny retained its pinned hash. These
checks used disposable data outside the live local installation.

## Bundled official Epic Manny — 2026-11-07

This revision includes the licensed Epic template `SKM_Manny_Simple.fbx` (2,887,824
bytes) with 88 bones and 48,705 vertices, its Epic notice and source provenance.
Mixamo/Unity retain their official download/import entry points and no assets from
those providers are included. Earlier no-character/generic-template records below
are historical descriptions of their respective revisions.

The source FBX's two document-URL strings were changed to repository-relative
values of identical byte length. Every other FBX byte is unchanged; the original
export and distributed-file SHA-256 hashes are recorded in the asset provenance.
The distributed file and its exact size/hash are explicitly listed in the resource
allowlist. Other character files, generated imports, runtime/model folders and
private work data remain excluded.

- All 53 regression tests passed, including fresh UE availability, same-size
  payload-tamper rejection, first-use registration/reuse and path relocation.
- Background integration started from an empty isolated target registry. First
  UE export imported the bundled resource once, then subsequent requests reused
  its verified registration. Native remains the default; absent Mixamo/Unity
  resources disable only their own target slots.
- The existing accepted 219-frame source was retargeted and exported with the
  actual release worker/Blender code. All preview matrices matched the repaired
  local reference exactly. Source motion and protected existing assets retained
  their hashes; no new neural inference ran.
- Both skinned and bones-only FBXs were reopened. Original 88-bone hierarchy was
  retained, skin-weight maximum difference was 0, and maximum evaluated vertex
  roundtrip error across all frames was 0.00000794 m. The bones-only file had no
  mesh and retained frames 1–219.

These checks ran from the background with the existing pinned runtime. No desktop
computer-use inspection, new runtime installation or Unreal-engine import test
was performed. Publication additionally requires clean-clone source/manifest
checks, described in the publishing guide.

## Official-target and hand-fix synchronization — 2026-11-07

This revision replaces the earlier generated-compatible-template workflow below
with separately imported official X Bot, Manny Simple and DefaultMale targets.
Earlier generic-template results are historical checks of the removed feature.
No licensed character, private clip, model weight or runtime was copied into Git.

- Background-only source verification was used for this synchronization; no
  computer-use inspection or desktop GUI control was performed.
- All 50 source regression tests passed using the existing pinned GUI/shared
  runtime. Offscreen widget tests cover English default, language switching,
  missing official targets, registration errors and native export availability.
- The release code imported the three existing official FBXs into an isolated
  data folder: X Bot 65 bones/24,746 vertices, Manny Simple 88/48,705 and DefaultMale
  68/7,510. Original source hashes remained unchanged and the new target receipts
  verified. Moving the isolated installation preserved all three registrations.
- The release Blender bridge rebaked UE and Unity from the accepted same-motion
  cached body solution. Across 219 frames, every preview matrix matched the
  accepted repaired local version exactly (maximum component difference 0).
  This reused the existing source motion and ran no new inference.
- Local repair evidence was rechecked: protected official resources and the
  unchanged Mixamo FBX retained their hashes; all 219 non-finger body frames
  matched the preceding body solution. Rest matrices, hierarchy, mesh topology
  and skin weights were unchanged. Actual FBX reimport maximum evaluated-vertex
  differences were 0.00000794 m (UE) and 0.00000333 m (Unity); reimported weight
  differences were 0. These numerical checks support the same-clip regression,
  not a claim that all motions or engine imports have been visually certified.
- Registration pins relative local asset paths, validates required files and
  refuses empty/incomplete hash receipts. Replacement preserves prior asset
  versions. Missing targets have no generic or legacy-preset fallback.

Both `check_source.py` and `check_fork.py` passed with zero errors for 2,635
tracked files. A fresh clone of the reviewed source passed both audits and all
50 regressions. That clone contained no model, runtime, cache, character-work,
configuration or project folders. Tests reused the existing validated runtime
from outside the clone; this was not a fresh runtime installation. The source
manifest excludes local assets/data and retains only the pre-approved upstream
sample/importer/native-module resources. The original upstream README, license,
notices and pinned installer/dependency files remain unchanged.

This synchronization does not repeat GPU inference or Unreal/Unity engine import.
The clone/manifest verification was repeated after adding this validation record;
no application code changed during that final documentation step.

## Source and upstream review

- Merged the complete upstream history through the baseline above, including
  installer recovery, recursive FlowHMR download callbacks, per-actor export
  origin placement and symmetrical rest-pose export. The last upstream fetch
  during preparation still resolved to that commit.
- Preserved the local bilingual UI, selective Fusion pipeline, shared scene
  origin, detector selection, skeleton export and stability fixes. New upstream
  export controls are translated and remain default-off.
- Compared the pre-existing component license/notice/copyright files with
  upstream byte for byte; all remain unchanged. The root third-party notices
  append the fork's additional obligations. The original `LICENSE` SHA-256 remains
  `d652f82d5865fac9a47223d6ab6ed1fbd5f8b3fd9e6ee1c3a1c9769d3a4d3ebd`.
  Additional resource/dependency obligations are documented in
  [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md).
- `README.upstream.md` is an unmodified snapshot of the baseline README. The
  English and Chinese fork guides describe the added workflows, official resource
  acquisition, built-in/custom targets, update behavior and license boundaries.
  All 12 upstream README sections and its Markdown links remain represented in
  the English fork README. The 2,593 baseline upstream paths are present, as are
  all 54 tracked paths modified in the original local installation. All 48
  existing component license/notice/copyright-related files are byte-identical.
- `tools/check_source.py` and `tools/check_fork.py` audit tracked source,
  dependencies, imports, relative documentation links and payload exclusions.
  `SOURCE_MANIFEST.json` records file sizes and SHA-256 values, excluding itself.
  The only approved binary/media source exceptions are the exact upstream-listed
  correction module, shader libraries and three demonstration clips.

## Installation and launch on the preparation PC

Started with no installed runtime in the separate validation checkout, then ran
`install.cmd --verify-all` successfully (exit code 0). Reused hash-verified official
download archives to reduce network transfer; did **not** copy installed runtime
directories. All six profiles (`shared`, `gui`, `flow`, `hand`, `htd`, `exmr`)
were rebuilt, checked against package RECORD hashes/import requirements and
promoted. The pinned ONNX Runtime dependency and its added dependencies were
downloaded from official PyPI. Blender and FFmpeg were prepared by the installer.
Both optional support components in this base installer, PEAR and camera
alignment, finished with `ready` status. Model weights remain a separate step.

The installed source launcher completed its native smoke test with success,
worker exit code 0 and empty worker stderr. The English main window and rendered
3D grid were inspected. No video or 3D inference was loaded for this launch test;
no saved language preference was needed. This was a new environment on the
existing Windows/NVIDIA PC, **not a clean-Windows or other-GPU test**.

## Added resources and interface

- Downloaded the official HumanArt archive linked in [the guide](FORK_GUIDE.md).
  Its `end2end.onnx` is 396,283,264 bytes and matches SHA-256
  `8e9ea96a176bd48501eaaa77216e49ee30794d2f8ba80c7b9862beca4ea972da`.
  The real Model Manager import helper accepted it and marked the detector ready.
  The newly installed ONNX Runtime 1.22.0 created a session with CUDA and CPU
  providers and processed one synthetic black image without error (zero boxes,
  shape `[0, 4]`). This verifies setup/invocation, not detection accuracy.
- Confirmed every existing official model entry keeps its upstream identity.
  VGGT-Omega uses the official checksum; the local mirror is neither bundled nor
  substituted. The official VGGT weights were not downloaded/inferred again.
- Actually registered UE5 and Unity-style FBX targets through
  `tools/setup_export_skeleton.py` using read-only existing local inputs. All six
  required generated target artifacts were produced. The target data and source
  characters are excluded from the public tree. These earlier custom-target tests
  are separate from the subsequent built-in animated export checks below.
- Checked 55 model manual pages in English and Chinese, preserving official URLs
  and filenames. Inspected English/Chinese export dialogs, target registration
  dialogs and the Chinese HumanArt instructions. New source-export controls stay
  within their dialog and retain their values through language/format changes.

## Regression checks and reproducible handoff

`runtime\python.exe -I -X utf8 -B tools\run_fork_tests.py` passed **42 tests**
using the rebuilt runtime. Coverage includes Fusion weights/regions and source
reuse, actor/timing/tracking mismatch rejection, shared origin/camera projection
and saved-view rebasing, detector cache identity, target registration and
preservation, branch-safe updates and pending markers, language defaults/settings,
Qt callbacks, upstream download callbacks and per-actor export origins. Added
template checks cover topology/fingers, availability without a private target,
verified cache reuse/rebuild and preservation of custom targets. Fixtures
are synthetic and temporary; no personal capture data is included.

After committing the reviewed source, a second clone was created from the commit
history and audited again. The final handoff directory contains no installed
`models`, `runtime*`, `.setup`, `cache`, `projects` or `character_work` directories.
The installed validation checkout and reports are retained separately. Original
installation tracked files were checked against their preparation-time hashes.

## Redistributable built-in skeleton integration

The shipped templates are original source definitions and original analytic
foot/palm contact proxies, with no vendor character files. Blender generates
targets locally on first export. The three selectors are enabled without any
`character_work/presets` data. A complete user-registered target still takes
precedence and is not replaced. This round did not change the inference runtime
lock or numerical motion-reconstruction pipelines.

Actual tests used the production `worker_boot.py rig_export` entry and existing
completed captures as read-only inputs; no new video inference was required:

| Source selection | Compatible target | Frames / fps | Export and FBX reimport |
| --- | --- | --- | --- |
| FlowHMR initial | Mixamo | 91 / 30 | Passed; 52 bones, no mesh |
| FlowHMR initial | UE5 | 91 / 30 | Passed; 56 bones, no mesh |
| FlowHMR initial | Unity | 91 / 30 | Passed; 53 bones, no mesh |
| FlowHMR corrected initial | UE5 | 91 / 30 | Passed; 56 bones, no mesh |
| Existing Fusion initial | Unity | 304 / 30 | Passed; 53 bones, no mesh |

Every reimport checked all frames against the pre-export baked animation,
including exact bone-name/parent sets, rest matrices, first/last keyframe, frame
rate and animated fingers. Across these five exports, the maximum bone-position
roundtrip error was `0.000004582 m` (about `0.0046 mm`), maximum rotation-matrix
element error `0.000006333` and maximum rest-matrix element error `0.000000477`.
These are FBX roundtrip errors relative to the retargeted bake, not motion-capture
accuracy or agreement with the source character's different proportions.
All output files, registered targets, body models and test captures stay outside
the Git source distribution. Original source-take files were checked unchanged.
The final native launcher smoke test again opened the default-English main window
and rendered viewport successfully after the integration.

These checks establish the reviewed source/installation/export path on this PC. They do
not claim new full GPU video reconstruction for every model, Fusion quality on
all clips, universal old-cache compatibility, a new optional MAMMA/PromptHMR native
build, Unity/Unreal animation import or standalone executable packaging. Account
access, provider terms, supported hardware and separately acquired model/body
files are still required by the documented deployment workflow.
