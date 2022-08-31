# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Copyright © 2022, spyder-vim
#
# Licensed under the terms of the MIT license
# ----------------------------------------------------------------------------
"""
spyder-vim Main Widget.
"""
import re
import bisect
from time import time

from qtpy.QtWidgets import (QWidget, QLineEdit, QHBoxLayout, QTextEdit, QLabel,
                            QSizePolicy, QApplication)
from qtpy.QtGui import QTextCursor, QTextDocument
from qtpy.QtCore import Qt, QObject, QRegularExpression, Signal, QPoint

# Spyder imports
from spyder.config.gui import is_dark_interface
from spyder.api.translations import get_translation

# Localization
_ = get_translation("spyder_vim.spyder")


VIM_COMMAND_PREFIX = ":!/?"
VIM_PREFIX = "acdfFgmritTyzZ@'`\"<>"
RE_VIM_PREFIX_STR = r"^(\d*)([{prefixes}].|[^{prefixes}0123456789])(.*)$"
RE_VIM_PREFIX = re.compile(RE_VIM_PREFIX_STR.format(prefixes=VIM_PREFIX))

VIM_VISUAL_OPS = "bdehHjJklLnNpPGyw$^0 \r\b%~<>"
VIM_VISUAL_PREFIX = "agi"
VIM_ARG_PREFIX = "fFr\""

RE_VIM_VISUAL_PREFIX = re.compile(
    RE_VIM_PREFIX_STR.format(prefixes=VIM_VISUAL_PREFIX))

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
    "^": "CARET",
    "\"": "QUOTE",
    "%": "PERCENT",
    "~": "TILDE"
}
INDENT = "    "


