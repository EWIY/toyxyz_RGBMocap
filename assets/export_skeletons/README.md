# Redistributable export skeleton templates

The three compatible templates are authored in
[`mocap/builtin_skeletons.py`](../../mocap/builtin_skeletons.py). Their numeric
proportions, T-pose geometry and analytic contact proxies are original project
content under the root [MIT license](../../LICENSE). No vendor character mesh,
texture, animation, bind matrix or extracted model data is included here.

Mixamo, Unreal Engine and Unity names identify interoperability targets; the
templates are not official vendor assets or an endorsement. Unity Humanoid uses
an Avatar mapping rather than one mandatory FBX hierarchy. The UE5 template has
a root, pelvis, five spine/two neck bones and named fingers, but does not reproduce
every mannequin twist, IK, corrective or control bone. Engine/character retargeting
may still be needed. There is no claim of an identical vendor bind pose.

After installation, select **Output Skeleton > Mixamo Humanoid / UE5 compatible
skeleton / Unity Humanoid** and export FBX. First use builds small local files with
the installed Blender from source, without downloading a target character. These
generated caches include simple foot/palm proxies for the existing contact solver;
the exported FBX contains bones and animation only.

Generated targets are hash-checked in ignored `cache/export-targets/`. Optional
user-registered targets in `character_work/presets/` take precedence and remain
private. See the [fork guide](../../docs/FORK_GUIDE.md) for preparation and limits.
