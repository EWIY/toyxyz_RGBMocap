"""Chinese help pages; measurements are supplied by the original guide."""
from html import escape

# Keep filenames and the provider's actual menu names verbatim in download help.
MANUAL_STEPS = {
 'humanart': '用于风格化人物的可选检测器。通过“打开下载页”取得官方 OpenMMLab yolox_x_8xb8-300e_humanart-a39d44ed.zip，阅读提供方与 HumanArt 条款后解压，在此导入其中的 ONNX 模型。应用会将它登记为 models/yolox/yolox_x_humanart.onnx。不要选择 ZIP 或其他大小的 YOLOX 模型。install.cmd 会安装固定版本的 ONNX Runtime GPU，能使用 CUDA 时优先使用，否则回退 CPU。本 Fork 不再分发权重。',
 'flow_metadata': '从下方链接下载应用支持版本的 FlowHMR 仓库根目录 config.json，可直接自动下载。请在本行导入未修改的 JSON。它是检查点元数据，与 flowhmr_latest/config.yml 不同，不能用来替换推理 YAML。',
 'exmr_config': '通过下方“支持的文件”下载 config.json。它是官方 ExMR 检查点元数据，与 exmr.safetensors 固定到同一版本。回到 ExMR 配置行导入原始 JSON，不要修改或重命名。此小文件也可自动下载。',
 'mano_right': '1. 打开下方推荐下载链接或点击“打开下载页”，进入对应文件的官方下载服务器。登录并接受提供方条款；如需注册，请到 MANO 官网注册。\n2. 下载 mano_v1_2.zip。若浏览 MANO 官网，选择 Models & Code > Models & Code。\n3. 解压 ZIP，打开 mano_v1_2/models。\n4. 回到“手部模型 / MANO 右手”一行，点击“导入”，选择完整的 MANO_RIGHT.pkl。\nHandFlow 用右手标准模型处理双手，并将左手结果镜像还原；SMPL-H 下载文件不能替代此手部模型。',
 'smplx': '1. 打开下方 SMPL-X 下载页，注册或登录并接受提供方条款。\n2. 在 SMPL-X Model 中选择 Download SMPL-X v1.1 (NPZ+PKL, 830 MB)，使用标准 v1.1 版本。\n3. 下载并解压 models_smplx_v1_1.zip。\n4. 打开 models/smplx，选择完整的 SMPLX_NEUTRAL.npz。\n5. 回到“身体模型 / SMPL-X 中性”一行，点击“导入”，选择该 NPZ 文件。通过校验后状态由“缺失”变为“就绪”。',
 'pva': '通过下方官方 Google Drive 链接下载 pvanet.pt，然后在此导入。Google Drive 可能暂时限制公开文件下载；若浏览器也受限，请稍后重试或导入已下载的官方副本。本应用不会登录账户或使用账户令牌。',
 'smplh': '1. 打开下方推荐的 AMASS 下载链接或点击“打开下载页”，进入官方下载服务器。登录并接受提供方条款；如需注册，请到 MANO 官网注册。\n2. 下载 smplh.tar.xz。在 MANO 官网，它位于 Models & Code，名称为 Extended SMPL+H model，并标有 used in AMASS project。这是本应用推荐的模型。\n3. 解压 smplh.tar.xz；若先得到 TAR 文件，请继续解压。\n4. 打开 smplh/neutral，保留完整的 model.npz。\n5. 回到“身体模型 / AMASS SMPL-H 中性”一行，导入 smplh/neutral/model.npz。这是含 16 个形状分量的中性模型。',
 'flow_vggt': '1. 打开 Hugging Face 上的 facebook/VGGT-Omega，登录、阅读条件并按需申请访问。\n2. 获得访问权限后打开 Files and versions。\n3. 下载 vggt_omega_1b_512.pt；下方文件链接可在授权后直接打开对应页面。\n4. 回到“场景相机 / VGGT-Omega 512”一行，点击“导入”并选择下载的 PT 文件。\n本应用不需要您的账户密码或访问令牌。',
 'flowhmr': '1. 打开下方支持的文件链接，进入应用支持版本的 flowhmr_latest。\n2. 下载 flowhmr_latest.ckpt。自行浏览仓库时请选择 flowhmr_latest，不要选择 flowhmr_base。\n3. 回到“动作 / FlowHMR latest”一行，导入 CKPT 文件；还须在独立配置行导入配套的 config.yml。',
 'flow_config': '1. 打开下方支持的文件链接，进入应用支持版本的 flowhmr_latest/config.yml。\n2. 保存文件。若浏览器显示正文，点击文件下载按钮或使用“另存为”保存 config.yml。\n3. 回到 FlowHMR 配置行导入文件，必须与支持的 flowhmr_latest 检查点配套。',
 'mamma': '1. 打开下方 MAMMA 官网并点击 Data。\n2. 按需注册账户，阅读并接受提供方条款后登录。\n3. 在下载页下载 mamma_mask_full_cvpr.ckpt。\n4. 回到此窗口，点击“导入”并选择该 CKPT 文件。\n本应用不会索取您的密码或账户令牌。',
 'mamma_vertices': '1. 打开下方 MAMMA 官网并点击 Data。\n2. 按需注册账户，阅读并接受提供方条款后登录。\n3. 下载 verts_512.pkl。\n4. 回到此窗口，点击“导入”并选择完整的 PKL 文件。\n这是需要注册授权的表面对应点数据，不能用普通 SMPL-X 人体模型替代。导入会校验支持的 SHA-256，不会执行该文件。',
 'pear_geocalib': '由 PEAR 相机对齐与 MAMMA 自动背景重力估计共用。MAMMA 在三维拟合前使用它，提供手动标定时无需使用。PEAR 的自动相机对齐（含单机位）也使用它。对齐不是跟踪的必要条件：若支持或模型缺失，PEAR 会提示并继续使用所选相机，停用融合与对齐脚锁定。请从官方 v1.0 发布页下载 geocalib-pinhole.tar，在此直接导入原始 TAR，无需解压。代码为 Apache-2.0，检查点为 CC BY 4.0；详见官方 LICENSE-WEIGHTS。复用已有 VGGT 权重。',
 'pear': '通过链接下载官方 pear_model.pt 检查点，然后在此导入。',
 'pear_geometry': '1. 阅读并接受 SMPL-X 与 FLAME 提供方条款，按需注册或登录。PEAR 需要 SMPL-X 2020 和 FLAME 2020，不能用标准 SMPL-X v1.1 或 MAMMA locked-head 模型替代。\n2. 打开下方 PEAR Preparation，通过其中官方 Google Drive 资源包链接下载 assets.zip。\n3. 在此导入原始 assets.zip。应用会校验 SHA-256，仅解压所需几何文件；源 ZIP 保持原样，不会复制到模型目录。\n4. 几何资源包遵循独立的提供方限制，RGB MoCap 不再分发这些数据。',
}


