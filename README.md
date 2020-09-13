2020 USA State Presidential Election Polls
==========================================

#### Overview

This project analyzes 2020 USA Presididential Election polling data from https://electoral-vote.com/.  You might have already noticed that there hasn't been much in the way of polling data compared to other years.  This is mostly due to the COVID-19 pandemic and its health & economics effects.  I verified this for myself when I limited poll data to the last 2 or 3 months (AGE_THRESHOLD in src/stpolls_data_defs.py).  For comparison purposes, assuming that a state had polls in the last 2-3 months, I only looked at the last 3 polls (3-element arrays are built-in to src/stpolls_main_analyze.py).  The reason for both limitations is that the polls are much more volatile this year, in my opinion, even more so than 2016, as hard as that is to believe.

The project shell scripts are should be runnable on any O/S that supports the Bash shell, the GNU (Linux/Unix) command line utilities, and Python 3.  I have tested only on Xubuntu Linux 20.04 and MacOS High Sierra.

#### Dependencies

```
matplotlib
numpy
pandas
sqlite3
```

#### Installation

```
None required.
```

#### Invocation from a terminal window command-line

```
cd <to-high-level-folder>
fetch.sh # Get the latest CSV file.
load.sh # Initialize a new database and load it from the CSV file.
process.sh # Perform analysis and produce plots.
```

#### Licensing

This is NOT commercial software; instead, usage is covered by the GNU General Public License version 3 (2007). In a nutshell, please feel free to use the project and share it as you will but please don't sell it. Thank you!

See the LICENSE file for the GNU licensing information.

Feel free to create an issue record for any questions, bugs, or enhancement requests. I'll respond as soon as I can.

Richard Elkins

Dallas, Texas, USA, 3rd Rock, Sol, ...
