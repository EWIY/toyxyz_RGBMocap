# Official export targets: acquire, import, preview and export

RGBMoCap captures motion on its native body representation. FlowHMR uses SMPL-H;
choosing a target skeleton does not change that inference model. This fork can
retarget selected motion to three official reference characters. Epic Manny Simple
is included with its skeleton and skinned mesh; Mixamo X Bot and Unity DefaultMale
are acquired separately. The earlier generated compatible templates are removed.

## Obtain a target

| Output Skeleton | Official reference used for validation | Acquisition |
| --- | --- | --- |
| Mixamo Humanoid | Adobe X Bot in T pose | Obtain the skinned character FBX from [Adobe Mixamo](https://www.mixamo.com/), using the Adobe sign-in/download flow. Keep the mesh and skeleton together. |
| UE5 compatible skeleton | Epic `SKM_Manny_Simple` | Included at `character_library/UE5/SKM_Manny_Simple.fbx` (2,887,824 bytes). First UE5 export prepares it locally. Source: the [official Third Person template](https://dev.epicgames.com/documentation/en-us/unreal-engine/third-person-template-in-unreal-engine); see [asset provenance and Epic notice](../assets/export_skeletons/ue5_manny/NOTICE.md). |
| Unity Humanoid | Unity Technologies `DefaultMale` | Get the FBX and optional textures from the official [Standard Assets Characters repository](https://github.com/Unity-Technologies/Standard-Assets-Characters). The validated revision is `8f185aa3c782d824976653dd6a6476312daad241`, path `Assets/_Standard Assets/Characters/Models/Male/Models/DefaultMale.fbx`. |

The validated imports contained 65, 88 and 68 bones respectively. These counts
describe the tested resource versions; they are not a universal engine requirement.
Unity Humanoid uses an Avatar mapping, not one mandatory FBX skeleton. Other
characters and mannequin variants may require additional adaptation. The target
is a reference character, not an Unreal Control Rig or automatic Unity Avatar setup.

Manny is distributed as Epic template Examples with its [separate license notice](../assets/export_skeletons/ue5_manny/LICENSE.txt). Its two document-URL metadata strings are made repository-relative; all other FBX bytes are preserved. Imported caches remain local.

Acquire Mixamo/Unity resources under their publishers' terms. RGBMoCap's MIT license
does not relicense character assets, textures or derived character data. Review the
terms linked by Adobe/Epic and the official [Unity repository license](https://github.com/Unity-Technologies/Standard-Assets-Characters/blob/master/LICENSE.md)
for your intended use. The importer's structure/hash checks do not authenticate a
file's publisher or authorize redistribution.

## Import and register once

1. Run `install.cmd` and start `RGBMoCap.cmd` normally.
2. Manny needs no character download. Select **UE5 compatible skeleton** and export;
   the background worker prepares the bundled FBX on first use. Alternatively,
   open **File > Export Skeleton Targets... > Prepare bundled Manny** first.
3. For Mixamo/Unity, use that dialog's official source link and place the acquired
   skinned FBX under `character_library/Mixamo/` or `character_library/Unity/`.
   Choose **Import official FBX...** to register it for direct target export.
   Their original assets are not bundled. For project preview, the **Add
   Character...** dropdown can add these files directly without registration.
4. The Blender importer prepares a new local asset version; registration validates
   the hierarchy and file hashes. Later exports reuse the registered target.
   A previously registered official UE target takes priority over bundled preparation.
5. Native capture remains the default. Missing Mixamo/Unity resources disable only
   their corresponding target slots. No self-authored skeleton is substituted.

Equivalent commands after installation:

```cmd
runtime\python.exe -I -X utf8 -B tools\setup_official_target.py --skeleton mixamo --file "D:\Characters\X_Bot_TPose.fbx"
runtime\python.exe -I -X utf8 -B tools\setup_official_target.py --skeleton ue5 --bundled
runtime\python.exe -I -X utf8 -B tools\setup_official_target.py --skeleton unity --file "D:\Characters\DefaultMale.fbx"
```

The [character library](CHARACTER_LIBRARY.md) and its textures remain local.
The local registry is `config/official-export-targets.json`. Imported assets are
versioned under `character_work/official_targets/{mixamo,ue5,unity}/`. Both paths
are ignored by Git. The bundled source FBX stays in the versioned asset folder. Registry paths are relative to the installation, so moving
the prepared installation does not require the maintainer's drive paths.

An incomplete or wrong-family import never replaces a working registration.
To register a new version explicitly, add `--replace`; it retains old asset
directories and saves the preceding registry. Failed staging folders are retained
for diagnosis. Export verifies registered hashes and reports missing/changed data
instead of silently selecting a different rig. Ordinary updates do not delete
your older presets, character jobs or animation results; those are user data.

### DefaultMale textures

The FBX stores a skeleton and skinned mesh, but Unity's separate `.mat` bindings
are not sufficient for Blender to restore its textures automatically. To reproduce
the tested textured preview, download `DefaultMale_Albedo.tif` and
`DefaultMale_Normal.tif` from the same pinned official repository revision under
`Assets/_Standard Assets/Characters/Models/Male/Textures/`. Place them as follows:

```text
character_library/Unity/
  DefaultMale.fbx
  DefaultMale.materials.json
  Textures/
    DefaultMale_Albedo.tif
    DefaultMale_Normal.tif
```

Copy the supplied [binding recipe](../assets/export_skeletons/unity-defaultmale.materials.json)
beside the FBX and rename it to `DefaultMale.materials.json` before import. The
importer checks the FBX and texture hashes, accepts only textures beside that FBX
or in its child folders, and packs the images into the local character asset.
Different source bytes require a reviewed matching recipe; keep hash validation
enabled. This changes material bindings without editing bones, topology or weights.

Some Manny exports refer to the original author's unavailable normal/environment
images. The importer reports missing images and retains the material colours.
This workflow does not recreate missing vendor texture files or engine shaders.

## Preview the same motion in one viewport

1. Capture normally on **Native capture skeleton** and select the desired result.
   Apply source contact correction first if wanted.
2. Select **Epic Manny Simple (bundled)** from **Add Character...** above People.
   For Mixamo/Unity, place the downloaded FBX and textures in `character_library/`
   and select it from the same dropdown. **File > Import Character...** remains
   available. Adding a character starts in rest pose, without automatic retargeting.
   Target-slot registration alone does not add a row to the project.
3. Right-click the imported character row and select **Retarget > [source person]**.
   Repeat using the same source/result for the other characters.
4. Hide the source mesh if desired. Use the row checkboxes to show one target at
   a time, hold the same timeline frame and camera settings, then play the clip.
   With **Follow Actor**, the selected source trajectory remains the common
   camera reference even when its mesh is hidden.

Selecting **Output Skeleton** changes FBX export; it does not replace the viewport
mesh. To review target deformation, use the imported character workflow above.
Existing character animations must be retargeted again to use the UE/Unity hand
repair; the update does not rewrite historical animations automatically.

## Export and finger adaptation

Choose Mixamo, UE5 or Unity under **Output Skeleton** and export FBX. Automatic
and Installed official character both use the registered official target.
**Include target mesh** retains its original skinned mesh; uncheck it for bones
and animation only. Use **Native capture skeleton** for the existing source export.

UE/Unity finger transfer decodes the source export basis for rotations and neutral
offsets, then uses actual joint-to-joint directions, palm frames and rest-relative
local rotations. Blender display tails are not used as anatomical axes. Target
bone names, authored rest matrices, mesh topology and skin weights are retained;
no finger clamping or smoothing is added. Mixamo keeps its existing finger adapter.
The same-motion regression is described in [FORK_VALIDATION.md](FORK_VALIDATION.md).
Engine import, Avatar setup and other motion clips still need their own review.

## Output path boundaries

Target FBX output uses the absolute destination selected by the user. A missing
`.fbx` suffix is added; a different suffix or missing parent folder is rejected.
There is no fallback to a maintainer-specific export address. Ordinary project
output folders, including Unicode names and spaces, remain supported.

The worker resolves path aliases before checking the destination. Final FBXs
cannot be written into program resources, model/runtime directories or internal
caches or `character_library/`, or over registered original character files. Original-file hardlink
aliases are rejected too. Blender checks its active animation input folder again
before creating the temporary export file. Temporary output stays beside the
chosen destination and replaces it only after successful FBX writing.

Local job receipts may record absolute paths for local processing; these ignored
receipts and caches are excluded from the repository. Bundled resource metadata
contains repository-relative document URLs.