def manual_steps(key, filename, sam_file=None):
 if key in MANUAL_STEPS:
  text = MANUAL_STEPS[key]
  if key in {'mano_right', 'smplh'}:
   text += '\n若 MANO 官网出现 502 Bad Gateway，可通过下方推荐下载链接进入官方下载服务器并登录。若仍失败，请稍后重试或导入已有官方副本。本应用不需要您的密码或访问令牌。'
  return text
 if sam_file:
  return ('1. 打开 Hugging Face 上的 facebook/sam-3d-body-dinov3，登录并阅读提供方条件，按需申请访问。\n'
          '2. 获得权限后打开下方支持的文件链接，使用应用支持的版本与确切文件。\n'
          f'3. 点击文件下载按钮下载 {sam_file}。这是单个文件，请勿下载其他 SAM 模型系列。\n'
          f'4. 回到本行点击“导入”，选择 {filename}。\n'
          '5. 对其他两个 SAM 行重复操作：model.ckpt、model_config.yaml 与 assets/mhr_model.pt 均必需，三者须使用同一支持版本。\n'
          '本应用不需要您的账户密码或访问令牌。')
 if key.startswith('mamma_body'):
  return ('到 SMPL-X 官网注册并接受条款。下载 SMPL-X with removed head bun (NPZ, 392 MB)，'
          f'解压后导入 locked-head 版本的 {filename}。GVHMR/ExMR 使用的标准 SMPL-X v1.1 与此不同，不能替代。'
          'MAMMA 数据与源码分别受到非商业使用和再分发限制。')
 if key in {'phmr_droidcalib', 'phmr_metric3d'}:
  return '可选：仅移动相机（DroidCalib + Metric3D）需要。运行 Setup_PromptHMR.cmd 并选择相机扩展，下载或导入经过校验的确切文件。固定相机无需这些文件。'
 if key.startswith('phmr_'):
  return '请阅读官方 PromptHMR 非商业许可，从官方来源下载对应的确切文件，再在本行导入。Google Drive 可能需要通过浏览器手动下载。'
 if key == 'smpl':
  return f'从官网取得中性人体模型，接受提供方条款，解压后点击“导入”并选择 {filename}。'
 return f'通过下方来源链接下载 {filename}，回到本行点击“导入”以登记下载文件。只有应用支持的模型版本才能通过校验。'


