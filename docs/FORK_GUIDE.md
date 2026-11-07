# Fork workflows and resource preparation

The application starts in English. Use **Language > 中文** for Chinese; the
preference is saved only in ignored `cache/gui-language.json`. Missing or invalid
preferences fall back to English. Third-party diagnostics and provider website
menu names can remain in their original language.

## Selective FlowHMR + GVHMR Fusion

Prepare both engines' required files in Model Manager. Select **FlowHMR + GVHMR ·
Fusion**, set the guidance weight and regions, and run **Reconstruct 3D**. The
default guides the three torso spine joints, neck and head at 100%. Zero weight
and unchecked regions preserve FlowHMR local rotations. Root, legs, shoulders,
local arm rotations and fingers remain FlowHMR. Hands can move in world space
when the torso changes; their original trajectory is not pinned.

Both engines see the same prepared video and actor observations. Sources are
reused only with matching video content, timing, tracking and actor identity.
Missing sources run sequentially in their own existing runtimes. Source contact
correction precedes fusion; required changes use private copies and do not
overwrite the original FlowHMR/GVHMR model projects. Weight-only changes reuse
the source captures. No learned fusion checkpoint, extra temporal smoothing or
time warping is introduced. See [Fusion implementation and limits](models/FUSION.md).

## Shared FlowHMR scene origin

`flow_origin.py` chooses the earliest complete take, with stable actor/path
tie-breaking, and projects its initial placed pelvis onto the horizontal plane.
That one XZ offset is shared by actors, source cameras, scene previews and saved
view rebasing. It preserves vertical height, relative placement and the actual
motion trajectory. It does not center every actor separately, remove travel or
perform foot locking.

Derived placement receipts use version 3 and include the reference identity.
Completed version-2 results remain readable. **Prepare Preview** migrates derived
placement using verified completed sources; it does not silently replace original
`flow_prediction.pt` data or pretend that old inference was rerun. Prepare affected
actors consistently if the reference take changes. Mixing old/new scene origins
is rejected with an actionable message. Saved orbit views carry an origin marker
so reapplying the same rebase does not translate the view twice.

The newer upstream **Place at origin** export checkbox is a separate, default-off
operation on exported FBX/BVH copies. It centers each actor independently and can
change relative actor placement. The fork's shared source-scene origin does not.
**Symmetrical rest pose** is also default-off and changes exported reference
geometry, not committed motion. Both options remain disabled for Blender bundles.

## Optional resource preparation

### HumanArt detector

Default tracking remains **YOLOv8x**. For an alternative on stylised/armoured
people, select **Actor Detector > YOLOX-X (HumanArt)** and open **Model Manager**.
Its HumanArt row provides **Manual Download...** and **Import...**.

