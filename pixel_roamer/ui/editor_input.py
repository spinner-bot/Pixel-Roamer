"""SDL text/IME editing shared by map rename and exact configuration input."""
import pygame
from map_config import validate_config
from maps import list_maps, rename_map
from pixel_roamer.ui.config import _EDITABLE_FIELDS


class EditorTextInput:
    def __init__(self, browser):
        self.browser = browser
        self.app = browser.app
        self.selected = False
        self.composition = ''

    @property
    def active(self):
        return self.app._dev_renaming or self.app._dev_inputting

    def pause(self):
        self.composition = ''
        pygame.key.stop_text_input()

    def resume(self):
        if self.active:
            pygame.key.start_text_input()

    def cancel(self):
        self.app._dev_inputting = self.app._dev_renaming = False
        self.app._dev_input_text = ''
        self.app._dev_error = ''
        self.selected = False
        self.pause()

    def begin(self, rename=False):
        self.cancel()
        self.app._dev_renaming = rename
        self.app._dev_inputting = not rename
        if rename:
            self.app._dev_input_text = list_maps().get(self.app._dev_selected_id, '')
        else:
            path, _, kind, _, _ = _EDITABLE_FIELDS[self.app._dev_edit_field_idx]
            value = self.browser._get_field_value(self.app._dev_edit_config, path)
            self.app._dev_input_text = ('true' if value else 'false') if kind == 'bool' else str(value)
        self.selected = True
        self.resume()

    def set_rect(self, rect):
        scale = self.app.scale
        x, y, w, h = rect
        pygame.key.set_text_input_rect(pygame.Rect(
            round(x * scale + self.app.draw_offset_x), round(y * scale + self.app.draw_offset_y),
            max(1, round(w * scale)), max(1, round(h * scale))))

    def display(self):
        value = '' if self.selected and self.composition else self.app._dev_input_text
        return value + (f'[{self.composition}]' if self.composition else '') + '▌'

    def _append(self, text):
        self.composition = ''
        text = ''.join(ch for ch in text if ch.isprintable())
        if self.app._dev_renaming:
            limit = 64
            if any(ch in '/\\:*?"<>|' for ch in text):
                self.app._dev_error = '名称不能包含路径分隔符或特殊字符'
                return
        else:
            limit = 256
            _, _, kind, _, _ = _EDITABLE_FIELDS[self.app._dev_edit_field_idx]
            if kind in ('int', 'float'):
                allowed = '+-' if kind == 'int' else '+-.eE'
                if any(not ch.isdecimal() and ch not in allowed for ch in text):
                    self.app._dev_error = '请输入有效数字'
                    return
            elif kind == 'bool' and any(not ch.isalnum() for ch in text):
                self.app._dev_error = '请输入 true/false、是/否或 1/0'
                return
        value = ('' if self.selected else self.app._dev_input_text) + text
        if len(value) > limit:
            self.app._dev_error = f'最多输入 {limit} 个字符'
            return
        if text:
            self.app._dev_input_text = value
            self.selected = False
            self.app._dev_error = ''
        self.composition = ''

    def _submit(self):
        if self.app._dev_renaming:
            name = self.app._dev_input_text.strip()
            previous_folder = list_maps().get(self.app._dev_selected_id)
            if not name:
                self.app._dev_error = '地图名称不能为空'
                return
            if not rename_map(self.app._dev_selected_id, name):
                self.app._dev_error = '名称不可用，请检查重复、长度或文件权限'
                return
            self.app._init_dev_selection()
            if self.app._dev_edit_dirty:
                if name != previous_folder:
                    self.app._dev_edit_config.setdefault('world', {})['name'] = name
            else:
                self.app._dev_edit_config = self.browser._get_edit_config(self.app._dev_selected_id)
        else:
            path, _, kind, _, choices = _EDITABLE_FIELDS[self.app._dev_edit_field_idx]
            value = self.browser._parse_input_value(self.app._dev_input_text, kind)
            if value is None:
                self.app._dev_error = '输入格式无效，请修改后确认'
                return
            if kind == 'str' and isinstance(choices, list) and value not in choices:
                self.app._dev_error = '可选值：' + ' / '.join(choices)
                return
            section, field = path.split('.', 1)
            try:
                validate_config({section: {field: value}})
            except ValueError as error:
                self.app._dev_error = str(error)
                return
            self.browser._set_field_value(self.app._dev_edit_config, path, value)
            self.app._dev_edit_dirty = True
        self.cancel()

    def handle(self, event):
        if not self.active:
            return False
        if event.type == pygame.TEXTEDITING:
            self.composition = event.text
        elif event.type == pygame.TEXTINPUT:
            self._append(event.text)
        elif event.type == pygame.KEYDOWN:
            if self.composition:
                if event.key == pygame.K_ESCAPE:
                    self.composition = ''
                return True
            if event.key == pygame.K_ESCAPE:
                self.cancel()
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self._submit()
            elif event.key == pygame.K_a and getattr(event, 'mod', 0) & pygame.KMOD_CTRL:
                self.selected = True
            elif event.key in (pygame.K_BACKSPACE, pygame.K_DELETE):
                self.app._dev_input_text = ('' if self.selected or event.key == pygame.K_DELETE
                                            else self.app._dev_input_text[:-1])
                self.selected = False
            # Printable KEYDOWN text is ignored: SDL TEXTINPUT commits it once.
        return True
