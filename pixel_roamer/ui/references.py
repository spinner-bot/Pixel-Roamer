"""A shared player-facing catalog browser; technical asset data stays in JSON."""
from collections import OrderedDict
import json
from pathlib import Path
import re
import pygame
import game_text as gt
import buff_data  # Register the validated catalog independently of Creature imports.
from block_types_data import BLOCK_TYPES
from buff_system import BUFF_TYPES, BuffInstance
from pixel_roamer.ui.theme import PALETTE as P, panel, key_hint


class ReferenceBrowser:
    CACHE_BYTES = 16 * 1024 * 1024

    def __init__(self, app):
        self.app = app
        self._images = OrderedDict()
        self._image_bytes = 0
        self._detail_scroll = {"block": 0, "buff": 0}
        self._detail_max = {"block": 0, "buff": 0}
        path = Path(__file__).resolve().parents[2] / 'data/effect_descriptions.json'
        self.effects = json.loads(path.read_text())['effects']

    def _state(self, kind, field, value=None, write=False):
        name = f'_dev_{kind}_detail_id' if field == 'detail' else f'_dev_{kind}_browser_{field}'
        if write:
            setattr(self.app, name, value)
        return getattr(self.app, name)

    @staticmethod
    def _catalog(kind):
        return BLOCK_TYPES if kind == 'block' else BUFF_TYPES

    def _layout(self, kind):
        ids = sorted(self._catalog(kind))
        cursor = max(0, min(self._state(kind, 'cursor'), len(ids) - 1))
        self._state(kind, 'cursor', cursor, True)
        grid = self._state(kind, 'mode') == 'grid'
        cols, visible = (8, 4) if grid else (1, 8)
        row = cursor // cols
        first = self._state(kind, 'scroll')
        first = min(first, row)
        first = max(first, row - visible + 1)
        first = max(0, min(first, max(0, (len(ids) + cols - 1) // cols - visible)))
        self._state(kind, 'scroll', first, True)
        cells = []
        for index in range(first * cols, min(len(ids), (first + visible) * cols)):
            col, row = index % cols, index // cols - first
            rect = pygame.Rect(64 + col * 184, 180 + row * 156, 176, 148) if grid else pygame.Rect(64, 180 + row * 78, 1472, 70)
            cells.append((index, ids[index], rect))
        return ids, cells

    def _image(self, kind, item, size):
        key = kind, item.id, size
        if key not in self._images:
            from pattern import _draw_vector, _draw_bitmap, _draw_texture
            pattern = item.pattern if kind == 'block' else item.icon
            native = pygame.Surface((32, 32), pygame.SRCALPHA)
            native.fill(item.color if kind == 'block' else P['panel'])
            if pattern:
                renderer = {'vector': _draw_vector, 'bitmap': _draw_bitmap, 'texture': _draw_texture}.get(pattern[0])
                art = renderer(pattern, 32, 32) if renderer else None
                if art is not None:
                    native.blit(art, (0, 0))
            image = pygame.transform.scale(native, (size, size))
            self._images[key] = image
            self._image_bytes += image.get_pitch() * image.get_height()
            while self._image_bytes > self.CACHE_BYTES:
                _, removed = self._images.popitem(last=False)
                self._image_bytes -= removed.get_pitch() * removed.get_height()
        self._images.move_to_end(key)
        return self._images[key]

    @staticmethod
    def _description(item):
        return re.sub(r'\{\d+\}', 'X', item.desc)

    def _block_lines(self, item):
        lines = ['实体方块，可以站立。' if item.is_solid else '非实体，可以穿过。']
        if item.climbable:
            lines.append('可攀爬：使用 W / 上键攀爬，消耗体力。')
        if item.swim_f > 0:
            lines.append('液体：使用 W / 上键向上游泳。')
        if item.one_way:
            lines.append('单向平台：可从下方跳过，从上方落地。')
        if item.damage_ps:
            lines.append(f'接触伤害：每秒 {item.damage_ps:g} 点。')
        if item.surface_f > 1:
            lines.append('表面较滑，离开输入后仍会滑行。')
        elif item.surface_f < 1:
            lines.append('表面阻力较大，水平移动更容易停下。')
        if item.k_stamina != 1:
            lines.append(f'接触时体力消耗倍率：{item.k_stamina:g}。')
        if item.special:
            lines.append(self.effects.get(item.special, item.special))
        for index, buff_id in enumerate(item.buff_ids):
            buff = BUFF_TYPES[buff_id]
            params = item.buff_params_list[index] if index < len(item.buff_params_list) else ()
            duration = item.buff_durations[index] if index < len(item.buff_durations) else None
            text = BuffInstance(buff_id, params, duration).format_desc()
            lines.append(f'{buff.name2}：{text}')
        return lines

    def _draw_detail(self, kind, surface, item):
        panel(surface, (64, 60, 164, 46))
        gt.draw(surface, '返回  Esc', 146, 72, 21, P['text'], 'sans', center_x=True)
        gt.draw(surface, gt.elide(item.name2 or item.name, 1200, 42), 264, 62, 42, P['text'], 'sans')
        gt.draw(surface, f'#{item.id}  /  {item.name}', 266, 124, 21, P['muted'])
        panel(surface, (64, 206, 464, 542))
        panel(surface, (560, 206, 976, 542))
        surface.blit(self._image(kind, item, 320), (136, 280))
        gt.draw(surface, '像素图案', 296, 650, 21, P['muted'], 'sans', center_x=True)
        if kind == 'block':
            lines = self._block_lines(item)
        else:
            category = {'positive': '有益状态', 'neutral': '中性状态', 'negative': '有害状态'}[item.category]
            lines = [category, self._description(item), f'最大叠层：{item.max_stacks}']
            if 'X' in lines[1]:
                lines.append('X 由触发来源决定；身上图标可查看当前数值。')
            if item.conflicts:
                lines.append('会清除：' + '、'.join(BUFF_TYPES[i].name2 for i in item.conflicts))
            if item.cleanup_by:
                lines.append('可被清除：' + '、'.join(BUFF_TYPES[i].name2 for i in item.cleanup_by))
        old_clip = surface.get_clip()
        clip = pygame.Rect(588, 234, 920, 454)
        surface.set_clip(clip)
        y = 246 - self._detail_scroll[kind]
        for text in lines:
            # Gameplay descriptions fit the panel rather than exposing raw vector code.
            for line in self._wrap(text, 880, 24):
                gt.draw(surface, line, 596, y, 24, P['text'], 'sans')
                y += 34
            y += 15
        surface.set_clip(old_clip)
        self._detail_max[kind] = max(0, y + self._detail_scroll[kind] - clip.bottom)
        if self._detail_max[kind]:
            gt.draw(surface, '滚轮 / PageUp / PageDown 查看更多', 596, 706, 18, P['muted'], 'sans')
        key_hint(surface, 'Esc', '返回图鉴', 64, 826)

    @staticmethod
    def _wrap(text, width, size):
        lines, line = [], ''
        font = gt._get_font('sans', size)
        for char in text:
            if line and font.get_rect(line + char).width > width:
                lines.append(line)
                line = ''
            line += char
        return lines + [line]

    def _draw(self, kind, surface, dt):
        surface.fill(P['background'])
        catalog = self._catalog(kind)
        detail = self._state(kind, 'detail')
        if detail is not None:
            self._draw_detail(kind, surface, catalog[detail])
            return
        title = '方块图鉴' if kind == 'block' else '状态图鉴'
        gt.draw(surface, title, 64, 54, 48, P['text'], 'sans')
        gt.draw(surface, '点击卡片查看详情；按 Tab 切换网格或列表。', 66, 124, 21, P['muted'], 'sans')
        for text, x, active in (('方块 B', 1120, kind == 'block'), ('状态 U', 1308, kind == 'buff')):
            panel(surface, (x, 66, 176, 46), active)
            gt.draw(surface, text, x + 88, 78, 21, P['text'], 'sans', center_x=True)
        ids, cells = self._layout(kind)
        cursor = self._state(kind, 'cursor')
        grid = self._state(kind, 'mode') == 'grid'
        name_key = 'name2' if self._state(kind, 'show_name2') else 'name'
        for index, item_id, rect in cells:
            item = catalog[item_id]
            panel(surface, rect, index == cursor)
            size = 80 if grid else 48
            x, y = (rect.centerx - 40, rect.y + 10) if grid else (rect.x + 18, rect.y + 11)
            surface.blit(self._image(kind, item, size), (x, y))
            label = getattr(item, name_key) or item.name
            if grid:
                gt.draw(surface, gt.elide(label, rect.w - 14, 18), rect.centerx, rect.y + 100,
                        18, P['text'], 'sans', center_x=True)
                gt.draw(surface, f'#{item_id}', rect.x + 12, rect.y + 126, 15, P['muted'])
            else:
                gt.draw(surface, gt.elide(label, 400, 24), rect.x + 84, rect.y + 9, 24, P['text'], 'sans')
                gt.draw(surface, f'#{item_id}  {item.name}', rect.x + 85, rect.y + 41, 15, P['muted'])
                description = ' · '.join(self._block_lines(item)[:2]) if kind == 'block' else self._description(item)
                gt.draw(surface, gt.elide(description, 850, 21), rect.x + 560, rect.y + 24, 21, P['muted'], 'sans')
        key_hint(surface, 'Esc', '返回地图', 64, 850)
        key_hint(surface, 'Tab', '切换视图', 290, 850)
        key_hint(surface, 'N', '中英文', 540, 850)
        gt.draw(surface, f'{cursor + 1} / {len(ids)}', 1536, 852, 18, P['muted'], right_x=True)

    def _run_block_browser(self, surface, dt):
        self._draw('block', surface, dt)

    def _run_buff_browser(self, surface, dt):
        self._draw('buff', surface, dt)

    def _handle(self, kind, event):
        catalog = self._catalog(kind)
        ids = sorted(catalog)
        detail = self._state(kind, 'detail')
        if event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN):
            pos = event.pos if hasattr(event, 'pos') else pygame.mouse.get_pos()
            point = ((pos[0] - self.app.draw_offset_x) / self.app.scale,
                     (pos[1] - self.app.draw_offset_y) / self.app.scale)
            click = event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
            if detail is not None:
                if click and pygame.Rect(64, 60, 164, 46).collidepoint(point):
                    self._state(kind, 'detail', None, True)
                return
            if click and 66 <= point[1] < 112:
                other = 'block' if 1120 <= point[0] < 1296 else 'buff' if 1308 <= point[0] < 1484 else None
                if other:
                    setattr(self.app, '_dev_block_browser', other == 'block')
                    setattr(self.app, '_dev_buff_browser', other == 'buff')
                    return
            for index, item_id, rect in self._layout(kind)[1]:
                if rect.collidepoint(point):
                    self._state(kind, 'cursor', index, True)
                    if click:
                        self._state(kind, 'detail', item_id, True)
                        self._detail_scroll[kind] = 0
                    return
        if detail is not None and event.type == pygame.MOUSEWHEEL:
            self._detail_scroll[kind] = max(0, min(self._detail_max[kind], self._detail_scroll[kind] - event.y * 48))
            return
        if event.type == pygame.MOUSEWHEEL and detail is None:
            step = 8 if self._state(kind, 'mode') == 'grid' else 1
            self._state(kind, 'cursor', max(0, min(len(ids) - 1, self._state(kind, 'cursor') - event.y * step)), True)
            return
        if event.type != pygame.KEYDOWN:
            return
        if detail is not None:
            if event.key in (pygame.K_ESCAPE, pygame.K_b if kind == 'block' else pygame.K_u):
                self._state(kind, 'detail', None, True)
            elif event.key in (pygame.K_PAGEUP, pygame.K_PAGEDOWN):
                delta = -240 if event.key == pygame.K_PAGEUP else 240
                self._detail_scroll[kind] = max(0, min(self._detail_max[kind], self._detail_scroll[kind] + delta))
            return
        if event.key in (pygame.K_ESCAPE, pygame.K_b if kind == 'block' else pygame.K_u):
            setattr(self.app, f'_dev_{kind}_browser', False)
        elif event.key in (pygame.K_b, pygame.K_u):
            self.app._dev_block_browser = event.key == pygame.K_b
            self.app._dev_buff_browser = event.key == pygame.K_u
        elif event.key == pygame.K_TAB:
            self._state(kind, 'mode', 'list' if self._state(kind, 'mode') == 'grid' else 'grid', True)
            self._state(kind, 'scroll', 0, True)
        elif event.key == pygame.K_n:
            self._state(kind, 'show_name2', not self._state(kind, 'show_name2'), True)
        elif event.key == pygame.K_RETURN:
            self._state(kind, 'detail', ids[self._state(kind, 'cursor')], True)
            self._detail_scroll[kind] = 0
        else:
            step = 8 if self._state(kind, 'mode') == 'grid' else 1
            delta = {pygame.K_UP: -step, pygame.K_DOWN: step, pygame.K_LEFT: -1,
                     pygame.K_RIGHT: 1, pygame.K_PAGEUP: -step * 4, pygame.K_PAGEDOWN: step * 4}.get(event.key)
            if delta is not None:
                self._state(kind, 'cursor', max(0, min(len(ids) - 1, self._state(kind, 'cursor') + delta)), True)
            elif event.key in (pygame.K_HOME, pygame.K_END):
                self._state(kind, 'cursor', 0 if event.key == pygame.K_HOME else len(ids) - 1, True)

    def _handle_block_browser_input(self, event):
        self._handle('block', event)

    def _handle_buff_browser_input(self, event):
        self._handle('buff', event)
