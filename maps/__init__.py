"""
地图注册表。

每个地图是 maps/ 下的一个子文件夹，文件夹名即地图名。
子文件夹内必须包含一个 map.py 文件，该文件暴露：
  - MAP_ID : int  地图唯一ID
  - world  : World  已生成的地图实例
可选的 config.json 文件为地图属性配置文件（世界重力、玩家属性等）。

地图 ID 分配规则：
  - 1 ~ 500         测试地图
  - 501 ~ 1000      系统地图（新手引导、限时活动等）
  - 1001 ~ 100000   主线地图（关卡、副本等）
  - 100000+         自定义地图（未来联网时可拼接玩家ID）
"""
import os
import json
import importlib
import ast

_MAP_REGISTRY_SIGNATURE = None
_MAP_REGISTRY_CACHE = {}
_MAP_SUMMARY_CACHE = {}


def _load_map(map_name: str):
    """加载指定地图文件夹的 map.py 模块。"""
    return importlib.import_module(f"maps.{map_name}.map")


def get_map(map_id: int):
    """从生成模板创建独立的新一局，并应用 config.json（若存在）。"""
    name = _map_registry().get(map_id)
    if name is None:
        raise KeyError(f"地图ID {map_id} 不存在")
    world = _load_map(name).world.create_session()
    _apply_config(world, name)
    return world


def list_maps() -> dict:
    """列出可用地图目录；只读取 MAP_ID 元数据，不生成地图。"""
    return dict(_map_registry())


