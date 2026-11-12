"""Optional Chinese UI translation with a File/Help-level language switch.

The upstream GUI is English-only and does not use Qt's tr()/QTranslator, so this
module translates known widget strings in place after the window is built. The
switch lives in a new "Language" menu, is stored under cache/gui-language.json,
and can also be forced with RGBMOCAP_LANG=zh. Strings that are not in the table
stay in English; a restart applies the choice to every panel.
"""

import json
import os
from collections import OrderedDict

from PySide6.QtCore import QObject, QEvent, QSignalBlocker
from PySide6.QtGui import QAction, QActionGroup
from PySide6.QtWidgets import (
    QAbstractButton,
    QComboBox,
    QGroupBox,
    QLabel,
    QLineEdit,
    QMenu,
    QMessageBox,
    QTabWidget,
    QTableWidget,
    QDoubleSpinBox,
    QSpinBox,
    QApplication,
    QWidget,
)

from .paths import ROOT

SETTINGS = ROOT / "cache" / "gui-language.json"
DEFAULT_LANGUAGE = "en"
_FORMATTED_ORIGINALS = OrderedDict()
_FORMATTED_TEMPLATES = OrderedDict()


class _LocalizedText(str):
    """Retain the source of a translated label used inside another message."""
    def __new__(cls, value, original):
        result = super().__new__(cls, value)
        result.original = original
        return result

