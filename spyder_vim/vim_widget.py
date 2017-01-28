# -*- coding: utf-8 -*-

from __future__ import (
    print_function, unicode_literals, absolute_import, division)

import re
from time import time

from qtpy.QtWidgets import (QWidget, QLineEdit, QHBoxLayout, QTextEdit, QLabel,
                            QSizePolicy, QApplication)
from qtpy.QtGui import QTextCursor
from qtpy.QtCore import Qt


VIM_COMMAND_PREFIX = ":!/?"
VIM_PREFIX = "cdfFgmrtTyzZ@'`\"<>"
RE_VIM_PREFIX_STR = r"^(\d*)([{prefixes}].|[^{prefixes}0123456789])(.*)$"
RE_VIM_PREFIX = re.compile(RE_VIM_PREFIX_STR.format(prefixes=VIM_PREFIX))

VIM_VISUAL_OPS = "hjklGyw"
VIM_VISUAL_PREFIX = "agi"
RE_VIM_VISUAL_PREFIX = re.compile(RE_VIM_PREFIX_STR.format(prefixes=
                                                           VIM_VISUAL_PREFIX))
SYMBOLS_REPLACEMENT = {
    "!": "EXCLAMATION",
    "?": "QUESTION",
    "<": "LESS",
    ">": "GREATER",
    "|": "PIPE",
    " ": "SPACE",
    "\b": "BACKSPACE",
    "\r": "RETURN",
    "@": "AT",
    "$": "DOLLAR",
    "0": "ZERO",
}