def load_map_config(map_id: int) -> dict:
    """加载指定地图的配置文件，返回字典。若不存在返回空字典。"""
    maps_dir = os.path.dirname(__file__)
    name = _map_registry().get(map_id)
    if name is None:
        return {}
    config_path = os.path.join(maps_dir, name, "config.json")
    if os.path.isfile(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_map_config(map_id: int, config: dict):
    """保存地图配置到 config.json。"""
    maps_dir = os.path.dirname(__file__)
    name = _map_registry().get(map_id)
    if name is None:
        raise KeyError(f"地图ID {map_id} 不存在，无法保存配置")
    config_path = os.path.join(maps_dir, name, "config.json")
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def get_map_folder_name(map_id: int) -> str:
    """根据地图ID获取文件夹名。"""
    name = _map_registry().get(map_id)
    if name is None:
        raise KeyError(f"地图ID {map_id} 不存在")
    return name


def get_map_summary(map_id: int) -> dict:
    """读取地图尺寸/模式/循环属性，不导入或生成地图实例。"""
    name = _map_registry().get(map_id)
    if name is None:
        raise KeyError(f"地图ID {map_id} 不存在")

    summary = _MAP_SUMMARY_CACHE.get(map_id)
    if summary is None:
        map_path = os.path.join(os.path.dirname(__file__), name, "map.py")
        with open(map_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=map_path)

        constants = {}
        for statement in tree.body:
            if not isinstance(statement, ast.Assign):
                continue
            try:
                value = ast.literal_eval(statement.value)
            except (ValueError, TypeError):
                continue
            if len(statement.targets) == 1 and isinstance(statement.targets[0], ast.Name):
                constants[statement.targets[0].id] = value
            elif (len(statement.targets) == 1
                  and isinstance(statement.targets[0], (ast.Tuple, ast.List))
                  and isinstance(value, (tuple, list))
                  and len(value) == len(statement.targets[0].elts)):
                for target, item in zip(statement.targets[0].elts, value):
                    if isinstance(target, ast.Name):
                        constants[target.id] = item
            elif isinstance(value, (tuple, list)) and len(value) == len(statement.targets):
                for target, item in zip(statement.targets, value):
                    if isinstance(target, ast.Name):
                        constants[target.id] = item

        world_call = next((node for node in ast.walk(tree)
                           if isinstance(node, ast.Call)
                           and isinstance(node.func, ast.Name)
                           and node.func.id == "World"), None)
        if world_call is None:
            raise ValueError(f"地图 {name} 未声明 World(...) 配置")

        args = {keyword.arg: keyword.value for keyword in world_call.keywords if keyword.arg}

        def resolve(field, default):
            node = args.get(field)
            if node is None:
                return default
            try:
                value = ast.literal_eval(node)
            except (ValueError, TypeError):
                value = constants.get(node.id) if isinstance(node, ast.Name) else None
            return default if value is None else value

        summary = {
            "width": resolve("w", None),
            "height": resolve("h", None),
            "mode": resolve("mode", "adventure"),
            "loop_x": resolve("loop_x", False),
            "loop_y": resolve("loop_y", False),
        }
        if summary["width"] is None or summary["height"] is None:
            raise ValueError(f"地图 {name} 的 World(...) 缺少静态宽高")
        _MAP_SUMMARY_CACHE[map_id] = summary

    result = dict(summary)
    config_world = load_map_config(map_id).get("world", {})
    for key in ("width", "height", "mode", "loop_x", "loop_y"):
        if key in config_world:
            result[key] = config_world[key]
    return result


def _apply_config(world, map_name: str):
    """将 config.json 中的属性覆盖到 world 实例上。"""
    maps_dir = os.path.dirname(__file__)
    config_path = os.path.join(maps_dir, map_name, "config.json")
    if not os.path.isfile(config_path):
        return
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except (json.JSONDecodeError, IOError):
        return

    # 应用 world 属性
    world_attrs = config.get("world", {})
    for key, value in world_attrs.items():
        if hasattr(world, key):
            # 特殊处理：fill_color 可能是 list，转为 tuple
            if key == "fill_color" and isinstance(value, list):
                value = tuple(value)
            setattr(world, key, value)

    # player 属性存入 world 供外部读取
    world.player_config = config.get("player", {})


def rename_map(map_id: int, new_name: str) -> bool:
    """彻底重命名地图：文件夹名、World.name 一起改。返回是否成功。"""
    import shutil
    import sys
    maps_dir = os.path.dirname(__file__)
    name = _map_registry().get(map_id)
    if name is None:
        return False
    old_path = os.path.join(maps_dir, name)
    new_path = os.path.join(maps_dir, new_name)
    if name == new_name:
        return True
    if os.path.exists(new_path):
        return False
    try:
        shutil.move(old_path, new_path)
        module = sys.modules.get(f"maps.{name}.map")
        if module is not None and hasattr(module, "world"):
            module.world.name = new_name
        return True
    except OSError:
        return False


def _discover_folders() -> list:
    """扫描 maps/ 下所有合法的地图子文件夹。"""
    maps_dir = os.path.dirname(__file__)
    folders = []
    for d in sorted(os.listdir(maps_dir)):
        full = os.path.join(maps_dir, d)
        if os.path.isdir(full) and not d.startswith("_") and not d.startswith("."):
            map_py = os.path.join(full, "map.py")
            if os.path.isfile(map_py):
                folders.append(d)
    return folders


def _read_map_id(map_name: str) -> int:
    """从地图源码静态读取顶层整数 MAP_ID，避免导入时运行地图生成器。"""
    map_path = os.path.join(os.path.dirname(__file__), map_name, "map.py")
    with open(map_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=map_path)

    for statement in tree.body:
        if isinstance(statement, ast.Assign):
            has_map_id = any(
                isinstance(target, ast.Name) and target.id == "MAP_ID"
                for target in statement.targets
            )
            value_node = statement.value
        elif isinstance(statement, ast.AnnAssign):
            has_map_id = isinstance(statement.target, ast.Name) and statement.target.id == "MAP_ID"
            value_node = statement.value
        else:
            continue
        if has_map_id:
            value = ast.literal_eval(value_node)
            if isinstance(value, int):
                return value
            break
    raise ValueError(f"地图 {map_name} 的 map.py 必须定义整数 MAP_ID")


def _map_registry() -> dict:
    """缓存 {地图ID:目录名}，目录或 map.py 改动时自动刷新。"""
    global _MAP_REGISTRY_SIGNATURE, _MAP_REGISTRY_CACHE
    maps_dir = os.path.dirname(__file__)
    folders = _discover_folders()
    signature = tuple(
        (name, os.stat(os.path.join(maps_dir, name, "map.py")).st_mtime_ns,
         os.stat(os.path.join(maps_dir, name, "map.py")).st_size)
        for name in folders
    )
    if signature == _MAP_REGISTRY_SIGNATURE:
        return _MAP_REGISTRY_CACHE

    registry = {}
    for name in folders:
        map_id = _read_map_id(name)
        if map_id in registry:
            raise ValueError(f"地图ID {map_id} 重复: {registry[map_id]} 和 {name}")
        registry[map_id] = name
    _MAP_REGISTRY_SIGNATURE = signature
    _MAP_REGISTRY_CACHE = registry
    _MAP_SUMMARY_CACHE.clear()
    return registry
