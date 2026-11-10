# 游戏数据

静态定义保存在 `catalogs/`，由 `resource_catalog.py` 在对应模块首次加载时读取和校验，不执行数据文件中的代码。路径相对于项目目录解析，启动工作目录不影响资源加载。

| 文件 | 内容 |
|---|---|
| `blocks.json` | 方块 ID、名称、物理/接触属性、功能和像素图案 |
| `buffs.json` | 状态 ID、分类、参数描述、叠层限制、冲突、图标、已实现处理器名 |
| `costumes.json` | 默认时装 ID、尺寸和各动画状态的像素帧 |
| `interface.json` | 设置页帧率选项、地图编辑字段、标签、默认值和步长 |

前三个目录采用统一头部：

```json
{
  "schema_version": 1,
  "kind": "blocks",
  "entries": [{"id": 0, "name": "air", "name2": "空气", "is_solid": false}]
}
```

同一目录的 ID 必须唯一且保持稳定。方块字段对应 `BlockType`，状态字段对应 `BuffType`；缺省字段使用数据类型默认值，未知字段、非有限数值、错误颜色/图案及无效关联会被拒绝。JSON 里的数组在方块/状态定义中转换为元组；时装保留像素数组。`special` / `tick` 是程序中已有处理器的标识，新增数据不会自动实现新机制。

图案沿用三段格式：`["vector", [宽, 高], 指令数组]`、`["bitmap", 尺寸, 像素行]` 或 texture 格式。矢量指令支持 `fill`、`rect` 和 `circle`。RGB/RGBA 分量为 0～255；时装像素 `0` 表示透明，所有帧的行列必须匹配声明尺寸。

格式化数据：`python3 scripts/format_catalogs.py`。迁移前所有方块定义、图案、状态图标和时装帧都有哈希基线；运行 `python3 -m unittest discover -s tests -p test_catalogs.py -v` 验证属性及像素一致性。未来有意修改外观时应保留修改前后截图并明确更新相应视觉基线。

地图的运行配置仍放在 `maps/<目录>/config.json`，沿用地图编辑器保存/加载和 `map_config.py` 数值校验。生成地图的算法保留在 Python 中，内容定义和执行逻辑分离。
