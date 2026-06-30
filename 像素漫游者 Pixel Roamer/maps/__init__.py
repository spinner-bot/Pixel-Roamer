"""
地图注册表。

每个地图是 maps/ 下的一个子文件夹，文件夹名即地图名。
子文件夹内必须包含一个 map.py 文件，该文件暴露：
  - MAP_ID : int  地图唯一ID
  - world  : World  已生成的地图实例
可选的 config.json 文件为地图属性配置文件（世界重力、玩家属性等）。
"""
import os
import json
import importlib


def _load_map(map_name: str):
    """加载指定地图文件夹的 map.py 模块。"""
    return importlib.import_module(f"maps.{map_name}.map")


def get_map(map_id: int):
    """根据地图ID加载对应的 World 实例，并应用 config.json（若存在）。"""
    for name in _discover_folders():
        module = _load_map(name)
        if module.MAP_ID == map_id:
            world = module.world
            _apply_config(world, name)
            return world
    raise KeyError(f"地图ID {map_id} 不存在")


def list_maps() -> dict:
    """列出所有可用地图，返回 {id: name} 字典。"""
    result = {}
    for name in _discover_folders():
        module = _load_map(name)
        result[module.MAP_ID] = name
    return result


def load_map_config(map_id: int) -> dict:
    """加载指定地图的配置文件，返回字典。若不存在返回空字典。"""
    maps_dir = os.path.dirname(__file__)
    for name in _discover_folders():
        module = _load_map(name)
        if module.MAP_ID == map_id:
            config_path = os.path.join(maps_dir, name, "config.json")
            if os.path.isfile(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            return {}
    return {}


def save_map_config(map_id: int, config: dict):
    """保存地图配置到 config.json。"""
    maps_dir = os.path.dirname(__file__)
    for name in _discover_folders():
        module = _load_map(name)
        if module.MAP_ID == map_id:
            config_path = os.path.join(maps_dir, name, "config.json")
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            return
    raise KeyError(f"地图ID {map_id} 不存在，无法保存配置")


def get_map_folder_name(map_id: int) -> str:
    """根据地图ID获取文件夹名。"""
    for name in _discover_folders():
        module = _load_map(name)
        if module.MAP_ID == map_id:
            return name
    raise KeyError(f"地图ID {map_id} 不存在")


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
    maps_dir = os.path.dirname(__file__)
    for name in _discover_folders():
        module = _load_map(name)
        if module.MAP_ID == map_id:
            old_path = os.path.join(maps_dir, name)
            new_path = os.path.join(maps_dir, new_name)
            if name == new_name:
                return True
            if os.path.exists(new_path):
                return False
            try:
                shutil.move(old_path, new_path)
                module.world.name = new_name
                return True
            except OSError:
                return False
    return False


def _discover_folders() -> list:
    """扫描 maps/ 下所有合法的地图子文件夹。"""
    maps_dir = os.path.dirname(__file__)
    folders = []
    for d in os.listdir(maps_dir):
        full = os.path.join(maps_dir, d)
        if os.path.isdir(full) and not d.startswith("_") and not d.startswith("."):
            map_py = os.path.join(full, "map.py")
            if os.path.isfile(map_py):
                folders.append(d)
    return folders
