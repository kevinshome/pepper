<img src="https://commedesgarcons.s-ul.eu/8NolAhU8" width="54%"></img> 
<img src="https://commedesgarcons.s-ul.eu/FgxMAvXS" width="45%"></img> 

<div align="center">

[![license-mit](https://img.shields.io/pypi/l/pepper-cli)](https://github.com/kevinshome/pepper/blob/main/LICENSE)
[![code-style-black](https://img.shields.io/badge/code%20style-black-black)](https://github.com/psf/black)
[![github-issues](https://img.shields.io/github/issues/kevinshome/pepper)](https://github.com/kevinshome/pepper/issues)
[![github-pull-requests](https://img.shields.io/github/issues-pr/kevinshome/pepper)](https://github.com/kevinshome/pepper/pulls)
![pypi-python-versions](https://img.shields.io/pypi/pyversions/pepper-cli)
[![pypi-package-version](https://img.shields.io/pypi/v/pepper-cli)](https://pypi.org/project/pepper-cli/)

</div>

# Getting Started

The recommended way to install pepper, is via pip, with the following command: 

```
pip install pepper-cli
```

If you want a more bleeding-edge release, however, it can be installed from the main GitHub branch with: 

```
pip install git+https://github.com/kevinshome/pepper.git
```

# PEP Basic Info

To get basic information about a PEP (for this example, let's use 683), we would run the command: 

```
pepper info 683
```

Which will return the following:

```
PEP 683 – Immortal Objects, Using a Fixed Refcount
(https://peps.python.org/pep-0683)

	Author: Eric Snow <ericsnowcurrently at gmail.com>
		Eddie Elizondo <eduardo.elizondorueda at gmail.com>
	Discussions-To: https://discuss.python.org/t/18183
	Status: Accepted
	Type: Standards Track
	Created: 10-Feb-2022
	Python-Version: 3.12
	Post-History: 16-Feb-2022, 19-Feb-2022, 28-Feb-2022, 12-Aug-2022
	Resolution: https://discuss.python.org/t/18183/26
```

# PEP Search

To search for a PEP (for this example, let's search for "Python 3" in the title), we would run the command:

```
pepper search title "Python 3"
```

Which would return the following:

```
Results for 'title' query: 'Python 3'
---------------------------------------
| Type/Status | PEP | Title | Authors |
---------------------------------------

SR | 348 | Exception Reorganization for Python 3.0 | Cannon
IF | 375 | Python 3.1 Release Schedule | Peterson
IF | 392 | Python 3.2 Release Schedule | Brandl
IF | 398 | Python 3.3 Release Schedule | Brandl
SF | 414 | Explicit Unicode Literal for Python 3.3 | Ronacher, Coghlan
IF | 429 | Python 3.4 Release Schedule | Hastings
IF | 430 | Migrating to Python 3 as the default online documentation | Coghlan
SW | 469 | Migration of dict iteration code to Python 3 | Coghlan
IF | 478 | Python 3.5 Release Schedule | Hastings
IF | 494 | Python 3.6 Release Schedule | Deily
IA | 537 | Python 3.7 Release Schedule | Deily
IA | 569 | Python 3.8 Release Schedule | Langa
IA | 596 | Python 3.9 Release Schedule | Langa
IA | 619 | Python 3.10 Release Schedule | Salgado
SR | 641 | Using an underscore in the version portion of Python 3.10 compatibility tags | Cannon, Dower, Warsaw
IA | 664 | Python 3.11 Release Schedule | Salgado
IA | 693 | Python 3.12 Release Schedule | Wouters
PF | 3000 | Python 3000 | GvR
PF | 3099 | Things that will Not Change in Python 3000 | Brandl
PF | 3100 | Miscellaneous Python 3.0 Plans | Cannon
SF | 3109 | Raising Exceptions in Python 3000 | Winter
SF | 3110 | Catching Exceptions in Python 3000 | Winter
SF | 3111 | Simple input built-in in Python 3000 | Roberge
SF | 3112 | Bytes literals in Python 3000 | Orendorff
SF | 3115 | Metaclasses in Python 3000 | Talin
SF | 3138 | String representation in Python 3000 | Ishimoto
```

# Viewing a PEP

To view a PEP, there are two options. First, you can open the PEP in a new tab in your default web browser by running: 

```
pepper open 801
```

However, if you install pepper with the `webview` extra, you can use the command:

```
pepper view 801
```

To open an independent webview window, with the PEP page pulled up on it. 

Whichever method you choose, it is recommened to set an alias to it (i.e. `alias pep="pepper view"` for webview). This way, to open PEP 801, you would simply run the command `pep 801`.

# Disclaimer

This software is released under the terms of the [MIT License](https://github.com/kevinshome/pepper/blob/main/LICENSE)