ZH = {
    # menus / actions
    "File": "文件",
    "Help": "帮助",
    "Language": "语言",
    "Open Video...": "打开视频…",
    "Open Project...": "打开项目…",
    "Import Character...": "导入角色…",
    "Save Project As...": "项目另存为…",
    "Export FBX...": "导出 FBX…",
    "Export Character...": "导出角色…",
    "Open Project Folder": "打开项目文件夹",
    "Exit": "退出",
    "Check System": "检查系统",
    "Controls": "操作说明",
    "Rename...": "重命名…",
    "Remove Character": "移除角色",
    # panels / groups
    "People": "人物",
    "Movie Clip": "视频片段",
    "3D Viewport": "3D 视口",
    "Timeline": "时间轴",
    "Console": "控制台",
    "Overlays": "叠加",
    "Bone Overlay": "骨骼叠加",
    "Motion Workspace": "动作工作台",
    "AI Motion Model": "AI 动捕模型",
    "Model Guide": "模型指南",
    "? Model Guide": "? 模型指南",
    "Motion Correction": "动作修正",
    "Processing Resources": "处理资源",
    "ExMR Settings": "ExMR 设置",
    "FlowHMR Settings": "FlowHMR 设置",
    "GVHMR Models": "GVHMR 模型",
    "Ground Contact / Correction Floor": "地面接触 / 修正地面",
    "Correction Mode": "修正模式",
    "Lock Preset": "锁定预设",
    "Camera / Sampling": "相机 / 采样",
    # checkboxes / buttons
    "Enable Correction": "启用修正",
    "Foot": "脚",
    "Hand": "手",
    "Fast SAM": "快速 SAM",
    "HTD Refine": "HTD 细化",
    "Auto Floor Height": "自动地面高度",
    "Auto Scene Floor": "自动场景地面",
    "Find person": "查找人物",
    "Analyze 2D": "分析 2D",
    "Reconstruct 3D": "重建 3D",
    "Prepare Preview": "准备预览",
    "Cancel Job": "取消任务",
    "Apply Correction": "应用修正",
    "Model Manager": "模型管理",
    "Download All": "全部下载",
    "Auto Download": "自动下载",
    "Manual Download...": "手动下载…",
    "Open Download Page": "打开下载页",
    "Import...": "导入…",
    "Frame All": "全览",
    "Reset Trim": "恢复裁剪",
    "Reset Locks": "重置锁定",
    "Follow Actor": "跟随角色",
    "First Frame (Home)": "首帧（Home）",
    "Previous Frame (Left Arrow)": "上一帧（←）",
    "Next Frame (Right Arrow)": "下一帧（→）",
    "Last Frame (End)": "末帧（End）",
    "Camera": "相机",
    # labels / values
    "Static Camera": "静止相机",
    "Moving Camera / SimpleVO": "移动相机 / SimpleVO",
    "Moving / Unknown - Auto": "移动 / 未知 - 自动",
    "Every Frame": "每帧",
    "Every 2 Frames": "每 2 帧",
    "Every 5 Frames": "每 5 帧",
    "Every 10 Frames": "每 10 帧",
    "Every 30 Frames": "每 30 帧",
    "Automatic": "自动",
    "Low Memory": "低内存",
    "Flat Ground": "平地",
    "Multi Level": "多级地面",
    "Normal": "普通",
    "Weak": "弱",
    "Strong": "强",
    "Floor Height (World Y)": "地面高度（世界 Y）",
    "Floor Height (Shared World Y)": "地面高度（共享世界 Y）",
    "Pelvis Height Offset (from Auto)": "骨盆高度偏移（相对自动）",
    "Resource Mode": "资源模式",
    "Native SMPL-H body and hands": "原生 SMPL-H 身体与手部",
    "No clip loaded": "未加载片段",
    "Clip: no video": "片段：无视频",
    "0.00 / 0.00 s": "0.00 / 0.00 秒",
    # status / dialogs
    "Ready. Open a video or a project.": "就绪。请打开视频或项目。",
    "Open a video or drop it into the workspace": "打开视频或将其拖入工作区",
    "Cancel": "取消",
    "Close": "关闭",
    "Failed": "失败",
    "Failed to start": "启动失败",
    "Cannot start the processing engine. Check the app installation.": "无法启动处理引擎，请检查安装。",
    "Processing stopped. See the console for details.": "处理已停止，请查看控制台。",
    "Complete. Play the result or open the project folder.": "完成。可播放结果或打开项目文件夹。",
    "FBX export complete.": "FBX 导出完成。",
    "Model setup complete.": "模型设置完成。",
    "Character preview ready.": "角色预览已就绪。",
    "Downloads complete. Check Model Manager for any required imports.": "下载完成，请在模型管理器中检查需要导入的文件。",
    "2D analysis complete. View the estimated joints over the video.": "2D 分析完成，可在视频上查看估计关节。",
    "2D observations loaded. Prepare the body model to reconstruct full-body motion.": "2D 观测已加载，请准备身体模型以重建全身动作。",
    "Motion loaded. Play the animation or adjust the video clip range.": "动作已加载，可播放或调整视频片段范围。",
    "Prepare the required motion models first.": "请先准备所需的动捕模型。",
    "Check at least one person in the People list to extract motion.": "请至少勾选一位人物来提取动作。",
    "Check Person 1 in the People list to reconstruct it.": "请在人物列表中勾选 Person 1 以重建。",
    "Reconstruct a person before applying the shared scene floor.": "请先重建人物，再应用共享场景地面。",
    "No prepared source motion": "没有可用的源动作",
    "Apply contact changes before retargeting.": "重定向之前请先应用接触修正。",
    "Character motion is out of date. Apply Correction or retarget it again.": "角色动作已过期，请应用修正或重新重定向。",
    "Too many imported characters (maximum 8).": "导入角色过多（最多 8 个）。",
    "Invalid person color": "无效的人物颜色",
    "Invalid character project path": "无效的角色项目路径",
    "This model is not part of the selected motion tool.": "该模型不属于当前动捕工具。",
    "Only checked contact types are corrected.": "只修正勾选的接触类型。",
    "Automatic lowering varies by frame.": "自动下沉量逐帧变化。",
    "Restore the full clip for playback and reconstruction": "恢复完整片段用于播放和重建",
    "Enter a frame number to jump to it. The first frame is 1.": "输入帧号跳转（首帧为 1）。",
    "Choose a viewing direction. This changes the camera, not the motion.": "选择视角方向，仅改变相机，不改变动作。",
    "Choose the AI model used to create motion. Open Model Guide for a comparison.": "选择用于生成动作的 AI 模型，可在模型指南中对比。",
    "Estimate floor height from the motion. Turn off to enter the height yourself.": "从动作估计地面高度；关闭后可手动输入。",
    "Move the viewing camera with the person during playback. Does not change the animation.": "播放时相机跟随人物，不改变动画。",
    "Show the skeleton used for FBX export over the motion mesh. Display only.": "在动作网格上显示 FBX 骨架（仅显示）。",
    "Show tracked people and detected body points over the video. Display only.": "在视频上显示人物与检测到的身体点（仅显示）。",
    "Fit the full clip in the timeline.": "在时间轴中显示完整片段。",
    "Fit all visible people in the 3D view.": "在 3D 视口中框选所有可见人物。",
    "Show or hide processing details and error messages.": "显示或隐藏处理详情与错误信息。",
    "Change preview playback speed. Exported timing stays unchanged.": "改变预览播放速度，导出时序不变。",
    "Current playback time / clip duration, in seconds.": "当前播放时间 / 片段总长（秒）。",
    "Show how to seek, trim and edit contact timings.": "查看跳转、裁剪与接触编辑说明。",
    "Show how to choose, rename and display people.": "查看人物选择、重命名与显示说明。",
    "Open the model provider website in your browser.": "在浏览器中打开模型提供方网站。",
    "Download or import the files needed by the selected AI model.": "下载或导入所选 AI 模型需要的文件。",
    "Stop the current processing queue. Completed results are kept.": "停止当前处理队列，已完成结果会保留。",
    "Stop the current download or import queue. Completed files are kept.": "停止当前下载/导入队列，已完成文件会保留。",
    "Close these download instructions.": "关闭下载说明。",
    "Select the downloaded model file to check and import it. These instructions stay open.": "选择已下载的模型文件进行校验并导入；说明窗口保持打开。",
    "Download this file automatically. If it fails, use Manual Download or Import an existing copy.": "自动下载该文件；失败时可用手动下载或导入已有副本。",
    "Choose a model file you already downloaded. The app checks it before replacing any existing file.": "选择已下载的模型文件，应用会先校验再替换。",
    "Close Model Manager. Any running download or import continues in the main workspace.": "关闭模型管理器；正在进行的下载/导入会继续。",
    "Imported session characters were kept separately: the project would exceed 8 characters.": "导入的角色已单独保留：项目最多 8 个角色。",
    "Saving contact-lock timing...": "正在保存接触锁定…",
    "Stopping...": "正在停止…",
    "Cancelling project save...": "正在取消项目保存…",
    "Cancelled. Completed stages will be reused next time.": "已取消，已完成的阶段下次会复用。",
    "Contact-lock timing saved. Apply Correction to update the motion and FBX.": "接触锁定已保存，应用修正以更新动作和 FBX。",
    "Contact-lock timing was not saved. Edit or reset the tracks to retry saving.": "接触锁定未保存，请编辑或重置轨道后重试。",
    "Correction settings changed. Preview shows the last applied motion.\nApply Correction to update the pelvis, contacts and FBX.": "修正设置已更改，预览仍显示上次应用的动作。\n应用修正以更新骨盆、接触和 FBX。",
    "Contact-lock timing changed. Preview shows the last applied correction.\nApply Correction to update the motion and FBX.": "接触锁定已更改，预览仍显示上次应用的修正。\n应用修正以更新动作和 FBX。",
    "Multi Level uses the inferred height of each foot contact. This floor value is unused; switch to Flat Ground to edit it.": "多级地面使用每个脚接触的推断高度，此地面值不使用；切换到平地模式可编辑。",
    "Higher values raise the correction floor. Use the Correction Floor checkbox to preview it; Apply Correction updates the motion.": "数值越大修正地面越高；勾选视口下方的修正地面可预览；应用修正后更新动作。",
    "Enable Correction Floor below the viewport to preview this height.\nHigher values raise the correction floor.\nApply Correction updates the motion.": "勾选视口下方的修正地面可预览该高度。\n数值越大修正地面越高。\n应用修正后更新动作。",
    "Correction Floor below the viewport shows the shared plane for all people.\nHigher values raise the correction floor.\nApply Correction updates available actors.": "视口下方的修正地面显示所有人的共享平面。\n数值越大修正地面越高。\n应用修正后更新可用角色。",
    "Workspace Controls": "工作区操作",
    "Language": "语言",
    "Language changed. Restart RGB MoCap to translate every panel.": "语言已切换。重启 RGB MoCap 可翻译所有面板。",
}

