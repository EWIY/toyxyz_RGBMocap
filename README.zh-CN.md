# RGB MoCap

[English](README.md) · [原项目](https://github.com/toyxyz/toyxyz_RGBMocap) · [上游原版说明与致谢](README.upstream.md)

Windows 本地视频动捕工具，支持接触修正、角色重定向和动画导出。
本分支增加以下功能，**新安装默认英文**。

## 本分支功能

| 功能 | 用途 |
| --- | --- |
| 中英文界面 | Language 菜单、中文帮助和偏好保存。 |
| FlowHMR + GVHMR Fusion | 以 FlowHMR 为基础，用可调权重的 GVHMR 引导躯干、颈部和头部。 |
| FlowHMR 共享原点 | 人物和相机一起平移，保留相对位置与行走位移。 |
| HumanArt 检测器 | 在 YOLOv8x 外可选 YOLOX-X HumanArt。 |
| 角色库 | People 上方固定下拉栏添加角色，支持 FBX、VRM、PMX 和子文件夹。 |
| 官方角色导出 | 内置 Epic Manny Simple；Mixamo X Bot、Unity DefaultMale 提供官方下载与导入入口，可导出带原始蒙皮或仅骨架的动画。 |
| 预览与修复 | 同视窗、同时间线对比，UE5/Unity 手指适配、滚轮防误触及后台稳定性修复。 |

## 安装

需要 64 位 Windows、支持的 NVIDIA 显卡与驱动、OpenGL 4.3、Git for Windows
及可写目录。基础运行环境约占 34 GiB，模型和工程另计。

```cmd
git clone --branch custom https://github.com/EWIY/toyxyz_RGBMocap.git RGBMoCap
cd RGBMoCap
install.cmd
RGBMoCap.cmd
```

启动后在 **Model Manager／模型管理器**下载或导入所选动捕模型的必需文件。
动捕权重及需注册的人体模型另行获取。可选 MAMMA、PromptHMR 分别运行
`Setup_MAMMA.cmd`、`Setup_PromptHMR.cmd`。
详见[安装与故障排查](docs/USER_GUIDE.md#install)。

## 动捕与导出

1. 选择动捕模型、打开视频并裁剪范围。ExMR、FlowHMR、GVHMR、Fusion 如需指定
   人物或处理多人，先点 **Find person／查找人物**；MAMMA、PromptHMR 使用各自的多人流程。
2. 点击 **Reconstruct 3D／重建 3D**。检查结果，按需编辑接触区间并点
   **Apply Correction／应用修正**。动捕继续使用原生人体模型，FlowHMR 对应 SMPL-H。
3. **File > Export...／文件 > 导出**输出原生 FBX、BVH 或 Blender 工程；
   **Export Preview...／导出预览**保存输入视频与当前视口并排的 MP4。
   角色预览与角色 FBX 导出见下节。

**Fusion：**选择 **FlowHMR + GVHMR · Fusion**，设置权重和区域；需准备两个引擎
的必需模型。[详细说明](docs/models/FUSION.md)。
**HumanArt：**选择 **Actor Detector > YOLOX-X (HumanArt)**，在模型管理器手动下载
官方 ZIP，再导入其中的 `end2end.onnx`。

## 添加角色与重定向

| 角色 | 获取及放置位置 |
| --- | --- |
| Epic Manny Simple | 已内置官方骨架与蒙皮；下拉栏直接选择 **Epic Manny Simple（内置）**，无需下载或找文件。 |
| Adobe Mixamo X Bot | 登录 [Mixamo](https://www.mixamo.com/) 下载带蒙皮的 T-pose FBX，放入 `character_library/Mixamo/`。 |
| Unity DefaultMale | 从 [Unity 官方仓库](https://github.com/Unity-Technologies/Standard-Assets-Characters/tree/8f185aa3c782d824976653dd6a6476312daad241/Assets/_Standard%20Assets/Characters/Models/Male) 获取 `DefaultMale.fbx`，与贴图一起放入 `character_library/Unity/`；见[贴图配置](docs/OFFICIAL_EXPORT_TARGETS.md#defaultmale-textures)。 |

`character_library/` 默认在程序安装目录内。其他受支持的角色和贴图也可按子文件夹
放入。下拉栏旁的文件夹按钮可直接打开此目录，重新展开下拉栏即可刷新。
原有 **File > Import Character...／文件 > 导入角色**仍可浏览其他位置。

1. 在 People 上方 **Add Character...／添加角色…** 下拉栏选择角色。导入后显示
   静置姿态，**添加本身不会自动重定向**。
2. 右键新角色行，选择 **Retarget > 源人物**，等待处理完成。对比多个角色时，
   使用同一个源人物和动作结果。
3. 用角色行复选框切换显示，在同一视窗、时间线和相机设置下对比。
   选中角色，使用 **File > Export Character...／文件 > 导出角色**输出 FBX，
   可选包含网格；PMX 另支持 VMD。

每个工程最多八个导入角色，骨骼需符合现有的受支持映射。
如需直接按目标骨架导出，选择 **Output Skeleton > UE5 compatible skeleton**，
首次使用会准备内置 Manny。Mixamo、Unity 在 **File > Export Skeleton Targets...
> Import official FBX...** 中登记。Output Skeleton 仅控制导出，不会替换视窗角色。
[角色库说明](docs/CHARACTER_LIBRARY.md) · [官方目标与贴图](docs/OFFICIAL_EXPORT_TARGETS.md)。

## 本地使用过的模型镜像

| 模型 | 镜像 |
| --- | --- |
| VGGT-Omega 512 | [wincentIsMe / VGGT-Omega](https://huggingface.co/wincentIsMe/VGGT-Omega/blob/main/vggt_omega_1b_512.pt) |
| GVHMR | [camenduru / GVHMR](https://huggingface.co/camenduru/GVHMR/blob/main/gvhmr/gvhmr_siga24_release.ckpt) |
| HMR2 | [camenduru / HMR2](https://huggingface.co/camenduru/GVHMR/blob/main/hmr2/epoch%3D10-step%3D25000.ckpt) |
| ViTPose-H Multi-COCO | [camenduru / ViTPose](https://huggingface.co/camenduru/GVHMR/blob/main/vitpose/vitpose-h-multi-coco.pth) |
| ViTPose-H WholeBody | [JunkyByte / easy_ViTPose](https://huggingface.co/JunkyByte/easy_ViTPose/blob/main/torch/wholebody/vitpose-h-wholebody.pth) |

镜像文件与支持版本字节不同时，需核对来源后修改本地 `mocap/models.py` 的
`expected_sha256` 和大小检查，再重新导入；保留哈希校验。
上表 VGGT 镜像需要此调整，仓库默认仍使用官方校验。
[详细说明](docs/FORK_GUIDE.md#local-mirror-validation)。

## 文档与许可

[使用指南](docs/USER_GUIDE.md) · [动捕模型](docs/models/README.md) ·
[分支功能](docs/FORK_GUIDE.md) · [验证记录](docs/FORK_VALIDATION.md) ·
[维护与发布](docs/PUBLISHING.md)

基于 [toyxyz/RGBMoCap](https://github.com/toyxyz/toyxyz_RGBMocap)，上游基线为
[`5aaad4ee`](https://github.com/toyxyz/toyxyz_RGBMocap/commit/5aaad4eedf1d1eb388f1f96da123e7c411822594)。
保留原项目 [MIT 许可证](LICENSE)、[组件许可](THIRD_PARTY_NOTICES.md)和
[研究致谢](README.upstream.md)。内置 Manny 单独适用 [Epic 来源与许可说明](assets/export_skeletons/ue5_manny/NOTICE.md)，
Mixamo、Unity 角色遵循各自提供方条款。本地角色库、工程、模型权重、运行环境及缓存不进入 Git。