| Item | Official source / expected artifact |
| --- | --- |
| Model information | [OpenMMLab RTMPose](https://github.com/open-mmlab/mmpose/tree/main/projects/rtmpose) |
| Supported archive | [yolox_x_8xb8-300e_humanart-a39d44ed.zip](https://download.openmmlab.com/mmpose/v1/projects/rtmposev1/onnx_sdk/yolox_x_8xb8-300e_humanart-a39d44ed.zip) |
| File inside archive | `20230928/yolox_onnx/yolox_x_8xb8-300e_humanart-a39d44ed/end2end.onnx` |
| Registered location | `models/yolox/yolox_x_humanart.onnx` |
| ONNX size | `396283264` bytes |
| ONNX SHA-256 | `8e9ea96a176bd48501eaaa77216e49ee30794d2f8ba80c7b9862beca4ea972da` |

Review provider/HumanArt terms, download and extract the archive, then import
`end2end.onnx`. Do not import the ZIP or a different YOLOX size. Import validates
the stable copied bytes before publishing the registered file. The installer
pins ONNX Runtime GPU 1.22.0 and its missing dependencies; it does not ship or
automatically acquire the detector weights. CUDA is preferred when usable, with
CPU fallback. A better result for one difficult clip does not establish a general
accuracy improvement.

New person-discovery/tracking cache identities include the selected detector and
its model revision. Switching to HumanArt therefore does not silently reuse a
YOLOv8 discovery result. Already published motion remains separate; rerun the
desired tracking/reconstruction action explicitly when replacing observations.

### Official Mixamo / UE5 / Unity export targets

The project-authored compatible templates have been removed. The supported
reference characters are official Adobe X Bot, Epic Manny Simple and Unity
DefaultMale. Manny's official skeleton and skinned mesh are bundled; X Bot and
DefaultMale retain separate official acquisition/import routes.
See [official sources, registration and preview](OFFICIAL_EXPORT_TARGETS.md).

Keep Native capture skeleton for capture. Register the official FBX through
File > Export Skeleton Targets for Mixamo/Unity. UE5 export prepares the included
Manny automatically if no official UE target is registered. Include
target mesh controls whether the original skin is included. Assets, hashes and
per-installation registry stay local. The sole bundled character is the separately
licensed [Epic Manny template](../assets/export_skeletons/ue5_manny/NOTICE.md).
If a target is absent or damaged, there is no generic/private-preset fallback.
Ordinary File > Import Character remains available for other licensed characters.

UE/Unity hand rotation transfer uses actual phalanges and palm references, decodes
the source export basis and preserves the target bind offsets. It changes no
official bone names, rest matrices, mesh topology or weights. Mixamo retains its
existing adapter. Retarget existing character animations again after updating;
they are not silently rewritten. Unity still requires Avatar configuration in
the intended engine; this workflow does not reproduce engine control rigs.

## Official model identities

Public source uses the upstream official model URLs and SHA-256 values.
VGGT-Omega's expected hash is
`c02da418b18bb01d0392598d3f6147366bcde1bb70fd08a5e3bf7925b0667934`.
Obtain its supported official file through the existing Model Manager guidance
and provider access process. A locally substituted mirror is not treated as
equivalent, and checksum verification is not disabled. Preparing this fork does
not modify any model, receipt or setting in a separate older installation.

### Local mirror validation

The README mirror table documents the maintainer's existing local file sources;
it does not change the public model registry. GVHMR, HMR2, ViTPose-H Multi-COCO
and ViTPose-H WholeBody download receipts record hashes matching the current
registry. Those exact files work with the existing validation.

The locally substituted VGGT-Omega mirror is
[`wincentIsMe/VGGT-Omega`, `vggt_omega_1b_512.pt`](https://huggingface.co/wincentIsMe/VGGT-Omega/blob/main/vggt_omega_1b_512.pt).
The local import receipt records 4,576,706,322 bytes and SHA-256:

```text
6742f744ff83aee8918d27a5f9008181167034c4311693875bba5a59165233f2
```

This differs from the default official hash above. To intentionally use this
specific alternative, first verify the downloaded file's SHA-256, provenance,
version and applicable terms. In your own working copy, set the `flow_vggt`
entry's `expected_sha256` in `mocap/models.py` to the verified hash and review
`minimum_bytes` against the chosen artifact; then use Model Manager **Import**
to validate/register it. Re-import creates a matching receipt: do not forge a
receipt, clear the expected hash or disable validation. A different future mirror
file needs its own review, not automatic acceptance of the hash printed here.

These values come from the existing import receipt and mirror note, with the
current file's size/timestamp matching that receipt; this documentation edit did
not rehash multi-gigabyte installed weights or run a new model comparison. A
matching hash identifies bytes, not model quality. Public-source preparation keeps
the official default hash and preserves the original installation's settings.

Changing a validation pin is a tracked source edit. The updater protects such
edits; manage/commit them deliberately before updating rather than discarding
them to force an update.

## Local data and upstream boundaries

Git excludes `models/`, `runtime*/`, `.setup/`, `cache/`, `projects/`,
`character_work/`, `character_scenes/`, local preferences and backup files.
The upstream's explicitly hash-listed shader libraries, small prebuilt correction
module and approved demonstration clips remain: they are required/source-approved
resources, not a copied installed runtime or private character collection.

The original MIT text, third-party notices and component licenses remain intact.
Fusion includes GVHMR's conditions; adding another engine does not remove them.
See [notices](../THIRD_PARTY_NOTICES.md) and [recorded validation](FORK_VALIDATION.md).
