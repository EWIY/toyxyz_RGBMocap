# Character library

Use **Add Character...** above **People** to add a character without browsing for
its file. Official **Epic Manny Simple (bundled)** is available immediately from
the included resource. Other library models appear after you put them in
`character_library/`, under the installation/data folder by default. Its folder
button creates and opens this location. Reopen the dropdown to refresh.

```text
character_library/
  UE5/
    SKM_Manny_Simple.fbx
  Mixamo/
    X Bot.fbx
  Unity/
    DefaultMale.fbx
    DefaultMale.materials.json
    Textures/
      DefaultMale_Albedo.tif
      DefaultMale_Normal.tif
  My Character/
    My Character.vrm
```

- **Mixamo:** sign in to [Adobe Mixamo](https://www.mixamo.com/) and download a
  skinned T-pose FBX. Put it under `character_library/Mixamo/`.
- **Unity:** get DefaultMale from the [official repository](https://github.com/Unity-Technologies/Standard-Assets-Characters/tree/8f185aa3c782d824976653dd6a6476312daad241/Assets/_Standard%20Assets/Characters/Models/Male).
  Put the FBX under `character_library/Unity/`. For textures, use the supplied
  [binding recipe](../assets/export_skeletons/unity-defaultmale.materials.json),
  renamed to `DefaultMale.materials.json`, and the official images shown above.
  See [texture instructions](OFFICIAL_EXPORT_TARGETS.md#defaultmale-textures).
- Other supported FBX, VRM and PMX files can use any subfolder. Keep their texture
  paths intact and unzip packages first. File/folder links and junctions are
  skipped. The library uses existing humanoid mappings; it does not auto-map
  arbitrary rigs. Up to eight imported characters per project are supported.

## Retarget, preview and export

1. Reconstruct motion normally and choose the desired source/result. Apply contact
   correction first if needed. FlowHMR still captures on native SMPL-H.
2. Select a character from **Add Character...**. The background importer creates
   a project-owned asset and selects its new row. It starts in rest pose;
   **adding a character does not retarget automatically**.
3. Right-click that row and choose **Retarget > [source person]**. Wait for the job
   to finish. Repeat with the same source/result for each comparison character.
4. Use the row checkboxes to compare in the same viewport/timeline with fixed
   camera settings. Select the target and use **File > Export Character...** for
   FBX with or without its mesh; PMX also supports VMD.

**File > Import Character...** continues to browse files elsewhere. Separately,
**Output Skeleton** controls direct source-to-target FBX export. Use **File >
Export Skeleton Targets... > Import official FBX...** to register Mixamo/Unity
for that selector. Adding a preview character does not register an export slot.

Library sources stay unchanged; project imports retain their own prepared assets
and available packed textures. Replacing a library file affects future imports.
Export cannot write into the library; a newly imported character's original file
is also protected against overwrite through a hardlink alias.

Only the approved Epic resource is bundled, at
`character_library/UE5/SKM_Manny_Simple.fbx`, with its
[Epic notice](../assets/export_skeletons/ue5_manny/NOTICE.md). It appears in the
dropdown once as **Epic Manny Simple (bundled)**; direct UE5 export uses this same
verified file. No second FBX copy is kept under `assets/`. Manny uses material
colours where its original referenced images are unavailable. Mixamo/Unity files
must be acquired under their providers' terms. Only this exact FBX and `character_library/README.md` are versioned. All other
library files, including user characters, textures and sidecars, are excluded
from Git. The Epic license and provenance remain at their existing linked paths.

The viewport uses supported tangent-space normal maps when importing a character with a compatible material.