MANUAL_AVOID = {
 'humanart': 'ZIP 压缩包、PyTorch 检查点，以及其他大小或版本的 YOLOX 模型。',
 'exmr': 'FootMR 独立权重、config.json（请使用独立的 ExMR 配置行）或仓库 ZIP。',
 'exmr_config': '修改过的 JSON、其他版本、HTML 网页或 exmr.safetensors。请使用“支持的文件”链接取得配套版本。',
 'exmr_sapiens': 'Sapiens v1、0.3B 模型，或分割、深度、法线检查点。',
 'mano_right': 'SMPL+H 压缩包、MANO_LEFT.pkl 或外层 ZIP 文件。',
 'smplx': 'removed-head-bun 变体、Julia 模型、SMPL-X 2020、VPoser、男性/女性模型、SMPLX_NEUTRAL.pkl 或外层 ZIP。GVHMR 请使用上面列出的标准 v1.1 中性 NPZ。',
 'flow_vggt': '256_text、416、原始 VGGT 检查点或仓库 ZIP，均不能替代所需的 Omega 512 检查点。',
 'flowhmr': 'flowhmr_base 或其他检查点版本。',
 'flow_config': 'flowhmr_base 配置、config.json、HTML 网页或与检查点版本不同的配置。',
 'flow_metadata': 'config.yml、修改过的 JSON、HTML 网页或其他版本。',
 'flow_sam': 'SAM 图像分割、SAM 3D Objects、独立 DINOv3 权重或其他版本文件。请在各自匹配的行分别导入这三个支持的 SAM 文件。',
}
MANUAL_AVOID['flow_sam_config'] = MANUAL_AVOID['flow_mhr'] = MANUAL_AVOID['flow_sam']

