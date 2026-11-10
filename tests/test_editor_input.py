import os
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
import pygame
from pixel_roamer.ui.map_browser import MapBrowser
from pixel_roamer.ui.config import _EDITABLE_FIELDS


def key(code, unicode='', mod=0):
    return pygame.event.Event(pygame.KEYDOWN, key=code, unicode=unicode, mod=mod)


class EditorInputTests(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.app = SimpleNamespace(_dev_edit_mode=True, _dev_block_browser=False,
            _dev_buff_browser=False, _dev_inputting=False, _dev_renaming=False,
            _dev_selected_id=1, _dev_input_text='', _dev_edit_field_idx=0,
            _dev_error='', _dev_edit_dirty=False, _init_dev_selection=Mock(),
            _dev_edit_config={'world': {'gravity': -6.5}, 'player': {'f_y': .9965}},
            scale=.5, draw_offset_x=12, draw_offset_y=7)
        self.browser = MapBrowser(self.app)

    def tearDown(self):
        self.browser.text_input.cancel()

    def text(self, text):
        self.browser.handle_dev_input(pygame.event.Event(pygame.TEXTINPUT, text=text))

    def select(self, path):
        self.app._dev_edit_field_idx = next(i for i, field in enumerate(_EDITABLE_FIELDS) if field[0] == path)
        self.browser.handle_dev_input(key(pygame.K_RETURN))

    def test_chinese_composition_commits_once_before_rename_confirmation(self):
        self.browser.handle_dev_input(key(pygame.K_r))
        self.browser.handle_dev_input(pygame.event.Event(pygame.TEXTEDITING, text='晨', start=0, length=1))
        self.assertIn('晨', self.browser.text_input.display())
        with patch('pixel_roamer.ui.editor_input.rename_map', return_value=True) as rename, \
             patch.object(self.browser, '_get_edit_config', return_value=self.app._dev_edit_config):
            self.browser.handle_dev_input(key(pygame.K_RETURN))
            rename.assert_not_called()
            self.text('晨光林径')
            self.browser.handle_dev_input(key(pygame.K_KP_ENTER))
            rename.assert_called_once_with(1, '晨光林径')
        self.assertFalse(self.app._dev_renaming)

    def test_printable_keydown_is_not_duplicated_with_textinput(self):
        self.select('world.gravity')
        self.browser.handle_dev_input(key(pygame.K_8, unicode='8'))
        self.text('8')
        self.assertEqual(self.app._dev_input_text, '8')
        self.browser.handle_dev_input(key(pygame.K_KP_ENTER))
        self.assertEqual(self.app._dev_edit_config['world']['gravity'], 8)

    def test_open_and_confirm_damping_preserves_fourth_decimal(self):
        self.select('player.f_y')
        self.assertEqual(self.app._dev_input_text, '0.9965')
        self.browser.handle_dev_input(key(pygame.K_RETURN))
        self.assertEqual(self.app._dev_edit_config['player']['f_y'], .9965)

    def test_invalid_value_stays_editable_and_does_not_replace_configuration(self):
        self.select('world.gravity')
        self.text('1e999')
        self.browser.handle_dev_input(key(pygame.K_RETURN))
        self.assertTrue(self.app._dev_inputting)
        self.assertTrue(self.app._dev_error)
        self.assertEqual(self.app._dev_edit_config['world']['gravity'], -6.5)
        self.browser.handle_dev_input(key(pygame.K_a, mod=pygame.KMOD_CTRL))
        self.text('-8.25')
        self.browser.handle_dev_input(key(pygame.K_RETURN))
        self.assertFalse(self.app._dev_inputting)
        self.assertEqual(self.app._dev_edit_config['world']['gravity'], -8.25)

    def test_failed_rename_keeps_input_and_success_preserves_other_dirty_values(self):
        self.app._dev_edit_config['world']['gravity'] = -8.25
        self.app._dev_edit_dirty = True
        self.browser.handle_dev_input(key(pygame.K_r))
        self.text('新地图')
        with patch('pixel_roamer.ui.editor_input.rename_map', return_value=False):
            self.browser.handle_dev_input(key(pygame.K_RETURN))
        self.assertTrue(self.app._dev_renaming)
        self.assertEqual(self.app._dev_input_text, '新地图')
        self.assertTrue(self.app._dev_error)
        with patch('pixel_roamer.ui.editor_input.rename_map', return_value=True):
            self.browser.handle_dev_input(key(pygame.K_RETURN))
        self.assertEqual(self.app._dev_edit_config['world'], {'gravity': -8.25, 'name': '新地图'})
        self.assertTrue(self.app._dev_edit_dirty)

    def test_text_mode_ends_on_cancel_and_candidate_rect_scales_with_view(self):
        with patch('pygame.key.start_text_input') as start, patch('pygame.key.stop_text_input') as stop, \
             patch('pygame.key.set_text_input_rect') as rectangle:
            self.select('world.gravity')
            start.assert_called_once()
            self.browser.text_input.set_rect((200, 100, 600, 30))
            rectangle.assert_called_once_with(pygame.Rect(112, 57, 300, 15))
            self.browser.handle_dev_input(key(pygame.K_ESCAPE))
            self.assertGreaterEqual(stop.call_count, 2)
        self.assertFalse(self.app._dev_inputting)

    def test_unchanged_rename_does_not_replace_display_name_in_dirty_config(self):
        self.app._dev_edit_dirty = True
        self.app._dev_edit_config['world']['name'] = '原显示名称'
        self.browser.handle_dev_input(key(pygame.K_r))
        with patch('pixel_roamer.ui.editor_input.rename_map', return_value=True):
            self.browser.handle_dev_input(key(pygame.K_RETURN))
        self.assertEqual(self.app._dev_edit_config['world']['name'], '原显示名称')

    def test_rejected_composition_commit_does_not_leave_editor_stuck(self):
        self.browser.handle_dev_input(key(pygame.K_r))
        self.browser.handle_dev_input(pygame.event.Event(pygame.TEXTEDITING, text='新', start=0, length=1))
        self.text('新/地图')
        self.assertTrue(self.app._dev_error)
        self.assertEqual(self.browser.text_input.composition, '')
        self.browser.handle_dev_input(key(pygame.K_ESCAPE))
        self.assertFalse(self.app._dev_renaming)

    def test_decimal_shortcuts_do_not_accumulate_binary_display_noise(self):
        self.app._dev_edit_config['player']['w'] = .1
        self.app._dev_edit_field_idx = next(i for i, f in enumerate(_EDITABLE_FIELDS) if f[0] == 'player.w')
        self.browser.handle_dev_input(key(pygame.K_RIGHT))
        self.browser.handle_dev_input(key(pygame.K_RIGHT))
        self.assertEqual(self.app._dev_edit_config['player']['w'], .3)
