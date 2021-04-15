import pathlib
import shlex
import stat
import subprocess


def subprocessRun(command, stdout=None, cwd=None):
    args = shlex.split(command)

    # print(arguments)
    # print(stdout)

    return subprocess.run(args, stdout=stdout, text=True, cwd=cwd)


def subprocessPopen(command, stdout=None, cwd=None):
    args = shlex.split(command)

    # print(arguments)
    # print(stdout)

    return subprocess.Popen(args, stdout=stdout, text=True, cwd=cwd)


def subprocessCheckOutput(command):
    args = shlex.split(command)

    # print(arguments)

    return subprocess.run(args, text=True, capture_output=True).stdout.strip()


def getFilesWithExtension(path, extension):
    return pathlib.Path(path).glob(extension)


def allowExecutablePermissions(files):
    for file in files:
        file.chmod(file.stat().st_mode | stat.S_IEXEC)
