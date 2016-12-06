# -*- coding: utf-8 -*-

from __future__ import (
    print_function, unicode_literals, absolute_import, division)

import re

from qtpy.QtWidgets import (QWidget, QLineEdit, QHBoxLayout, QTextEdit, QLabel,
                            QSizePolicy, QApplication)
from qtpy.QtGui import QTextCursor
from qtpy.QtCore import Qt


VIM_COMMAND_PREFIX = ":!/?"
VIM_PREFIX = "cdfFmrtTyzZ@'`\"<>"
RE_VIM_PREFIX_STR = r"^(\d*)([{prefixes}].|[^{prefixes}0123456789])(.*)$"
RE_VIM_PREFIX = re.compile(RE_VIM_PREFIX_STR.format(prefixes=VIM_PREFIX))
SYMBOLS_REPLACEMENT = {
    "!": "EXCLAMATION",
    "?": "QUESTION",
    "<": "LESS",
    ">": "GREATER",
    "|": "PIPE",
    " ": "SPACE",
    "@": "AT",
    "$": "DOLLAR",
    "0": "ZERO",
}


# %% Vim shortcuts
class VimKeys(object):
    def __init__(self, widget):
        self._widget = widget

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
        editor = self._widget.editor()
        cursor = editor.textCursor()
        cursor.movePosition(movement, n=repeat)
        editor.setTextCursor(cursor)
        self._widget.update_vim_cursor()

    # %% Movement
    def h(self, repeat=1):
        # TODO: stop at start of line
        self._move_cursor(QTextCursor.Left, repeat)

    def j(self, repeat=1):
        self._move_cursor(QTextCursor.Down, repeat)

    def k(self, repeat=1):
        self._move_cursor(QTextCursor.Up, repeat)

    def l(self, repeat=1):
        # TODO: stop at end of line
        self._move_cursor(QTextCursor.Right, repeat)

    def w(self, repeat=1):
        self._move_cursor(QTextCursor.NextWord, repeat)

    def SPACE(self, repeat=1):
        self._move_cursor(QTextCursor.Right, repeat)

    def DOLLAR(self, repeat=1):
        self._move_cursor(QTextCursor.EndOfLine)

    def ZERO(self, repeat=1):
        self._move_cursor(QTextCursor.StartOfLine)

    def G(self, repeat):
        editor = self._widget.editor()
        editor.go_to_line(repeat)
        self._widget.update_vim_cursor()

    # %% Insertion
    def i(self, repeat):
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

    # %% Editing
    def u(self, repeat):
        for count in range(repeat):
            self._widget.editor().undo()
        self._widget.update_vim_cursor()

    # %% Deletions
    def dd(self, repeat):
        editor = self._widget.editor()
        cursor = editor.textCursor()
        cursor.movePosition(QTextCursor.StartOfLine)
        cursor.movePosition(QTextCursor.Down, QTextCursor.KeepAnchor, repeat)
        editor.setTextCursor(cursor)
        editor.cut()
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
    def yy(self, repeat):
        editor = self._widget.editor()
        cursor = editor.textCursor()
        cursor.movePosition(QTextCursor.StartOfLine)
        cursor.movePosition(QTextCursor.Down, QTextCursor.KeepAnchor, repeat)
        text = cursor.selectedText()
        QApplication.clipboard().setText(text)

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

    def p(self, repeat=1):
        editor = self._widget.editor()
        cursor = editor.textCursor()
        text = QApplication.clipboard().text()
        lines = text.splitlines(True)
        if len(lines) == 1 and text.endswith(('\u2029', '\u2028', '\n', '\r')):
            startPosition = cursor.block().position()
            indentSize = len(text) - len(text.lstrip())
            text = "\n" + text.rstrip()
            text *= repeat
            cursor.movePosition(QTextCursor.EndOfLine)
            cursor.insertText(text)
            cursor.setPosition(startPosition)
            editor.setTextCursor(cursor)
            if indentSize:
                self.l(indentSize)
            self.j()
        else:
            self.l()
            self.P(repeat)

    def P(self, repeat):
        editor = self._widget.editor()
        cursor = editor.textCursor()
        text = QApplication.clipboard().text()
        lines = text.splitlines(True)
        if len(lines) == 1 and text.endswith(('\u2029', '\u2028', '\n', '\r')):
            cursor.movePosition(QTextCursor.StartOfLine)
            startPosition = cursor.position()
            indentSize = len(text) - len(text.lstrip())
            text *= repeat
            cursor.insertText(text)
            cursor.setPosition(startPosition)
            editor.setTextCursor(cursor)
            if indentSize:
                self.l(indentSize)
            self._widget.update_vim_cursor()
        elif len(lines) > 1:
            startPosition = cursor.position()
            text = text.lstrip()
            text *= repeat
            cursor.insertText(text)
            cursor.setPosition(startPosition)
            editor.setTextCursor(cursor)
            self._widget.update_vim_cursor()
        else:
            for i in range(repeat):
                editor.paste()

    # %% Files
    def ZZ(self, repeat):
        self._widget.main.editor.save_action.trigger()
        self._widget.main.editor.close_action.trigger()
        self._widget.commandline.setFocus()


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
            self.clear()
        else:
            QLineEdit.keyPressEvent(self, event)

    def focusInEvent(self, event):
        QLineEdit.focusInEvent(self, event)
        self.parent().update_vim_cursor()
        self.clear()

    def focusOutEvent(self, event):
        QLineEdit.focusOutEvent(self, event)
        self.parent().editor().clear_extra_selections('vim_cursor')


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
        else:
            match = RE_VIM_PREFIX.match(text)
            if not match:
                return
            repeat, key, leftover = match.groups()
            repeat = int(repeat) if repeat else 1
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
