# 像素漫游者 Pixel Roamer
This is a game I designed 10 years ago, and I finally possess the technical ability to bring it to fruition.

## 运行

需要 Python 3.10 或更新版本。

```bash
python -m pip install -r requirements.txt
python main.py
```

加载页完成后按 Enter/空格进入主页，按 Esc 可跳过加载。主页选择“开始游戏”后，在地图列表中选择地图并按 Enter 开始。

## 操作

- A/D 或方向键：左右移动
- 空格：跳跃；游泳时靠近岸边可快速上岸
- W/↑：攀爬或向上游泳；S/↓：停止攀爬
- F：切换飞行模式
- C：切换时装
- 游戏中 Esc：返回地图列表；Backspace：打开设置
- F1/F2：调整帧率上限

## 回归检查

```bash
python -m unittest discover -s tests -v
```

测试使用 SDL dummy 视频/音频驱动，覆盖角色交互、快速碰撞、循环渲染、地图重开、出生点、神殿路线、配置保存/加载，以及实际主循环的页面切换、暂停、死亡和胜负状态。

持续运行检查（每张地图模拟 10 分钟，并逐个检查现有方块）：

```bash
python scripts/audit_runtime.py --frames 36000 --block-frames 300 --output /tmp/pixel-roamer-audit.json
```

模拟输入和离屏绘制不能替代实体键盘、显示器、音频设备及完整关卡游玩验收。修复历程和实测数据见 [持续迭代记录](docs/进展报告/2026-11-11_持续迭代与玩法回归.md)。

地图编辑器保存时检查数值范围、类型、方块 ID 和 RGB 颜色；错误信息显示在编辑页底部。无效配置文件加载时发出警告，使用地图源码默认配置。摩擦系数必须在 0～1 之间，重力范围为 -1000～1000，移动/跳跃速度为 0～1000；其他范围见 `map_config.py`。

## 项目结构

- `main.py`：启动入口；`pixel_roamer/application.py`：窗口和页面协调。
- `pixel_roamer/world_session.py` / `world_view.py`：世界规则更新与绘制。
- `pixel_roamer/ui/`：HUD、设置、地图浏览/编辑及方块/buff 图鉴。
- `collision.py` / `status_effects.py`：碰撞几何和状态数值处理。
- `data/catalogs/`：方块、buff、时装及编辑字段 JSON；格式见 [数据说明](data/README.md)。
- `maps/`：现有地图生成算法和配置；`tests/`：自动回归与主循环场景。