EXTRA = {
    # viewport / timeline / viewer painted text
    "No motion loaded\n\nReconstruct a motion or open a project\nto compare the initial and refined animation.": "未加载动作\n\n请重建动作或打开项目\n以对比初始与细化后的动画。",
    "Open a video to begin\nMP4 · MOV · AVI": "打开视频开始\nMP4 · MOV · AVI",
    "User Perspective": "用户透视",
    "LMB: Orbit  |  MMB / RMB: Pan  |  Wheel: Zoom  |  Double-click: Frame": "左键：旋转  |  中/右键：平移  |  滚轮：缩放  |  双击：全览",
    "Frame": "帧",
    "Video": "视频",
    "Motion": "动作",
    "Source clip": "源片段",
    "No motion data": "无动作数据",
    "Body animation": "身体动画",
    "L foot": "左脚",
    "R foot": "右脚",
    "L hand": "左手",
    "R hand": "右手",
    "Disabled": "未启用",
    "Apply Correction to generate locks": "应用修正以生成锁定",
    "Clip": "片段",
    # correction descriptions
    "Gentler correction, with some sliding allowed to preserve more of the original movement.": "较轻修正，允许少量滑动以保留更多原始动作。",
    "Balanced contact correction. Holds stable contacts while keeping transitions smooth.": "平衡模式：稳定保持接触，同时让过渡更平滑。",
    "Firmer holds, including less certain contacts. May resist intentional slides; review the result.": "更强保持，包含不太确定的接触；可能抵抗有意的滑动，请检查结果。",
    "Correction settings changed. Preview shows the last applied motion.\nApply Correction to update the pelvis, contacts and FBX.": "修正设置已更改，预览仍显示上次应用的动作。\n应用修正以更新骨盆、接触和 FBX。",
    "Contact-lock timing changed. Preview shows the last applied correction.\nApply Correction to update the motion and FBX.": "接触锁定已更改，预览仍显示上次应用的修正。\n应用修正以更新动作和 FBX。",
    # tooltips
    "Close the model guide.": "关闭模型指南。",
    "Compare motion quality, finger support, speed and memory use.": "对比动作质量、手指支持、速度与内存占用。",
    "Check to reconstruct and show; select to edit. Use ? for help.": "勾选以重建并显示；选中以编辑。按 ? 查看帮助。",
    "Import a Mixamo FBX, VRM or PMX humanoid. Right-click its People row to retarget a source person.": "导入 Mixamo FBX、VRM 或 PMX 人形角色；右键人物行可重定向源动作。",
    "ExMR: body and finger tracking. Generally fast, with good motion quality in our subjective tests.": "ExMR：身体与手指跟踪，速度较快，主观测试中动作质量良好。",
    "FlowHMR: body and finger tracking. Slow, with the best overall motion quality in our subjective tests.": "FlowHMR：身体与手指跟踪，速度最慢，主观测试中整体动作质量最好。",
    "GVHMR: body tracking with optional hand and foot refinement. Sometimes better for unusual poses such as backflips in our subjective tests.": "GVHMR：身体跟踪，可选手/脚细化；主观测试中对后空翻等异常姿势有时更好。",
    "Checked: save the character mesh and skeleton animation. Unchecked: save only the skeleton and animation.": "勾选：保存角色网格与骨骼动画；取消：只保存骨骼与动画。",
    "Find body points in the video for GVHMR refinement. Reconstruct 3D normally includes this step when needed.": "在视频中检测身体点用于 GVHMR 细化；需要时“重建 3D”会包含此步骤。",
    "Improve body motion consistency over time. Uses a saved result when available; otherwise run Reconstruct 3D.": "提升身体动作的时序一致性；有缓存结果时复用，否则请运行“重建 3D”。",
    "Restore automatic foot and hand contact timings for this person. Click Apply Correction to update the motion.": "恢复该人物的自动脚/手接触时序；之后点“应用修正”更新动作。",
    "Find people in the video so you can choose who to reconstruct. Useful for multiple people or a specific person.": "在视频中查找人物，便于选择要重建的人；多人或指定人物时可用。",
    "Show download links and instructions. Download in your browser, then use Import in the instructions or this row.": "显示下载链接与说明；在浏览器下载后，用说明窗口或本行的“导入”。",
    "Choose a visible section of this person's motion. Separate takes avoid filling gaps while the person is out of view.": "选择该人物动作中可见的片段；分成多个 take 可避免出画时硬填。",
    "Show active foot and hand contacts as colored discs. Colors match the timeline. Display only; does not enable correction.": "以彩色圆盘显示当前脚/手接触（颜色对应时间轴）；仅显示，不启用修正。",
    "Save the displayed skeleton animation as FBX. For multiple people, each checked person gets a separate named file and rig.": "把当前显示的骨骼动画保存为 FBX；多人时每个勾选人物各出一个文件。",
    "Floor height in meters along the vertical Y axis. Turn off Auto Floor Height to edit. The gray reference grid stays at zero.": "沿竖直 Y 轴的地面高度（米）；关闭“自动地面高度”后可编辑。灰色参考网格固定在 0。",
    "Reduce foot sliding during ground contact. Click Apply Correction to update. Turning this off keeps your saved contact timings.": "减少脚在地面接触时的滑动；点“应用修正”更新。关闭后保留已保存的接触时序。",
    "Automatic balances speed and available memory. Low Memory processes smaller image batches while keeping the same motion quality.": "自动模式在速度与可用内存间平衡；低内存模式使用更小批次，动作质量不变。",
    "Prepare the 3D mesh and skeleton from the selected motion result. Available after reconstruction; does not run AI inference again.": "从所选动作结果准备 3D 网格与骨骼；重建后可用，不会重跑 AI 推理。",
    "Create 3D motion for checked people in the trimmed video range using the selected model and settings. Reuses valid completed steps.": "用所选模型与设置，为裁剪范围内勾选的人物生成 3D 动作；有效步骤会复用。",
    "Update contact correction using these settings and timeline timings. Rebuilds the preview and export without running the AI model again.": "按当前设置与时间轴时序更新接触修正；重建预览与导出，不重跑 AI 模型。",
    "Reduce small changes between frames for smoother motion. Turn off to keep the unsmoothed result. Applies next time you run Reconstruct 3D.": "减少帧间细小变化以让动作更平滑；关闭则保留未平滑结果。下次重建 3D 生效。",
    "Choose Static Camera if the camera stays still without zooming. Choose Moving Camera if it moves. Applies next time you run Reconstruct 3D.": "相机不动且不缩放时选“静止相机”；会移动则选“移动相机”。下次重建 3D 生效。",
    "Use contact correction to reduce sliding. Off shows the uncorrected result. Click Apply Correction after changing settings or contact timings.": "用接触修正减少滑动；关闭则显示未修正结果。改设置或接触时序后请点“应用修正”。",
    "Improve foot angles using foot keypoints, after HTD if enabled. This does not lock feet to the floor. Run Reconstruct 3D if no saved result is available.": "用脚部关键点改善脚部角度（若启用 HTD 则在之后）；不会把脚锁到地面。无缓存时请运行重建。",
    "Step left estimates time for the current step; Total left estimates the remaining queue. Estimates appear once enough timing data is available and may change.": "“剩余步”估算当前步骤耗时；“剩余总时”估算整个队列。数据足够后才显示，可能变化。",
    "Speed up image processing with the same model files. Small differences in motion and automatic contacts are possible. Applies next time you run Reconstruct 3D.": "用相同模型文件加速图像处理；动作与自动接触可能有小差异。下次重建 3D 生效。",
    "Download missing public model files. Files requiring registration must be downloaded manually and imported. Completed downloads are kept if you cancel.": "下载缺失的公开模型文件；需要注册的文件须手动下载后导入。取消时已完成的下载会保留。",
    "Add finger tracking to GVHMR without changing body or wrist motion. Requires HandFlow and MANO files in Model Manager. Run Reconstruct 3D if no saved result is available.": "为 GVHMR 增加手指跟踪，不改变身体与手腕动作；需要 HandFlow 与 MANO 模型。无缓存时请运行重建。",
    "Flat Ground uses one floor height. Multi Level keeps each contact at its inferred height for stairs or slopes. It does not reconstruct the surfaces. Apply Correction to update.": "平地模式使用单一地面高度；多级地面让每个接触保持推断高度，适合楼梯/斜坡，但不重建表面。点“应用修正”更新。",
    "Reduce hand sliding when resting on a floor or table by adjusting the arm. Review contact timings in the timeline, then click Apply Correction. Does not reposition the whole body for hanging poses.": "靠调整手臂减少手在地面/桌面支撑时的滑动；先在时间轴检查接触时序，再点“应用修正”。不会为悬挂姿势移动整个身体。",
    "Choose Static Camera only if the camera stays still without zooming. Otherwise start with Moving / Unknown - Auto. Frame intervals control camera analysis only; shorter intervals use more memory. Applies on Reconstruct 3D.": "仅当相机静止且不缩放时选“静止相机”；否则先用“移动 / 未知 - 自动”。帧间隔只影响相机分析，越短越占内存。重建 3D 时生效。",
}

