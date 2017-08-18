# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Spyder Project Contributors
#
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)
# -----------------------------------------------------------------------------
"""Vim Plugin."""

from spyder_vim.vim_widget import VimWidget
from qtpy.QtCore import Signal

# Local imports
from spyder.config.base import _
from spyder.config.gui import fixed_shortcut
from spyder.plugins import SpyderPluginWidget


# %%
class Vim(SpyderPluginWidget):  # pylint: disable=R0904
    """Implements a Vim-like command mode."""

    focus_changed = Signal()
    CONF_SECTION = "Vim"
    CONFIGWIDGET_CLASS = None

    def __init__(self, parent):
        """Main plugin constructor."""
        SpyderPluginWidget.__init__(self, parent)
        self.main = parent
        self.initialize_plugin()
        self.vim_cmd = VimWidget(self.main.editor, self.main)

    # %% SpyderPlugin API
    def get_plugin_title(self):
        """Return widget title."""
        return _("Vim")

    def get_plugin_icon(self):
        """Return widget icon."""
        return  # self.get_icon('vim.png')

    def register_plugin(self):
        """Register plugin in Spyder's main window."""
        self.focus_changed.connect(self.main.plugin_focus_changed)
        self.vim_cmd.editor_widget.layout().addWidget(self.vim_cmd)
        fixed_shortcut("Esc", self.vim_cmd.editor_widget.editorsplitter,
                       self.vim_cmd.commandline.setFocus)

    def get_focus_widget(self):
        """Return vim command line and give it focus."""
        return self.vim_cmd.commandline

    def get_plugin_actions(self):
        return []
