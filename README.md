# RGB MoCap

[简体中文](README.zh-CN.md) · [Upstream project](https://github.com/toyxyz/toyxyz_RGBMocap) · [Original README and credits](README.upstream.md)

A Windows app for local video motion capture, contact correction, character
retargeting and animation export. This fork adds the features below.
**English is the default interface.**

## Features added by this fork

| Feature | What it does |
| --- | --- |
| English / Chinese interface | Language menu, translated help and saved preference. |
| FlowHMR + GVHMR Fusion | Uses FlowHMR motion with adjustable GVHMR guidance for torso, neck and head. |
| Shared FlowHMR origin | Moves people and camera together, preserving their relative placement and travel. |
| HumanArt detector | Optional YOLOX-X HumanArt alongside YOLOv8x. |
| Character library | Fixed **Add Character...** dropdown above People; supports FBX, VRM, PMX and subfolders. |
| Official target characters | Epic Manny Simple is included. Mixamo X Bot and Unity DefaultMale have official download/import routes. Export bones alone or with the original skin. |
| Preview and fixes | Shared viewport/timeline, tangent-space normal-map preview, UE5/Unity finger adaptation, scroll protection and worker stability fixes. |

## Install

Requires 64-bit Windows, a supported NVIDIA GPU/driver, OpenGL 4.3, Git for Windows
and a writable folder. Base runtimes need about 34 GiB, plus models and projects.

```cmd
git clone --branch custom https://github.com/EWIY/toyxyz_RGBMocap.git RGBMoCap
cd RGBMoCap
install.cmd
RGBMoCap.cmd
```

In **Model Manager**, download or import the files required by the selected
capture model. Model weights and registered body models are separate downloads.
Optional MAMMA, PromptHMR, GEM-X and SAM 3.1 use `Setup_MAMMA.cmd`,
`Setup_PromptHMR.cmd`, `Setup_GEMX.cmd` and `Setup_SAM31.cmd`, respectively.
See [installation and troubleshooting](docs/USER_GUIDE.md#install).

## Capture and export

1. Choose a capture model, open a video and trim the range. For a specific person
   or several people with ExMR/FlowHMR/GVHMR/Fusion, use **Find person** first.
   MAMMA and PromptHMR have their own multi-person workflows.
2. Click **Reconstruct 3D**. Review the result; edit contacts and use **Apply
   Correction** when needed. Capture stays on the native body model
   (FlowHMR uses SMPL-H).
3. Use **File > Export...** for native FBX/BVH/Blender output. **Export Preview...**
   saves the input video beside the current viewport. For character preview and
   character FBX export, follow the next section.

**Fusion:** choose **FlowHMR + GVHMR · Fusion**, then set guidance weight/regions.
Both engines' model files are required. [Details](docs/models/FUSION.md).
**HumanArt:** choose **Actor Detector > YOLOX-X (HumanArt)**, then use Model
Manager's manual download/import for the official ZIP's `end2end.onnx`.

## Recent upstream features

- [GEM-X](docs/models/GEMX.md) captures one person from a fixed camera and exports the native SOMA Native77 rig.
- [SAM 3.1](docs/models/SAM31.md) adds text and click selection to Find person in ExMR, FlowHMR and GVHMR.
- [Blender bone streaming](docs/USER_GUIDE.md#stream-bones-to-blender) previews source bones and bakes them to Actions.
- [Source export options](docs/USER_GUIDE.md#fbx-and-blender) include Maya-compatible FBX, origin placement and symmetrical rest pose.

### Blender bone streaming demo

https://github.com/user-attachments/assets/cc0e79bb-ecce-4752-ae14-3b6cea30c810

[Download the original MP4](docs/samples/streaming-to-blender.mp4?raw=1)

## Add a character and retarget

| Character | Where to get it / put it |
| --- | --- |
| Epic Manny Simple | Included with its original skeleton and skin. Select **Epic Manny Simple (bundled)** in the dropdown; no download or file browsing is needed. |
| Adobe Mixamo X Bot | Download a skinned T-pose FBX from [Mixamo](https://www.mixamo.com/) after signing in. Put it in `character_library/Mixamo/`. |
| Unity DefaultMale | Get `DefaultMale.fbx` from [Unity's official repository](https://github.com/Unity-Technologies/Standard-Assets-Characters/tree/8f185aa3c782d824976653dd6a6476312daad241/Assets/_Standard%20Assets/Characters/Models/Male). Put it and its textures in `character_library/Unity/`; see [texture setup](docs/OFFICIAL_EXPORT_TARGETS.md#defaultmale-textures). |

The library is under the installation folder by default. Put other supported
characters and their textures in its subfolders too. The folder button beside
the dropdown opens it; reopen the dropdown to refresh. **File > Import
Character...** still browses external files.

1. Select a character from **Add Character...** above People. It is added in rest
   pose; adding it does **not** retarget automatically.
2. Right-click its new People row, choose **Retarget > [source person]**, and wait
   for processing. Use the same source/result for each character you compare.
3. Toggle row checkboxes to compare in the same viewport and timeline. Keep the
   camera settings fixed. Select the character and use **File > Export
   Character...** for FBX, with or without its mesh (PMX also supports VMD).

Up to eight characters per project. Files must use a supported humanoid mapping.
For direct target export, **Output Skeleton > UE5 compatible skeleton** prepares
bundled Manny on first use. Register Mixamo/Unity through **File > Export Skeleton
Targets... > Import official FBX...**. Output Skeleton changes export only;
it does not replace the viewport character.
[Character library](docs/CHARACTER_LIBRARY.md) · [Official targets and textures](docs/OFFICIAL_EXPORT_TARGETS.md).

## Model mirrors used locally

| Model | Mirror |
| --- | --- |
| VGGT-Omega 512 | [wincentIsMe / VGGT-Omega](https://huggingface.co/wincentIsMe/VGGT-Omega/blob/main/vggt_omega_1b_512.pt) |
| GVHMR | [camenduru / GVHMR](https://huggingface.co/camenduru/GVHMR/blob/main/gvhmr/gvhmr_siga24_release.ckpt) |
| HMR2 | [camenduru / HMR2](https://huggingface.co/camenduru/GVHMR/blob/main/hmr2/epoch%3D10-step%3D25000.ckpt) |
| ViTPose-H Multi-COCO | [camenduru / ViTPose](https://huggingface.co/camenduru/GVHMR/blob/main/vitpose/vitpose-h-multi-coco.pth) |
| ViTPose-H WholeBody | [JunkyByte / easy_ViTPose](https://huggingface.co/JunkyByte/easy_ViTPose/blob/main/torch/wholebody/vitpose-h-wholebody.pth) |

A mirror whose bytes differ needs a reviewed local change to model validation
(`expected_sha256` and size in `mocap/models.py`), followed by re-import. Keep
checksum validation enabled. The listed VGGT mirror needs this adjustment; this
repository retains official upstream defaults.
[Validation details](docs/FORK_GUIDE.md#local-mirror-validation).

## Guides and licenses

[User guide](docs/USER_GUIDE.md) · [Capture models](docs/models/README.md) ·
[Fork details](docs/FORK_GUIDE.md) · [Validation](docs/FORK_VALIDATION.md) ·
[Publishing](docs/PUBLISHING.md)

Based on [toyxyz/RGBMoCap](https://github.com/toyxyz/toyxyz_RGBMocap), upstream
baseline [`1b03843`](https://github.com/toyxyz/toyxyz_RGBMocap/commit/1b0384367fc6b63932c82f1c9c5cb4243a91de2e).
Retain the original [MIT license](LICENSE), [component notices](THIRD_PARTY_NOTICES.md)
and [research credits](README.upstream.md). Bundled Manny has separate
[Epic terms and provenance](assets/export_skeletons/ue5_manny/NOTICE.md).
Mixamo/Unity assets retain their providers' terms. Local character libraries,
projects, model weights, runtimes and caches are excluded from Git.
