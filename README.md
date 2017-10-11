# spyder-vim
Spyder Plugin for executing Vim commands inside the code editor. We currently support the following keybindings and commands: https://github.com/spyder-ide/spyder-vim/issues/1

## Project Info
[![Project License](https://img.shields.io/pypi/l/spyder-vim.svg)](./LICENSE.txt)
[![pypi version](https://img.shields.io/pypi/v/spyder-vim.svg)](https://pypi.python.org/pypi/spyder-vim)

## Build status
[![CircleCI](https://circleci.com/gh/spyder-ide/spyder-vim.svg?style=svg)](https://circleci.com/gh/spyder-ide/spyder-vim)
[![Coverage Status](https://coveralls.io/repos/github/spyder-ide/spyder-vim/badge.svg?branch=master)](https://coveralls.io/github/spyder-ide/spyder-vim?branch=master)

## Installation
To install this plugin, you can use either ``pip`` or ``conda`` package managers, as it follows:

Build from source:
```
git clone https://github.com/spyder-ide/spyder-vim
cd spyder-vim
python setup.py install .
```

Using conda:
```
conda install spyder-vim -c spyder-ide
```

## Dependencies
This project depends on [Spyder](https://github.com/spyder-ide/spyder).

## Changelog
Visit our [CHANGELOG](CHANGELOG.md) file to know more about our new features and improvements.

## Development and contribution
Do you want to request a new keybind for the plugin? Please submit it to our [Commands](https://github.com/spyder-ide/spyder-vim/issues/1) issue page. Feel free to open a PR to implement it.

To start contributing to this project, you can execute ``pip install -U .`` to test your changes on Spyder. We follow PEP8 and PEP257 style guidelines.

# Overview
![alt tag](/doc/example.gif)
