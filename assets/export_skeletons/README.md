# Official export target setup resources

The former project-authored generic skeleton templates and their generator have
been removed. The [official Epic Manny Simple FBX](ue5_manny/NOTICE.md) is included
with its original skeleton/skin and separate Epic terms. First UE5 export prepares
a local cache; no generated cache is committed. Mixamo and Unity assets remain
separately acquired. See [target setup](../../docs/OFFICIAL_EXPORT_TARGETS.md).

`unity-defaultmale.materials.json` is a declarative binding recipe for the pinned
official DefaultMale FBX and two separately acquired official textures. It contains
filenames, SHA-256 pins and material bindings only. Copy it beside the matching
FBX as `DefaultMale.materials.json`; retain the referenced `Textures/` folder.
The provider's resource terms continue to apply to downloaded assets. RGBMoCap
code remains under the root [MIT license](../../LICENSE), with component notices
in [THIRD_PARTY_NOTICES.md](../../THIRD_PARTY_NOTICES.md).
