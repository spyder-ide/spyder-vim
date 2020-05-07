# -*- coding: utf-8 -*-
#
# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License
#

"""Tests for the plugin."""

# Standard library imports
import os
import os.path as osp

# Test library imports
import pytest
try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock  # Python 2

# Qt imports
from qtpy.QtCore import Qt
from qtpy.QtGui import QTextCursor
from qtpy.QtWidgets import QWidget, QVBoxLayout, QApplication

# Spyder imports
# from spyder.utils.fixtures import setup_editor
from spyder.widgets.editor import EditorStack

# Local imports
from spyder_vim.vim import Vim
from spyder_vim.vim_widget import RE_VIM_PREFIX


LOCATION = osp.realpath(osp.join(
    os.getcwd(), osp.dirname(__file__)))


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
    text = ('   123\n'
            'line 1\n'
            'line 2\n'
            'line 3\n'
            'line 4')  # a newline is added at end
    editor_stack = EditorStack(None, [])
    editor_stack.set_introspector(Mock())
    editor_stack.set_find_widget(Mock())
    editor_stack.set_io_actions(Mock(), Mock(), Mock(), Mock())
    finfo = editor_stack.new(osp.join(LOCATION, 'foo.txt'), 'utf-8', text)
    main = MainMock(editor_stack)
    # main.show()
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


def test_k_command(vim_bot):
    """Test k command (Cursor moves up)."""
    main, editor_stack, editor, vim, qtbot = vim_bot
    editor.stdkey_backspace()
    cmd_line = vim.get_focus_widget()
    line, _ = editor.get_cursor_line_column()
    qtbot.keyClicks(cmd_line, 'k')
    new_line, _ = editor.get_cursor_line_column()
    assert new_line == line - 1


def test_arrowup_command(vim_bot):
    """Test k command (Cursor moves up)."""
    main, editor_stack, editor, vim, qtbot = vim_bot
    editor.stdkey_backspace()
    cmd_line = vim.get_focus_widget()
    line, _ = editor.get_cursor_line_column()
    qtbot.keyPress(editor, Qt.Key_Up)
    new_line, _ = editor.get_cursor_line_column()
    assert new_line == line - 1


def test_h_command(vim_bot):
    """Test h command (Cursor moves to the left)."""
    main, editor_stack, editor, vim, qtbot = vim_bot
    editor.stdkey_backspace()
    cmd_line = vim.get_focus_widget()
    _, col = editor.get_cursor_line_column()
    qtbot.keyClicks(cmd_line, 'h')
    _, new_col = editor.get_cursor_line_column()
    assert new_col == col - 1


def test_j_command(vim_bot):
    """Test j command (Cursor moves down)."""
    main, editor_stack, editor, vim, qtbot = vim_bot
    editor.stdkey_backspace()
    editor.stdkey_up(True)
    cmd_line = vim.get_focus_widget()
    line, _ = editor.get_cursor_line_column()
    qtbot.keyClicks(cmd_line, 'j')
    new_line, _ = editor.get_cursor_line_column()
    assert new_line == line + 1


def test_arrowdown_command(vim_bot):
    """Test k command (Cursor moves up)."""
    main, editor_stack, editor, vim, qtbot = vim_bot
    editor.stdkey_backspace()
    editor.stdkey_up(True)
    cmd_line = vim.get_focus_widget()
    line, _ = editor.get_cursor_line_column()
    qtbot.keyPress(editor, Qt.Key_Down)
    new_line, _ = editor.get_cursor_line_column()
    assert new_line == line + 1


def test_l_shortchut(vim_bot):
    """Test j command (Cursor moves right)."""
    main, editor_stack, editor, vim, qtbot = vim_bot
    editor.stdkey_backspace()
    qtbot.keyPress(editor, Qt.Key_Left)
    cmd_line = vim.get_focus_widget()
    _, col = editor.get_cursor_line_column()
    qtbot.keyClicks(cmd_line, 'l')
    _, new_col = editor.get_cursor_line_column()
    assert new_col == col + 1


