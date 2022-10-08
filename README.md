# spyder-vim

## Project Info

[![Project License](https://img.shields.io/pypi/l/spyder-vim.svg)](./LICENSE.txt)
[![pypi version](https://img.shields.io/pypi/v/spyder-vim.svg)](https://pypi.python.org/pypi/spyder-vim)
[![Join the chat at https://gitter.im/spyder-ide/public](https://badges.gitter.im/spyder-ide/spyder.svg)](https://gitter.im/spyder-ide/public)
[![OpenCollective Backers](https://opencollective.com/spyder/backers/badge.svg?color=blue)](#backers)
[![OpenCollective Sponsors](https://opencollective.com/spyder/sponsors/badge.svg?color=blue)](#sponsors)

## Build status

![Linux tests](https://github.com/spyder-ide/spyder-vim/workflows/Linux%20tests/badge.svg)
![Macos tests](https://github.com/spyder-ide/spyder-vim/workflows/Macos%20tests/badge.svg)
![Window tests](https://github.com/spyder-ide/spyder-vim/workflows/Windows%20tests/badge.svg)
[![Coverage Status](https://coveralls.io/repos/github/spyder-ide/spyder-vim/badge.svg?branch=master)](https://coveralls.io/github/spyder-ide/spyder-vim?branch=master)

----

# Overview

Spyder Plugin for executing Vim commands inside the code editor. Although it does not currently support many VIM commands, it will be developed gradually.

<img src="/doc/example.gif" width="600">

| Category     | supported commands                                                            |
| ------------ | ----------------------------------------------------------------------------- |
| Movement     | h, j, k, l, w, b, e, space, backspace, return, $, 0, ^, G, gg, zz, H, L, M, % |
| Change       | x, r, o, O, u, d, dd, dw, D, c, cc, cw, J, ~, <, >, <<, >>                    |
| Copy & Paste | yy, yw, y$, p, P                                                              |
| Search       | /, ?, n, N, f, F                                                              |
| mode         | i, I, a, A, v, V                                                              |
| Register     | -, 0, 1, unamed                                                               |
| File         | ZZ, gt, gT, :w, :q, :wq, :n, :e                                               |

## Installation

To install this plugin, you can use either the ``conda`` or ``pip`` package managers, as it follows:

Using conda:

```
conda install spyder-vim -c conda-forge
```

Using pip (only if you don't use Anaconda):

```
pip install spyder-vim
```

## Usage

After installing Spyder-vim, you need to close Spyder and start it again, in case it's running, so that the plugin is loaded by it. Afterwards, you should see it at the bottom of the editor, as displayed in the animated screenshot above.

## Dependencies

This project depends on [Spyder](https://github.com/spyder-ide/spyder).

## Changelog

Visit our [CHANGELOG](CHANGELOG.md) file to know more about our new features and improvements.

## Development and contribution

Do you want to request a new keybind for the plugin? Please submit it to our [Commands](https://github.com/spyder-ide/spyder-vim/issues/1) issue page. Feel free to open a PR to implement it.

To start contributing to the source code of this project, please check our [contributing guide](https://github.com/spyder-ide/spyder-vim/blob/master/CONTRIBUTING.md) to setup a development environment and be able to test your changes on Spyder. We follow PEP8 and PEP257 style guidelines.

Everyone is welcome to contribute!

## Sponsors

Spyder is funded thanks to the generous support of

[![Quansight](https://user-images.githubusercontent.com/16781833/142477716-53152d43-99a0-470c-a70b-c04bbfa97dd4.png)](https://www.quansight.com/)[![Numfocus](https://i2.wp.com/numfocus.org/wp-content/uploads/2017/07/NumFocus_LRG.png?fit=320%2C148&ssl=1)](https://numfocus.org/)

and the donations we have received from our users around the world through [Open Collective](https://opencollective.com/spyder/):

[![Sponsors](https://opencollective.com/spyder/sponsors.svg)](https://opencollective.com/spyder#support)

## More information

[Main Website](https://www.spyder-ide.org/)

[Download Spyder (with Anaconda)](https://www.anaconda.com/download/)

[Online Documentation](https://docs.spyder-ide.org/)

[Spyder Github](https://github.com/spyder-ide/spyder)

[Troubleshooting Guide and FAQ](
https://github.com/spyder-ide/spyder/wiki/Troubleshooting-Guide-and-FAQ)

[Development Wiki](https://github.com/spyder-ide/spyder/wiki/Dev:-Index)

[Gitter Chatroom](https://gitter.im/spyder-ide/public)

[Google Group](https://groups.google.com/group/spyderlib)

[@Spyder_IDE on Twitter](https://twitter.com/spyder_ide)

[@SpyderIDE on Facebook](https://www.facebook.com/SpyderIDE/)

[Support Spyder on OpenCollective](https://opencollective.com/spyder/)