ZH["Choose contact strength. Normal is the starting point. Apply Correction to update; manually edited timings stay unchanged."] = "选择接触强度。普通是起点；点“应用修正”更新，手动编辑的时序不会改变。"
for _key, _value in {
    "Floor Grid": "地面网格",
    "Correction Floor": "修正地面",
    "Motion Path": "运动轨迹",
    "Lock": "锁定",
    "Name": "名称",
}.items():
    ZH.setdefault(_key, _value)
for _key, _value in {
    "Smooth Motion": "平滑动作",
    "Perspective": "透视",
    "Front": "前视角",
    "Back": "后视角",
    "Right": "右视角",
    "Left": "左视角",
    "Top": "顶视角",
    "Bottom": "底视角",
}.items():
    ZH.setdefault(_key, _value)
for _key, _value in {
    "Motion Workspace   |": "动作工作台   |",
    "Play (Space)": "播放（Space）",
    "Pause (Space)": "暂停（Space）",
    "ExMR Models": "ExMR 模型",
    "FlowHMR Models": "FlowHMR 模型",
    "Show the reference grid at height zero. Does not change ground contact.": "在高度 0 显示参考网格；不改变地面接触。",
    "Show the correction floor height as an orange plane. Display only.": "以橙色平面显示修正地面高度；仅显示。",
    "Show the path followed by the person.": "显示人物的运动路径。",
    "Show each person's name above their mesh. Rename people by right-clicking the People list. Display only.": "在网格上方显示人物名称；右键人物列表可重命名；仅显示。",
    "0 keeps automatic hip height. Positive values undo some automatic lowering; negative values lower the hips further during contact. Raising can weaken foot locks. Apply Correction to update.": "0 表示保持自动髋高；正值抵消部分自动下沉，负值在接触时进一步压低髋部。提高可能削弱脚部锁定。点“应用修正”更新。",
    "Reconstruct 3D automatically tracks one person. For several people or a specific person, use Find person first.\n\nCheck a person to reconstruct and show them. Select a row to preview their motion and edit their contact timings. Selecting a row does not change its checkbox.\n\nRight-click a row to rename it. Click its color square to change the display color. Names are used for FBX files and rigs; colors affect the preview only.\n\nIf a person has separate visible sections, use the take list to switch between them.\n\nAutomatic single-person tracking may switch people when they cross or overlap. Use Find person when keeping a specific identity matters.": "“重建 3D”会自动跟踪一个人；多人或指定人物时请先用“查找人物”。\n\n勾选人物以重建并显示；选中某行可预览其动作并编辑接触时序，选中行不会改变勾选状态。\n\n右键某行可重命名；点击颜色方块可改显示颜色。名称会用于 FBX 文件名与骨架，颜色只影响预览。\n\n若一个人有多个可见片段，用 take 列表切换。\n\n自动单人跟踪在人物交叉或重叠时可能切换目标；需要保持特定身份时请用“查找人物”。",
}.items():
    ZH.setdefault(_key, _value)