def test_arrowright_shortchut(vim_bot):
    """Test j command (Cursor moves right)."""
    main, editor_stack, editor, vim, qtbot = vim_bot
    editor.stdkey_backspace()
    qtbot.keyPress(editor, Qt.Key_Left)
    cmd_line = vim.get_focus_widget()
    _, col = editor.get_cursor_line_column()
    qtbot.keyPress(editor, Qt.Key_Right)
    _, new_col = editor.get_cursor_line_column()
    assert new_col == col + 1


def test_arrowleft_shortchut(vim_bot):
    """Test j command (Cursor moves right)."""
    main, editor_stack, editor, vim, qtbot = vim_bot
    editor.stdkey_backspace()
    qtbot.keyPress(editor, Qt.Key_Right)
    cmd_line = vim.get_focus_widget()
    _, col = editor.get_cursor_line_column()
    qtbot.keyPress(editor, Qt.Key_Left)
    _, new_col = editor.get_cursor_line_column()
    assert new_col == col - 1


def test_w_shortchut(vim_bot):
    """Test w command (Cursor moves to the next word)."""
    main, editor_stack, editor, vim, qtbot = vim_bot
    editor.stdkey_backspace()
    editor.moveCursor(QTextCursor.PreviousWord, QTextCursor.KeepAnchor)
    qtbot.keyPress(editor, Qt.Key_Left)
    cmd_line = vim.get_focus_widget()
    _, col = editor.get_cursor_line_column()
    qtbot.keyClicks(cmd_line, 'w')
    _, new_col = editor.get_cursor_line_column()
    assert new_col == col + 1


def test_b_shortchut(vim_bot):
    """Test b command (Cursor moves to the previous word)."""
    main, editor_stack, editor, vim, qtbot = vim_bot
    editor.stdkey_backspace()
    qtbot.keyPress(editor, Qt.Key_Left)
    editor.moveCursor(QTextCursor.NextWord, QTextCursor.KeepAnchor)
    cmd_line = vim.get_focus_widget()
    _, col = editor.get_cursor_line_column()
    qtbot.keyClicks(cmd_line, 'b')
    _, new_col = editor.get_cursor_line_column()
    assert new_col == col - 1