# %% Vim shortcuts
class VimKeys(QObject):
    """Wrap Vim command actions."""

    mode_changed = Signal(str)
    def __init__(self, widget):
        """Main commands constructor."""
        QObject.__init__(self)
        self._widget = widget
        self._prev_cursor = None
        self.visual_mode = False
        self.search_dict = {}
        self.registers = {}
        for i in range(10):
            self.registers[str(i)] = ""
        self.registers["unnamed"] = ("", False)
        self.register = "unnamed"

    def __call__(self, key, repeat):
        """Execute vim command."""
        leftover = ""
        if key.startswith("_"):
            return
        elif key[0] in "fFr":
            leftover = key[1]
            key = key[0]
        elif key[0] in "ia" and self.visual_mode == "char":
            leftover = key[1]
            key = key[0]
        elif key[0] == "\"":
            leftover = key[1]
            key = key[0]
        for symbol, text in SYMBOLS_REPLACEMENT.items():
            key = key.replace(symbol, text)
        try:
            method = self.__getattribute__(key)
        except AttributeError:
            print("unknown key", key)
        else:
            if leftover:
                method(leftover, repeat)
            else:
                method(repeat=repeat)

    def QUOTE(self, leftover, repeat=1):
        """Set the register value"""
        self.register = leftover

    def set_register(self, text, mode, register="unnamed", cut=False):
        """Set the register value inside the dictionary of registers."""
        # Delete and small delete registers
        if cut and (mode == "line" or text.find("\n") != -1):
            for i in reversed(range(2, 9)):
                self.registers[str(i)] = self.registers[str(i-1)] 
            self.registers["1"] = (text, mode) 
        else:
            self.registers["0"] = (text, mode)
            self.registers["-"] = (text, mode) 
            pass
        # General register
        if register in [str(i) for i in range(10)]:
            pass
        elif register in [".", "%", "#" ":"]:
            pass # To implement
        elif register.islower():
            self.registers[register] = (text, mode) 
        elif register.isupper():
            previous_text, _ = self.get_register(register.lower())
            self.registers[register.lower()] = (previous_text + text, mode) 
        self.registers["unamed"] = (text, mode) 
        self.register = "unnamed"

    def get_register(self, register="unnamed"):
        """Get the register from the dictionary of registers."""
        if register in self.registers:
            text, mode = self.registers[str(register)]
        else:
            text = ""
            mode = False
        self.register = "unnamed"
        return text, mode

    def _move_cursor(self, movement, repeat=1):
        cursor = self._editor_cursor()
        cursor.movePosition(movement, n=repeat)
        self._widget.editor().setTextCursor(cursor)
        self._widget.update_vim_cursor()

    def _set_cursor(self, pos, mode=QTextCursor.KeepAnchor):
        cursor = self._editor_cursor()
        cursor.setPosition(pos, mode)
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
            cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor,
                                n=lines)
            line = cursor.selectedText().replace('\u2029', '\n')
            line += '\n'
            return line

    def _update_selection_type(self, selection_type):
        cur_time = int(time())
        self._widget.selection_type = (cur_time, selection_type)

    def exit_visual_mode(self):
        """Exit visual mode."""
        self.mode_changed.emit("normal")
        editor = self._widget.editor()
        editor.clear_extra_selections('vim_visual')
        self._widget.update_vim_cursor()
        self.visual_mode = False

    def exit_insert_mode(self):
        """Exit insert mode."""
        self.mode_changed.emit("normal")
        editor = self._widget.editor()
        cursor = self._editor_cursor()
        editor.clear_extra_selections('vim_visual')
        if cursor.atBlockEnd():
           self.h()
        self._widget.update_vim_cursor()

    def search(self, key, reverse=False):
        """"Search regular expressions key inside document"""
        editor = self._widget.editor()
        cursor = QTextCursor(editor.document())
        cursor.movePosition(QTextCursor.Start)
        # Find key in document forward
        search_stack = []
        cursor = editor.document().find(QRegularExpression(key),
                        options=QTextDocument.FindCaseSensitively)
        selection = QTextEdit.ExtraSelection()
        back = Qt.black
        fore = Qt.blue
        while not cursor.isNull():
            selection = QTextEdit.ExtraSelection()
            selection.format.setBackground(fore)
            selection.format.setForeground(back)
            selection.cursor = cursor
            search_stack.append(selection)
            cursor = editor.document().find(QRegularExpression(key), cursor,
                                        QTextDocument.FindCaseSensitively)
        editor.set_extra_selections('search', [i for i in search_stack])
        search_dict = {"stack": search_stack, "reverse": reverse}
        return search_dict

    def n(self, repeat=1, reverse=False):
        """Move cursor to the next searched key"""
        cursor = self._editor_cursor()
        search_stack = self.search_dict.get("stack", None)
        if not search_stack:
            return
        if not self.search_dict["reverse"]^reverse:
            place = bisect.bisect([i.cursor.selectionStart() 
                          for i in search_stack], cursor.position())
            if place == len(search_stack):
                self._set_cursor(search_stack[0].cursor.selectionStart(),
                                 QTextCursor.MoveAnchor)
            else:
                self._set_cursor(search_stack[place].cursor.selectionStart(),
                                 QTextCursor.MoveAnchor)
        else:
            place = bisect.bisect_left([i.cursor.selectionStart() 
                          for i in search_stack], cursor.position())
            if place == 0:
                self._set_cursor(search_stack[-1].cursor.selectionStart(),
                                 QTextCursor.MoveAnchor)
            else:
                self._set_cursor(search_stack[place-1].cursor.selectionStart(),
                                QTextCursor.MoveAnchor)
        if repeat > 1:
            self.n(repeat - 1, reverse=reverse)

    def N(self, repeat=1):
        """Move cursor to the previous searched key"""
        self.n(repeat, reverse=True)

    # %% Movement
    def h(self, repeat=1):
        """Move cursor to the left."""
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
                self.h(repeat - 1)

    def j(self, repeat=1):
        """Move cursor down."""
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
        else:
            line = self._get_line(cursor)
            if line != '\n' and cursor.atBlockEnd():
                self._move_cursor(QTextCursor.Left)

    def k(self, repeat=1):
        """Move the cursor up."""
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
            if start == 0:
                pass
            elif cursor.position() < start:
                self._move_selection(cur_block.position(), move_start=True)
            else:
                self._move_selection(cur_block.next().position())
        else:
            line = self._get_line(cursor)
            if line != '\n' and cursor.atBlockEnd():
                self._move_cursor(QTextCursor.Left)

    def l(self, repeat=1):  # analysis:ignore
        """Move cursor to the right."""
        cursor = self._editor_cursor()
        if self.visual_mode == 'char':
            if not cursor.atBlockEnd():
                prev_cursor_pos = self._prev_cursor.position()
                start, end = self._get_selection_positions()
                if cursor.position() >= \
                   prev_cursor_pos:
                    self._move_selection(end + 1)
                else:
                    self._move_selection(start + 1, move_start=True)
                self._move_cursor(QTextCursor.Right)
        else:
            self._move_cursor(QTextCursor.Right)
            cursor = self._editor_cursor()
            if cursor.atBlockEnd():
                self._move_cursor(QTextCursor.Left)
        if repeat > 1:
            self.l(repeat - 1)

    def w(self, repeat=1):
        """Move to the next word."""
        self._move_cursor(QTextCursor.NextWord)
        cursor = self._editor_cursor()
        if cursor.atBlockEnd():
            self._move_cursor(QTextCursor.NextWord)
        if self.visual_mode == 'char':
            cursor = self._editor_cursor()
            self._move_selection(cursor.position())
        if repeat > 1:
            self.w(repeat - 1)

    def b(self, repeat=1):
        """Move to the previous word."""
        self._move_cursor(QTextCursor.PreviousWord)
        cursor = self._editor_cursor()
        if cursor.atBlockEnd():
            self._move_cursor(QTextCursor.PreviousWord)
        if self.visual_mode == 'char':
            cursor = self._editor_cursor()
            self._move_selection(cursor.position(), move_start=True)
        if repeat > 1:
            self.b(repeat - 1)

    def e(self, repeat=1):
        """Go to end of current word.

        Or go to end of next word if cursor is currently on whitespace.
        """
        cursor = self._editor_cursor()
        cur_pos_in_block = cursor.positionInBlock()
        char = self._get_line(cursor)[cur_pos_in_block:cur_pos_in_block + 2]
        if not char.isalnum():
            self.w(repeat=1)
        self._move_cursor(QTextCursor.EndOfWord)
        self.h(repeat=1)
        if self.visual_mode == 'char':
            cursor = self._editor_cursor()
            self._move_selection(cursor.position())
        if repeat > 1:
            self.e(repeat - 1)

    def f(self, leftover, repeat=1):
        """Go to the next ocurrence of a character."""
        cursor = self._editor_cursor()
        cur_pos_in_block = cursor.positionInBlock()
        text = self._get_line(cursor)[cur_pos_in_block + 1:]
        char_indices = []
        for i, char in enumerate(text):
            if char == leftover:
                char_indices.append(cur_pos_in_block + i + 1)
        try:
            index = char_indices[repeat - 1]
            self.l(repeat=index - cur_pos_in_block)
        except IndexError:
            pass

    def F(self, leftover, repeat=1):
        """Go to the previous ocurrence of a character."""
        cursor = self._editor_cursor()
        cur_pos_in_block = cursor.positionInBlock()
        text = self._get_line(cursor)[:cur_pos_in_block]
        char_indices = []
        for i, char in enumerate(text):
            if char == leftover:
                char_indices.append(i)
        try:
            index = char_indices[-repeat]
            self.h(repeat=cur_pos_in_block - index)
        except IndexError:
            pass

    def r(self, leftover, repeat=1):
        """Replace the character under the cursor with character of argument."""
        editor = self._widget.editor()
        cursor = self._editor_cursor()

        if self.visual_mode:
            cur_pos, end_pos = self._get_selection_positions()
            if self.visual_mode == 'char':
                end_pos += 1
        else:
            cur_pos = cursor.position()
            cursor.movePosition(QTextCursor.EndOfBlock)
            line_end_pos = cursor.position()
            if line_end_pos - cur_pos < repeat:
                self._widget.update_vim_cursor()
                return
            end_pos = cur_pos + repeat

        cursor.setPosition(cur_pos)
        cursor.setPosition(end_pos, QTextCursor.KeepAnchor)
        text = cursor.selectedText().replace('\u2029', '\n')
        text_sub = re.sub(r'.', leftover, text)
        cursor.insertText(text_sub)

        if self.visual_mode:
            self.exit_visual_mode()
            cursor.setPosition(cur_pos)
            editor.setTextCursor(cursor)
        else:
            self.h(1)

        self._widget.update_vim_cursor()

    def SPACE(self, repeat=1):
        """Move cursor to the right."""
        self._move_cursor(QTextCursor.Right, repeat)
        editor = self._widget.editor()
        cursor = editor.textCursor()
        if (self.visual_mode == 'char'):
            start, end = self._get_selection_positions()
            if cursor.position() < start:
                self._move_selection(cursor.position(), move_start=True)
            else:
                self._move_selection(cursor.position())
        else:
            if cursor.atBlockEnd():
                self._move_cursor(QTextCursor.Right, repeat)

    def BACKSPACE(self, repeat=1):
        """Move cursor to the left."""
        self._move_cursor(QTextCursor.Left, repeat)
        editor = self._widget.editor()
        cursor = editor.textCursor()
        if (self.visual_mode == 'char'):
            start, end = self._get_selection_positions()
            if cursor.position() < start:
                self._move_selection(cursor.position(), move_start=True)
            else:
                self._move_selection(cursor.position())
        else:
            if cursor.atBlockEnd():
                self._move_cursor(QTextCursor.Left, repeat)

    def RETURN(self, repeat=1):
        """Move to the start of the next line."""
        self._move_cursor(QTextCursor.Down, repeat)
        self._move_cursor(QTextCursor.StartOfLine, repeat)
        editor = self._widget.editor()
        cursor = editor.textCursor()
        if (self.visual_mode == 'char'):
            start, end = self._get_selection_positions()
            if cursor.position() < start:
                self._move_selection(cursor.position(), move_start=True)
            else:
                self._move_selection(cursor.position())

    def DOLLAR(self, repeat=1):
        """Go to the end of the current line."""
        self._move_cursor(QTextCursor.EndOfLine)
        if (self.visual_mode == 'char'):
            editor = self._widget.editor()
            cursor = editor.textCursor()
            start, end = self._get_selection_positions()
            if cursor.position() < start:
                self._move_selection(cursor.position(), move_start=True)
            else:
                self._move_selection(cursor.position())
        else:
            self._move_cursor(QTextCursor.Left)

    def ZERO(self, repeat=1):
        """Go to the start of the current line."""
        self._move_cursor(QTextCursor.StartOfLine)
        if (self.visual_mode == 'char'):
            editor = self._widget.editor()
            cursor = editor.textCursor()
            start, end = self._get_selection_positions()
            if cursor.position() < start:
                self._move_selection(cursor.position(), move_start=True)
            else:
                self._move_selection(cursor.position())

    def CARET(self, repeat=1):
        """Go to the first non-blank character of the line."""
        editor = self._widget.editor()
        cursor = editor.textCursor()
        text = self._get_line(cursor)
        if text.strip():
            start_of_line = len(text) - len(text.lstrip())
            cursor.setPosition(cursor.block().position() + start_of_line)
            editor.setTextCursor(cursor)
            self._widget.update_vim_cursor()
        if (self.visual_mode == 'char'):
            editor = self._widget.editor()
            cursor = editor.textCursor()
            start, end = self._get_selection_positions()
            if cursor.position() < start:
                self._move_selection(cursor.position(), move_start=True)
            else:
                self._move_selection(cursor.position())

    def G(self, repeat=-1):
        """Go to the first non-blank character of the last line."""
        if repeat == -1:
            self._move_cursor(QTextCursor.End)
            if self.visual_mode:
                self._move_selection(self._editor_cursor().position())
        else:
            self.gg(repeat)

    def gg(self, repeat=1):
        """Go to the first position of the first line."""
        editor = self._widget.editor()
        editor.go_to_line(repeat)
        self._widget.update_vim_cursor()
        if self.visual_mode:
            start, stop = self._get_selection_positions()
            cursor = self._editor_cursor()
            cur_block = cursor.block()
            if cursor.position() < start:
                if self.visual_mode == 'line':
                    self._move_selection(cursor.position(), move_start=True)
                else:
                    self._move_selection(cur_block.position(), move_start=True)
            else:
                if self.visual_mode == 'line':
                    self._move_selection(cur_block.next().position())
                else:
                    self._move_selection(cursor.position())

    def zz(self, repeat=1):
        """Center the current line"""
        editor = self._widget.editor()
        line, _ = editor.get_cursor_line_column()
        editor.go_to_line(line + 1)
        self._widget.update_vim_cursor()

    def H(self, repeat=1):
        """Move cursor to the top of the page"""
        editor = self._widget.editor()
        position = editor.cursorForPosition(QPoint(0, 0)).position()
        self._set_cursor(position, mode=QTextCursor.MoveAnchor)

    def L(self, repeat=1):
        """Move cursor to the bottom of the page"""
        editor = self._widget.editor()
        position = editor.cursorForPosition(QPoint(0, editor.viewport().height())).position()
        self._set_cursor(position, mode=QTextCursor.MoveAnchor)

    def M(self, repeat=1):
        """Move cursor to the middle of the page"""
        editor = self._widget.editor()
        position = editor.cursorForPosition(QPoint(0, int((editor.viewport().height())*0.5))).position()
        self._set_cursor(position, mode=QTextCursor.MoveAnchor)

    def PERCENT(self, repeat=1):
        """Go to matching bracket"""
        editor = self._widget.editor()
        cursor = self._editor_cursor()
        text = editor.toPlainText()
        position = cursor.position()
        # Find starting position      
        start_position = -1
        for i, j in enumerate(text[position::]):
            if j in list("([{"):
                start_char = j
                start_position = i + position + 1
                sub_text = text[start_position::]
                break
            elif j in list(")]}"):
                start_char = j
                start_position = i + position
                sub_text = reversed(text[0:start_position])
                break
        if start_position == -1:
            return
        # Find final position      
        end_position = -1
        stack = [start_char]
        for i, j in enumerate(sub_text):
            if j == "(" and stack[-1] == ")":
                stack.pop()
            elif j == "[" and stack[-1] == "]":
                stack.pop()
            elif j == "{" and stack[-1] == "}":
                stack.pop()
            elif j == ")" and stack[-1] == "(":
                stack.pop()
            elif j == "]" and stack[-1] == "[":
                stack.pop()
            elif j == "}" and stack[-1] == "{":
                stack.pop()
            elif j in list("([{)]}"):
                stack.append(j)
            if not stack and start_char in list("([{"):
                end_position = start_position + i 
                break
            elif not stack and start_char in list(")]}"):
                end_position = start_position - i - 1
                break
        if end_position == -1:
            return
        # Move cursor
        if self.visual_mode == 'char':
            selection = editor.get_extra_selections('vim_visual')[0]
            if position > end_position:
                selection.cursor.setPosition(position+1)
                selection.cursor.setPosition(end_position - 1,
                                             QTextCursor.KeepAnchor)
            else:
                selection.cursor.setPosition(position)
                selection.cursor.setPosition(end_position,
                                             QTextCursor.KeepAnchor)
            editor.set_extra_selections('vim_visual', [selection])
            self._set_cursor(end_position)
        else:
            self._set_cursor(end_position, mode=QTextCursor.MoveAnchor)

    # %% Insertion
    def i(self, leftover=None, repeat=1):
        """Insert text before the cursor."""
        if leftover is None:
            self._widget.editor().setFocus()
        elif leftover in list("\"\'([{<>}])"):
            editor = self._widget.editor()
            cursor = self._editor_cursor()
            text = editor.toPlainText()
            position = cursor.position()
            # Find the starting position
            start_position = -1
            if leftover == "(":
                leftover = ")"
            elif leftover == "[":
                leftover = "]"
            elif leftover == "{":
                leftover = "}"
            elif leftover == "<":
                leftover = ">"
            stack = []
            stack.append(leftover)
            for i, j in enumerate(reversed(text[0:position])):
                if j == "(" and stack[-1] == ")":
                    stack.pop()
                elif j == "[" and stack[-1] == "]":
                    stack.pop()
                elif j == "{" and stack[-1] == "}":
                    stack.pop()
                elif j == "\"" and stack[-1] == "\"":
                    stack.pop()
                elif j == "\'" and stack[-1] == "\'":
                    stack.pop()
                elif j == "<" and stack[-1] == ">":
                    stack.pop()
                elif j in list(")]}>\"\'"):
                    stack.append(j)
                if not stack:
                     start_position = len(text[0:position]) - i
                     break
            if start_position == -1:
                return

            # Find the matching character
            if leftover == ")":
                leftover = "("
            elif leftover == "]":
                leftover = "["
            elif leftover == "}":
                leftover = "{"
            elif leftover == ">":
                leftover = "<"
            stack = []
            stack.append(leftover)
            end_position = -1
            for i, j in enumerate(text[start_position::]):
                if j == ")" and stack[-1] == "(":
                    stack.pop()
                elif j == "]" and stack[-1] == "[":
                    stack.pop()
                elif j == "}" and stack[-1] == "{":
                    stack.pop()
                elif j == "\"" and stack[-1] == "\"":
                    stack.pop()
                elif j == "\'" and stack[-1] == "\'":
                    stack.pop()
                elif j == ">" and stack[-1] == "<":
                    stack.pop()
                elif j in list("([{<\"\'"):
                    stack.append(j)
                if not stack:
                     end_position = i + start_position - 1
                     break

            selection = editor.get_extra_selections('vim_visual')[0]
            selection.cursor.setPosition(start_position)
            selection.cursor.setPosition(end_position,
                                             QTextCursor.KeepAnchor)
            editor.set_extra_selections('vim_visual', [selection])
            self._set_cursor(end_position)


            

    def I(self, repeat):
        """Insert text before the first non-blank in the line."""
        self._move_cursor(QTextCursor.StartOfLine)
        self._widget.editor().setFocus()

    def a(self, leftover=None, repeat=1):
        """Append text after the cursor."""
        if not leftover:
            cursor = self._editor_cursor()
            line = self._get_line(cursor)
            if line != '\n':
                self._move_cursor(QTextCursor.Right)
            self._widget.editor().setFocus()
        elif leftover in list("\"\'([{<>}])"):
            editor = self._widget.editor()
            cursor = self._editor_cursor()
            text = editor.toPlainText()
            position = cursor.position()
            # Find the starting position
            start_position = -1
            if leftover == "(":
                leftover = ")"
            elif leftover == "[":
                leftover = "]"
            elif leftover == "{":
                leftover = "}"
            elif leftover == "<":
                leftover = ">"
            stack = []
            stack.append(leftover)
            for i, j in enumerate(reversed(text[0:position])):
                if j == "(" and stack[-1] == ")":
                    stack.pop()
                elif j == "[" and stack[-1] == "]":
                    stack.pop()
                elif j == "{" and stack[-1] == "}":
                    stack.pop()
                elif j == "\"" and stack[-1] == "\"":
                    stack.pop()
                elif j == "\'" and stack[-1] == "\'":
                    stack.pop()
                elif j == "<" and stack[-1] == ">":
                    stack.pop()
                elif j in list(")]}>\"\'"):
                    stack.append(j)
                if not stack:
                     start_position = len(text[0:position]) - i
                     break
            if start_position == -1:
                return

            # Find the matching character
            if leftover == ")":
                leftover = "("
            elif leftover == "]":
                leftover = "["
            elif leftover == "}":
                leftover = "{"
            elif leftover == ">":
                leftover = "<"
            stack = []
            stack.append(leftover)
            end_position = -1
            for i, j in enumerate(text[start_position::]):
                if j == ")" and stack[-1] == "(":
                    stack.pop()
                elif j == "]" and stack[-1] == "[":
                    stack.pop()
                elif j == "}" and stack[-1] == "{":
                    stack.pop()
                elif j == "\"" and stack[-1] == "\"":
                    stack.pop()
                elif j == "\'" and stack[-1] == "\'":
                    stack.pop()
                elif j == ">" and stack[-1] == "<":
                    stack.pop()
                elif j in list("([{<\"\'"):
                    stack.append(j)
                if not stack:
                     end_position = i + start_position - 1
                     break

            selection = editor.get_extra_selections('vim_visual')[0]
            selection.cursor.setPosition(start_position-1)
            selection.cursor.setPosition(end_position+1,
                                             QTextCursor.KeepAnchor)
            editor.set_extra_selections('vim_visual', [selection])
            self._set_cursor(end_position+1)

    def A(self, repeat):
        """Append text at the end of the line."""
        self._move_cursor(QTextCursor.EndOfLine)
        self._widget.editor().setFocus()

    def o(self, repeat):
        """Begin a new line below the cursor and insert text."""
        editor = self._widget.editor()
        cursor = editor.textCursor()
        cursor.movePosition(QTextCursor.EndOfLine)
        cursor.insertText("\n")
        editor.setTextCursor(cursor)
        editor.setFocus()
        self._widget.update_vim_cursor()

    def O(self, repeat):
        """Begin a new line above the cursor and insert text."""
        editor = self._widget.editor()
        cursor = editor.textCursor()
        cursor.movePosition(QTextCursor.StartOfLine)
        cursor.insertText("\n")
        cursor.movePosition(QTextCursor.Up)
        editor.setTextCursor(cursor)
        editor.setFocus()
        self._widget.update_vim_cursor()

    # %% Editing and cases(visual)
    def u(self, repeat):
        """Undo changes."""
        if not self.visual_mode:
            for count in range(repeat):
                self._widget.editor().undo()
            self._widget.update_vim_cursor()
        else:
            # TODO: make selection lowercase
            pass

    def U(self, repeat):
        """Undo all latest changes on one line."""
        if self.visual_mode:
            # TODO: make selection uppercase
            pass

    # %% Deletions
    def d(self, repeat):
        editor = self._widget.editor()
        selection = editor.get_extra_selections('vim_visual')[0]
        cursor = selection.cursor
        if self.visual_mode == 'char':
            cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor)
            self._update_selection_type('char')
        elif self.visual_mode == 'line':
            self._update_selection_type('line')
        else:
            self._update_selection_type('block')
        text = cursor.selectedText().replace('\u2029', '\n')
        self.set_register(text, self._widget.selection_type[1], register=self.register, cut=True)
        self.register = "unnamed"
        editor.setTextCursor(cursor)
        editor.cut()
        self.exit_visual_mode()

    def dd(self, repeat):
        """Delete line."""
        editor = self._widget.editor()
        cursor = editor.textCursor()
        cursor.movePosition(QTextCursor.StartOfLine)
        if not cursor.movePosition(QTextCursor.Down, QTextCursor.KeepAnchor, repeat):
            cursor.movePosition(QTextCursor.Up)
            cursor.movePosition(QTextCursor.EndOfLine)
            cursor.movePosition(QTextCursor.End, QTextCursor.KeepAnchor, repeat)
        text = cursor.selectedText()
        self.set_register(text, "line", register=self.register, cut=True)
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

    def cc(self, repeat):
        """Delete line then insert"""
        self.dd(repeat)
        self.O(repeat=1)

    def D(self, repeat):
        """Delete the characters under the cursor until the end of the line."""
        editor = self._widget.editor()
        cursor = editor.textCursor()
        cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
        cursor.movePosition(QTextCursor.Down, QTextCursor.KeepAnchor,
                            repeat - 1)
        text = cursor.selectedText().replace('\u2029', '\n')
        self.set_register(text, self._widget.selection_type[1], register=self.register, cut=True)
        editor.setTextCursor(cursor)
        editor.cut()
        self.h()
        self._widget.update_vim_cursor()

    def J(self, repeat):
        """Join lines, with a minimum of two lines."""
        editor = self._widget.editor()
        cursor = editor.textCursor()
        n_block = editor.blockCount()

        if self.visual_mode:
            selection = editor.get_extra_selections('vim_visual')[0]

            cursor_pos_start, cursor_pos_end = self._get_selection_positions()
            cursor_pos_start, cursor_pos_end = sorted([cursor_pos_start,
                                                       cursor_pos_end])
            if self.visual_mode == 'line':
                cursor_pos_end -= 1

            selection.cursor.setPosition(cursor_pos_start)
            no_block_start = selection.cursor.blockNumber()

            selection.cursor.setPosition(cursor_pos_end)
            no_block_end = selection.cursor.blockNumber()

            self.exit_visual_mode()

            if no_block_start == no_block_end:
                no_block_end += 1

            cursor_pos_start = min([cursor_pos_start, cursor_pos_end])
        else:
            no_block_start = cursor.blockNumber()
            no_block_end = cursor.blockNumber() + repeat
            cursor_pos_start = cursor.position()

        if no_block_end >= n_block - 1:
            no_block_end = n_block - 1

        if no_block_start == no_block_end:
            return

        n_line = no_block_end - no_block_start + 1
        text_list = ['']
        cursor.setPosition(cursor_pos_start)
        for _ in range(n_line - 1):
            cursor.movePosition(QTextCursor.NextBlock)
            text = cursor.block().text().lstrip()
            if text:
                text_list.append(text)

        # Replace text
        cursor.setPosition(cursor_pos_start)
        cursor.movePosition(QTextCursor.EndOfLine)
        cursor.movePosition(QTextCursor.NextBlock, QTextCursor.KeepAnchor,
                            n_line - 1)
        cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
        cursor.insertText(' '.join(text_list))

        # Move position of cursor
        cursor.movePosition(QTextCursor.EndOfBlock)
        cursor.movePosition(QTextCursor.Left, n=len(text_list[-1]) + 1)
        editor.setTextCursor(cursor)

        self._widget.update_vim_cursor()

    def _cut_word(self, repeat, move_operation):
        """Cut words."""
        editor = self._widget.editor()
        cursor = editor.textCursor()
        cursor.movePosition(move_operation, QTextCursor.KeepAnchor,
                            repeat)
        text = cursor.selectedText().replace('\u2029', '\n')
        self.set_register(text, self._widget.selection_type[1], register=self.register, cut=True)
        editor.setTextCursor(cursor)
        editor.cut()
        self._widget.update_vim_cursor()

    def dw(self, repeat):
        """Cut words."""
        self._cut_word(repeat, QTextCursor.NextWord)

    def cw(self, repeat):
        """Cut words and edit."""
        if repeat == 1:
            self._cut_word(repeat, QTextCursor.EndOfWord)
        else:
            self._cut_word(repeat-1, QTextCursor.NextWord)
            self._cut_word(1, QTextCursor.EndOfWord)
        self.i()

    def x(self, repeat):
        """Delete the character under cursor with delete from EndOfLine."""
        editor = self._widget.editor()
        cursor = editor.textCursor()
        cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, repeat)
        text = cursor.selectedText().replace('\u2029', '\n')
        break_index = text.find('\n')
        if break_index != -1:
            cursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor,
                           len(text)-break_index)
            text = cursor.selectedText().replace('\u2029', '\n')
            self.set_register(text, self._widget.selection_type[1], register=self.register, cut=True)
            editor.setTextCursor(cursor)
            editor.cut()
            self._move_cursor(QTextCursor.Left)
        else:
            editor.setTextCursor(cursor)
            editor.cut()
        cursor = editor.textCursor()
        cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, repeat)
        if cursor.selectedText().replace('\u2029', '\n') == '\n':
            self._move_cursor(QTextCursor.Left)
        self._widget.update_vim_cursor()

    # %% Copy
    def y(self, repeat):
        """Copy selected line."""
        editor = self._widget.editor()
        selection = editor.get_extra_selections('vim_visual')[0]
        cursor = selection.cursor
        if self.visual_mode == 'char':
            cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor)
        text = cursor.selectedText().replace('\u2029', '\n')
        self.set_register(text, self.visual_mode, register=self.register)
        QApplication.clipboard().setText(text)
        cursor.setPosition(cursor.selectionStart())
        if self.visual_mode == 'char':
            self._update_selection_type('char')
            editor.setTextCursor(cursor)
            if text[0] == '\n':
                self._move_cursor(QTextCursor.Left)
        elif self.visual_mode == 'line':
            self._update_selection_type('line')
            editor.setTextCursor(cursor)
            self._move_cursor(QTextCursor.StartOfLine)
        else:
            self._update_selection_type('block')
            self._move_cursor(QTextCursor.StartOfLine)
        self.exit_visual_mode()

    def yy(self, repeat):
        """Copy line."""
        cursor = self._editor_cursor()
        text = self._get_line(cursor, lines=repeat)
        QApplication.clipboard().setText(text)
        self._update_selection_type("line")
        self.set_register(text, self._widget.selection_type[1], register=self.register)

    def yw(self, repeat):
        """Copy word."""
        editor = self._widget.editor()
        cursor = editor.textCursor()
        cursor.movePosition(QTextCursor.NextWord, QTextCursor.KeepAnchor,
                            repeat - 1)
        cursor.movePosition(QTextCursor.EndOfWord, QTextCursor.KeepAnchor)
        text = cursor.selectedText().replace('\u2029', '\n')
        QApplication.clipboard().setText(text)
        self.set_register(text, self._widget.selection_type[1], register=self.register)

    def yDOLLAR(self, repeat):
        """Copy until end of line."""
        editor = self._widget.editor()
        cursor = editor.textCursor()
        cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor,
                            repeat)
        text = cursor.selectedText().replace('\u2029', '\n')
        QApplication.clipboard().setText(text)
        self.set_register(text, self._widget.selection_type[1], register=self.register)

    def p(self, repeat):
        """Paste line below current line, paste characters after cursor."""
        register = self.register
        __, selection_state = self.get_register(register=self.register)
        self.register = register
        if selection_state == 'line':
            self._move_cursor(QTextCursor.Down)
            self.P(repeat)
        elif selection_state == 'char':
            self._move_cursor(QTextCursor.Right)
            self.P(repeat)
        else:
            # TODO: implement pasting block text after implementing visual mode
            self.P()

    def P(self, repeat):
        """Paste line above current line, paste characters before cursor."""
        text, selection_state = self.get_register(register=self.register)
        lines = text.splitlines()
        mode_state = self.visual_mode
        if mode_state:
            self.d(1)
        editor = self._widget.editor()
        cursor = editor.textCursor()
        if selection_state == 'line':
            if not mode_state:
                text *= repeat
                startBlockPosition = cursor.block().position()
                cursor.movePosition(QTextCursor.StartOfLine)
                cursor.insertText(text)
                cursor.setPosition(startBlockPosition)
                if lines[0].strip():
                    cursor.movePosition(QTextCursor.NextWord)
                cursor.movePosition(QTextCursor.StartOfLine)
                editor.setTextCursor(cursor)
            elif mode_state == 'char':
                text *= repeat
                text = '\n' + text
                cursor.insertText(text)
            elif mode_state == 'line':
                text *= repeat
                cursor.insertText(text)

        elif selection_state == 'char':
            if mode_state == 'line':
                text = text + '\n'
            startPosition = cursor.position()
            for i in range(repeat):
                cursor.insertText(text)
            if len(lines) > 1 or mode_state == 'line':
                cursor.setPosition(startPosition)
                editor.setTextCursor(cursor)
            self.h()
        else:
            # TODO: implement pasting block text after implementing visual mode
            pass
        self._widget.update_vim_cursor()

    # %% Files
    def ZZ(self, repeat):
        """Save and close current file."""
        self._widget.main.editor.save_action.trigger()
        self._widget.main.editor.close_action.trigger()
        self._widget.commandline.setFocus()

    # %% Visual mode
    def v(self, repeat):
        """Start Visual mode per character."""
        self.mode_changed.emit("visual")
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

    def V(self, repeat):
        """Start Visual mode per line."""
        self.mode_changed.emit("vline")
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

    # TODO: CTRL + V sets visual mode to 'block'
    def gt(self, repeat):
        """Cycle to next file."""
        editorstack = self._widget.editor_widget.get_current_editorstack()
        if repeat == -1:
            editorstack.tabs.tab_navigate(1)
        else:  # {i}gt: go to tab in position i
            idx = repeat - 1
            if editorstack.get_stack_count() > idx:
                editorstack.set_stack_index(idx)
        self._widget.commandline.setFocus()

    def gT(self, repeat):
        """Cycle to previous file."""
        editorstack = self._widget.editor_widget.get_current_editorstack()
        for _ in range(repeat):
            editorstack.tabs.tab_navigate(-1)
        self._widget.commandline.setFocus()

    def TILDE(self, repeat):
        """
        Switch case of the character under the cursor
        and move the cursor to the right.
        """
        editor = self._widget.editor()
        cursor = self._editor_cursor()

        if self.visual_mode:
            cur_pos, end_pos = self._get_selection_positions()
        else:
            cur_pos = cursor.position()
            end_pos = cur_pos + repeat

            cursor.movePosition(QTextCursor.EndOfBlock)
            line_end_pos = cursor.position()
            if line_end_pos < end_pos:
                end_pos = line_end_pos

        cursor.setPosition(cur_pos)
        cursor.setPosition(end_pos, QTextCursor.KeepAnchor)
        text = cursor.selectedText()
        cursor.insertText(text.swapcase())

        if self.visual_mode:
            self.exit_visual_mode()
            cursor.setPosition(cur_pos)
            editor.setTextCursor(cursor)
        else:
            if cursor.atBlockEnd():
                self.h(1)

        self._widget.update_vim_cursor()

    def _get_selected_block_number(self, repeat=1):
        """Return selected block number."""
        editor = self._widget.editor()
        cursor = self._editor_cursor()
        if self.visual_mode:
            selection = editor.get_extra_selections('vim_visual')[0]

            cursor_pos_start, cursor_pos_end = self._get_selection_positions()
            cursor_pos_start, cursor_pos_end = sorted([cursor_pos_start,
                                                       cursor_pos_end])
            if self.visual_mode == 'line':
                cursor_pos_end -= 1

            selection.cursor.setPosition(cursor_pos_start)
            start_block_no = selection.cursor.blockNumber()

            selection.cursor.setPosition(cursor_pos_end)
            end_block_no = selection.cursor.blockNumber()
        else:
            start_block_no = cursor.block().blockNumber()
            end_block_no = start_block_no + repeat - 1
            if end_block_no >= editor.blockCount():
                end_block_no = editor.blockCount() - 1

        return start_block_no, end_block_no

    def _get_pos_of_block(self, block_no):
        """Return start position & end position of block."""
        editor = self._widget.editor()
        block = editor.document().findBlockByNumber(block_no)
        start_pos = block.position()
        end_pos = start_pos + block.length() - 1
        return start_pos, end_pos

    def _get_text_of_blocks(self, start_block_no, end_block_no):
        """Return text of blocks."""
        text_list = []
        editor = self._widget.editor()
        for no in range(start_block_no, end_block_no + 1):
            block = editor.document().findBlockByNumber(no)
            text_list.append(block.text())

        return text_list

    def GREATER(self, repeat=1):
        """Shift lines rightwards in visual mode."""
        cursor_pos_start, _ = self._get_selection_positions()
        start_block_no, end_block_no = self._get_selected_block_number(1)
        n_line = end_block_no - start_block_no + 1
        self.exit_visual_mode()

        editor = self._widget.editor()
        cursor = self._editor_cursor()
        cursor.setPosition(cursor_pos_start)
        editor.setTextCursor(cursor)

        self.GREATERGREATER(repeat=n_line)

    def GREATERGREATER(self, repeat=1):
        """Shift lines rightwards."""
        editor = self._widget.editor()
        cursor = self._editor_cursor()

        start_block_no, end_block_no = self._get_selected_block_number(repeat)
        cursor_start_pos, __ = self._get_pos_of_block(start_block_no)
        __, end_pos = self._get_pos_of_block(end_block_no)

        text_list = self._get_text_of_blocks(start_block_no, end_block_no)
        text_list_indent = []
        for text in text_list:
            if text:
                text_list_indent.append(INDENT + text)
            else:
                text_list_indent.append(text)
        text_indent = '\n'.join(text_list_indent)

        # Replace text
        cursor.setPosition(cursor_start_pos)
        cursor.setPosition(end_pos, QTextCursor.KeepAnchor)
        cursor.insertText(text_indent)

        # Move cursor position
        cursor.setPosition(cursor_start_pos)
        editor.setTextCursor(cursor)
        self.CARET()

    def LESS(self, repeat=1):
        """Shift lines leftwards in visual mode."""
        cursor_pos_start, _ = self._get_selection_positions()
        start_block_no, end_block_no = self._get_selected_block_number(1)
        n_line = end_block_no - start_block_no + 1
        self.exit_visual_mode()

        editor = self._widget.editor()
        cursor = self._editor_cursor()
        cursor.setPosition(cursor_pos_start)
        editor.setTextCursor(cursor)

        self.LESSLESS(repeat=n_line)

    def LESSLESS(self, repeat=1):
        """Shift lines leftwards."""
        editor = self._widget.editor()
        cursor = self._editor_cursor()

        start_block_no, end_block_no = self._get_selected_block_number(repeat)
        cusor_start_pos, __ = self._get_pos_of_block(start_block_no)
        __, end_pos = self._get_pos_of_block(end_block_no)

        text_list = self._get_text_of_blocks(start_block_no, end_block_no)
        text_list_indent = []
        len_indent = len(INDENT)
        for text in text_list:
            n_space = len(text) - len(text.lstrip())
            idx_discard = min([n_space, len_indent])
            text_list_indent.append(text[idx_discard:])
        text_indent = '\n'.join(text_list_indent)

        # Replace text
        cursor.setPosition(cusor_start_pos)
        cursor.setPosition(end_pos, QTextCursor.KeepAnchor)
        cursor.insertText(text_indent)

        # Move cursor position
        start_pos, __ = self._get_pos_of_block(start_block_no)
        cursor.setPosition(cusor_start_pos)
        editor.setTextCursor(cursor)
        self.CARET()

