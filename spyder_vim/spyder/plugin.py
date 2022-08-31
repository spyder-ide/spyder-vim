# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Copyright © 2022, spyder-vim
#
# Licensed under the terms of the MIT license
# ----------------------------------------------------------------------------
"""
spyder-vim Plugin.
"""

# Third-party imports
from qtpy.QtCore import Qt, Signal
from qtpy.QtGui import QIcon, QKeySequence
from qtpy.QtWidgets import QShortcut

# Spyder imports
from spyder.api.plugins import Plugins, SpyderPluginV2
from spyder.api.plugin_registration.decorators import on_plugin_available
from spyder.api.translations import get_translation

# Local imports
from spyder_vim.spyder.confpage import SpyderVimConfigPage
from spyder_vim.spyder.container import SpyderVimContainer
from spyder_vim.spyder.widgets import VimWidget

_ = get_translation("spyder_vim.spyder")


class SpyderVim(SpyderPluginV2):
    """
    spyder-vim plugin.
    """

    NAME = "spyder_vim"
    REQUIRES = [Plugins.Editor]
    OPTIONAL = []
    CONTAINER_CLASS = SpyderVimContainer
    CONF_SECTION = NAME
    CONF_WIDGET_CLASS = SpyderVimConfigPage

    # --- Signals

    # --- SpyderPluginV2 API
    # ------------------------------------------------------------------------
    @staticmethod
    def get_name():
        return _("spyder-vim")

    def get_description(self):
        return _("A plugin to enable vim keybindings to the spyder editor")

    def get_icon(self):
        return QIcon()

    def on_initialize(self):
        pass

    @on_plugin_available(plugin=Plugins.Editor)
    def on_editor_available(self):
        """
        Set up interactions when Editor plugin available.
        """
        editor = self.get_plugin(Plugins.Editor)
        self.vim_cmd = VimWidget(editor, self.main)
        editor.layout().addWidget(self.vim_cmd)
        sc = QShortcut(
            QKeySequence("Esc"),
            editor.editorsplitter,
            self.vim_cmd.commandline.setFocus)
        sc.setContext(Qt.WidgetWithChildrenShortcut)

    def check_compatibility(self):
        valid = True
        message = ""  # Note: Remember to use _("") to localize the string
        return valid, message

    def on_close(self, cancellable=True):
        return True

    # --- Public API
    # ------------------------------------------------------------------------
