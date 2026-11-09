# Character library

The bundled Epic Manny Simple is at `UE5/SKM_Manny_Simple.fbx`.
Select **Epic Manny Simple (bundled)** in **Add Character...** above People,
then right-click its new row and choose **Retarget > [source person]**.
The same verified FBX supplies the UE5 Output Skeleton target.

See the existing [Epic notice](../assets/export_skeletons/ue5_manny/NOTICE.md),
[license](../assets/export_skeletons/ue5_manny/LICENSE.txt) and
[provenance](../assets/export_skeletons/ue5_manny/PROVENANCE.json).
The bundled file is unchanged; missing author-side textures are not included.

Put your own supported FBX, VRM and PMX files and textures in subfolders here.
For example, use `Mixamo/` for a separately acquired X Bot and `Unity/` for
DefaultMale and its textures. Reopen the dropdown to refresh.
See the [full library workflow](../docs/CHARACTER_LIBRARY.md).

Only this guide and the exact bundled Manny FBX are versioned. All other
characters, textures and sidecars remain ignored user data. Do not replace or
edit the bundled FBX; use a separate subfolder for a modified character.