# %% Vim commands
class VimCommands(object):
    """Colon prefix commands."""

    def __init__(self, widget):
        """Main constructor."""
        self._widget = widget

    def __call__(self, cmd):
        """Execute colon prefix command."""
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
        """Save current file."""
        self._widget.main.editor.save_action.trigger()
        self._widget.commandline.setFocus()

    def q(self, args=""):
        """Close current file."""
        self._widget.main.editor.close_action.trigger()
        self._widget.commandline.setFocus()

    def wq(self, args=""):
        """Save and close current file."""
        self.w(args)
        self.q()

    def n(self, args=""):
        """Create new file."""
        self._widget.main.editor.new_action.trigger()
        self._widget.commandline.setFocus()

    def e(self, args=""):
        """Reload current file."""
        args = args.strip()
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
        """Go to line."""
        editor = self._widget.editor()
        editor.go_to_line(int(args))
        self._widget.update_vim_cursor()


# %%
class VimLineEdit(QLineEdit):
    """Vim Command input."""

    def keyPressEvent(self, event):
        """Capture Backspace and ESC Keypresses."""
        if event.key() == Qt.Key_Escape:
            if self.parent().vim_keys.visual_mode:
                self.parent().vim_keys.exit_visual_mode()
            self.clear()
        elif event.key() == Qt.Key_Backspace:
            self.setText(self.text() + "\b")
        elif event.key() == Qt.Key_Return:
            self.setText(self.text() + "\r")
            self.parent().on_return()
        elif event.key() == Qt.Key_Left and not self.text():
            self.setText("h")
        elif event.key() == Qt.Key_Right and not self.text():
            self.setText("l")
        elif event.key() == Qt.Key_Up and not self.text():
            self.setText("k")
        elif event.key() == Qt.Key_Down and not self.text():
            self.setText("j")
        else:
            QLineEdit.keyPressEvent(self, event)

    def focusInEvent(self, event):
        """Enter command mode."""
        QLineEdit.focusInEvent(self, event)
        self.clear()
        self.parent().on_mode_changed("normal")
        self.parent().vim_keys.exit_insert_mode()

    def focusOutEvent(self, event):
        """Enter editor mode."""
        super().focusOutEvent(event)
        self.parent().editor().clear_extra_selections('vim_cursor')
        self.parent().editor().clear_extra_selections('search')
        self.parent().on_mode_changed("insert")
        if self.parent().vim_keys.visual_mode:
            self.parent().vim_keys.exit_visual_mode()


