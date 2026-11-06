# Fork validation record

This file records the public-source preparation on 2026-11-07. Upstream baseline:
`5aaad4eedf1d1eb388f1f96da123e7c411822594`. Historical upstream and earlier local
measurements remain in [VALIDATION.md](VALIDATION.md); they are not new tests of
this source preparation.

No GitHub repository has been modified by this preparation. The public branch is
`custom`; its eventual GitHub owner and repository name are still placeholders.

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
  acquisition, missing-target setup, update behavior and license boundaries.
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
  characters are excluded from the public tree. Mixamo aliases and registration
  contracts were checked with synthetic tests; a new Mixamo character import and
  animated FBX retarget/export were not run in this preparation.
- Checked 55 model manual pages in English and Chinese, preserving official URLs
  and filenames. Inspected English/Chinese export dialogs, target registration
  dialogs and the Chinese HumanArt instructions. New source-export controls stay
  within their dialog and retain their values through language/format changes.

## Regression checks and reproducible handoff

`runtime\python.exe -I -X utf8 -B tools\run_fork_tests.py` passed **39 tests**
using the rebuilt runtime. Coverage includes Fusion weights/regions and source
reuse, actor/timing/tracking mismatch rejection, shared origin/camera projection
and saved-view rebasing, detector cache identity, target registration and
preservation, branch-safe updates and pending markers, language defaults/settings,
Qt callbacks, upstream download callbacks and per-actor export origins. Fixtures
are synthetic and temporary; no personal capture data is included.

After committing the reviewed source, a second clone was created from the commit
history and audited again. The final handoff directory contains no installed
`models`, `runtime*`, `.setup`, `cache`, `projects` or `character_work` directories.
The installed validation checkout and reports are retained separately. Original
installation tracked files were checked against their preparation-time hashes.

These checks establish the reviewed source/installation path on this PC. They do
not claim new full GPU video reconstruction for every model, Fusion quality on
all clips, universal old-cache compatibility, a new optional MAMMA/PromptHMR native
build, Unity/Unreal animation import or standalone executable packaging. Account
access, provider terms, supported hardware and separately acquired model/body
files are still required by the documented deployment workflow.
