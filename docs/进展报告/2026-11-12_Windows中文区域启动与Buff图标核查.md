# A94：Windows 中文区域启动兼容、单文件启动器与 Buff 图标核查

## 启动崩溃与复现输入

在中文 Windows（默认 GBK 区域编码）上直接执行 `python main.py`，游戏在构造界面时崩溃：

```
File "pixel_roamer/ui/help_overlay.py", line 12, in __init__
    data = json.loads(path.read_text())
UnicodeDecodeError: 'gbk' codec can't decode byte 0x90 in position 66
```

`data/controls.json` 等资源是 UTF-8，`Path.read_text()` 未指定编码时按区域编码解码。逐个修复后同一路径又依次暴露 `theme.py`、`references.py`、`map_selector.py` 的同类读取；全部改为显式 `encoding="utf-8"`。复现只需在 GBK 区域设置下启动，不涉及地图或键盘输入。

全量测试同时暴露同类问题：审计脚本用 `text=True` 读取 `git show` 的 UTF-8 源码输出，以及测试自身用默认编码写/读 UTF-8 内容。处理范围：

- 37 个审计脚本、41 处 `git show` 子进程读取补 `encoding='utf-8'`；
- `tests/test_config.py` 临时 `map.py` 改为 UTF-8 写入；
- `tests/test_audio.py` 在临时 wav 清理前 `pygame.mixer.music.unload()`，解决 Windows 文件占用（WinError 32）；
- `scripts/audit_cove_frost_layout.py` 的冲突探针读取源码补 UTF-8。该处 `UnicodeDecodeError` 是 `ValueError` 子类，曾被 `except ValueError` 吞掉并把“拒绝非空格覆盖”误报为 false。

修复前后原始日志：[修复前全量](evidence/2026-11-12_windows_gbk_unittest_before.txt)（357 项，24 FAIL + 2 ERROR）、[UI 修复后全量](evidence/2026-11-12_windows_gbk_unittest_after_ui_fixes.txt)（357 项，24 FAIL + 2 ERROR 降至 1 FAIL）。最后一个失败定位为上条审计脚本编码问题，单独复跑 `tests.test_cove_frost_pool` 3 项通过；最终全量重跑 357 项全部通过（603.285 秒），见[最终全量日志](evidence/2026-11-12_windows_gbk_unittest_final.txt)。

## 启动器

新增 `Pixel Roamer游戏启动器.bat`，与项目根目录同放即可双击或从任意目录调用（`%~dp0` 定位）。检测顺序：

1. `PIXEL_ROAMER_PYTHON` 显式指定的解释器；
2. PATH 上的 `python` / `py -3` / `python3` 中已能 `import pygame` 的一个，直接复用，不创建环境；
3. 已有 `.venv` 且有 pygame 时直接启动；缺 pygame 只补装依赖；
4. 以上都没有才创建项目内 `.venv` 并安装 `requirements.txt`。

仅创建项目内 `.venv`，不改动系统 Python 的 site-packages，因此不存在重复安装到全局环境。首次实测在 `.venv` 中自动安装 `pygame==2.6.1`；之后 dummy 视频/音频驱动启动 10–20 秒无异常（超时主动终止，非崩溃）。`.venv/`、`.tmp/` 已加入 `.gitignore`。

## Buff 图标与“翻身上岸”核查

两项反馈都做了真实主循环/生产会话复现：

- 同时挂 7 个 buff（ID 1–7）进入地图，HUD 记录 7 个图标矩形，按 5 列平铺为 2+5，见[离屏实拍](evidence/2026-11-12_hud_seven_buff_tiling.png)。平铺逻辑（`k % 5`、`k // 5`、1.2 倍步进）未改变；历史上只有 `7da7f9b` 抽取与 `68ebbca` 图标缓存优化。
- 水中触发真实上岸流程，逐帧记录玩家 buff 与 HUD 图标数，见[上岸逐帧轨迹](evidence/2026-11-12_shore_exit_buff_trace.txt)：`shore_exit`（58，翻身上岸）与 `soaked`（15，浸湿）同时存在，HUD 同时画出 2 个图标；上岸状态约 4 帧结束，buff 58 按设计在 0.3 秒后过期，而浸湿仍有约 1 秒。

因此“只看到浸湿”不是图标被改掉，也不是 buff 未挂上，而是 0.3 秒可见窗口短于浸湿。该 0.3 秒上限是既有设计（[双岸上岸修复](2026-11-12_双岸上岸方向与横移下沉修复.md)明确“没有修改 0.3 秒 Buff 时长”），经确认本次**保持 0.3 秒不变**，不改机制。

## 验证与未覆盖边界

- 代表性子集（air jump、cove lake、spawn connectivity、config、audio、cove frost pool）全部通过。
- 最终全量 357 项测试在修复后重跑全部通过（603.285 秒）。
- 启动器验证使用 SDL dummy 驱动与超时终止，不等于实体键盘、显示器、音频设备及完整关卡验收。
- 文字区域相关修复只覆盖本机中文 Windows 的 GBK 默认编码；未在英文/日文区域及无区域环境的机器上实测。
- Buff 图标平铺与上岸 buff 生命周期为离屏/生产会话数值证据，未做逐像素对比和实机长时间试玩。