for _key, _value in {
    "Timeline Help": "时间轴帮助",
    "Click or drag the frame ruler, or drag the blue frame-number box to seek.\nThe thin playhead line does not capture clicks.\nWheel: zoom | Shift + wheel or MMB: pan\n\nVideo clip edges: trim the playback and reconstruction range.\nFrame All: fit the full timeline | Reset Trim: restore the full clip.\n\nL/R foot and L/R hand: drag empty space to add a lock.\nDrag a lock to move it; drag its edges to resize it.\nDouble-click empty space to add a short lock.\nDelete: remove selected lock | Ctrl+Z / Ctrl+Y: undo / redo\nRight-click: editing and reset-to-automatic commands.\n\nApply Correction updates the preview motion and FBX after timing edits.": "点击或拖动帧标尺，或拖动蓝色帧号框来跳转。\n细播放头线不响应点击。\n滚轮：缩放 | Shift+滚轮 或 中键：平移\n\n视频片段边缘：裁剪播放与重建范围。\n全览：显示完整时间轴 | 恢复裁剪：还原完整片段。\n\n左脚/右脚、左手/右手：在空白处拖动可添加锁定。\n拖动锁定可移动；拖动边缘可调整长度。\n双击空白处添加短锁。\nDelete：删除选中锁定 | Ctrl+Z / Ctrl+Y：撤销/重做\n右键：编辑与恢复自动命令。\n\n修改时序后，点“应用修正”更新预览动作与 FBX。",
}.items():
    ZH.setdefault(_key, _value)
