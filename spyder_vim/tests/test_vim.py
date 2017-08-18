# -*- coding: utf-8 -*-

from __future__ import (
    print_function, unicode_literals, absolute_import, division)

from spyder_vim.vim_widget import RE_VIM_PREFIX


class TestCommandRegexp(object):
    def test_prefix_no_match(self):
        match = RE_VIM_PREFIX.match("d")
        assert match is None

    def test_one_char(self):
        groups = RE_VIM_PREFIX.match("D").groups()
        assert groups == ("", "D", "")

    def test_two_chars_command(self):
        groups = RE_VIM_PREFIX.match("dd").groups()
        assert groups == ("", "dd", "")

    def test_number_no_match(self):
        match = RE_VIM_PREFIX.match("11")
        assert match is None

    def test_number_and_zero_no_match(self):
        match = RE_VIM_PREFIX.match("10")
        assert match is None

    def test_two_chars_repeat(self):
        groups = RE_VIM_PREFIX.match("2D").groups()
        assert groups == ("2", "D", "")

    def test_three_chars_repeat(self):
        groups = RE_VIM_PREFIX.match("21D").groups()
        assert groups == ("21", "D", "")

    def test_three_chars_with_zero_repeat(self):
        groups = RE_VIM_PREFIX.match("20D").groups()
        assert groups == ("20", "D", "")
