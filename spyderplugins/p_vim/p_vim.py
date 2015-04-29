# -*- coding: utf-8 -*-
u"""
:author: Joseph Martinot-Lagarde

Created on Sat Jan 19 14:57:57 2013
"""
from __future__ import (
    print_function, unicode_literals, absolute_import, division)

import re

from spyderlib.qt.QtGui import QWidget, QLineEdit, QHBoxLayout, QTextCursor
from spyderlib.qt.QtCore import Qt

# Local imports
# TODO: activate translation
#from spyderlib.baseconfig import get_translation
#_ = get_translation("p_autopep8", dirname="spyderplugins.autopep8")
_ = lambda txt: txt
from spyderlib.utils.qthelpers import create_action
try:
    from spyderlib.py3compat import to_text_string
except ImportError:
    # Python 2
    to_text_string = unicode

from spyderlib.plugins import SpyderPluginMixin


VIM_PREFIX = "cdfFmrtTyzZ@'`\"<>"
VIM_COMMAND_PREFIX = ":!/?"
RE_VIM_PREFIX = re.compile(r"^(\d*)([{0}].|[^{0}])(.*)$".format(VIM_PREFIX))


# %% Vim shortcuts
class VimKeys(object):
    def __init__(self, widget):
        self._widget = widget

    def __call__(self, key, repeat):
        if key.startswith("_"):
            return
        try:
            method = self.__getattribute__(key)
        except AttributeError:
            print("unknown key", key)
        else:
            method(repeat)

    def _move_cursor(self, movement):
        editor = self._widget.editor()
        cursor = editor.textCursor()
        cursor.movePosition(movement)
        editor.setTextCursor(cursor)

    # %% Movement
    def h(self, repeat):
        self._move_cursor(QTextCursor.Left)

    def j(self, repeat):
        self._move_cursor(QTextCursor.Down)

    def k(self, repeat):
        self._move_cursor(QTextCursor.Up)

    def l(self, repeat):
        self._move_cursor(QTextCursor.Right)

    def w(self, repeat):
        self._move_cursor(QTextCursor.NextWord)

    # %% Insertion
    def i(self, repeat):
        self._widget.editor().setFocus()

    def a(self, repeat):
        self.l()
        self.i()

    # %% Deletions

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


# %%
class VimWidget(QWidget):
    """
    Pylint widget
    """

    def __init__(self, parent):
        QWidget.__init__(self, parent)

        # Build widget
        self.setWindowTitle("Vim commands")
        self.commandline = QLineEdit(self)
        self.commandline.textChanged.connect(self.on_text_changed)
        self.commandline.returnPressed.connect(self.on_return)

        hlayout1 = QHBoxLayout()
        hlayout1.addWidget(self.commandline)
        self.setLayout(hlayout1)

        # Initialize available commands
        self.vim_keys = VimKeys(self)
        self.vim_commands = VimCommands(self)

    def on_text_changed(self, text):
        if not text or text[0] in VIM_COMMAND_PREFIX:
            return
        match = RE_VIM_PREFIX.match(text)
        print(text)
        if not match:
            return
        repeat, key, leftover = match.groups()
        repeat = int(repeat) if repeat else 1
        if not repeat:
            return
        self.vim_keys(key, repeat)
        self.commandline.setText(leftover)

    def on_return(self):
        text = self.commandline.text()
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
        editorstack = self.main.editor.get_current_editorstack()
        index = editorstack.get_stack_index()
        finfo = editorstack.data[index]
        return finfo.editor

    def move_cursor(self, movement):
        editor = self.editor()
        cursor = editor.textCursor()
        cursor.movePosition(movement)
        editor.setTextCursor(cursor)


class Vim(VimWidget, SpyderPluginMixin):  # pylint: disable=R0904

    """Python source code automatic formatting based on autopep8.

    QObject is needed to register the action.
    """
    CONF_SECTION = "Vim"
    CONFIGWIDGET_CLASS = None

    def __init__(self, parent):
        VimWidget.__init__(self, parent=parent)
        SpyderPluginMixin.__init__(self, parent)
        self.initialize_plugin()

    # %% SpyderPlugin API
    def get_plugin_title(self):
        """Return widget title"""
        return _("Vim")

    def get_plugin_icon(self):
        """Return widget icon"""
        return  # self.get_icon('vim.png')

    def register_plugin(self):
        """Register plugin in Spyder's main window"""
        self.main.add_dockwidget(self)
        vim_command_act = create_action(
            self.main, _("Vim command mode"),
            icon=None,
            triggered=self.commandline.setFocus)
        self.register_shortcut(vim_command_act, context=Qt.ApplicationShortcut,  # "Editor",
                               name="Enter vim command mode", default="Esc")
        self.main.source_menu_actions += [None, vim_command_act]

    def apply_plugin_settings(self, options):
        """Needs to be redefined."""
        pass

    def get_plugin_actions(self):
        return []

    def get_focus_widget(self):
        """
        Return the widget to give focus to when
        this plugin's dockwidget is raised on top-level
        """
        return self.commandline

    def refresh_plugin(self):
        """Refresh widget"""
        pass