for _key, _value in {
    "No confident automatic hand contacts. Add hand lock intervals in the timeline if needed.": "没有可靠的自动手部接触；如需锁定，请在时间轴添加手部锁定区间。",
    "A non-contact foot penetrates the correction floor; check floor height and contact timing.": "非接触脚穿过了修正地面；请检查地面高度与接触时序。",
}.items():
    ZH.setdefault(_key, _value)
for _tool in ("ExMR", "FlowHMR", "GVHMR"):
    _english = f"Only checked contact types are corrected. Uses the selected {_tool} result."
    ZH.setdefault(_english, f"只修正勾选的接触类型；使用所选 {_tool} 结果。")
for _key, _value in {
    "Some short contact gaps still require rapid foot motion; inspect contact timing.": "部分接触间隙过短，仍需要快速抬脚；请检查接触时序。",
    "Some contact transitions exceed anatomical reach; inspect floor height and timing.": "部分接触过渡超出人体可达范围；请检查地面高度与时序。",
    "Multi Level estimates contacts from motion. Terrain and object collisions are not solved.": "多级地面只根据动作估计接触；不求解地形与物体碰撞。",
}.items():
    ZH.setdefault(_key, _value)
for _key, _value in {
    "Output Skeleton": "输出骨架",
    "Native capture skeleton": "原生捕获骨架（SMPL-X / SMPL-H）",
    "Choose the skeleton used by Export FBX. Presets write a bone-only FBX for that engine; native keeps the capture skeleton.": "选择“导出 FBX”使用的骨架；预置骨架会导出该引擎可用的纯骨骼 FBX，原生则保留捕获骨架。",
    "Export Skeleton FBX": "导出所选骨架",
    "Export Selected Skeleton": "导出所选骨架",
}.items():
    ZH.setdefault(_key, _value)
for _key, _value in {
    "Detect 2D body points for preview. Does not run 3D reconstruction.": "检测 2D 人体关键点用于预览；不会运行 3D 重建。",
}.items():
    ZH.setdefault(_key, _value)
for _key, _value in {
    "Actor Detector": "人物检测器",
    "YOLOv8x is the default COCO person detector. YOLOX-X (HumanArt) detects stylised and armored characters better; it runs on the GPU when available and falls back to CPU.": "YOLOv8x 是默认的 COCO 人物检测器；YOLOX-X（HumanArt）对风格化或盔甲角色检测更好，优先用 GPU，不可用时回退 CPU。",
}.items():
    ZH.setdefault(_key, _value)
ZH.update(EXTRA)
from .i18n_zh import ZH as _ADDITIONAL_ZH
ZH.update(_ADDITIONAL_ZH)
_REVERSE = {value: key for key, value in ZH.items()}
# Short generic words are translated only by exact lookup; replacing them inside
# longer English sentences would corrupt tooltips (for example "Right-click").
_BLOCK_EXCLUDE = {
    "Frame", "Video", "Motion", "Lock", "Name", "Disabled", "Foot", "Hand",
    "Camera", "Console", "People", "Timeline", "Cancel", "Close", "Failed",
    "Automatic", "Normal", "Weak", "Strong", "Perspective", "Front", "Back",
    "Right", "Left", "Top", "Bottom", "Language", "File", "Help", "Exit",
    "Controls", "Overlays", "FootMR", "HandFlow", "Smooth", "Open", "Save",
}
_FORWARD_SORTED = sorted(
    ((key, value) for key, value in ZH.items() if len(key) >= 8 and key not in _BLOCK_EXCLUDE),
    key=lambda item: len(item[0]), reverse=True)