# %% Vim shortcuts
class VimKeys(object):
    def __init__(self, widget):
        self._widget = widget
        self._prev_cursor = None
        self.visual_mode = False

    def __call__(self, key, repeat):
        if key.startswith("_"):
            return
        for symbol, text in SYMBOLS_REPLACEMENT.items():
            key = key.replace(symbol, text)
        try:
            method = self.__getattribute__(key)
        except AttributeError:
            print("unknown key", key)
        else:
            method(repeat)

    def _move_cursor(self, movement, repeat=1):
        cursor = self._editor_cursor()
        cursor.movePosition(movement, n=repeat)
        self._widget.editor().setTextCursor(cursor)
        self._widget.update_vim_cursor()

    def _move_selection(self, pos, move_start=False):
        """Move visually selected text.

        Positional arguments:
        pos -- position to move selection

        Keyword arguments:
        move_start -- set start of selection to pos (default False)
        """
        editor = self._widget.editor()
        selection = editor.get_extra_selections('vim_visual')[0]
        if self.visual_mode == 'char':
            if move_start:
                selection.cursor.setPosition(pos)
                selection.cursor.setPosition(self._prev_cursor.position(),
                                             QTextCursor.KeepAnchor)
            else:
                selection.cursor.setPosition(self._prev_cursor.position())
                selection.cursor.setPosition(pos, QTextCursor.KeepAnchor)
        if self.visual_mode == 'line':
            prev_cursor_block = self._prev_cursor.block()
            if move_start:
                next_cursor_block = prev_cursor_block.next()
                selection.cursor.setPosition(pos)
                selection.cursor.setPosition(next_cursor_block.position(),
                                             QTextCursor.KeepAnchor)
            else:
                selection.cursor.setPosition(prev_cursor_block.position())
                selection.cursor.setPosition(pos, QTextCursor.KeepAnchor)
        editor.set_extra_selections('vim_visual', [selection])
        editor.update_extra_selections()

    def _get_selection_positions(self):
        editor = self._widget.editor()
        selection = editor.get_extra_selections('vim_visual')[0]
        start = selection.cursor.selectionStart()
        end = selection.cursor.selectionEnd()
        return start, end

    def _editor_cursor(self):
        """Return editor's cursor."""
        editor = self._widget.editor()
        cursor = editor.textCursor()
        return cursor

    def _get_line(self, editor_cursor, lines=1):
        """Return the line at cursor position."""
        try:
            cursor = QTextCursor(editor_cursor)
        except TypeError:
            print("ERROR: editor_cursor must be an instance of QTextCursor")
        else:
            cursor.movePosition(QTextCursor.StartOfLine)
            cursor.movePosition(QTextCursor.Down, QTextCursor.KeepAnchor,
                                n=lines)
            line = cursor.selectedText()
            return line

    def _update_selection_type(self, selection_type):
        cur_time = int(time())
        self._widget.selection_type = (cur_time, selection_type)

    def exit_visual_mode(self):
        """Exit visual mode."""
        editor = self._widget.editor()
        editor.clear_extra_selections('vim_visual')
        self._widget.update_vim_cursor()
        self.visual_mode = False

    # %% Movement
    def h(self, repeat=1):
        cursor = self._editor_cursor()
        if not cursor.atBlockStart():
            if self.visual_mode == 'char':
                prev_cursor_pos = self._prev_cursor.position()
                start, end = self._get_selection_positions()
                if cursor.position() > \
                   prev_cursor_pos:
                    self._move_selection(end - 1)
                else:
                    self._move_selection(start - 1, move_start=True)
            self._move_cursor(QTextCursor.Left)
            if repeat > 1:
                self.h(repeat-1)

    def j(self, repeat=1):
        self._move_cursor(QTextCursor.Down, repeat)
        cursor = self._editor_cursor()
        if self.visual_mode == 'char':
            start, end = self._get_selection_positions()
            if cursor.position() > end:
                self._move_selection(cursor.position())
            else:
                self._move_selection(cursor.position(), move_start=True)
        elif self.visual_mode == 'line':
            start, end = self._get_selection_positions()
            cur_block = cursor.block()
            if cursor.position() >= end:
                if not cursor.atEnd():
                    self._move_selection(cur_block.next().position())
            else:
                self._move_selection(cur_block.position(), move_start=True)

    def k(self, repeat=1):
        self._move_cursor(QTextCursor.Up, repeat)
        cursor = self._editor_cursor()
        if self.visual_mode == 'char':
            start, end = self._get_selection_positions()
            if cursor.position() < start:
                self._move_selection(cursor.position(), move_start=True)
            else:
                self._move_selection(cursor.position())
        elif self.visual_mode == 'line':
            start, end = self._get_selection_positions()
            cur_block = cursor.block()
            if cursor.position() < start:
                self._move_selection(cur_block.position(), move_start=True)
            else:
                self._move_selection(cur_block.next().position())

    def l(self, repeat=1):
        cursor = self._editor_cursor()
        if not cursor.atBlockEnd():
            if self.visual_mode == 'char':
                prev_cursor_pos = self._prev_cursor.position()
                start, end = self._get_selection_positions()
                if cursor.position() >= \
                   prev_cursor_pos:
                    self._move_selection(end + 1)
                else:
                    self._move_selection(start + 1, move_start=True)
            self._move_cursor(QTextCursor.Right)
            if repeat > 1:
                self.l(repeat-1)

    def w(self, repeat=1):
        self._move_cursor(QTextCursor.NextWord, repeat)
        if self.visual_mode == 'char':
            cursor = self._editor_cursor()
            self._move_selection(cursor.position())

    def SPACE(self, repeat=1):
        self._move_cursor(QTextCursor.Right, repeat)

    def BACKSPACE(self, repeat=1):
        self._move_cursor(QTextCursor.Left, repeat)

    def RETURN(self, repeat=1):
        editor = self._widget.editor()
        cursor = editor.textCursor()
        cursor.movePosition(QTextCursor.NextBlock, n=repeat)
        text = self._get_line(cursor)
        if text.isspace() or not text:
            pass
        elif text[0].isspace():
            cursor.movePosition(QTextCursor.NextWord)
        editor.setTextCursor(cursor)
        self._widget.update_vim_cursor()

    def DOLLAR(self, repeat=1):
        self._move_cursor(QTextCursor.EndOfLine)

    def ZERO(self, repeat=1):
        self._move_cursor(QTextCursor.StartOfLine)

    def G(self, repeat=-1):
        if repeat == -1:
            self._move_cursor(QTextCursor.End)
            if self.visual_mode:
                self._move_selection(self._editor_cursor().position())
        else:
            self.gg(repeat)

    def gg(self, repeat=1):
        editor = self._widget.editor()
        editor.go_to_line(repeat)
        self._widget.update_vim_cursor()

    # %% Insertion
    def i(self, repeat):
        self._widget.editor().setFocus()

    def I(self, repeat):
        self._move_cursor(QTextCursor.StartOfLine)
        self._widget.editor().setFocus()

    def a(self, repeat):
        self.l()
        self._widget.editor().setFocus()

    def A(self, repeat):
        self._move_cursor(QTextCursor.EndOfLine)
        self._widget.editor().setFocus()

    def o(self, repeat):
        editor = self._widget.editor()
        cursor = editor.textCursor()
        cursor.movePosition(QTextCursor.EndOfLine)
        cursor.insertText("\n")
        editor.setTextCursor(cursor)
        editor.setFocus()

    def O(self, repeat):
        editor = self._widget.editor()
        cursor = editor.textCursor()
        cursor.movePosition(QTextCursor.StartOfLine)
        cursor.insertText("\n")
        cursor.movePosition(QTextCursor.Up)
        editor.setTextCursor(cursor)
        editor.setFocus()

    # %% Editing and cases(visual)
    def u(self, repeat):
        if not self.visual_mode:
            for count in range(repeat):
                self._widget.editor().undo()
            self._widget.update_vim_cursor()
        else:
            # TODO: make selection lowercase
            pass

    def U(self, repeat):
        if self.visual_mode:
            # TODO: make selection uppercase
            pass

    # %% Deletions
    def dd(self, repeat):
        editor = self._widget.editor()
        cursor = editor.textCursor()
        cursor.movePosition(QTextCursor.StartOfLine)
        cursor.movePosition(QTextCursor.Down, QTextCursor.KeepAnchor, repeat)
        editor.setTextCursor(cursor)
        editor.cut()
        self._update_selection_type("line")
        text = self._get_line(cursor)
        if text.isspace() or not text:
            pass
        elif text[0].isspace():
            cursor.movePosition(QTextCursor.NextWord)
        editor.setTextCursor(cursor)
        self._widget.update_vim_cursor()

    def D(self, repeat):
        editor = self._widget.editor()
        cursor = editor.textCursor()
        cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
        cursor.movePosition(QTextCursor.Down, QTextCursor.KeepAnchor,
                            repeat - 1)
        editor.setTextCursor(cursor)
        editor.cut()
        self._widget.update_vim_cursor()

    def dw(self, repeat):
        editor = self._widget.editor()
        cursor = editor.textCursor()
        cursor.movePosition(QTextCursor.EndOfWord, QTextCursor.KeepAnchor,
                            repeat)
        editor.setTextCursor(cursor)
        editor.cut()
        self._widget.update_vim_cursor()

    def cw(self, repeat):
        self.dw(repeat)
        self.i(repeat)

    # %% Copy
    def y(self, repeat):
        editor = self._widget.editor()
        selection = editor.get_extra_selections('vim_visual')[0]
        cursor = selection.cursor
        text = cursor.selectedText()
        QApplication.clipboard().setText(text)
        if self.visual_mode == 'char':
            self._update_selection_type('char')
        elif self.visual_mode == 'line':
            self._update_selection_type('line')
        else:
            self._update_selection_type('block')
        editor.setTextCursor(self._prev_cursor)
        self._move_cursor(QTextCursor.StartOfLine)
        self.exit_visual_mode()

    def yy(self, repeat):
        cursor = self._editor_cursor()
        text = self._get_line(cursor, lines=repeat)
        QApplication.clipboard().setText(text)
        self._update_selection_type("line")

    def yw(self, repeat):
        editor = self._widget.editor()
        cursor = editor.textCursor()
        cursor.movePosition(QTextCursor.NextWord, QTextCursor.KeepAnchor,
                            repeat - 1)
        cursor.movePosition(QTextCursor.EndOfWord, QTextCursor.KeepAnchor)
        text = cursor.selectedText()
        QApplication.clipboard().setText(text)

    def yDOLLAR(self, repeat):
        editor = self._widget.editor()
        cursor = editor.textCursor()
        cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor,
                            repeat)
        text = cursor.selectedText()
        QApplication.clipboard().setText(text)

    def p(self, repeat):
        if self._widget.selection_type[1] == 'line':
            self.j()
            self.P(repeat)
        elif self._widget.selection_type[1] == 'char':
            self.l()
            self.P(repeat)
        else:
            # TODO: implement pasting block text after implementing visual mode
            self.P()

    def P(self, repeat):
        editor = self._widget.editor()
        cursor = editor.textCursor()
        text = QApplication.clipboard().text()
        lines = text.splitlines()
        if self._widget.selection_type[1] == 'line':
            text *= repeat
            startBlockPosition = cursor.block().position()
            cursor.movePosition(QTextCursor.StartOfLine)
            cursor.insertText(text)
            cursor.setPosition(startBlockPosition)
            if lines[0].strip():
                cursor.movePosition(QTextCursor.NextWord)
            editor.setTextCursor(cursor)
        elif self._widget.selection_type[1] == 'char':
            startPosition = cursor.position()
            for i in range(repeat):
                editor.paste()
            if len(lines) > 1:
                cursor.setPosition(startPosition)
                editor.setTextCursor(cursor)
        else:
            # TODO: implement pasting block text after implementing visual mode
            pass
        self._widget.update_vim_cursor()

    # %% Files
    def ZZ(self, repeat):
        self._widget.main.editor.save_action.trigger()
        self._widget.main.editor.close_action.trigger()
        self._widget.commandline.setFocus()

    # %% Visual mode
    def v(self, repeat):
        self.visual_mode = 'char'
        editor = self._widget.editor()
        cursor = editor.textCursor()
        self._prev_cursor = cursor
        selection = QTextEdit.ExtraSelection()
        back = Qt.white  # selection.format.background().color()
        fore = Qt.gray   # selection.format.foreground().color()
        selection.format.setBackground(fore)
        selection.format.setForeground(back)
        selection.cursor = editor.textCursor()
        editor.set_extra_selections('vim_visual', [selection])
        editor.update_extra_selections()

    def V(self, repeat):
        self.visual_mode = 'line'
        editor = self._widget.editor()
        cursor = editor.textCursor()
        self._prev_cursor = cursor
        selection = QTextEdit.ExtraSelection()
        back = Qt.white  # selection.format.background().color()
        fore = Qt.gray   # selection.format.foreground().color()
        selection.format.setBackground(fore)
        selection.format.setForeground(back)
        selection.cursor = editor.textCursor()
        selection.cursor.movePosition(QTextCursor.StartOfLine)
        selection.cursor.movePosition(QTextCursor.Down,
                                      QTextCursor.KeepAnchor)
        editor.set_extra_selections('vim_visual', [selection])
        editor.update_extra_selections()

    # TODO: CTRL + V sets visual mode to 'block'


