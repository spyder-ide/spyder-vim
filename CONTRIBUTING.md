# Contributing to the Spyder Vim plugin

:+1::tada: 
First off, thanks for taking the time to contribute to the Spyder Vim
plugin! 
:tada::+1:

## General guidelines for contributing

The Spyder Vim plugin is developed as part of the wider Spyder project.
In general, the guidelines for contributing to Spyder also apply here.
Specifically, all contributors are expected to abide by
[Spyder's Code of Conduct](https://github.com/spyder-ide/spyder/blob/master/CODE_OF_CONDUCT.md).

There are many ways to contribute and all are valued and welcome. 
You can help other users, write documentation, spread the word, submit
helpful issues on the
[issue tracker](https://github.com/spyder-ide/spyder-vim/issues)
with problems you encounter or ways to improve the plugin, test the development
version, or submit a pull request on GitHub.

The rest of this document explains how to set up a development environment.

## Setting up a development environment

This section explains how to set up a conda environment to run and work on the
development version of the Spyder vim plugin.

### Creating a conda environment

This creates a new conda environment with the name `spydervim-dev`.

```bash
$ conda create -n spydervim-dev -c conda-forge python=3.9
$ conda activate spydervim-dev
```

### Cloning the repository

This creates a new directory `spyder-vim` with the source code of the
Spyder Vim plugin.

```bash
$ git clone https://github.com/spyder-ide/spyder-vim.git
$ cd spyder-vim
```

### Installing dependencies

This installs Spyder, QtPy and all other dependencies of the plugin into
the conda environment.

```bash
$ conda install -c conda-forge --file requirements/conda.txt
```

### Installing the plugin

This installs the Spyder Vim plugin so that Spyder will use it.

```bash
$ pip install --no-deps -e .
```

### Running Spyder

You are done! You can run Spyder as normal and it should load the Vim
plugin.

```bash
$ spyder
```

### Running Tests

This command installs the test dependencies in the conda environment.

```bash
$ conda install -c conda-forge --file requirements/tests.txt
```

You can now run the tests with a simple

```bash
$ pytest
```