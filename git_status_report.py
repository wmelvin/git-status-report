#!/usr/bin/env python3

import argparse
import shutil
import subprocess
import sys

from datetime import datetime
from pathlib import Path
from typing import List


app_name = "git_status_report.py"
app_version = "221011.1"

do_print_git_output = False

run_dt = datetime.now()


class GitStatusReport:
    def __init__(self) -> None:
        self.rpt_lines: List = []
        self.msg_lines: List = []
        self.err_lines: List = []
        self.repos_found: bool = False

    def rpt_text(self) -> str:
        return "\n".join(self.rpt_lines)

    def msg_text(self) -> str:
        return "\n".join(self.msg_lines)

    def err_text(self) -> str:
        return "\n".join(self.err_lines)

    def get_git_status(self, git_path: Path):
        STATUS_CLEAN = "nothing to commit, working tree clean"

        rpt_new = []
        msg_new = []
        err_new = []

        if not git_path.is_dir():
            return rpt_new

        repo_path = git_path.parent

        print(f"Checking '{repo_path}'.")

        rpt_new.append(f"{'-' * 70}\nRepository: '{repo_path}'\n")

        result = run_git(repo_path, ["status", "-u"])

        if result is None:
            err_new.append("ERROR: Failed to run git command.")
        else:
            if result.returncode == 0:
                rpt_new.append(result.stdout)
                if STATUS_CLEAN not in result.stdout:
                    msg_new.append(f"Repo '{repo_path}' has changes.")
            else:
                err_new.append(f"ERROR ({result.returncode})")
                if result.stderr is not None:
                    err_new.append(f"STDERR:\n{result.stderr}\n")
                if result.stdout is not None:
                    err_new.append(f"STDOUT:\n{result.stdout}\n")

        if err_new:
            rpt_new += err_new
            err_new.insert(0, f"ERRORS in 'get_git_status' for '{git_path}'")

        self.rpt_lines += rpt_new
        self.msg_lines += msg_new
        self.err_lines += err_new

    def get_git_remote(self, repo_path: Path, remote: str):
        UP_TO_DATE = "(up to date)"

        rpt_new = []
        msg_new = []
        err_new = []

        rpt_new.append(f"{'- ' * 35}\nRemote: '{remote}'\n")

        result = run_git(repo_path, ["remote", "show", remote])

        if result is None:
            err_new.append("ERROR: Failed to run git command.")
        else:
            if result.returncode == 0:
                rpt_new.append(result.stdout)
                if UP_TO_DATE not in result.stdout:
                    msg_new.append(f"Repo '{repo_path}' has changes.")
            else:
                err_new.append(f"ERROR ({result.returncode})")
                if result.stderr is not None:
                    err_new.append(f"STDERR:\n{result.stderr}\n")
                if result.stdout is not None:
                    err_new.append(f"STDOUT:\n{result.stdout}\n")

        if err_new:
            rpt_new += err_new
            err_new.insert(
                0,
                "ERRORS in 'get_git_remote' for "
                + f"'{repo_path}' remote '{remote}'.",
            )

        self.rpt_lines += rpt_new
        self.msg_lines += msg_new
        self.err_lines += err_new

    def get_git_remotes(self, git_path: Path):
        rpt_new = []
        err_new = []

        if not git_path.is_dir():
            return

        repo_path = git_path.parent

        result = run_git(repo_path, ["remote", "show"])

        if result is None:
            err_new.append("ERROR: Failed to run git command.")
        else:
            if result.returncode == 0:
                remotes = [s for s in result.stdout.split("\n") if s]
                for remote in remotes:
                    self.get_git_remote(git_path, remote)
            else:
                err_new.append(f"ERROR ({result.returncode})")
                if result.stderr is not None:
                    err_new.append(f"STDERR:\n{result.stderr}\n")
                if result.stdout is not None:
                    err_new.append(f"STDOUT:\n{result.stdout}\n")

        if err_new:
            rpt_new += err_new
            err_new.insert(
                0,
                f"ERRORS in 'get_git_remotes' for '{repo_path}'.",
            )

        self.rpt_lines += rpt_new
        self.err_lines += err_new


def run_git(run_dir, args) -> subprocess.CompletedProcess:
    assert isinstance(args, list)

    git_exe = shutil.which("git")

    if git_exe is None:
        sys.stderr.write(
            "ERROR - Cannot find 'git' command. Make sure Git is installed.\n"
        )
        sys.exit(1)

    cmds = [git_exe] + args

    result = subprocess.run(
        cmds,
        cwd=str(run_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
    )

    if do_print_git_output:
        if result.stdout is not None:
            print(f"\nSTDOUT:\n{result.stdout.strip()}\n")

        if result.stderr is not None:
            print(f"\nSTDERR:\n{result.stderr.strip()}\n")

    return result


def get_args(argv):
    ap = argparse.ArgumentParser(
        description="Create a simple status report for Git repositories "
        "under a given path."
    )

    ap.add_argument(
        "dir_name",
        nargs="?",
        help="Name of directory to scan for Git repositories.",
    )

    ap.add_argument(
        "-o",
        "--output",
        dest="file_name",
        action="store",
        help="Name of output file.",
    )

    ap.add_argument(
        "-t",
        "--timestamp",
        dest="dt_tag",
        action="store_true",
        help="Add a timestamp (date_time) tag to the output file name.",
    )

    args = ap.parse_args(argv[1:])

    if args.dir_name is None:
        dir_path = Path.cwd()
    else:
        dir_path = Path(args.dir_name).expanduser().resolve()

    if not dir_path.is_dir():
        sys.stderr.write(f"ERROR - Not a directory: '{dir_path}'\n")
        sys.exit(1)

    if args.file_name is None:
        out_path = Path.cwd() / "git-status-report.txt"
    else:
        out_path = Path(args.file_name).expanduser().resolve()

    if not out_path.parent.exists():
        sys.stderr.write(
            f"ERROR - Cannot find output directory: '{out_path.parent}'\n"
        )
        sys.exit(1)

    if args.dt_tag:
        dt = run_dt.strftime("%Y%m%d_%H%M%S")
        out_path = out_path.with_suffix(f".{dt}{out_path.suffix}")

    return (dir_path, out_path)


def process_repos(dir_path: Path) -> GitStatusReport:
    rpt = GitStatusReport()

    print(f"Searching '{dir_path}'.")

    git_dirs = sorted(dir_path.glob("**/.git"))
    if len(git_dirs) == 0:
        rpt.rpt_lines.append(f"No repositories found under '{dir_path}'.")
    else:
        rpt.repos_found = True
        for p in git_dirs:
            rpt.get_git_status(p)
            rpt.get_git_remotes(p)

        dt = run_dt.strftime("%Y-%m-%d %H:%M:%S")
        rpt.rpt_lines.append(f"\n{'-' * 70}")
        rpt.rpt_lines.append(
            f"Created {dt} by {app_name} version {app_version}."
        )

    return rpt


def main(argv):
    dir_path, out_path = get_args(argv)

    rpt = process_repos(dir_path)

    s = rpt.msg_text()
    if s:
        s = f"{'-' * 70}\nMESSAGES:\n\n{s}\n\n"
        print(s)

    t = rpt.err_text()
    if t:
        t = f"{'-' * 70}\nERRORS:\n\n{t}\n\n"
        print(t)

    if rpt.repos_found:
        print(f"\nWriting '{out_path}'.")
        with open(out_path, "w") as f:
            if s:
                f.write(s)
            if t:
                f.write(t)
            f.write(rpt.rpt_text())
    else:
        print(f"\n{rpt.rpt_text()}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