# %% Vim commands
class VimCommands(object):
    def __init__(self, widget):
        self._widget = widget

    def __call__(self, cmd):
        if not cmd or cmd.startswith("_"):
            return
        cmd = cmd.split(None, 1)
        args = cmd[1] if len(cmd) > 1 else ""
        cmd = cmd[0]

        if cmd.isdigit():
            self.NUMBER(cmd)
        else:
            try:
                method = self.__getattribute__(cmd)
            except AttributeError:
                print("unknown command", cmd)
            else:
                method(args)

    # %% Files
    def w(self, args=""):
        self._widget.main.editor.save_action.trigger()
        self._widget.commandline.setFocus()

    def q(self, args=""):
        self._widget.main.editor.close_action.trigger()
        self._widget.commandline.setFocus()

    def wq(self, args=""):
        self.w(args)
        self.q()

    def n(self, args=""):
        self._widget.main.editor.new_action.trigger()
        self._widget.commandline.setFocus()

    def e(self, args=""):
        if not args:  # Revert without asking
            editor = self._widget.main.editor
            editorstack = editor.get_current_editorstack()
            editorstack.reload(editorstack.get_stack_index())
        elif args == ".":
            self._widget.main.editor.open_action.trigger()
        else:
            print("not implemented")

        self._widget.commandline.setFocus()

    def NUMBER(self, args=""):
        editor = self._widget.editor()
        editor.go_to_line(int(args))
        self._widget.update_vim_cursor()


