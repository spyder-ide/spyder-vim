# -*- coding: utf-8 -*-
#
# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License
#

"""Tests for the plugin."""

# Test library imports
import os
import pytest

# Local imports
from spyder_vim.vim_widget import RE_VIM_PREFIX


def test_prefix_no_match(self):
    """Test that prefix regex does not match invalid prefix."""
    match = RE_VIM_PREFIX.match("d")
    assert match is None


def test_one_char(self):
    """Test that prefix regex matches valid single prefix."""
    groups = RE_VIM_PREFIX.match("D").groups()
    assert groups == ("", "D", "")


def test_two_chars_command(self):
    """Test that prefix regex matches valid pairs of prefixes"""
    groups = RE_VIM_PREFIX.match("dd").groups()
    assert groups == ("", "dd", "")


def test_number_no_match(self):
    """Test that prefix regex does not match invalid number combinations."""
    match = RE_VIM_PREFIX.match("11")
    assert match is None


def test_number_and_zero_no_match(self):
    """Test that prefix regex does not match 10 combination."""
    match = RE_VIM_PREFIX.match("10")
    assert match is None


def test_two_chars_repeat(self):
    """Test that prefix regex matches two prefix combinations."""
    groups = RE_VIM_PREFIX.match("2D").groups()
    assert groups == ("2", "D", "")


def test_three_chars_repeat(self):
    """Test that prefix regex matches three prefix combinations."""
    groups = RE_VIM_PREFIX.match("21D").groups()
    assert groups == ("21", "D", "")


def test_three_chars_with_zero_repeat(self):
    """Test that prefix regex matches three combinations that contain 0."""
    groups = RE_VIM_PREFIX.match("20D").groups()
    assert groups == ("20", "D", "")
