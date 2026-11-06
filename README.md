# RGB MoCap — Fusion and bilingual interface fork

[简体中文](README.zh-CN.md) · [Original project](https://github.com/toyxyz/toyxyz_RGBMocap) · [Unmodified upstream README](README.upstream.md)

This community fork preserves the original RGB MoCap application and adds the
local workflows described below. **English remains the default interface.**
The source incorporates upstream
[`5aaad4ee`](https://github.com/toyxyz/toyxyz_RGBMocap/commit/5aaad4eedf1d1eb388f1f96da123e7c411822594),
including installer recovery and the FlowHMR download-progress callback repair.
Original authorship, component licenses and research citations are retained.

## Fork additions

| Addition | Behavior and limits |
| --- | --- |
| English / Chinese interface | Language menu, translated controls/dialogs/help and a saved local preference. New installations start in English. |
| FlowHMR + GVHMR Fusion | Keep FlowHMR as the base; guide torso, neck and head rotations with GVHMR at 0–100% weight. Matching source captures are reused; missing captures run in separate runtimes. |
| Shared FlowHMR scene origin | Rebase actors and camera together around the first complete take's initial pelvis projected onto the horizontal plane. Preserve relative placement, vertical height and motion. |
| HumanArt person detection | Optional YOLOX-X HumanArt alongside default YOLOv8x, with an official download page and checked ONNX import in Model Manager. |
| More output skeletons | Register your own licensed Mixamo, UE5 or Unity-style FBX target and export bone-only FBX. Native source skeleton export needs no target assets. |
| Stability fixes | Retain local wheel-edit protection, UTF-8 worker output, empty-contact handling and reviewed cache/preview fixes. |

These additions include worker dispatch, scene/camera handling, previews and
exports; copying only the GUI or only the backend is insufficient.
No model weights, registered body models, vendor characters, installed runtimes,
caches or personal projects are distributed in this Git tree.

### Using the added workflows

- **Fusion:** choose **FlowHMR + GVHMR · Fusion**, set guidance weight/regions,
  then **Reconstruct 3D**. Defaults are 100% on torso, neck and head. Root, legs,
  local arm rotations and fingers remain FlowHMR; a changed torso can still move
  the hands in world space. Source contact correction precedes fusion. No extra
  smoothing, retiming or learned fusion checkpoint is added. Both engines'
  required files must be prepared. See [Fusion](docs/models/FUSION.md).
- **Scene origin:** the common horizontal reference is not foot locking or
  in-place motion. Legacy completed scenes remain readable; use **Prepare
  Preview** for affected people to migrate derived placement consistently.
  Original prediction files are preserved.
- **HumanArt:** select **Actor Detector > YOLOX-X (HumanArt)**, open Model Manager,
  use **Manual Download...**, then import the official ZIP's `end2end.onnx`.
  Its supported SHA-256 is checked before registration at
  `models/yolox/yolox_x_humanart.onnx`. Detection quality depends on footage.
- **Export targets:** open **File > Export Skeleton Targets...**, follow
  **Official Source**, obtain a licensed humanoid FBX with a mesh, then
  **Import FBX...**. Registered targets become available under **Output Skeleton**.
  Targets and generated results stay local. Unity Humanoid does not specify one
  universal FBX hierarchy; only supported mappings are accepted.

[Fork guide and official resource sources](docs/FORK_GUIDE.md) ·
[Fork verification record](docs/FORK_VALIDATION.md) ·
[Maintaining and publishing](docs/PUBLISHING.md)

The descriptions, examples and dated measurements below come from the upstream
application. They are retained as context, not presented as new fork benchmarks.

![RGB MoCap workspace showing video tracking and a 3D motion preview](docs/images/rgbmocap-workspace.png)

A native Windows app that turns video into editable human animation. Review and
export motion with AI processing running locally.

## Sample videos

### Motion capture

https://github.com/user-attachments/assets/b948dd8c-43b9-493a-9d7f-2fae0317695e

[Download original sample](docs/samples/motion-capture.mp4)

### Character retargeting

https://github.com/user-attachments/assets/1759f1bf-a0d0-409f-84d8-dde9409cfe6f

[Download original sample](docs/samples/character-retargeting.mp4)

### Multi Cam MoCap

https://github.com/user-attachments/assets/4c0b290b-4a65-4287-8d22-c63c96b3d080

[Download original sample](docs/samples/multi-cam-mocap.mp4)

## Install and run

1. Install [Git for Windows](https://git-scm.com/download/win). Open **Command Prompt**
   in a writable folder where you want to install RGB MoCap. Replace the two
   `YOUR_...` components with your fork's actual owner/repository, then clone its
   **custom** branch:

   ```cmd
   git clone --branch custom https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPOSITORY.git RGBMoCap
   cd RGBMoCap
   ```

2. Prepare the runtimes for ExMR, FlowHMR and GVHMR with their supported add-ons,
   plus PEAR live-preview support,
   Blender, FFmpeg and native motion correction. AI weights and registered body
   files are downloaded separately in Model Manager:

   ```cmd
   install.cmd
   ```

3. Start the app:

   ```cmd
   RGBMoCap.cmd
   ```

   Keep the console open while the app runs. Prepare the AI model files separately
   using **Model Manager**; some require account registration and manual download.

To update, close the app and run `update.cmd` on a clean branch tracking your
fork (normally `custom` tracking `origin/custom`). It fast-forwards that branch
and verifies/repairs dependencies; merging new upstream changes is a separate
maintainer operation. Do not discard tracked edits to bypass its protection. See the
[installation guide](docs/USER_GUIDE.md#install) for disk space, prerequisites
and recovery.

Updates reuse recently verified, unchanged runtimes. If PEAR or camera-alignment
support preparation fails after the base installation succeeds, the base app
remains usable; rerun `install.cmd` to retry the unavailable support. See
[verification and repair](docs/USER_GUIDE.md#installation-verification-and-repair).

### Optional model runtimes

`install.cmd` prepares ExMR, FlowHMR, GVHMR and the small shared-runtime support
for [PEAR live preview](docs/models/PEAR.md). Install the following only if
you use them, after the base installation:

| Model | Separate setup command | Installation and usage |
| --- | --- | --- |
| MAMMA | `Setup_MAMMA.cmd` | [MAMMA guide](docs/MAMMA.md) |
| PromptHMR | `Setup_PromptHMR.cmd` | [PromptHMR guide](docs/models/PROMPTHMR.md) |

MAMMA and PromptHMR require **Visual Studio 2022 C++ Build Tools**, the Windows SDK and
**CUDA Toolkit 12.8** for local native builds. Close the app and review the
provider terms before setup. Then reopen it and prepare the selected model's
files in **Model Manager**. Their optional runtimes do not require each other;
`install.cmd` and `update.cmd` do not install them.

PEAR reuses the base shared runtime with a small support overlay prepared by
`install.cmd` and `update.cmd`. No separate setup or compiler is required.
Model files are prepared separately.

### Install with an AI agent

After cloning, open this repository folder in a local coding agent such as Codex.
The [agent guide](docs/AGENT_GUIDE.md) covers setup, models, capture, retargeting,
projects and resources. For example, ask:

```text
Help me install and run RGB MoCap on this Windows PC.
Read AGENTS.md and docs/AGENT_GUIDE.md first. Check the GPU and free disk space,
run install.cmd, and launch RGBMoCap.cmd. Help me prepare the ExMR model files.
Preserve existing models, projects and settings, and keep the pinned runtimes.
Tell me when I need to sign in, accept provider terms or download a file manually.
```

For multi-camera capture, add:

```text
Also enable MAMMA. Follow docs/MAMMA_AGENT_SETUP.md to check the C++/CUDA tools,
run Setup_MAMMA.cmd after the required license review, and verify the native CUDA
modules. Help me prepare its models without changing the other model runtimes.
```

For PromptHMR instead, add:

```text
Also enable PromptHMR. Follow docs/models/PROMPTHMR.md and docs/AGENT_GUIDE.md.
Check the C++/CUDA tools, run Setup_PromptHMR.cmd after the required license
review, verify its CUDA checks, and help prepare the exact Model Manager files.
Keep other runtimes and existing projects unchanged.
```

MAMMA's [agent setup guide](docs/MAMMA_AGENT_SETUP.md) and the
[PromptHMR guide](docs/models/PROMPTHMR.md) include build checks and recovery.
Provider login and license acceptance remain your responsibility;
do not put passwords or account tokens in the agent chat.

## Features

- Reconstruct one or several people and preview the body mesh and animation bones.
- Reduce sliding with foot/palm contact correction and editable contact timings.
- Retarget motion to Mixamo FBX, VRM and PMX humanoid characters.
- Export source animation as FBX or BVH (Generic/Blender or 3ds Max Biped), with optional leading T-pose, per-person origin placement and symmetrical rest pose; export characters as FBX with or without meshes,
  or PMX character motion as VMD for MMD.
- Export portable Blender projects with source animation, video and saved cameras; MAMMA can include animated body meshes and every camera.
- Save side-by-side input video and the current 3D viewport as MP4 with **File > Export Preview...** (offline models).
- Inspect source-video/bone alignment in Camera Preview and display saved cameras in 3D, with optional background rotation refinement for FlowHMR/ExMR.
- Save projects with separate results for each AI model.
- Reduce FlowHMR memory use with query-batched attention and optional sparse hand sampling; optional HaMeR refines fingers. See [controls and trade-offs](docs/models/FLOWHMR.md#controls) and [measured time/memory comparisons](docs/PERFORMANCE.md#flowhmr-query-batches-and-four-frame-hands-2026-11-03).
- Track webcam or video input in real time with PEAR's experimental body/finger bone preview; tracking and poses may be unstable.

## How it works

1. Select an AI model and prepare its files in **Model Manager**, then use
   **File > Open Video**. For MAMMA, select it before opening synchronized camera
   videos; thumbnails switch the preview and one timeline trim applies to all views.
2. For ExMR, FlowHMR or GVHMR, optionally use **Find person** to select people.
   PromptHMR tracks people together during reconstruction.
   MAMMA detects people during reconstruction; keep **VGGT-Omega + GeoCalib (Automatic)** and
   enter an approximate **Reference Height (m)**, or import camera calibration.
   Click **Reconstruct 3D**.
3. Review the motion, edit contacts if needed and **Apply Correction**.
4. Use **File > Export...** to choose FBX, BVH or a portable Blender project, or import a character, retarget the motion and export it.

**PEAR · Live (Experimental)** tracks webcam or video input in real time. Tracking
and pose estimates may be unstable. Click **Start Live Tracking** to attempt camera
alignment and begin the bone preview. If alignment fails, tracking continues from
the selected camera with a warning; camera fusion and aligned foot lock are unavailable.
Recording, offline correction and export are unavailable in this live mode.
See the [PEAR guide](docs/models/PEAR.md) for its controls.

## Supported AI models

In our subjective tests, **PromptHMR** could improve relative placement and
interactions between multiple people in a **single video**, but its overall
motion quality was lower than **ExMR**. It does not support finger tracking.

| Model / original project | Body representation | Fingers | Setup and use |
| --- | --- | --- | --- |
| [PEAR](https://github.com/Pixel-Talk/PEAR) · experimental live preview; may be unstable | SMPL-X / FLAME | Included | [PEAR guide](docs/models/PEAR.md) |
| [ExMR](https://github.com/twehrbein/ExMR) | SMPL-X | Included | [ExMR guide](docs/models/EXMR.md) |
| [FlowHMR](https://github.com/flowhmr/flowhmr) | SMPL-H | Included | [FlowHMR guide](docs/models/FLOWHMR.md) |
| FlowHMR + GVHMR Fusion | SMPL-H | From FlowHMR | [Fusion guide](docs/models/FUSION.md) |
| [GVHMR](https://github.com/zju3dv/GVHMR) | SMPL-X | Optional HandFlow add-on | [GVHMR guide](docs/models/GVHMR.md) |
| [MAMMA](https://mamma.is.tue.mpg.de/) · multi-view motion capture | SMPL-X | Included | [MAMMA guide](docs/MAMMA.md) |
| [PromptHMR](https://github.com/yufu-wang/PromptHMR) | SMPL-X | Not generated | [PromptHMR guide](docs/models/PROMPTHMR.md) |

Requires 64-bit Windows, a compatible NVIDIA GPU/driver and OpenGL 4.3.
Model files are acquired separately; some require registration and license acceptance.

**Installed models and runtimes:** approximately **67.9 GB (63.2 GiB)** for the
five offline models, including supported add-ons, Blender and FFmpeg. Based on the measured inventory plus GeoCalib for automatic MAMMA gravity, excluding
projects, caches or retained downloads; shared files are counted once.

| Configuration | Runtime | Models | Total |
| --- | ---: | ---: | ---: |
| ExMR + FlowHMR + GVHMR and supported add-ons | 12.35 GiB | 28.89 GiB | 41.23 GiB |
| MAMMA additional files | 6.11 GiB | 3.53 GiB | 9.65 GiB |
| PromptHMR additional files, Fixed Camera | 6.22 GiB | 6.13 GiB | 12.34 GiB |
| **Five offline models** | **24.68 GiB** | **38.55 GiB** | **63.22 GiB** |
| PEAR live preview, additional | Small support overlay; shared runtime reused | ~2.84 GiB | ~2.85 GiB |

Including PEAR, the estimated combined model/runtime total is about
**66.07 GiB (70.9 GB)**, before the additional space listed below. GeoCalib weights (about **0.11 GiB**) are shared by MAMMA and PEAR and counted once; both also reuse VGGT. See the
[PEAR camera guide](docs/models/PEAR.md#multiple-fixed-cameras-and-camera-align).

Optional PromptHMR moving-camera support adds approximately **18.6 MiB** of
native modules and **1.55 GiB** of weights beyond these totals; see its model guide.

**MAMMA and PromptHMR require separate runtime installation:** run
`Setup_MAMMA.cmd` or `Setup_PromptHMR.cmd` after `install.cmd`, as described
[above](#optional-model-runtimes). They are not installed by `install.cmd` or
`update.cmd`; obtain weights separately in Model Manager.

App source, C++/CUDA compiler tools, installation temporary files and saved work
need additional space. These are measured sizes, not a setup free-space guarantee.
See [storage and installation details](docs/USER_GUIDE.md#installed-size).

[Cache and project cleanup: paths and deletion effects](docs/USER_GUIDE.md#storage-and-cleanup).

## Resources and speed

Start with **Resource Mode > Automatic**. It uses the fast supported path when
memory permits and falls back to a supported Low Memory path when needed.
Memory-saving methods depend on the model; **Low Memory** can trade slower
loading/transfers and more system RAM for lower VRAM use. See each model's guide
for implemented options and limits. **Resource Safety**, below Resource Mode,
defaults on. Turn it off to bypass low-RAM stopping and the VRAM allocator limit;
Automatic batching and actual allocation-error handling stay active. See the
[Resource Safety details](docs/PERFORMANCE.md#resource-safety).

Short paired tests reduced peak allocated VRAM from **5.68 to 3.87 GiB** for ExMR
and **6.10 to 2.77 GiB** for FlowHMR. Separate short-clip tests of connected
processing phases cut worker time by **44% for ExMR** and **24% for FlowHMR**,
with unchanged measured peak VRAM. These are different tests, not full-job
speed guarantees. See [resource modes, measured savings and acceleration](docs/PERFORMANCE.md)
for conditions, per-model results, direct-video preprocessing and output differences.

FlowHMR's **Adaptive Batching** selects 1–16 Fast SAM frames from available memory;
Low Memory uses one. Warm feature tests took 16–23% less time at batch 16 than at
batch 4, with peak allocated VRAM rising from 3.84 to 5.43 GiB. Whole-job gains can
be smaller. Batch selection and OOM retry messages appear in Console and CMD.

## Documentation

- [User guide: installation, controls and settings](docs/USER_GUIDE.md)
- [Model guides: files, defaults, options and limitations](docs/models/README.md)
- [Research papers and citations](docs/CITATIONS.md)
- [Recorded processing time, VRAM and RAM](docs/USER_GUIDE.md#recorded-processing-time-and-vram)
- [Resource modes and measured optimizations](docs/PERFORMANCE.md)
- [MAMMA: additional installation, model files and multi-video workflow](docs/MAMMA.md)
- [PromptHMR: additional installation, model files and camera workflows](docs/models/PROMPTHMR.md)
- [Development and builds](docs/BUILD.md)
- [Agent operating and development guide](docs/AGENT_GUIDE.md)
- [Source validation](docs/VALIDATION.md)
- [Third-party notices and model terms](THIRD_PARTY_NOTICES.md)

Original RGB MoCap code and documentation use the [MIT License](LICENSE).
Third-party components and model files retain their own licenses.

The original project is **[toyxyz / RGB MoCap](https://github.com/toyxyz/toyxyz_RGBMocap)**
and its contributors. The complete original README is retained in
[README.upstream.md](README.upstream.md), including its acknowledgments. The root
MIT grant does not relicense third-party code, derived modifications, model
weights or characters. Fusion does not remove GVHMR or other provider conditions.
Read [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md); no unrestricted commercial
license is claimed for the combined application.