_BACKWARD_SORTED = sorted(
    ((value, key) for key, value in ZH.items() if len(key) >= 8 and key not in _BLOCK_EXCLUDE),
    key=lambda item: len(item[0]), reverse=True)


def _translate_text_block(value: str, to_zh: bool) -> str:
    """Replace whole phrases inside plain text or the tooltip HTML wrapper."""
    for source, target in (_FORWARD_SORTED if to_zh else _BACKWARD_SORTED):
        if source and source in value:
            value = value.replace(source, target)
    return value


def to_english(value: str) -> str:
    if isinstance(value, _LocalizedText):
        return value.original
    return _FORMATTED_ORIGINALS.get(value, _REVERSE.get(value, _translate_text_block(value, False)))


def _english_value(kind, value: str) -> str:
    """Snapshot English originals even if a widget was set through t() already."""
    if kind == "tooltip":
        from .tooltips import plain_tooltip
        value = plain_tooltip(value)
    return to_english(value)



def _load() -> str:
    env = os.environ.get("RGBMOCAP_LANG")
    if env in {"en", "zh"}:
        return env
    try:
        settings = json.loads(SETTINGS.read_text(encoding="utf-8"))
        lang = settings.get("language") if isinstance(settings, dict) else None
        return lang if isinstance(lang, str) and lang in {"en", "zh"} else DEFAULT_LANGUAGE
    except (OSError, ValueError):
        return DEFAULT_LANGUAGE


def _save(lang: str) -> None:
    SETTINGS.parent.mkdir(parents=True, exist_ok=True)
    SETTINGS.write_text(json.dumps({"language": lang}, indent=1), encoding="utf-8")


def language() -> str:
    global _CURRENT
    if _CURRENT is not None:
        return _CURRENT
    _CURRENT = _load()
    return _CURRENT


_CURRENT = None


def translate_block(text: str) -> str:
    """Translate known phrases inside a longer, dynamically composed message."""
    return _translate_text_block(text, language() == "zh")


def t(text: str, **values) -> str:
    """Translate one UI string at call time; unknown strings pass through."""
    global _CURRENT
    if _CURRENT is None:
        _CURRENT = language()
    if isinstance(text, _LocalizedText):
        text = text.original
    if values:
        original = text.format(**{key: value.original if isinstance(value, _LocalizedText) else value for key, value in values.items()})
        rendered = t(text).format(**{key: t(value) if isinstance(value, _LocalizedText) else value for key, value in values.items()})
        if text in ZH:
            _FORMATTED_TEMPLATES[original] = (text, values)
            _FORMATTED_TEMPLATES.move_to_end(original)
            while len(_FORMATTED_TEMPLATES) > 1024:
                _FORMATTED_TEMPLATES.popitem(last=False)
        if rendered != original:
            _FORMATTED_ORIGINALS[rendered] = original
            _FORMATTED_ORIGINALS.move_to_end(rendered)
            while len(_FORMATTED_ORIGINALS) > 1024:
                _FORMATTED_ORIGINALS.popitem(last=False)
        return _LocalizedText(rendered, original) if text in ZH or rendered != original else rendered
    if text not in ZH and text in _FORMATTED_TEMPLATES:
        template, fields = _FORMATTED_TEMPLATES[text]
        return t(template, **fields)
    if _CURRENT == "zh" and text not in ZH:
        for suffix in ("...", "…"):
            if text.endswith(suffix) and text[:-len(suffix)] in ZH:
                return ZH[text[:-len(suffix)]] + "…"
        if " · " in text:
            return " · ".join(t(part) for part in text.split(" · "))
    if _CURRENT == "zh" and text not in ZH and "\n" in text and "<" not in text:
        return "\n".join(t(line) for line in text.split("\n"))
    rendered = (ZH.get(text, _translate_text_block(text, True) if "<" in text and ">" in text else text)
                if _CURRENT == "zh" else text)
    return _LocalizedText(rendered, text) if text in ZH or rendered != text else rendered