# %%
class VimLineEdit(QLineEdit):
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            if self.parent().vim_keys.visual_mode:
                self.parent().vim_keys.exit_visual_mode()
            self.clear()
        elif event.key() == Qt.Key_Backspace:
            self.setText(self.text() + "\b")
        elif event.key() == Qt.Key_Return:
            self.setText(self.text() + "\r")
            self.parent().on_return()
        else:
            QLineEdit.keyPressEvent(self, event)

    def focusInEvent(self, event):
        QLineEdit.focusInEvent(self, event)
        self.parent().vim_keys.h()
        self.clear()

    def focusOutEvent(self, event):
        QLineEdit.focusOutEvent(self, event)
        self.parent().editor().clear_extra_selections('vim_cursor')
        if self.parent().vim_keys.visual_mode:
            self.parent().vim_keys.exit_visual_mode()


class VimWidget(QWidget):
    """
    Vim widget
    """
    def __init__(self, editor_widget):
        self.editor_widget = editor_widget
        QLineEdit.__init__(self, editor_widget)

        # Build widget
        self.commandline = VimLineEdit(self)
        self.commandline.textChanged.connect(self.on_text_changed)
        self.commandline.returnPressed.connect(self.on_return)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        hlayout = QHBoxLayout()
        hlayout.addWidget(QLabel("Vim:"))
        hlayout.addWidget(self.commandline)
        hlayout.setContentsMargins(1, 1, 1, 1)
        self.setLayout(hlayout)
        self.selection_type = (int(time()), "char")
        QApplication.clipboard().dataChanged.connect(self.on_copy)

        # Initialize available commands
        self.vim_keys = VimKeys(self)
        self.vim_commands = VimCommands(self)

    def on_text_changed(self, text):
        if not text or text[0] in VIM_COMMAND_PREFIX:
            return
        print(text)
        if text.startswith("0"):
            # Special case to simplify regexp
            repeat, key, leftover = 1, "0", text[1:]
        elif text.startswith("G"):
            repeat, key, leftover = -1, "G", text[1:]
        else:
            if self.vim_keys.visual_mode:
                match = RE_VIM_VISUAL_PREFIX.match(text)
            else:
                match = RE_VIM_PREFIX.match(text)
            if not match:
                return
            repeat, key, leftover = match.groups()
            repeat = int(repeat) if repeat else 1
        if self.vim_keys.visual_mode and len(key) == 1:
            if key not in VIM_VISUAL_OPS:
                print("unknown key")
                self.commandline.setText(leftover)
                return
        self.vim_keys(key, repeat)
        self.commandline.setText(leftover)

    def on_return(self):
        text = self.commandline.text()
        if not text:
            return
        cmd_type = text[0]
        print(text)
        if cmd_type == ":":  # Vim command
            self.vim_commands(text[1:])
        elif cmd_type == "!":  # Shell command
            pass
        elif cmd_type == "/":  # Forward search
            pass
        elif cmd_type == "?":  # Reverse search
            pass
        self.commandline.clear()

    def on_copy(self):
        cur_time = int(time())
        if cur_time != self.selection_type[0]:
            self.selection_type = (cur_time, "char")

    def editor(self):
        # Retrieve text of current opened file
        editorstack = self.editor_widget.get_current_editorstack()
        index = editorstack.get_stack_index()
        finfo = editorstack.data[index]
        return finfo.editor

    def update_vim_cursor(self):
        selection = QTextEdit.ExtraSelection()
        back = Qt.white  # selection.format.background().color()
        fore = Qt.black  # selection.format.foreground().color()
        selection.format.setBackground(fore)
        selection.format.setForeground(back)
        selection.cursor = self.editor().textCursor()
        selection.cursor.movePosition(QTextCursor.Right,
                                      QTextCursor.KeepAnchor)
        self.editor().set_extra_selections('vim_cursor', [selection])
        self.editor().update_extra_selections()