def test_f_shortchut(vim_bot):
    """Cursor moves to the next ocurrence of a character."""
    main, editor_stack, editor, vim, qtbot = vim_bot
    editor.go_to_line(2)
    # editor.stdkey_up(True)
    editor.moveCursor(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
    cmd_line = vim.get_focus_widget()
    line, col = editor.get_cursor_line_column()
    qtbot.keyClicks(cmd_line, 'fe')
    qtbot.keyClicks(cmd_line, 'i')
    new_line, new_col = editor.get_cursor_line_column()
    print(line, col)
    print(new_line, new_col)
    assert new_col == col + len('lin')


def test_uppercase_f_shortchut(vim_bot):
    """Cursor moves to the previous ocurrence of a character."""
    main, editor_stack, editor, vim, qtbot = vim_bot
    editor.go_to_line(2)
    # editor.stdkey_up(True)
    editor.moveCursor(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
    qtbot.keyPress(editor, Qt.Key_Right)
    qtbot.keyPress(editor, Qt.Key_Right)
    cmd_line = vim.get_focus_widget()
    line, col = editor.get_cursor_line_column()
    qtbot.keyClicks(cmd_line, 'Fi')
    qtbot.keyClicks(cmd_line, 'i')
    new_line, new_col = editor.get_cursor_line_column()
    print(line, col)
    print(new_line, new_col)
    assert new_col == col - 1


def test_space_command(vim_bot):
    """Cursor moves to the right."""
    main, editor_stack, editor, vim, qtbot = vim_bot
    editor.stdkey_backspace()
    editor.go_to_line(4)
    # editor.stdkey_up(True)
    editor.moveCursor(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
    qtbot.keyPress(editor, Qt.Key_Right)
    qtbot.keyPress(editor, Qt.Key_Right)
    cmd_line = vim.get_focus_widget()
    line, col = editor.get_cursor_line_column()
    qtbot.keyClicks(cmd_line, ' ')
    new_line, new_col = editor.get_cursor_line_column()
    print(line, col)
    print(new_line, new_col)
    assert new_col == col + 1


def test_backspace_command(vim_bot):
    """Cursor moves to the left."""
    main, editor_stack, editor, vim, qtbot = vim_bot
    editor.stdkey_backspace()
    editor.go_to_line(4)
    # editor.stdkey_up(True)
    editor.moveCursor(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
    qtbot.keyPress(editor, Qt.Key_Right)
    qtbot.keyPress(editor, Qt.Key_Right)
    cmd_line = vim.get_focus_widget()
    line, col = editor.get_cursor_line_column()
    qtbot.keyClicks(cmd_line, '\b')
    new_line, new_col = editor.get_cursor_line_column()
    print(line, col)
    print(new_line, new_col)
    assert new_col == col - 1


def test_return_command(vim_bot):
    """Move to the start of the next line."""
    main, editor_stack, editor, vim, qtbot = vim_bot
    editor.stdkey_backspace()
    editor.go_to_line(2)
    # editor.stdkey_up(True)
    editor.moveCursor(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
    qtbot.keyPress(editor, Qt.Key_Right)
    qtbot.keyPress(editor, Qt.Key_Right)
    cmd_line = vim.get_focus_widget()
    line, _ = editor.get_cursor_line_column()
    qtbot.keyPress(cmd_line, Qt.Key_Return)
    new_line, _ = editor.get_cursor_line_column()
    # print(line, col)
    # print(new_line, new_col)
    assert new_line == line + 1


def test_dollar_command(vim_bot):
    """Go to the end of the current line."""
    main, editor_stack, editor, vim, qtbot = vim_bot
    editor.stdkey_backspace()
    editor.go_to_line(3)
    # editor.stdkey_up(True)
    editor.moveCursor(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
    cmd_line = vim.get_focus_widget()
    line, col = editor.get_cursor_line_column()
    qtbot.keyClicks(cmd_line, '$')
    new_line, new_col = editor.get_cursor_line_column()
    assert new_col == col + len('line 2')


def test_zero_command(vim_bot):
    """Go to the start of the current line."""
    main, editor_stack, editor, vim, qtbot = vim_bot
    editor.stdkey_backspace()
    editor.go_to_line(4)
    # editor.stdkey_up(True)
    editor.moveCursor(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
    cmd_line = vim.get_focus_widget()
    line, col = editor.get_cursor_line_column()
    qtbot.keyClicks(cmd_line, '0')
    new_line, new_col = editor.get_cursor_line_column()
    assert new_col == col - len('line 3')


def test_caret_command(vim_bot):
    """Go to the first non-blank character of the line."""
    main, editor_stack, editor, vim, qtbot = vim_bot
    editor.stdkey_backspace()
    editor.go_to_line(1)
    # editor.stdkey_up(True)
    editor.moveCursor(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
    cmd_line = vim.get_focus_widget()
    line, col = editor.get_cursor_line_column()
    qtbot.keyClicks(cmd_line, '^')
    new_line, new_col = editor.get_cursor_line_column()
    assert new_col == col - len('123')


def test_uppercase_g_command(vim_bot):
    """Go to the first non-blank character of the last line."""
    main, editor_stack, editor, vim, qtbot = vim_bot
    editor.stdkey_backspace()
    editor.go_to_line(1)
    # editor.stdkey_up(True)
    editor.moveCursor(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
    cmd_line = vim.get_focus_widget()
    line, col = editor.get_cursor_line_column()
    qtbot.keyClicks(cmd_line, 'G')
    new_line, new_col = editor.get_cursor_line_column()
    assert new_col == col and new_line == line + 4


def test_gg_command(vim_bot):
    """Go to the first position of the first line."""
    main, editor_stack, editor, vim, qtbot = vim_bot
    editor.stdkey_backspace()
    editor.go_to_line(1)
    # editor.stdkey_up(True)
    editor.moveCursor(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
    cmd_line = vim.get_focus_widget()
    line, col = editor.get_cursor_line_column()
    qtbot.keyClicks(cmd_line, 'gg')
    new_line, new_col = editor.get_cursor_line_column()
    assert new_col == 0 and new_line == 0


def test_uppercase_i_command(vim_bot):
    """Insert text before the first non-blank in the line."""
    main, editor_stack, editor, vim, qtbot = vim_bot
    editor.stdkey_backspace()
    editor.go_to_line(4)
    # editor.stdkey_up(True)
    editor.moveCursor(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
    cmd_line = vim.get_focus_widget()
    line, col = editor.get_cursor_line_column()
    qtbot.keyClicks(cmd_line, 'I')
    new_line, new_col = editor.get_cursor_line_column()
    assert new_col == 0


def test_a_command(vim_bot):
    """Append text after the cursor."""
    main, editor_stack, editor, vim, qtbot = vim_bot
    editor.stdkey_backspace()
    editor.go_to_line(2)
    # editor.stdkey_up(True)
    editor.moveCursor(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
    cmd_line = vim.get_focus_widget()
    line, col = editor.get_cursor_line_column()
    qtbot.keyClicks(cmd_line, 'a')
    new_line, new_col = editor.get_cursor_line_column()
    assert new_col == col + 1


def test_uppercase_a_command(vim_bot):
    """Append text at the end of the line."""
    main, editor_stack, editor, vim, qtbot = vim_bot
    editor.stdkey_backspace()
    editor.go_to_line(3)
    # editor.stdkey_up(True)
    editor.moveCursor(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
    cmd_line = vim.get_focus_widget()
    line, col = editor.get_cursor_line_column()
    qtbot.keyClicks(cmd_line, 'A')
    new_line, new_col = editor.get_cursor_line_column()
    assert new_col == col + len('line 2')


def test_o_command(vim_bot):
    """Begin a new line below the cursor and insert text."""
    main, editor_stack, editor, vim, qtbot = vim_bot
    editor.stdkey_backspace()
    editor.go_to_line(2)
    # editor.stdkey_up(True)
    editor.moveCursor(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
    qtbot.keyPress(editor, Qt.Key_Right)
    qtbot.keyPress(editor, Qt.Key_Right)
    cmd_line = vim.get_focus_widget()
    line, col = editor.get_cursor_line_column()
    qtbot.keyClicks(cmd_line, 'o')
    new_line, new_col = editor.get_cursor_line_column()
    assert new_line == line + 1 and new_col == 0


def test_uppercase_O_command(vim_bot):
    """Begin a new line above the cursor and insert text."""
    main, editor_stack, editor, vim, qtbot = vim_bot
    editor.stdkey_backspace()
    editor.go_to_line(3)
    # editor.stdkey_up(True)
    editor.moveCursor(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
    qtbot.keyPress(editor, Qt.Key_Right)
    qtbot.keyPress(editor, Qt.Key_Right)
    cmd_line = vim.get_focus_widget()
    line, col = editor.get_cursor_line_column()
    qtbot.keyClicks(cmd_line, 'O')
    new_line, new_col = editor.get_cursor_line_column()
    assert new_line == line and new_col == 0


def test_u_command(vim_bot):
    """Undo changes."""
    main, editor_stack, editor, vim, qtbot = vim_bot
    editor.stdkey_backspace()
    editor.go_to_line(3)
    # editor.stdkey_up(True)
    editor.moveCursor(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
    qtbot.keyPress(editor, Qt.Key_Right)
    qtbot.keyPress(editor, Qt.Key_Right)
    qtbot.keyClicks(editor, 'spam')
    editor.moveCursor(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
    cmd_line = vim.get_focus_widget()
    line, col = editor.get_cursor_line_column()
    qtbot.keyClicks(cmd_line, 'u')
    editor.moveCursor(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
    new_line, new_col = editor.get_cursor_line_column()
    assert new_col == col - len('spam')


def test_d_command(vim_bot):
    """Delete selection."""
    main, editor_stack, editor, vim, qtbot = vim_bot
    editor.stdkey_backspace()
    editor.go_to_line(3)
    # editor.stdkey_up(True)
    editor.moveCursor(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
    lines, cols = editor.get_cursor_line_column()
    editor.moveCursor(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
    cmd_line = vim.get_focus_widget()
    qtbot.keyPress(cmd_line, 'v')
    qtbot.keyPress(cmd_line, 'l')
    qtbot.keyPress(cmd_line, 'l')
    qtbot.keyClicks(cmd_line, 'd')
    editor.moveCursor(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
    new_lines, new_cols = editor.get_cursor_line_column()
    assert new_cols == cols - 2


def test_dd_command(vim_bot):
    """Delete line."""
    main, editor_stack, editor, vim, qtbot = vim_bot
    editor.stdkey_backspace()
    editor.go_to_line(3)
    # editor.stdkey_up(True)
    editor.moveCursor(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
    qtbot.keyPress(editor, Qt.Key_Right)
    qtbot.keyPress(editor, Qt.Key_Right)
    cmd_line = vim.get_focus_widget()
    num_lines = editor.get_line_count()
    qtbot.keyClicks(cmd_line, 'dd')
    # editor.moveCursor(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
    new_num_lines = editor.get_line_count()
    assert new_num_lines == num_lines - 1


def test_uppercase_d_command(vim_bot):
    """Delete line."""
    main, editor_stack, editor, vim, qtbot = vim_bot
    editor.stdkey_backspace()
    editor.go_to_line(3)
    # editor.stdkey_up(True)
    editor.moveCursor(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
    line, col = editor.get_cursor_line_column()
    editor.moveCursor(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
    qtbot.keyPress(editor, Qt.Key_Right)
    qtbot.keyPress(editor, Qt.Key_Right)
    cmd_line = vim.get_focus_widget()
    qtbot.keyClicks(cmd_line, 'D')
    editor.moveCursor(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
    new_line, new_col = editor.get_cursor_line_column()
    assert new_col == col - len('ne 2')


def test_dw_command(vim_bot):
    """Cut words."""
    main, editor_stack, editor, vim, qtbot = vim_bot
    editor.stdkey_backspace()
    editor.go_to_line(3)
    # editor.stdkey_up(True)
    editor.moveCursor(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
    line, col = editor.get_cursor_line_column()
    editor.moveCursor(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
    cmd_line = vim.get_focus_widget()
    qtbot.keyClicks(cmd_line, 'dw')
    editor.moveCursor(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
    new_line, new_col = editor.get_cursor_line_column()
    assert new_col == 2


def test_cw_command(vim_bot):
    """Cut words and edit."""
    main, editor_stack, editor, vim, qtbot = vim_bot
    editor.stdkey_backspace()
    editor.go_to_line(3)
    # editor.stdkey_up(True)
    editor.moveCursor(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
    line, col = editor.get_cursor_line_column()
    editor.moveCursor(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
    cmd_line = vim.get_focus_widget()
    qtbot.keyClicks(cmd_line, 'cw')
    editor.moveCursor(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
    new_line, new_col = editor.get_cursor_line_column()
    assert new_col == 2


def test_x_command(vim_bot):
    """Delete the character under the cursor wth delete from EndOfLine."""
    main, editor_stack, editor, vim, qtbot = vim_bot
    editor.stdkey_backspace()
    editor.go_to_line(1)
    # editor.stdkey_up(True)
    editor.moveCursor(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
    line, col = editor.get_cursor_line_column()
    editor.moveCursor(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
    cmd_line = vim.get_focus_widget()
    qtbot.keyClicks(cmd_line, 'x')
    editor.moveCursor(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
    new_line, new_col = editor.get_cursor_line_column()
    assert new_col == 5


def test_y_command(vim_bot):
    """Copy selected text on visual mode."""
    main, editor_stack, editor, vim, qtbot = vim_bot
    editor.stdkey_backspace()
    editor.go_to_line(3)
    editor.moveCursor(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
    cmd_line = vim.get_focus_widget()
    qtbot.keyClicks(cmd_line, 'v')
    qtbot.keyClicks(cmd_line, '3l')
    qtbot.keyClicks(cmd_line, 'y')
    clipboard = QApplication.clipboard().text()
    # editor.moveCursor(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
    # new_line, new_col = editor.get_cursor_line_column()
    assert clipboard == 'lin'


def test_yy_command(vim_bot):
    """Copy current line."""
    main, editor_stack, editor, vim, qtbot = vim_bot
    editor.stdkey_backspace()
    editor.go_to_line(3)
    editor.moveCursor(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
    cmd_line = vim.get_focus_widget()
    qtbot.keyClicks(cmd_line, 'V')
    qtbot.keyClicks(cmd_line, 'yy')
    clipboard = QApplication.clipboard().text()
    # editor.moveCursor(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
    # new_line, new_col = editor.get_cursor_line_column()
    assert clipboard[:-1] == 'line 2'


def test_yy_no_visual_command(vim_bot):
    """Copy current line."""
    main, editor_stack, editor, vim, qtbot = vim_bot
    editor.stdkey_backspace()
    editor.go_to_line(3)
    editor.moveCursor(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
    cmd_line = vim.get_focus_widget()
    # qtbot.keyClicks(cmd_line, 'V')
    qtbot.keyClicks(cmd_line, 'yy')
    clipboard = QApplication.clipboard().text()
    # editor.moveCursor(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
    # new_line, new_col = editor.get_cursor_line_column()
    assert clipboard[:-1] == 'line 2'


def test_yw_command(vim_bot):
    """Copy word."""
    main, editor_stack, editor, vim, qtbot = vim_bot
    editor.stdkey_backspace()
    editor.go_to_line(3)
    editor.moveCursor(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
    cmd_line = vim.get_focus_widget()
    # qtbot.keyClicks(cmd_line, 'v')
    qtbot.keyClicks(cmd_line, 'yw')
    clipboard = QApplication.clipboard().text()
    # editor.moveCursor(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
    # new_line, new_col = editor.get_cursor_line_column()
    assert clipboard == 'line'


def test_ydollar_command(vim_bot):
    """Copy until end of line."""
    main, editor_stack, editor, vim, qtbot = vim_bot
    editor.stdkey_backspace()
    editor.go_to_line(3)
    editor.moveCursor(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
    qtbot.keyPress(editor, Qt.Key_Right)
    qtbot.keyPress(editor, Qt.Key_Right)
    cmd_line = vim.get_focus_widget()
    # qtbot.keyClicks(cmd_line, 'v')
    qtbot.keyClicks(cmd_line, 'y$')
    clipboard = QApplication.clipboard().text()
    # editor.moveCursor(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
    # new_line, new_col = editor.get_cursor_line_column()
    assert clipboard == 'ne 2'


def test_p_command_char_mode(vim_bot):
    """Paste characters after cursor."""
    main, editor_stack, editor, vim, qtbot = vim_bot
    editor.stdkey_backspace()
    editor.go_to_line(2)
    editor.moveCursor(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
    qtbot.keyPress(editor, Qt.Key_Right)
    qtbot.keyPress(editor, Qt.Key_Right)
    cmd_line = vim.get_focus_widget()
    qtbot.keyClicks(cmd_line, 'v')
    qtbot.keyClicks(cmd_line, '2k')
    qtbot.keyClicks(cmd_line, 'y')
    qtbot.keyClicks(cmd_line, 'p')
    text = editor.toPlainText()
    expected_text = ('   123\n'
                     'l 123\n'
                     'liine 1\n'
                     'line 2\n'
                     'line 3\n'
                     'line 4')
    # clipboard = QApplication.clipboard().text()
    # editor.moveCursor(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
    # new_line, new_col = editor.get_cursor_line_column()
    assert text == expected_text


def test_p_command_line_mode(vim_bot):
    """Paste line below current line."""
    main, editor_stack, editor, vim, qtbot = vim_bot
    editor.stdkey_backspace()
    editor.go_to_line(3)
    editor.moveCursor(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
    qtbot.keyPress(editor, Qt.Key_Right)
    qtbot.keyPress(editor, Qt.Key_Right)
    cmd_line = vim.get_focus_widget()
    qtbot.keyClicks(cmd_line, 'V')
    qtbot.keyClicks(cmd_line, '2h')
    qtbot.keyClicks(cmd_line, 'y')
    qtbot.keyClicks(cmd_line, 'p')
    text = editor.toPlainText()
    expected_text = ('   123\n'
                     'line 1\n'
                     'line 2\n'
                     'line 2\n'
                     'line 3\n'
                     'line 4')
    # clipboard = QApplication.clipboard().text()
    # editor.moveCursor(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
    # new_line, new_col = editor.get_cursor_line_column()
    assert text == expected_text


def test_zz_command(vim_bot):
    """Save and close file."""
    main, editor_stack, editor, vim, qtbot = vim_bot
    editor.stdkey_backspace()
    editor.go_to_line(3)
    cmd_line = vim.get_focus_widget()
    qtbot.keyClicks(cmd_line, 'ZZ')
    main.editor.close_action.trigger.assert_called_once_with()
    main.editor.save_action.trigger.assert_called_once_with()


def test_w_command(vim_bot):
    """Save file."""
    main, editor_stack, editor, vim, qtbot = vim_bot
    editor.stdkey_backspace()
    editor.go_to_line(3)
    cmd_line = vim.get_focus_widget()
    qtbot.keyClicks(cmd_line, ':w')
    qtbot.keyPress(cmd_line, Qt.Key_Return)
    main.editor.save_action.trigger.assert_called_once_with()


def test_q_command(vim_bot):
    """Close file."""
    main, editor_stack, editor, vim, qtbot = vim_bot
    editor.stdkey_backspace()
    editor.go_to_line(3)
    cmd_line = vim.get_focus_widget()
    qtbot.keyClicks(cmd_line, ':q')
    qtbot.keyPress(cmd_line, Qt.Key_Return)
    main.editor.close_action.trigger.assert_called_once_with()


def test_wq_command(vim_bot):
    """Save and Close file."""
    main, editor_stack, editor, vim, qtbot = vim_bot
    editor.stdkey_backspace()
    editor.go_to_line(3)
    cmd_line = vim.get_focus_widget()
    qtbot.keyClicks(cmd_line, ':wq')
    qtbot.keyPress(cmd_line, Qt.Key_Return)
    main.editor.close_action.trigger.assert_called_once_with()
    main.editor.save_action.trigger.assert_called_once_with()


def test_e_command_no_args(vim_bot):
    """Reload file."""
    main, editor_stack, editor, vim, qtbot = vim_bot
    original_state = editor.toPlainText()
    editor.stdkey_backspace()
    editor.go_to_line(3)
    cmd_line = vim.get_focus_widget()
    qtbot.keyClicks(cmd_line, ':e')
    qtbot.keyPress(cmd_line, Qt.Key_Return)
    state = editor.toPlainText()
    assert original_state == state


def test_e_command_args(vim_bot):
    """Reload and open file."""
    main, editor_stack, editor, vim, qtbot = vim_bot
    editor.stdkey_backspace()
    editor.go_to_line(3)
    cmd_line = vim.get_focus_widget()
    qtbot.keyClicks(cmd_line, ':e .')
    qtbot.keyPress(cmd_line, Qt.Key_Return)
    main.editor.open_action.trigger.assert_called_once_with()


def test_colon_number_command(vim_bot):
    """Go to line."""
    main, editor_stack, editor, vim, qtbot = vim_bot
    editor.stdkey_backspace()
    editor.go_to_line(3)
    cmd_line = vim.get_focus_widget()
    qtbot.keyClicks(cmd_line, ':1')
    qtbot.keyPress(cmd_line, Qt.Key_Return)
    line, _ = editor.get_cursor_line_column()
    assert line == 0


def test_h_command_char_mode(vim_bot):
    """Select character to the left."""
    main, editor_stack, editor, vim, qtbot = vim_bot
    editor.stdkey_backspace()
    editor.go_to_line(3)
    editor.moveCursor(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
    qtbot.keyPress(editor, Qt.Key_Right)
    qtbot.keyPress(editor, Qt.Key_Right)
    cmd_line = vim.get_focus_widget()
    qtbot.keyClicks(cmd_line, 'v')
    qtbot.keyClicks(cmd_line, '2h')
    qtbot.keyClicks(cmd_line, 'y')
    clipboard = QApplication.clipboard().text()
    # editor.moveCursor(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
    # new_line, new_col = editor.get_cursor_line_column()
    assert clipboard == 'li'


def test_j_command_char_mode(vim_bot):
    """Select character down."""
    main, editor_stack, editor, vim, qtbot = vim_bot
    editor.stdkey_backspace()
    editor.go_to_line(3)
    editor.moveCursor(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
    qtbot.keyPress(editor, Qt.Key_Right)
    qtbot.keyPress(editor, Qt.Key_Right)
    cmd_line = vim.get_focus_widget()
    qtbot.keyClicks(cmd_line, 'v')
    qtbot.keyClicks(cmd_line, '2j')
    qtbot.keyClicks(cmd_line, 'y')
    clipboard = QApplication.clipboard().text()
    # editor.moveCursor(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
    # new_line, new_col = editor.get_cursor_line_column()
    # print(list('ne 2 line 3 li'))
    assert clipboard == u'ne 2\u2029line 3\u2029li'


def test_j_command_line_mode(vim_bot):
    """Select line down."""
    main, editor_stack, editor, vim, qtbot = vim_bot
    editor.stdkey_backspace()
    editor.go_to_line(3)
    editor.moveCursor(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
    qtbot.keyPress(editor, Qt.Key_Right)
    qtbot.keyPress(editor, Qt.Key_Right)
    cmd_line = vim.get_focus_widget()
    qtbot.keyClicks(cmd_line, 'V')
    qtbot.keyClicks(cmd_line, '2j')
    qtbot.keyClicks(cmd_line, 'y')
    clipboard = QApplication.clipboard().text()
    # editor.moveCursor(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
    # new_line, new_col = editor.get_cursor_line_column()
    assert clipboard == u'   123\u2029line 1\u2029'


def test_k_command_line_mode(vim_bot):
    """Select line up."""
    main, editor_stack, editor, vim, qtbot = vim_bot
    editor.stdkey_backspace()
    editor.go_to_line(3)
    editor.moveCursor(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
    qtbot.keyPress(editor, Qt.Key_Right)
    qtbot.keyPress(editor, Qt.Key_Right)
    cmd_line = vim.get_focus_widget()
    qtbot.keyClicks(cmd_line, 'V')
    qtbot.keyClicks(cmd_line, '2k')
    qtbot.keyClicks(cmd_line, 'y')
    clipboard = QApplication.clipboard().text()
    # editor.moveCursor(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
    # new_line, new_col = editor.get_cursor_line_column()
    assert clipboard == u'   123\u2029line 1\u2029line 2\u2029'


def test_gg_command_line_mode(vim_bot):
    """Select from first line character."""
    main, editor_stack, editor, vim, qtbot = vim_bot
    editor.stdkey_backspace()
    editor.go_to_line(3)
    editor.moveCursor(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
    qtbot.keyPress(editor, Qt.Key_Right)
    qtbot.keyPress(editor, Qt.Key_Right)
    cmd_line = vim.get_focus_widget()
    qtbot.keyClicks(cmd_line, 'V')
    qtbot.keyClicks(cmd_line, 'gg')
    qtbot.keyClicks(cmd_line, 'y')
    clipboard = QApplication.clipboard().text()
    # editor.moveCursor(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
    # new_line, new_col = editor.get_cursor_line_column()
    assert clipboard == u'   123\u2029line 1\u2029line 2\u2029'


def test_gg_command_char_mode(vim_bot):
    """Select from first line character."""
    main, editor_stack, editor, vim, qtbot = vim_bot
    editor.stdkey_backspace()
    editor.go_to_line(3)
    editor.moveCursor(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
    qtbot.keyPress(editor, Qt.Key_Right)
    qtbot.keyPress(editor, Qt.Key_Right)
    cmd_line = vim.get_focus_widget()
    qtbot.keyClicks(cmd_line, 'v')
    qtbot.keyClicks(cmd_line, 'gg')
    qtbot.keyClicks(cmd_line, 'y')
    clipboard = QApplication.clipboard().text()
    # editor.moveCursor(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
    # new_line, new_col = editor.get_cursor_line_column()
    assert clipboard == u'   123\u2029line 1\u2029li'
