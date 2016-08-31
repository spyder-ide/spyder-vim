# -*- coding: utf-8 -*-
u"""
:author: Joseph Martinot-Lagarde

Created on Sat Jan 19 14:57:57 2013
"""
from __future__ import (
    print_function, unicode_literals, absolute_import, division)

from .vim_widget import VimWidget

# Local imports
# TODO: activate translation
#from spyder.baseconfig import get_translation
#_ = get_translation("p_autopep8", dirname="spyderplugins.autopep8")
_ = lambda txt: txt
from spyder.config.gui import fixed_shortcut

from spyder.plugins import SpyderPluginMixin


# %%
class Vim(VimWidget, SpyderPluginMixin):  # pylint: disable=R0904

    """Python source code automatic formatting based on autopep8.

    QObject is needed to register the action.
    """
    CONF_SECTION = "Vim"
    CONFIGWIDGET_CLASS = None

    def __init__(self, parent):
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

    def closing_plugin(self, cancelable=False):
        """Perform actions before parent main window is closed"""
        return True
