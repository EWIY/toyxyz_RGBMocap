# FlowHMR + GVHMR selective fusion

Select **FlowHMR + GVHMR · Fusion** in **AI Motion Model**. Set the
guidance weight and bone regions below the selector, then click **Reconstruct
3D**. Motion Correction defaults on, like the existing offline models.

Defaults are **100%**, **Torso** (Spine, Spine1, Spine2), **Neck** and **Head**.
0% keeps FlowHMR exactly. Unchecking a region keeps its original local rotations.
The root, legs, shoulders, arms and fingers retain FlowHMR local motion; the arms
therefore move with a changed torso. Their original world-space hand trajectory
is not pinned. Frame count, timestamps, playback speed and body shape are kept.
There is no added temporal smoothing or time warping.

The workflow uses the same prepared video and actor observations for both
engines. It reuses current matching captures in this workspace, validates video
content, tracking, person identity and frame interval, and runs missing captures
automatically. A cache from another actor, trim range or prepared video is not
substituted. For multiple people, use **Find person**, check the intended actors
and reconstruct them together.

The two engines run sequentially in their existing separate runtimes. New Flow
captures use the normal Flow camera default (automatic VGGT sampling); already
computed Flow results retain their own camera/feature settings. Fusion does not
enable GVHMR HTD, FootMR or HandFlow. Model Manager lists the required Flow/GV
resources; no new learned checkpoint or environment is needed.

Motion Correction operates on the source captures **before** fusion. Fusion
keeps the corrected Flow lower body and root exactly, then applies the selected
GV orientation guidance. Changing correction options or contact timing uses
private source copies; existing FlowHMR and GVHMR projects are never overwritten.
Changing only weight/regions reuses the two captures and rebuilds just the fused
motion and its derived preview/export data.

The result is saved in the independent `fusion` model folder, with original and
corrected variants. It supports native SMPL-H solid mesh preview, the normal
bone overlay, camera view, BVH/FBX export and existing output-skeleton options.
The standard anatomical export fitting still applies: protected native motion
is exact, but export bone rotations may have small fitting differences. This is
an optional method based on the accepted Ogryn workflow, not a guarantee that
GVHMR is better for every torso/head pose or every video.

## Implementation and cache contract

- `fusion_sources`: find or create matching source captures. Privately generated
  captures live under the fusion group's `_fusion_sources/{flowhmr,gvhmr}`.
- `fusion_blend`: ensure requested source corrections, then launch
  `fusion_native` in the Flow runtime. The GUI's process-tree cancellation and
  resource policy also cover the child workers.
- `fusion_native`: keep the Flow SMPL-H shape and all unselected native tensor
  channels. Build GV body global rotations, apply one initial yaw alignment,
  and solve selected local rotations in parent order. Partial weights use
  shortest-arc rotation interpolation toward the parent-relative target.
- Per-result `*_fusion.json` records options, exact input identities, source
  files, output stamps and protected-motion assertions. Changed settings,
  upstream generations, tracking, timestamps, contact edits or pending writes
  invalidate the result. Pending failures preserve reusable upstream work.
- Preview/export uses the existing native SMPL-H exporter, with independent
  immutable artifact generations. Shared scenes retain Flow's placement.

Source references are relative to the fusion take. Sources normally belong to
the same workspace, so **Save Project As** carries them with the workspace.
Do not manually delete the original model folders used by a fusion result.

CPU regression tests: `python -m unittest discover -s tests -p test_fusion.py`
using the app's shared runtime and repository import path. Integration checks
on the development machine covered fresh 30-frame fixed-camera and 12-frame
automatic-camera two-engine captures, cached 155-frame overhead motion, a
two-person 219-frame scene, GUI reconstruction, solid mesh display, camera
overlays, weight changes, private correction copies, and native/Mixamo FBX
export with Blender import checks. Full inference for
all twelve original clips was not repeated for this integration.
