# SAM 3.1 可选人物追踪

[English](SAM31.md) · [动捕模型](README.md)

Windows 版的 **ExMR、FlowHMR 和 GVHMR** 可以在**查找人物（Find person）**旁选择 SAM 3.1。它根据文字提示和可选的点击标记追踪人物并填入人物列表，勾选人物后由当前动捕模型重建动作。**默认（Default）**继续使用原有追踪器。MAMMA、PromptHMR、GEM-X 和 PEAR 使用各自的人物检测流程。

## 安装

1. 在程序目录完成 `install.cmd` 后关闭 RGB MoCap，再运行 `Setup_SAM31.cmd`。安装需要 Git、网络，以及支持原生 bfloat16 的 NVIDIA CUDA 显卡。安装程序复用 ExMR 的 Python 与 Torch，在 `runtime_sam31/` 添加独立组件，安装固定版本的包并验证 CUDA attention。 [Meta SAM 条款](https://github.com/facebookresearch/sam3/blob/f1647e8d0c1d280991f4d1b7d974c2704537fe66/LICENSE)
2. 重新打开 RGB MoCap，选择 **ExMR**、**FlowHMR** 或 **GVHMR**。在 **Find person** 旁切换到 **SAM 3.1**，打开 **Model Manager（模型管理器）**，在 **SAM 3.1 Person Tracking (Optional)** 那一行点 **Auto Download**。这项可选权重需要从对应行获取。
3. 手动安装时，下载 `sam3.1_multiplex_fp16.safetensors`，在同一行点 **Import…**。文件约 **1.75 GB（1.63 GiB）**，导入时检查 SHA-256，默认存到 `models/sam31/`。这是程序使用的公开文件，可直接下载。 [Comfy-Org FP16 权重](https://huggingface.co/Comfy-Org/sam3.1/blob/5febd4769e8802cdfdb75e1f733abd8c68434a85/checkpoints/sam3.1_multiplex_fp16.safetensors)

## 选择和追踪人物

1. 打开视频，按 30 fps 的工作帧率裁剪到最多 **1,800 帧**，约一分钟。要用点击选人时，先停在裁剪范围内、人物清楚可见的一帧。
2. 选择 **SAM 3.1**，点击**查找人物**。可以直接使用默认的 `person`，或输入 `person in a red shirt` 这类短描述。只输入文字时，程序从裁剪起点开始追踪符合描述的人。
3. 要在同框多人中指定目标，可在弹窗里点一下每位目标人物的躯干。文字先找出当前帧的候选，点击再选中相应的分割区域。程序会沿裁剪范围追踪选中的人。右键撤销最后一个标记，**清除标记**清空全部标记。
4. 点击**开始追踪**，等人物列表出现后，勾选需要处理的人，再点**重建 3D**。

## 显存占用

SAM 3.1 比默认的 YOLOv8x + OSNet 追踪器占用更多显存。上游在多段 **286–568 个工作帧**的单视频中使用 `person` 提示，测得 PyTorch 已分配显存峰值为 **11.70–14.01 GiB**。与默认追踪器的差距尚未在相同输入上对照测量。

在一项另行开展的 MAMMA 实验中，三段 14.2 秒视频生成掩膜时，SAM 3.1 和 SAM 2.1 的显存峰值分别为 **10.68 GiB** 和 **1.77 GiB**。这组数字只对应实验中的掩膜阶段，程序的 MAMMA 流程使用 SAM 2.1。实际显存需求取决于素材和追踪设置，**Find person** 与 3D 重建分开执行。

## 排查

- 如果程序提示重新配置 SAM 3.1，关闭程序并重跑 `Setup_SAM31.cmd`。若模型管理器标记 **Missing**，在该行下载或导入权重。
- 提示词太宽泛时可能跟到背景人物。可换更具体的描述，或在清楚的一帧点击选人。长时间遮挡仍可能丢失目标或换人，点击未命中时可换到躯干更清楚的帧。
- 显存不足时缩短裁剪区间，或切回 **Default** 后重新点击 **Find person**。**Resource Safety** 对 SAM 3.1 生效。视频和提示词都在本地处理。

[上游验证记录](../VALIDATION.md#sam-31-person-discovery-2026-11-10)
