# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Copyright © 2022, spyder-vim
#
# Licensed under the terms of the MIT license
# ----------------------------------------------------------------------------
"""
spyder-vim Main Container.
"""
# Spyder imports
from spyder.api.config.decorators import on_conf_change
from spyder.api.translations import get_translation
from spyder.api.widgets.main_container import PluginMainContainer

_ = get_translation("spyder_vim.spyder")


class SpyderVimContainer(PluginMainContainer):

    # Signals

    # --- PluginMainContainer API
    # ------------------------------------------------------------------------
    def setup(self):
        pass

    def update_actions(self):
        pass

    # --- Public API
    # ------------------------------------------------------------------------
