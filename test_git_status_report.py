from pathlib import Path

import git_status_report


def test_run_git(tmp_path: Path):
    #  These tests require that git is installed on the host.
    assert git_status_report.run_git(tmp_path, ["--help"]).returncode == 0


def test_git_status(tmp_path: Path):
    work_repo = tmp_path / "a"
    work_repo.mkdir()
    assert work_repo.exists()

    file_a = work_repo / "a.txt"
    file_a.write_text("Hey, everyone!")

    assert git_status_report.run_git(
        work_repo, ["init", "-b", "main"]
    ).returncode == 0

    assert work_repo.joinpath('.git').exists()

    result = git_status_report.run_git(work_repo, ["status"])
    assert result.returncode == 0
    assert "Untracked" in result.stdout

    args = [
        "git_status_report.py",
        str(work_repo),
        "--output",
        "z-test-git-status.txt"
    ]

    ec = git_status_report.main(args)

    assert ec == 0


def test_git_w_1_remote(tmp_path: Path):
    work_repo = tmp_path / "a"
    work_repo.mkdir()
    assert work_repo.exists()

    file_a = work_repo / "a.txt"
    file_a.write_text("Hey, everyone!")

    assert git_status_report.run_git(
        work_repo, ["init", "-b", "main"]
    ).returncode == 0
    assert work_repo.joinpath('.git').exists()

    assert git_status_report.run_git(
        work_repo, ["add", "a.txt"]
    ).returncode == 0

    result = git_status_report.run_git(
        work_repo, ["status"]
    )
    assert result.returncode == 0
    assert "Untracked" not in result.stdout

    assert git_status_report.run_git(
        work_repo, ["commit", "-m", '"Initial commit."']
    ).returncode == 0

    remote_repo = tmp_path / "b.git"
    remote_repo.mkdir()
    assert remote_repo.exists()

    assert git_status_report.run_git(
        remote_repo, ["init", "-b", "main", "--bare"]
    ).returncode == 0
    assert remote_repo.joinpath('HEAD').exists()

    assert git_status_report.run_git(
        work_repo, ["remote", "add", "origin", str(remote_repo)]
    ).returncode == 0

    assert git_status_report.run_git(
        work_repo, ["push", "-u", "origin", "main"]
    ).returncode == 0

    args = [
        "git_status_report.py",
        str(work_repo),
        "-o",
        "z-test-git-w-1-remote.txt"
    ]
    ec = git_status_report.main(args)

    assert ec == 0


def test_git_w_2_remotes(tmp_path: Path):
    work_repo = tmp_path / "a"
    work_repo.mkdir()
    assert work_repo.exists()

    file_a = work_repo / "a.txt"
    file_a.write_text("Hey, everyone!")

    assert git_status_report.run_git(
        work_repo, ["init", "-b", "main"]
    ).returncode == 0
    assert work_repo.joinpath('.git').exists()

    assert git_status_report.run_git(
        work_repo, ["add", "a.txt"]
    ).returncode == 0

    result = git_status_report.run_git(
        work_repo, ["status"]
    )
    assert result.returncode == 0
    assert "Untracked" not in result.stdout

    assert git_status_report.run_git(
        work_repo, ["commit", "-m", '"Initial commit."']
    ).returncode == 0

    #  First remote.

    remote_1 = tmp_path / "b.git"
    remote_1.mkdir()
    assert remote_1.exists()

    assert git_status_report.run_git(
        remote_1, ["init", "-b", "main", "--bare"]
    ).returncode == 0
    assert remote_1.joinpath('HEAD').exists()

    assert git_status_report.run_git(
        work_repo, ["remote", "add", "origin", str(remote_1)]
    ).returncode == 0

    assert git_status_report.run_git(
        work_repo, ["push", "-u", "origin", "main"]
    ).returncode == 0

    #  Second remote.

    remote_2 = tmp_path / "c.git"
    remote_2.mkdir()
    assert remote_2.exists()

    assert git_status_report.run_git(
        remote_2, ["init", "-b", "main", "--bare"]
    ).returncode == 0
    assert remote_2.joinpath('HEAD').exists()

    assert git_status_report.run_git(
        work_repo, ["remote", "add", "backup", str(remote_2)]
    ).returncode == 0

    assert git_status_report.run_git(
        work_repo, ["push", "-u", "backup", "main"]
    ).returncode == 0

    args = [
        "git_status_report.py",
        str(work_repo),
        "-o",
        "z-test-git-w-2-remotes.txt"
    ]
    ec = git_status_report.main(args)

    assert ec == 0


def test_no_git_repo(tmp_path: Path):
    d = tmp_path / "no_repos"
    d.mkdir()
    assert d.exists()

    rpt = git_status_report.process_repos(d)

    assert rpt is not None
    assert "No repositories found" in rpt.rpt_text()


def test_not_a_git_repo(tmp_path: Path):
    d = tmp_path / "a"
    d.mkdir()
    p = d / ".git"
    p.mkdir()
    assert p.exists()

    rpt = git_status_report.process_repos(d)
    assert rpt is not None

    s = rpt.rpt_text()
    print(s)
    assert "ERROR (" in s

    t = rpt.err_text()
    print(t)
    assert "ERRORS" in t

    # assert 0