class VimWidget(QWidget):
    """Vim widget."""

    def __init__(self, editor_widget, main):
        """Main widget constructor."""
        self.editor_widget = editor_widget
        self.main = main
        QLineEdit.__init__(self, editor_widget)

        # Build widget
        self.commandline = VimLineEdit(self)
        self.commandline.textChanged.connect(self.on_text_changed)
        self.commandline.returnPressed.connect(self.on_return)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        hlayout = QHBoxLayout()
        self.status_label = QLabel("INSERT")
        self.status_label.setFixedWidth(60)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.on_mode_changed("insert")
        hlayout.addWidget(self.status_label)
        hlayout.addWidget(self.commandline)
        hlayout.setContentsMargins(5, 0, 0, 5)
        self.setLayout(hlayout)
        self.selection_type = (int(time()), "char")
        QApplication.clipboard().dataChanged.connect(self.on_copy)

        # Initialize available commands
        self.vim_keys = VimKeys(self)
        self.vim_commands = VimCommands(self)
        self.vim_keys.mode_changed.connect(self.on_mode_changed)

    def on_mode_changed(self, mode):
        if not is_dark_interface():
            self.status_label.setStyleSheet("QLabel { color: black, padding:2px }")
            if mode == "visual":
                self.status_label.setText("VISUAL")
                self.setStyleSheet("QLabel { background-color: #ffcc99 }")
            elif mode == "normal":
                self.status_label.setText("NORMAL")
                self.setStyleSheet("QLabel { background-color: #85e085 }")
            elif mode == "vline":
                self.status_label.setText("V-LINE")
                self.setStyleSheet("QLabel { background-color: #ffcc99 }")
            elif mode == "insert":
                self.status_label.setText("INSERT")
                self.setStyleSheet("QLabel { background-color: #b3c6ff }")
        else:
            self.status_label.setStyleSheet("QLabel { color: white, padding:2px }")
            if mode == "visual":
                self.status_label.setText("VISUAL")
                self.setStyleSheet("QLabel { background-color: #ff8000 }")
            elif mode == "normal":
                self.status_label.setText("NORMAL")
                self.setStyleSheet("QLabel { background-color: #29a329 }")
            elif mode == "vline":
                self.status_label.setText("V-LINE")
                self.setStyleSheet("QLabel { background-color: #ff8000 }")
            elif mode == "insert":
                self.status_label.setText("INSERT")
                self.setStyleSheet("QLabel { background-color: #3366ff }")

    def on_text_changed(self, text):
        """Parse input command."""
        if not text or text[0] in VIM_COMMAND_PREFIX:
            return

        if text.startswith("0"):
            # Special case to simplify regexp
            repeat, key, leftover = 1, "0", text[1:]
        elif text.startswith("G"):
            repeat, key, leftover = -1, "G", text[1:]
        elif text == "i" and not self.vim_keys.visual_mode:
            repeat, key, leftover = -1, "i", ""
        elif text == "a" and not self.vim_keys.visual_mode:
            repeat, key, leftover = -1, "a", ""
        elif text == "gt":
            repeat, key, leftover = -1, "gt", ""
        else:
            if self.vim_keys.visual_mode and text[0] not in VIM_ARG_PREFIX:
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
        """Execute command."""
        text = self.commandline.text()
        if not text:
            return
        cmd_type = text[0]
        cmd = text[1::].rstrip()
        if cmd_type == ":":  # Vim command
            self.vim_commands(text[1:])
        elif cmd_type == "!":  # Shell command
            pass
        elif cmd_type == "/":  # Forward search
            self.vim_keys.search_dict = self.vim_keys.search(cmd)
        elif cmd_type == "?":  # Reverse search
            self.vim_keys.search_dict = self.vim_keys.search(cmd, reverse=True)
        self.commandline.clear()

    def on_copy(self):
        """Capture text copy action."""
        cur_time = int(time())
        if cur_time != self.selection_type[0]:
            self.selection_type = (cur_time, "char")

    def editor(self):
        """Retrieve text of current opened file."""
        editorstack = self.editor_widget.get_current_editorstack()
        return editorstack.get_current_editor()

    def update_vim_cursor(self):
        """Update Vim cursor position."""
        selection = QTextEdit.ExtraSelection()
        if not is_dark_interface():
            back = Qt.white  # selection.format.background().color()
            fore = Qt.black  # selection.format.foreground().color()
        else:
            back = Qt.black  # selection.format.background().color()
            fore = Qt.white  # selection.format.foreground().color()
        selection.format.setBackground(fore)
        selection.format.setForeground(back)
        selection.cursor = self.editor().textCursor()
        selection.cursor.movePosition(QTextCursor.Right,
                                      QTextCursor.KeepAnchor)
        self.editor().set_extra_selections('vim_cursor', [selection])
