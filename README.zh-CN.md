# RGB MoCap — Fusion 与中英文界面分支

[English](README.md) · [本分支](https://github.com/EWIY/toyxyz_RGBMocap) · [原项目](https://github.com/toyxyz/toyxyz_RGBMocap) · [原版 README](README.upstream.md)

这是原版 RGB MoCap 的功能扩展分支，保留 Windows 本地动捕、接触修正、角色重定向
和导出流程。当前源码基于上游
[`5aaad4ee`](https://github.com/toyxyz/toyxyz_RGBMocap/commit/5aaad4eedf1d1eb388f1f96da123e7c411822594)，
包含安装恢复改进及 FlowHMR 下载回调修复。**首次启动默认英文。**

## 本分支增加的功能

| 功能 | 行为与边界 |
| --- | --- |
| 中英文界面 | Language 菜单、中文控件与帮助、弹窗及偏好保存；新安装默认 English。 |
| FlowHMR + GVHMR Fusion | 以 FlowHMR 为基础，由 GVHMR 按 0–100% 权重引导所选躯干、颈部与头部旋转；复用匹配的源动捕，自动计算缺少的部分。 |
| 共享场景原点 | 以首个完整片段首帧骨盆的水平位置为公共原点，人物与相机一起平移，保留相对位置、竖直高度及原始动作。 |
| HumanArt 检测器 | 在 YOLOv8x 外提供 YOLOX-X HumanArt；从官方来源另行下载 ONNX，在模型管理器校验并导入。 |
| 官方目标骨架导出 | 单独取得并导入官方 Adobe X Bot、Epic Manny Simple、Unity DefaultMale，使用原始骨架，可选保留蒙皮网格；官方素材只保存在本地，已移除自建兼容模板。 |
| 同视窗角色预览与手指适配 | 将同一动作重定向到多个角色，在同一视窗、时间线上切换显示；修复 UE5、Unity 的指节方向与静置姿态适配，保留官方骨架和蒙皮权重。 |
| 稳定性修复 | 保留滚轮误触防护、Windows UTF-8 输出、空接触数据处理、经过限定的缓存兼容和预览流程修复。 |

这些功能同时涉及界面、后台调度、预览、相机、场景和导出。本仓库不包含模型权重、
注册人体数据、角色素材、已安装环境、缓存、个人工程及重定向工作数据。

## 安装与启动

需要 **64 位 Windows、兼容的 NVIDIA 显卡与驱动、OpenGL 4.3、Git for Windows**
和可写目录。基础安装器当前估算约需 **34 GiB 可用空间**，不含动捕权重、工程和
可选环境；具体以安装器打印的估算为准。不同素材还需要额外内存和显存。

1. 安装 [Git for Windows](https://git-scm.com/download/win)，打开命令提示符。
   克隆本分支的 `custom` 分支：

   ```cmd
   git clone --branch custom https://github.com/EWIY/toyxyz_RGBMocap.git RGBMoCap
   cd RGBMoCap
   ```

2. 安装固定版本的软件依赖：

   ```cmd
   install.cmd
   ```

   安装器准备分离的 ExMR、FlowHMR、GVHMR、界面及附加功能环境，Blender、FFmpeg、
   原生修正模块、PEAR 支持，以及 HumanArt 的 ONNX Runtime 依赖。
   **不会自动取得动捕权重或需注册的人体模型。** 可选支持失败会单独报告，按提示重试。

3. 启动程序：

   ```cmd
   RGBMoCap.cmd
   ```

   保持控制台开启。在“模型管理器”准备所选模型文件。公开且支持的文件可自动下载；
   需要授权的文件请点击手动下载，在提供方注册并接受条款，再用“导入”校验。
   本程序不需要您的密码或访问令牌。

安装器使用固定版本、HTTPS 来源和 SHA-256 校验，不需要拷贝别人的 `runtime*`
目录。根目录历史 `requirements-*.txt` 是缓存身份输入，不能替代管理式安装。
更多说明见[安装与恢复指南](docs/USER_GUIDE.md#install)。

### 可选环境

完成基础安装后，按需运行 `Setup_MAMMA.cmd` 或 `Setup_PromptHMR.cmd`。
它们需要 Visual Studio 2022 C++ Build Tools、Windows SDK 和 CUDA Toolkit 12.8，
环境相互独立，不由 `install.cmd` / `update.cmd` 安装。
详见 [MAMMA](docs/MAMMA.md) 与 [PromptHMR](docs/models/PROMPTHMR.md)。
PEAR 复用基础支持，是不录制、不导出的实验性实时骨骼预览。

## 使用流程

1. 选择 AI 动捕模型并准备文件，再使用“文件 > 打开视频”。MAMMA 应先选择模型，
   再打开同一次表演的同步固定机位视频。
2. ExMR、FlowHMR、GVHMR 和 Fusion 需要指定人物或处理多人时，先用“查找人物”。
   否则会自动跟踪一个人。PromptHMR 与 MAMMA 使用各自的多人流程。
3. 裁剪视频范围，运行“重建 3D”。查看原始或修正后的结果，按需编辑接触区间，
   点击“应用修正”更新动作和关联角色。
4. “文件 > 导出”可输出原生 FBX、BVH 或便携 Blender 工程。“导出预览”可保存
   输入视频与当前视口并排的 MP4。导入 FBX、VRM、PMX 后的角色重定向仍然保留，
   PMX 可导出 VMD。

### Fusion

选择 **FlowHMR + GVHMR · Fusion**，设置引导权重与区域，再点击“重建 3D”。
默认以 100% 引导躯干、颈部和头部；0% 保留 FlowHMR。根运动、腿、手臂局部旋转
和手指沿用 FlowHMR，但躯干改变后，手的世界坐标路径仍可能改变。
源动作先进行接触修正，需要改动时使用私有源副本。不会额外平滑或重定时。

需准备 FlowHMR 与 GVHMR 的必需文件，无需额外训练的融合权重。结果在独立
`fusion` 工作区中，视频、人物、跟踪与帧范围一致时才复用。
详见 [Fusion 指南](docs/models/FUSION.md)。

### 场景原点

人物与相机共用水平参考，不是逐人独立居中，也不会把行走变成原地动作或增加脚锁。
旧版已完成场景仍可读取；需要迁移时，对相关人物使用“准备预览”，让派生位置和
相机保持一致，原始预测文件保留。详见[坐标及迁移说明](docs/FORK_GUIDE.md#shared-flowhmr-scene-origin)。

### HumanArt 与目标骨架

- **HumanArt：**选择“人物检测器 > YOLOX-X (HumanArt)”，在模型管理器点击
  手动下载，取得官方 ZIP 后导入其中的 `end2end.onnx`。校验后会放入
  `models/yolox/yolox_x_humanart.onnx`。默认仍是 YOLOv8x，不保证所有素材都改善。
- **官方目标骨架：**先从官方取得 X Bot、Manny Simple 或 DefaultMale，
  在“文件 > 导出骨架目标管理”点击“导入官方 FBX…”。动捕继续使用默认原生骨架，
  当前 FlowHMR 流程对应原生 SMPL-H；导出时再选择 Mixamo、UE5 或 Unity。
  勾选“包含目标网格”保留官方蒙皮，取消则仅导出骨骼和动画。
  未安装目标时只禁用相应目标选项，原生动捕仍可使用，不会回退到自建骨架。
- **同视窗预览：**通过“文件 > 导入角色”添加带蒙皮角色，右键角色行选择
  “重定向 > 源人物”。保持时间帧、视角和“跟随人物”设置一致，依次勾选角色显示。
  选择“输出骨架”本身不会替换视窗模型；隐藏源人物后，仍可使用其轨迹作为共同
  跟随相机参照。UE、Unity 手指改用真实指节方向、掌面和相对静置旋转，Mixamo
  沿用原适配；已有角色动画需要重新重定向才能应用修复。

官方链接、文件放置、导入登记、同视窗预览和限制见[官方目标准备与使用](docs/OFFICIAL_EXPORT_TARGETS.md)。

### 当前本地安装使用的模型镜像

以下链接根据本地下载／导入收据和镜像记录整理；仓库不包含模型文件。

| 模型 | 镜像文件 |
| --- | --- |
| VGGT-Omega 512 | [wincentIsMe / VGGT-Omega](https://huggingface.co/wincentIsMe/VGGT-Omega/blob/main/vggt_omega_1b_512.pt) |
| GVHMR | [camenduru / GVHMR](https://huggingface.co/camenduru/GVHMR/blob/main/gvhmr/gvhmr_siga24_release.ckpt) |
| HMR2 | [camenduru / HMR2](https://huggingface.co/camenduru/GVHMR/blob/main/hmr2/epoch%3D10-step%3D25000.ckpt) |
| ViTPose-H Multi-COCO | [camenduru / ViTPose](https://huggingface.co/camenduru/GVHMR/blob/main/vitpose/vitpose-h-multi-coco.pth) |
| ViTPose-H WholeBody | [JunkyByte / easy_ViTPose](https://huggingface.co/JunkyByte/easy_ViTPose/blob/main/torch/wholebody/vitpose-h-wholebody.pth) |

**镜像文件可能需要修改模型验证配置。** 当镜像 SHA-256 与程序支持的文件不同时，
需先确认来源与版本，再在本地 `mocap/models.py` 调整对应模型的 `expected_sha256`，
核对文件大小检查，并通过模型管理器重新导入；不要删除或关闭校验。
上表 VGGT-Omega 镜像需要这项本地调整，其余四个已记录文件与现有校验值一致，
使用相同文件时无需修改。发布版仍保留上游默认模型身份，具体参数见
[VGGT 镜像校验说明](docs/FORK_GUIDE.md#local-mirror-validation)。镜像继续受原模型条款约束，
尚未确认镜像与官方文件的效果完全等价。

## 保留的上游能力

支持 ExMR、FlowHMR、GVHMR、MAMMA、PromptHMR 和 PEAR；保留脚/手掌接触编辑、
多人及多个动作片段、角色重定向、Generic/Blender 与 3ds Max Biped BVH 配置、
可选首帧 T 姿势、便携 Blender 视频/相机工程及资源自适应处理。
原生 FBX/BVH 还保留默认关闭的“导出时移到原点”和“对称静止姿态”。前者会逐人
独立居中，与本分支人物和相机共用的场景原点处理不同；这些选项不作用于便携
Blender 工程或三套兼容骨架的重定向导出。
**资源保护默认开启。** 各模型设置见[模型指南](docs/models/README.md)。
上游历史性能测量见[性能说明](docs/PERFORMANCE.md)，这些不是本分支的新基准测试。

原项目演示：[动捕](docs/samples/motion-capture.mp4)、
[角色重定向](docs/samples/character-retargeting.mp4)、[多相机动捕](docs/samples/multi-cam-mocap.mp4)。

## 更新与发布检查

关闭程序，在跟踪自己 Fork 的干净分支运行 `update.cmd`，通常是 `custom` 跟踪
`origin/custom`。它会快进拉取并检查依赖；有源码修改时会停止，不能强制丢弃修改
来绕过保护。`--verify-all` 可强制完整运行环境校验。合并未来上游更新由维护者单独进行。

```cmd
runtime\python.exe -X utf8 -B tools\check_source.py
runtime\python.exe -X utf8 -B tools\check_fork.py
runtime\python.exe -X utf8 -B tools\run_fork_tests.py
```

前两个检查也可用普通 Python 3.10+。发布步骤见[维护说明](docs/PUBLISHING.md)，
实际验证范围和未覆盖部分见[本分支验证记录](docs/FORK_VALIDATION.md)。

## 原作者与许可证

原始应用由 **[toyxyz / RGB MoCap](https://github.com/toyxyz/toyxyz_RGBMocap)**
及其贡献者开发。本分支保留[原版 README](README.upstream.md)、
[研究引用](docs/CITATIONS.md)、[MIT 许可证](LICENSE)和[第三方许可说明](THIRD_PARTY_NOTICES.md)。
MIT 仅适用于其覆盖的原创代码与文档，不重新授权第三方代码、派生修改、模型权重或
角色素材。GVHMR/ExMR、MAMMA、PromptHMR、SMPL/MANO 等有各自条件，Fusion
不会消除限制；不能把整个组合应用一概当成无限制商用的 MIT 项目。
