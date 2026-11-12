# GEM-X

[English](GEMX.md) · [动捕模型](README.md)

GEM-X 从一段固定机位视频中自动选择一位主要人物，重建身体和手指动作。RGB MoCap 保留原生的 **SOMA Native77** 骨架、估计的体型及 SOMA MID 表面。预览时会给整段动作应用同一个垂直偏移，让人物靠近估计的地面，同时保留原动作的逐帧高度变化。上游测试中，GEM-X 处理较快，整体动作质量相对较低。

## 安装

1. 在 Windows 上运行 `install.cmd`，然后关闭 RGB MoCap。
2. 在程序目录运行 `Setup_GEMX.cmd`，阅读命令显示的上游条款。安装过程中预留 **12 GiB** 可用空间，模型文件另计。安装程序复用 ExMR 的 CPython 3.12.10，另外安装独立的 PyTorch 2.10（CUDA 12.8）、Transformers 5.3、ONNX Runtime 和 SOMA-X 0.3.3。[固定版本的 NVIDIA Warp](https://pypi.org/project/warp-lang/1.19.0/) 要求 Turing 或更新的 NVIDIA 显卡，以及 R580 系列或更新的驱动。安装使用预构建包，无需 Visual Studio 或 CUDA 编译器。
3. 重新打开 RGB MoCap，选择 **GEM-X**，进入 **Model Manager（模型管理器）**。**Download All** 会从 NVIDIA 和 OpenMMLab 获取九个所需文件。已经下载过的文件可以直接导入。手动安装人物检测模型时，从指定的 HumanArt YOLOX ZIP 中提取并导入 `end2end.onnx`。

实测中，共用 CUDA DLL 时，GEM-X 运行环境额外占用约 **2.13 GiB**。文件系统无法链接这些文件时，约占 **5.08 GiB**，另需 **7.11 GiB** 存放模型。安装只共享通过 SHA-256 白名单验证的 DLL，Torch 和 Python 依赖各自隔离。Blender 和 FFmpeg 使用基础安装提供的版本。如果更新后提示需要配置 GEM-X，重新运行 `Setup_GEMX.cmd`。

## 重建与导出

1. 选择 **File > Open Video（文件 > 打开视频）**，使用机位固定、主体清晰的素材。按 30 fps 的工作帧率裁剪到 **4–1,800 帧**。
2. 点击 **Reconstruct 3D（重建 3D）**。程序会自动跟踪主要人物，提取 2D 观测和身体特征，再预测整段 SOMA 动作及表面。用时间轴检查结果，开启 **Bone Overlay（骨骼叠加）**可显示 Native77 骨架。使用 **Save Project As（项目另存为）**可保留媒体和结果。
3. 通过 **File > Export（文件 > 导出）**输出 FBX、BVH 或 **Blender project + video**。FBX 和 BVH 按 30 fps 保存当前选中的原始或修正动作，包含 77 根骨骼及手指动画。BVH 使用 **Generic / Blender** 格式，单位为米，Y 轴向上。**Place at origin** 将首帧根节点在水平面归零并保留高度和后续位移。**Add T-pose before motion** 在动作前加一帧参考姿势。Blender 工程包括可编辑骨架、独立表面缓存和同步的 **Input Video** 场景，请把 `.blend`、`surface.pc2` 与 `video.mp4` 放在一起。
4. 要把动作转到角色上，可通过 **File > Import Character（导入角色）**添加人形角色，再右键角色行，选择 **Retarget > Person 1**。角色保留自身骨长，根运动按角色腿长缩放。重定向后使用角色平时的导出格式。

GEM-X 当前的离线流程使用固定机位。移动机位追踪、**Camera Preview** 和独立的 EgoHand 推理不适用于这条路径。动作尺度与空间位置来自估计。人物重叠或主体不清晰时，自动选人可能选错。

## 接触修正

开启 **Enable Correction（启用修正）**后，新重建会接着执行修正。已有结果可通过 **Apply Correction（应用修正）**处理，并在同一帧对照原始与修正姿势。可以在时间轴上调整脚部和手部锁定区间后再次应用。脚部默认开启，手部按需启用。**Flat Ground** 用于同一平面，**Multi Level** 可保留不同的支撑面高度。

自动接触区间根据 SOMA 脚底和手掌的运动估算。对刻意滑动、踩台阶或扶高处的动作，建议检查对应区间。求解器根据演员的关节位置和骨长处理接触，SOMA-X 再一起烘焙骨骼和表面。修正复用已保存的动作和四项 SOMA 几何资产，无需重跑视频推理。修正后的表面额外占用约 **6.2 MiB/秒**。导出和重定向会使用当前选中的动作版本。

## 资源与排查

**Automatic** 在显存充足时以四帧为一个图像批次，显存紧张时改用单帧。**Low Memory** 始终使用单帧。遇到 CUDA 分配失败时可降低批次重试。**Resource Safety** 继续使用程序现有的内存监控与 PyTorch 分配策略。批次设置不改变动作帧数或模型精度。

上游用 RTX 5090 测试了一段 9.8 秒的固定机位素材（294 帧），文件校验、推理和网格求值合计约 **104 秒**，PyTorch 已分配显存峰值为 **3.48 GiB**。这是一段素材的测量值。30 fps 的原生网格缓存约为 **6.2 MiB/秒**，保留项目目录即可保留缓存。

安装日志位于 `.setup/logs/gemx-*.log`。请保留 `runtime_gemx/`、`.setup/gemx-runtime.json` 和 `runtime_exmr/`。安装完成后可以清理 `.setup/gemx-downloads/`，以后修复可能重新下载。若模型校验失败，请重新导入对应的官方固定版本。

## 来源与许可

- [GEM-X 源码许可](https://github.com/NVlabs/GEM-X/blob/4aef1452e5df171deff4f293c08e643eb450981e/LICENSE) · [组件署名与条款](https://github.com/NVlabs/GEM-X/blob/4aef1452e5df171deff4f293c08e643eb450981e/ATTRIBUTIONS.md)
- [NVIDIA GEM-X 模型卡](https://huggingface.co/nvidia/GEM-X) · [SOMA-X 资产](https://huggingface.co/nvidia/SOMA-X) · [SOMA-X Python 包](https://pypi.org/project/py-soma-x/0.3.3/)
- [OpenMMLab RTMPose 与 HumanArt 检测器](https://github.com/open-mmlab/mmpose/tree/main/projects/rtmpose)

[模型下载锁定记录](../../installer/gemx-models.json) · [运行环境锁定记录](../../installer/gemx-runtime-lock.json) · [第三方声明](../../THIRD_PARTY_NOTICES.md) · [研究引用](../CITATIONS.md)
