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
from qtpy.QtWidgets import QVBoxLayout, QShortcut

# Spyder imports
from spyder.api.plugins import Plugins, SpyderPluginV2
from spyder.api.translations import get_translation

# Local imports
from spyder_vim.spyder.confpage import spyder_vimConfigPage
from spyder_vim.spyder.container import spyder_vimContainer
from spyder_vim.spyder.widgets import VimWidget

_ = get_translation("spyder_vim.spyder")


class spyder_vim(SpyderPluginV2):
    """
    spyder-vim plugin.
    """

    focus_changed = Signal()
    NAME = "spyder_vim"
    REQUIRES = []
    OPTIONAL = []
    CONTAINER_CLASS = spyder_vimContainer
    CONF_SECTION = NAME
    CONF_WIDGET_CLASS = spyder_vimConfigPage

    def __init__(self, parent, configuration=None):
        super().__init__(parent)
        self.vim_cmd = VimWidget(self.main.editor, self.main)
        layout = QVBoxLayout()
        layout.addWidget(self.vim_cmd)
        # self.setLayout(layout)

    # --- Signals

    # --- SpyderPluginV2 API
    # ------------------------------------------------------------------------
    @staticmethod
    def get_name():
        return _("spyder-vim")

    def get_description(self):
        return _("A plugin to enable vim keybingins to the spyder editor")

    def get_icon(self):
        return QIcon()

    def on_initialize(self):
        container = self.get_container()
        self.focus_changed.connect(self.main.plugin_focus_changed)
        self.vim_cmd.editor_widget.layout().addWidget(self.vim_cmd)
        sc = QShortcut(QKeySequence("Esc"), self.vim_cmd.editor_widget.editorsplitter, self.vim_cmd.commandline.setFocus)
        sc.setContext(Qt.WidgetWithChildrenShortcut)

    def check_compatibility(self):
        valid = True
        message = ""  # Note: Remember to use _("") to localize the string
        return valid, message

    def on_close(self, cancellable=True):
        return True

    # --- Public API
    # ------------------------------------------------------------------------
