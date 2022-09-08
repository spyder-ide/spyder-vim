# Release

Follow these steps to release a new version of spyder-vim.

In the commands below, replace `X.Y.Z` with the release version when needed.

**Note**: We use `pip` instead of `conda` here even on Conda installs, to ensure we always get the latest upstream versions of the build dependencies.

## PyPI and GitHub

You will need to have a local clone of the repo. The following steps supose a repo setup from a fork with and `upstream` remote pointing to the main `spyder-vim` repo

* Close [milestone on Github](https://github.com/spyder-ide/spyder-vim/milestones)

* Update local repo

  ```bash
  git restore . && git switch master && git pull upstream master
  ```

* Clean local repo

  ```bash
  git clean -xfdi
  ```

* Install/upgrade Loghub

  ```bash
  pip install --upgrade loghub
  ```

* Update `CHANGELOG.md` with Loghub: `loghub spyder-ide/spyder-vim --milestone vX.Y.Z`

* git add and git commit with "Update Changelog"

* Update `__version__` in `__init__.py` (set release version, remove `dev0`)

* Create release commit

  ```bash
  git commit -am "Release X.Y.Z"
  ```

* Update the packaging stack

  ```bash
  python -m pip install --upgrade pip
  pip install --upgrade --upgrade-strategy eager build setuptools twine wheel
  ```

* Build source distribution and wheel

  ```bash
  python -bb -X dev -W error -m build
  ```

* Check distribution archives

  ```bash
  twine check --strict dist/*
  ```

* Upload distribution packages to PyPI

  ```bash
  twine upload dist/*
  ```

* Create release tag

  ```bash
  git tag -a vX.Y.Z -m "Release X.Y.Z"
  ```

* Update `__version__` in `__init__.py` (add `.dev0` and increment minor)

* Create `Back to work` commit

  ```bash
  git commit -am "Back to work"
  ```

* Push new release commits and tags to `master`

  ```bash
  git push upstream master --follow-tags
  ```

* Create a [GitHub release](https://github.com/spyder-ide/spyder-vim/releases) from the tag

## Conda-Forge

To release a new version of `spyder-vim` on Conda-Forge:

* After the release on PyPI, an automatic PR in the [Conda-Forge feedstock repo for spyder-vim](https://github.com/conda-forge/spyder-vim-feedstock/pulls) should open.
  Merging this PR will update the respective Conda-Forge package.