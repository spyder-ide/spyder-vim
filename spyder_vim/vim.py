# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Spyder Project Contributors
#
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)
# -----------------------------------------------------------------------------
"""Vim Plugin."""


from spyder_vim.vim_widget import VimWidget

# Local imports
from spyder.config.base import _
from spyder.config.gui import fixed_shortcut
from spyder.plugins import SpyderPluginMixin


# %%
class Vim(VimWidget, SpyderPluginMixin):  # pylint: disable=R0904
    """Implements a Vim-like command mode."""

    CONF_SECTION = "Vim"
    CONFIGWIDGET_CLASS = None

    def __init__(self, parent):
        """Main plugin constructor."""
        VimWidget.__init__(self, editor_widget=parent.editor)
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
        self.editor_widget.layout().addWidget(self)
        fixed_shortcut("Esc", self.editor_widget.editorsplitter,
                       self.commandline.setFocus)

    def get_focus_widget(self):
        """
        Return the widget to give focus to when
        this plugin's dockwidget is raised on top-level
        """
        return self.commandline
