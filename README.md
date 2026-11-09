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

测试使用 SDL dummy 视频/音频驱动，可在无桌面环境中检查加载页、地图绘制、角色死亡/复活、音乐初始化和程序启动。
