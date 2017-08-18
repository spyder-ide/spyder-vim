# -*- coding: utf-8 -*-
#
# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License
#

"""Tests for the plugin."""

# Test library imports
import pytest
try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock  # Python 2

# Qt imports
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QVBoxLayout

# Spyder imports
# from spyder.utils.fixtures import setup_editor
from spyder.widgets.editor import EditorStack

# Local imports
from spyder_vim.vim import Vim
from spyder_vim.vim_widget import RE_VIM_PREFIX


class EditorMock(QWidget):
    """Editor plugin mock."""

    def __init__(self, editor_stack):
        """Editor Mock constructor."""
        QWidget.__init__(self, None)
        self.editor_stack = editor_stack
        self.editorsplitter = self.editor_stack
        self.open_action = Mock()
        self.new_action = Mock()
        self.save_action = Mock()
        self.close_action = Mock()

        layout = QVBoxLayout()
        layout.addWidget(self.editor_stack)
        self.setLayout(layout)

    def get_current_editorstack(self):
        """Return EditorStack instance."""
        return self.editor_stack


class MainMock(QWidget):
    """Spyder MainWindow mock."""

    def __init__(self, editor_stack):
        """Main Window Mock constructor."""
        QWidget.__init__(self, None)
        self.plugin_focus_changed = Mock()
        self.editor = EditorMock(editor_stack)
        layout = QVBoxLayout()
        layout.addWidget(self.editor)
        self.setLayout(layout)


@pytest.fixture
def editor_bot(qtbot):
    """Editorstack pytest fixture."""
    text = ('line 1\n'
            'line 2\n'
            'line 3\n'
            'line 4')  # a newline is added at end
    editor_stack = EditorStack(None, [])
    editor_stack.set_introspector(Mock())
    editor_stack.set_find_widget(Mock())
    editor_stack.set_io_actions(Mock(), Mock(), Mock(), Mock())
    finfo = editor_stack.new('foo.py', 'utf-8', text)
    main = MainMock(editor_stack)
    main.show()
    qtbot.addWidget(main)
    return main, editor_stack, finfo.editor, qtbot


@pytest.fixture
def vim_bot(editor_bot):
    """Create an spyder-vim plugin instance."""
    main, editor_stack, editor, qtbot = editor_bot
    vim = Vim(main)
    vim.register_plugin()
    return main, editor_stack, editor, vim, qtbot


def test_prefix_no_match():
    """Test that prefix regex does not match invalid prefix."""
    match = RE_VIM_PREFIX.match("d")
    assert match is None


def test_one_char():
    """Test that prefix regex matches valid single prefix."""
    groups = RE_VIM_PREFIX.match("D").groups()
    assert groups == ("", "D", "")


def test_two_chars_command():
    """Test that prefix regex matches valid pairs of prefixes."""
    groups = RE_VIM_PREFIX.match("dd").groups()
    assert groups == ("", "dd", "")


def test_number_no_match():
    """Test that prefix regex does not match invalid number combinations."""
    match = RE_VIM_PREFIX.match("11")
    assert match is None


def test_number_and_zero_no_match():
    """Test that prefix regex does not match 10 combination."""
    match = RE_VIM_PREFIX.match("10")
    assert match is None


def test_two_chars_repeat():
    """Test that prefix regex matches two prefix combinations."""
    groups = RE_VIM_PREFIX.match("2D").groups()
    assert groups == ("2", "D", "")


def test_three_chars_repeat():
    """Test that prefix regex matches three prefix combinations."""
    groups = RE_VIM_PREFIX.match("21D").groups()
    assert groups == ("21", "D", "")


def test_three_chars_with_zero_repeat():
    """Test that prefix regex matches three combinations that contain 0."""
    groups = RE_VIM_PREFIX.match("20D").groups()
    assert groups == ("20", "D", "")


def test_k_shortcut(vim_bot):
    """Test k shortcut (Cursor moves up)."""
    main, editor_stack, editor, vim, qtbot = vim_bot
    editor.stdkey_backspace()
    cmd_line = vim.get_focus_widget()
    line, _ = editor.get_cursor_line_column()
    qtbot.keyClicks(cmd_line, 'k')
    new_line, _ = editor.get_cursor_line_column()
    assert new_line == line - 1


def test_h_shortcut(vim_bot):
    """Test h shortcut (Cursor moves to the left)."""
    main, editor_stack, editor, vim, qtbot = vim_bot
    editor.stdkey_backspace()
    cmd_line = vim.get_focus_widget()
    _, col = editor.get_cursor_line_column()
    qtbot.keyClicks(cmd_line, 'h')
    _, new_col = editor.get_cursor_line_column()
    assert new_col == col - 1


def test_j_shortcut(vim_bot):
    """Test j shortcut (Cursor moves down)."""
    main, editor_stack, editor, vim, qtbot = vim_bot
    editor.stdkey_backspace()
    editor.stdkey_up(True)
    cmd_line = vim.get_focus_widget()
    line, _ = editor.get_cursor_line_column()
    qtbot.keyClicks(cmd_line, 'j')
    new_line, _ = editor.get_cursor_line_column()
    assert new_line == line + 1


def test_l_shortchut(vim_bot):
    """Test j shortcut (Cursor moves right)."""
    main, editor_stack, editor, vim, qtbot = vim_bot
    editor.stdkey_backspace()
    qtbot.keyPress(editor, Qt.Key_Left)
    cmd_line = vim.get_focus_widget()
    _, col = editor.get_cursor_line_column()
    qtbot.keyClicks(cmd_line, 'l')
    _, new_col = editor.get_cursor_line_column()
    assert new_col == col + 1
