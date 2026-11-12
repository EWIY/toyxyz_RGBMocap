# Blender 骨骼串流与源骨架导出

[English · Blender bone streaming](USER_GUIDE.md#stream-bones-to-blender) · [English · FBX and Blender](USER_GUIDE.md#fbx-and-blender)

## 在 Blender 同步预览骨架

1. 在 **Blender 4.5 或更新版本**打开 **Edit > Preferences > Add-ons**，从右上角菜单选择 **Install from Disk**，选中完整的 [RGB MoCap Bone Stream ZIP](../blender_addon/rgbmocap_bone_stream.zip?raw=1) 并启用插件。曾安装过早期的单文件版本时，先移除旧版。
2. 在 RGB MoCap 打开已有动捕结果的项目，在左侧 **Stream** 页将目标设为 **Blender**，勾选要发送的演员。**Stream** 的勾选与 **People** 页的可见性分别控制。
3. 在 Blender 的 3D 视口按 **N**，打开 **RGB MoCap > RGB MoCap Bone Stream**，点击 **Connect**。默认端口为 `49168`，连接限于本机。在 RGB MoCap 播放或拖动时间轴，Blender 中的骨架会跟随动作和根位移。

串流适用于已处理的离线源人物骨骼。连接绑定到 Blender 当前场景与视图层，切回该场景和视图层即可继续。取消勾选演员会隐藏对应骨架，**Disconnect** 会保留 Blender 中已有的对象。需要发送角色蒙皮或材质时，使用角色的 FBX 导出。

## 烘焙为 Blender Action

在 Blender 的 **Object Mode** 选择正在接收串流的骨架，点击 **Bake**。只有一套串流骨架时，插件会自动选用它。烘焙保存该演员整段已录制的动作和根运动，使用 Blender 当前场景的帧率。分段之间的空档会保持上一姿势，直到下一段开始。单次最多烘焙 **36,000 个时间轴帧**。

完成后，这套骨架会成为普通 Blender 对象，其他已勾选的演员继续串流。保存 `.blend` 即可保留 Action。需要移除闲置串流骨架时，可用 **Clean** 检查并确认，已烘焙或被其他对象引用的骨架会保留。

## 源骨架导出选项

通过 **File > Export…（文件 > 导出）**导出当前选中的源演员动作。以下选项默认关闭，角色重定向后的导出使用自己的设置。

| 选项 | 作用 |
| --- | --- |
| **FBX Compatibility (Maya)** | 点导出后，由随附的 Blender 在后台重新写入 FBX，保留源骨架的静止姿势和动画关键帧，用于 Maya 导入。 |
| **Place at origin** | 将每位演员的首帧根节点分别移到水平原点（X=0、Z=0），保留高度、朝向和后续位移。同一演员的多个导出片段共用这次偏移。双人互动需要保留相对站位时，保持关闭。 |
| **Symmetrical rest pose** | 将 SMPL 源骨架左右对应骨段的参考长度和方向做成对称。保留动作时序和旋转，手脚落点可能改变，接触也不会重新求解。 |
| **Add T-pose before motion** | 在原动作前插入一帧参考姿势。原动作顺延一帧，原本的骨架绑定姿势保留。 |

**Place at origin** 和 **Symmetrical rest pose** 用于支持的源骨架 FBX/BVH 导出。GEM-X 的 SOMA Native77 可用原点归位和前置参考姿势。[GEM-X 中文指南](models/GEMX.zh-CN.md)
