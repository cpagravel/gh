# gh [![MIT License][license-badge]](LICENSE.md)

## Synposis
gh is short for **G**it **H**istory - it's a commandline app with some neat features for improving your workflow with git
Note that gh is meant for in dark themed terminals

## Usage
Note that the output is colorized in the terminal and intended for a dark themed terminal. It doesn't show here - waiting for colorized text in Github markdown (re: https://github.com/github/markup/issues/369).
```
(master) $ gh # Show checkout history
#   BRANCH HISTORY
0   new_branch (0)
1   feature_branch (1)

(master) $ gh -c 0 # Checkout a branch
(new_branch) $
```

## Installation
Install from pip.
```
pip install githc
```

## Compatability
- Linux, Mac, Windows
- Git version >2
- Python3 (re: https://pythonclock.org/)

## TODO
- Use a class and get rid of globals (parser, item_count)
- Upload pictures to show colored text (or wish harder for github to support it)

## License MIT
[View project License](LICENSE.md).

[license-badge]: https://img.shields.io/badge/license-MIT-007EC7.svg
