# git_status_report.py

`git_status_report.py` is a command-line utility that searches a given path for Git repositories and writes a text file listing the status of any repositories.

The `git` command must be available.

The default output file name is `git-status-report.txt`.

## Command-line Usage

```
usage: git_status_report.py [-h] [-o FILE_NAME] [-t] [dir_name]

Create a simple status report for Git repositories under a given path.

positional arguments:
  dir_name              Name of directory to scan for Git repositories.

optional arguments:
  -h, --help            show this help message and exit
  -o FILE_NAME, --output FILE_NAME
                        Name of output file.
  -t, --timestamp       Add a timestamp (date_time) tag to the output file
                        name.
```