DESCRIPTIONS = {
'gemx':'在上游测试中处理速度较快，整体动作质量相对较低。Windows 上使用一段固定机位视频，裁剪至 60 秒以内。GEM-X 自动选出一位主要人物，用 SOMA Native77 骨架以 30 fps 重建身体和手指动作。可编辑手脚接触并修正骨架与网格。可导出 FBX 或 BVH 骨架动作、包含网格和视频的 Blender 工程，也可重定向到导入的角色。原生流程无需 SMPL 模型。基础安装后运行 Setup_GEMX.cmd，再从模型管理器准备公开文件。GEM-X 复用 ExMR 的 Python，推理依赖独立安装。详见 docs/models/GEMX.zh-CN.md。',
'fusion':'FlowHMR + GVHMR 按区域融合。保留 FlowHMR 根运动、腿部、手臂和手指的局部旋转；默认由 GVHMR 以 100% 权重引导躯干、颈部和头部。在模型下方调整权重或区域后点击“重建 3D”。匹配的动捕结果会复用，缺少的部分在独立环境中计算。先对源动作应用修正，再融合；结果保存在独立模型文件夹，支持网格预览和 FBX/BVH 导出，不额外平滑或重定时。此可选方法曾在欧格林片段上验证，不能保证改善所有动作。',
'pear':'实验性实时预览，跟踪与姿态估计可能不稳定。支持视频或摄像头，以及一个或多个固定视角下的单人身体和手指骨骼。打开视频时选择同步机位；摄像头在插槽和缩略图中分配不同设备。只选择输入不会加载 PEAR，点击“开始实时跟踪”才尝试相机对齐并开始推理。“停止”释放模型与摄像头。<br>相机对齐需要 VGGT 和 GeoCalib。单机位估计人体/深度尺度，多机位三角化；失败时明确提示，并退回所选相机的单视角跟踪，不执行相机融合或已对齐脚锁定。“相机对齐”可重试。相机位置、重力、地面与尺度均为估计，无法保证消除脚滑。改变输入、重置骨长或移动实际相机后须重新对齐。摄像头按到达时间近似配对，并非硬件同步。<br>骨长首次标定后保持固定；“重置骨长”从显示姿态重新标定，并重新对齐相机。世界位置默认开启，关闭时固定骨盆位移而保留旋转；逐帧不生成人体网格。输入支持旋转和 One Euro 滤波，骨骼旋转及世界位置可分别平滑、共用强度设置。位置滤波与世界位置开关相互独立；平滑会产生随动作变化的延迟。跳转只处理指定帧，播放时延续滤波。对齐后的轻量脚锁定默认开启，通过平滑因果过渡稳定低速近地脚，保持骨长及踝/脚趾方向；可达范围或地面误差仍会造成滑动。<br>使用 YOLOv8s 人物检测，检测框会影响姿态。摄像头在启动和对齐时保持连接，加载期间视频可以播放。选择“无”使用视频。此模式不支持查找人物、录制、离线动作修正、重定向或动作导出。安装器复用公共环境准备支持源码，不升级公共依赖或要求 CUDA 编译器。请在模型管理器准备权重和授权 SMPL-X 2020/FLAME 几何数据。详见 docs/models/PEAR.md。',
'prompthmr':'从单视频联合重建多个人物。既有主观测试中相对位置和交互可能更好，但整体动作质量低于 ExMR；接触、深度和穿模仍可能出错。默认固定相机；可选移动相机使用带遮罩的 DroidCalib + Metric3D，需要独立相机扩展和两个额外模型，跟踪和尺度可能漂移。人数默认 2，0 自动检测（最多 8），无需查找人物。交互提示默认开启，关闭后沿用官方默认视频流程。使用 SMPL-X 身体动作，不跟踪手指，手指保持中性姿态。支持可选脚/手接触修正、重定向和 FBX/BVH/Blender 导出。需要 Setup_PromptHMR.cmd 独立环境和权重，限非商业科研用途。详见 docs/models/PROMPTHMR.md。',
'mamma':'使用同一次表演的至少两个同步固定机位视频，重建一个或多个人物。不设固定机位数上限，实际容量取决于内存与显存。自动检测人物，无需查找人物，也不会自动同步视频。采用 SAM 2.1 遮罩和 FP32 特征点；自动相机通过 VGGT-Omega 估计位置，并由 GeoCalib 在三维拟合前估计背景重力。手动标定绕过这两项估计。GeoCalib 复用 Flow 支持层与共用权重。若背景重力不可靠，需要手动标定或更清晰的视角，不会用人物站姿代替竖直参考。保留身体、手指、原始结果和接触修正结果。互补视角更合适，遮挡及错误遮罩会造成误差。速度慢于单视频方法。需要 Setup_MAMMA.cmd 独立环境及注册授权的模型文件；限许可范围内使用。直接读取 SAM 视频帧，避免中间 RGB PNG；保留最终人物遮罩。详见 docs/MAMMA.md。',
'gvhmr':'单视频人体动作重建，可分别启用 HTD 身体优化、FootMR 踝部优化和 HandFlow 手指跟踪。附加功能使用各自隔离的依赖层，耗时会增加。接触修正是独立步骤。不同动作和遮挡条件下质量会变化，可与其他模型比较。',
'flowhmr':'身体与手指动捕，支持静止相机或自动相机估计。Fast SAM 可加速特征提取；自适应批量、GPU 手部裁剪和每 4 帧手部采样均可独立控制。自动模式通常使用 1–16 个空间帧批量，低内存模式使用单帧并保留手部采样。短片加载开销占比高，不能直接用单阶段速度推断整段速度。查询大小、采样间隔、批量及显存重试会显示在控制台。相机旋转优化仅影响相机显示，不改变源动作。<br>可选 HaMeR 手指优化默认关闭，使用 ExMR 手部裁剪和高斯旋转平滑，不使用 ExMR 的学习式 HandMR。仅替换手指，无效裁剪保留 FlowHMR 手部；更慢且仍可能抖动。启用后自动开启 Fast SAM 和每 4 帧 SAM 手部采样，但 HaMeR 本身逐帧处理。模型管理器复用 HaMeR/MANO，推理使用现有 ExMR 环境。改动设置后请重新重建。详见 docs/models/FLOWHMR.md。',
'exmr':'既有测试中速度较快、动作质量较好，可作为首次尝试。身体与手指联合跟踪，无需单独手指附加模块。可选相机旋转优化仅验证并修正背景相机显示，不改变源动作。',
}

