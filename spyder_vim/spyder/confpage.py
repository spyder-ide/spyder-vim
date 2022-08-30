# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Copyright © 2022, spyder-vim
#
# Licensed under the terms of the MIT license
# ----------------------------------------------------------------------------
"""
spyder-vim Preferences Page.
"""
from spyder.api.preferences import PluginConfigPage
from spyder.api.translations import get_translation

_ = get_translation("spyder_vim.spyder")


class SpyderVimConfigPage(PluginConfigPage):

    # --- PluginConfigPage API
    # ------------------------------------------------------------------------
    def setup_page(self):
        pass
