# -*- coding: utf-8 -*-
u"""
:author: Joseph Martinot-Lagarde

Created on Sat Jan 19 14:57:57 2013
"""
from __future__ import (
    print_function, unicode_literals, absolute_import, division)

import sys

from spyderlib.qt.QtGui import QWidget, QLineEdit, QHBoxLayout, QTextCursor
from spyderlib.qt.QtCore import QEventLoop

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


# %% Vim shortcuts
class VimKeys(object):
    def __init__(self, widget):
        self._widget = widget

    def __call__(self, key):
        if key.startswith("_"):
            return
        try:
            method = self.__getattribute__(key)
        except AttributeError:
            print("unknown key", key)
        else:
            method()

    def _move_cursor(self, movement):
        editor = self._widget.editor()
        cursor = editor.textCursor()
        cursor.movePosition(movement)
        editor.setTextCursor(cursor)

    # %% Movement
    def h(self):
        self._move_cursor(QTextCursor.Left)

    def j(self):
        self._move_cursor(QTextCursor.Down)

    def k(self):
        self._move_cursor(QTextCursor.Up)

    def l(self):
        self._move_cursor(QTextCursor.Right)

    def w(self):
        self._move_cursor(QTextCursor.NextWord)

    # %% Insertion
    def i(self):
        self._widget.editor().setFocus()

    def a(self):
        self.l()
        self.i()


# %% Vim commands
class VimCommands(object):
    def __init__(self, widget):
        self._widget = widget

    def __call__(self, cmd):
        if not cmd.startswith(":"):
            return
        cmd = cmd[1:]
        if cmd.startswith("_"):
            return
        try:
            cmd, args = cmd.split(None, 1)
        except ValueError:
            args = ""

        try:
            method = self.__getattribute__(cmd)
        except AttributeError:
            print("unknown command", cmd)
        else:
            method(args)

    def w(self, args=""):
        self._widget.main.editor.save_action.trigger()

    def q(self, args=""):
        self._widget.main.editor.close_action.trigger()

    def wq(self, args=""):
        self.w(args)
        self.q()

    def ZZ(self, args=""):
        self.wq()


# %%
class VimWidget(QWidget):
    """
    Pylint widget
    """

    def __init__(self, parent):
        QWidget.__init__(self, parent)

        self.setWindowTitle("Vim commands")
        self.commandline = QLineEdit(self)
        self.commandline.textChanged.connect(self.on_text_changed)
        self.commandline.returnPressed.connect(self.on_return)

        hlayout1 = QHBoxLayout()
        hlayout1.addWidget(self.commandline)
        self.setLayout(hlayout1)

        self.vim_keys = VimKeys(self)
        self.vim_commands = VimCommands(self)

    def on_text_changed(self, text):
        if not text:
            return
        if not text.startswith(":"):
            if text.isdigit():
                return
            print(text)
            self.commandline.clear()
            try:
                self.vim_keys(text)
            except KeyError:
                pass

    def on_return(self):
        text = self.commandline.text()
        print(text)
        self.vim_commands(text)
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