def _entries(root):
    entries = []

    def add(obj, kind, values):
        previous = getattr(obj, "_rgb_i18n_values", {}).get(kind)
        originals = previous[0] if previous and previous[1] == values else [_english_value(kind, value) for value in values]
        entries.append((obj, kind, originals))

    add(root, "window", [root.windowTitle()])
    for w in [root, *root.findChildren(QWidget)]:
        if w.isWindow():
            add(w, "window", [w.windowTitle()])
        if isinstance(w, QTableWidget):
            add(w, "headers", [w.horizontalHeaderItem(i).text() if w.horizontalHeaderItem(i) else "" for i in range(w.columnCount())])
        if isinstance(w, (QDoubleSpinBox, QSpinBox)):
            add(w, "prefix", [w.prefix()])
            add(w, "special", [w.specialValueText()])
        if isinstance(w, (QLabel, QAbstractButton)) and not isinstance(w, QGroupBox):
            add(w, "text", [w.text()])
        elif isinstance(w, QGroupBox):
            add(w, "title", [w.title()])
        elif isinstance(w, QComboBox):
            if not w.property('rgb_i18n_dynamic_items'):
                add(w, "combo", [w.itemText(i) for i in range(w.count())])
            if w.placeholderText():
                add(w, "combo_placeholder", [w.placeholderText()])
        elif isinstance(w, QTabWidget):
            add(w, "tabs", [w.tabText(i) for i in range(w.count())])
        elif isinstance(w, QLineEdit):
            add(w, "placeholder", [w.placeholderText()])
        if w.accessibleName():
            add(w, "accessible_name", [w.accessibleName()])
        if hasattr(w, "toolTip") and w.toolTip():
            add(w, "tooltip", [w.toolTip()])
    for menu in root.findChildren(QMenu):
        add(menu, "menutitle", [menu.title()])
        for act in menu.actions():
            if act.text():
                add(act, "action", [act.text()])
            if act.toolTip():
                add(act, "tooltip", [act.toolTip()])
    return entries


def _apply_value(obj, kind, value):
    if kind == "prefix":
        obj.setPrefix(value)
    elif kind == "special":
        obj.setSpecialValueText(value)
    elif kind == "headers":
        obj.setHorizontalHeaderLabels(value)
    elif kind == "window":
        obj.setWindowTitle(value)
    elif kind == "text":
        obj.setText(value)
    elif kind == "title":
        obj.setTitle(value)
    elif kind == "placeholder":
        obj.setPlaceholderText(value)
    elif kind == "accessible_name":
        obj.setAccessibleName(value)
    elif kind == "tooltip":
        from .tooltips import tooltip_text
        obj.setToolTip(tooltip_text(value))
    elif kind == "action":
        obj.setText(value)
    elif kind == "menutitle":
        obj.setTitle(value)
    elif kind == "combo":
        for i, text in enumerate(value):
            obj.setItemText(i, text)
    elif kind == "combo_placeholder":
        obj.setPlaceholderText(value)
    elif kind == "tabs":
        for i, text in enumerate(value):
            obj.setTabText(i, text)


def apply_language(root, lang: str, *, refresh=True) -> None:
    """Translate presentation without emitting model/selection change signals.

    Read current widget values each time: projects and dialog rows may have
    changed since the preceding switch. Never replay a stale startup snapshot.
    """
    global _CURRENT
    _CURRENT = lang
    from .theme import configure_font
    configure_font(QApplication.instance(), lang)
    for obj, kind, originals in _entries(root):
        with QSignalBlocker(obj):
            if kind in {"combo", "tabs", "headers"}:
                values = [t(v) if lang == "zh" else v for v in originals]
                _apply_value(obj, kind, values)
            else:
                value = originals[0]
                if lang == "zh":
                    value = t(value)
                _apply_value(obj, kind, value)
                if kind == "tooltip":
                    value = obj.toolTip()
                values = [value]
            if not hasattr(obj, "_rgb_i18n_values"):
                obj._rgb_i18n_values = {}
            obj._rgb_i18n_values[kind] = (list(originals), list(values))
    if refresh:
        hook = getattr(root, "retranslate_dynamic", None)
        if callable(hook):
            hook()
        for name in ("motion_view", "video_view", "timeline", "slider"):
            widget = getattr(root, name, None)
            if widget is not None:
                widget.update()


class _DialogTranslation(QObject):
    """Cover dialogs created after startup, including Qt standard buttons."""
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Show and isinstance(obj, QWidget) and obj.isWindow():
            apply_language(obj, language(), refresh=False)
        return False


def _choose(window, lang: str) -> None:
    _save(lang)
    apply_language(window, lang)
    title = "Language" if lang == "en" else "语言"
    msg = ("Language changed. Restart RGB MoCap to translate every panel." if lang == "en"
           else "语言已切换。重启 RGB MoCap 可翻译所有面板。")
    QMessageBox.information(window, title, msg)


def install(window) -> None:
    menu = window.menuBar().addMenu("Language")
    group = QActionGroup(menu)
    group.setExclusive(True)
    for code, name in (("en", "English"), ("zh", "中文")):
        action = QAction(name, menu)
        action.setCheckable(True)
        action.setChecked(language() == code)
        action.triggered.connect(lambda _checked=False, c=code: _choose(window, c))
        group.addAction(action)
        menu.addAction(action)
    app = QApplication.instance()
    if not hasattr(app, "_rgb_dialog_translation"):
        app._rgb_dialog_translation = _DialogTranslation(app)
        app.installEventFilter(app._rgb_dialog_translation)
    apply_language(window, language())
