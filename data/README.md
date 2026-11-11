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

`interface.json` 中的 player 字段默认值是游戏角色预设的统一来源，由 `resource_catalog.player_defaults()` 校验加载；`player_factory.create_world_player()` 用于实际启动和地图审计，地图 config.json 的 player 值覆盖该预设。编辑器读取同一份默认值，避免仅保存默认配置就改变物理参数。

方块与Buff允许分包：`catalogs/extensions/blocks_*.json`、`buffs_*.json`使用相同的schema头部，启动时按文件名排序合并到主目录。包内及跨包ID均须唯一，不能覆盖旧ID；关联项在合并后统一校验，可跨包引用。显式传入独立JSON路径时仅加载该文件，避免隐式污染编辑/测试数据。

新增效果方块优先通过`buff_ids`、`buff_params_list`和`buff_durations`关联已有Buff，保持参数/持续时间按位置对应；接触时记录来源方块ID。`blocks_magnetic.json`中的439磁引花仅关联14，不含特殊效果处理器；磁引的执行由Buff和世界上下文负责。新增行为仍需实现消费者并验证真实来源、效果及清理。

旧目录哈希基线保留；新ID在`tests/fixtures/catalog_extensions.json`单独登记完整定义、像素及非美术字段哈希。美术生成器重建主目录时不读取/覆写扩展包；新增包使用独立生成器（例如`python3 scripts/build_magnetic_block.py`）。新增数据须同时更新相关审计器，使静态盘点覆盖运行时有效目录。

数值型Buff的空参数`[]`表示使用对应处理器已有默认值，`[0]`表示显式零，二者不同。不要给所有效果统一填`[0]`：这会抵消恢复、减伤、轻羽、带电等效果，还可能把周期效果压到最小间隔。flag型参数按既有契约处理。A80已把33种旧方块中的37个错误数值占位改为空参数，不全局重解释API零。

有意修改旧玩法字段须在`tests/fixtures/catalog_gameplay_changes.json`逐字段登记前后值与原因。目录测试先确认运行时值准确等于登记的after，再将该字段恢复为before，与原历史完整定义/非美术哈希比较；其他字段不能夹带变化。不可改写历史哈希来吞掉差异。`scripts/repair_buff_source_defaults.py`可重放A80迁移，遇到后续不一致编辑会拒绝覆盖。美术生成从当前玩法字段出发，仅图标回退轮廓使用历史像素，避免撤销功能修复或对精修图标重复加工。