def guide_html(selected, tools, urls, benchmarks):
 from .i18n import t
 descriptions=''.join(f'<p><b>{escape(t(tool.label))}</b> &nbsp; <a href="{urls[key]}">原始项目</a><br>{DESCRIPTIONS[key]}</p>' for key,tool in tools.items())
 descriptions+='<p><b>查找人物</b>可在 ExMR、FlowHMR 和 GVHMR 中选用 SAM 3.1。输入 <code>person</code>，也可在预览帧上点击要保留的人物。先运行一次 Setup_SAM31.cmd，再从模型管理器准备公开 FP16 权重。详见 docs/models/SAM31.zh-CN.md。</p>'
 def label(s):
  for a,b in [('5s live video','5 秒实时视频'),('1 person','1 人'),('2 people','2 人'),('1 video','1 个视频'),('3 videos','3 个视频'),('median','中位数'),('ms/frame','毫秒/帧')]:s=s.replace(a,b)
  return s
 rows=''.join(('<tr bgcolor="#303f50">' if key==selected else '<tr>')+f'<td>{escape(t(tools[key].label))}</td>'+''.join('<td>'+label(v)+'</td>' for v in values)+'</tr>' for key,values in benchmarks.items())
 return '''<html><head><style>body {font-size:12px;} h3 {margin-top:15px;} a {color:#8ed2ff;} td,th {padding:7px;} th {text-align:left;background:#333;}</style></head><body><h3>选择动捕模型</h3><p>以下是既有测试视频的主观观察，不是通用排名或准确率基准。某个动作效果不好时，可尝试其他模型。</p>'''+descriptions+'''<p>“文件 > 导出”提供 FBX、BVH 和带视频/相机的便携 Blender 工程。MAMMA 还可导出包含勾选人体网格与全部相机的完整场景。GEM-X 支持 Native77 FBX、BVH 和 Blender 工程。导出的视频与网格目录应整体保存；导出不会额外执行动捕推理。</p><p><b>资源保护</b>默认开启，保留低内存停止和 PyTorch 显存分配上限。关闭只绕过这些限制，自适应批量、受支持的低内存流程和实际分配错误处理仍有效。偏好单独保存在本地，不写入工程。PEAR 隐藏离线资源控件，但继承此设置。详见 docs/PERFORMANCE.md。</p><h3>历史处理耗时与内存记录</h3><table width="98%" cellspacing="1"><tr><th>模型</th><th>输入</th><th>耗时</th><th>显存峰值 (GiB)</th><th>内存峰值 (GiB)</th></tr>'''+rows+'''</table><p>测试电脑：RTX 5090 32 GB · Ryzen 9 9950X · 96 GB RAM。这些是项目原有记录，不代表本轮测试结果。</p><p>GVHMR 开启 HTD、FootMR 和 HandFlow；FlowHMR 使用原始 SAM，当前 Fast SAM 可能更快。GVHMR、FlowHMR 和 ExMR 使用相同 7 秒片段，耗时不含跟踪、应用内修正、预览或导出。</p><p>MAMMA 使用不同的三机位同步视频，缩放至 1920×1080 范围，2 人、413 帧、30 fps；时间含预处理、修正与预览，内存统计覆盖遮罩、特征点、VGGT 和三维拟合，不能直接比较速度。该记录早于直接视频输入；后续四视角对照跳过中间 RGB PNG，使遮罩阶段快 17–21%，内存接近且遮罩完全一致，但这不是整条流程的加速比例。</p><p>PromptHMR 使用不同的固定相机视频：422 帧、30 fps、2 人，开启交互提示和动作修正。时间包括跟踪、原生推理、后续优化、修正、预览与骨骼准备，不含最终 FBX 写入；CUDA 保留显存峰值 7.83 GiB。</p><p>PEAR 统计预热后的固定骨长工作进程，不含模型启动、GUI 或采集。最大处理耗时 160.31 毫秒；可见应用在 5 秒内展示了 150 个同步画面/姿态，启动约 34 秒，此项未单独统计内存峰值。与离线整段重建耗时不可直接比较。</p><p>GEM-X 使用另一段 294 帧固定机位视频。耗时包括模型验证、视频准备、推理和 SOMA 网格计算，此项未记录内存峰值。</p><p>显存为 PyTorch 分配峰值，不是显卡总占用。ExMR/FlowHMR/GVHMR 内存为私有内存峰值，MAMMA/PromptHMR 为工作进程工作集峰值。较早的记录先于最新低内存改动，并非最低配置要求；结果随输入和电脑变化。离线模型支持脚/手接触修正以减少滑动，该功能与手指跟踪、踝部优化相互独立。</p></body></html>'''

def setup_html(model,size):
 license_url='https://github.com/cuevhv/mamma/blob/main/LICENSE' if model=='MAMMA' else 'https://github.com/yufu-wang/PromptHMR/blob/main/LICENSE'
 extra=('安装器为当前 GPU 编译 SAM 2 和 SDF 并验证 CUDA 内核。MAMMA 与 <a href="https://github.com/cuevhv/pytorch_sdf/blob/master/LICENSE">pytorch_sdf</a> 均有受限的非商业许可。主权重、对应点数据和三个人体 locked-head SMPL-X 文件需注册授权。请在 <a href="https://mamma.is.tue.mpg.de/">MAMMA 官网</a> 的 Data 页面注册、接受条款并下载，在模型管理器逐项导入；locked-head 人体来自独立 SMPL-X 网站。导入会检查 SHA-256。公开辅助权重可直接下载。' if model=='MAMMA' else '安装器为当前 GPU 编译 SAM2 并验证 CUDA 操作。可选相机提示选 Y，可编译 DroidCalib/LieTorch（请检查 AGPL/BSD 许可）。扩展复用本环境的 Python/Torch，构建需约 6 GiB 额外余量，另需约 1.55 GiB 相机权重；固定相机不需要这些扩展。复用标准 SMPL-X Neutral 和 SMPL Neutral，MAMMA locked-head 人体不能替代。Python 3.11 / Torch 2.7.1 CUDA 12.8 / timm 0.9.0 的包独立安装，已校验的相同下载包可复用，不依赖 MAMMA/SDF。支持固定或移动相机、最多 8 人自动跟踪、共同世界位置、交互提示、修正与导出，不生成手指动画。')
 doc='docs/MAMMA.md' if model=='MAMMA' else 'docs/models/PROMPTHMR.md'
 size=size.replace('approximately','约').replace('on this PC','（本机）')
 return f'''<h3>{model} 独立 Windows 运行环境</h3><p>已安装大小：<b>{escape(size)}</b>，不含权重与编译工具。安装期间建议保留 <b>18 GiB 可用空间</b>；其他模型环境保持独立。</p><ol><li>先用 install.cmd 准备基础应用。</li><li>安装 <a href="https://visualstudio.microsoft.com/downloads/">Visual Studio 2022 Build Tools</a>，包含“使用 C++ 的桌面开发”和 Windows SDK；安装 <a href="https://developer.nvidia.com/cuda-12-8-0-download-archive">CUDA Toolkit 12.8</a>。显卡驱动不包含编译器。</li><li>保存工作并关闭 RGB MoCap，运行应用目录中的 <b>Setup_{model}.cmd</b>。</li><li>阅读并接受允许使用范围内的上游许可；安装器下载固定版本的 Python、依赖和官方源码，编译并验证后启用。</li><li>重启应用，在模型管理器下载或导入所需文件。</li></ol><p>{extra}</p><p><a href="{license_url}">{model} 许可</a>限制为非商业科研用途。受限源码、编译模块和注册人体数据不随 RGB MoCap 再分发，而是在本地下载/构建。编译工具还会占用额外空间。其他组件遵循各自许可。</p><p>日志：<code>.setup/logs/{model.lower()}-*.log</code>。详细说明：<code>{doc}</code>。</p>'''
