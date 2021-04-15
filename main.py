#!/usr/bin/python

import argparse
import json
import pathlib
import shlex
import stat
import subprocess
import time

from testparser import printSomething
from util import (allowExecutablePermissions, getFilesWithExtension,
                  subprocessCheckOutput, subprocessPopen, subprocessRun)


def runTest(testScript, outputFile):
    testArgs = shlex.split(testScript)

    testFile = pathlib.Path(testArgs[0]).absolute()
    workingDir = testFile.parent

    with open(outputFile, 'w') as f:
        subprocess.run([str(testFile)] + testArgs[1:],
                       stdout=f, text=True, cwd=str(workingDir))


def runTestWithStressNg(testScript, outputFolder, configurations):
    for i, config in enumerate(configurations):
        currentLogFile = outputFolder / f"{i}.txt"

        stressNgCommand = f"stress-ng --cpu {config['cpuWorkers']} --cpu-load {config['cpuLoad']} --vm {config['vmWorkers']} --vm-bytes {config['vmBytes']}%"
        stressNgSubprocess = subprocessPopen(stressNgCommand)

        time.sleep(1)

        runTest(testScript, currentLogFile)

        stressNgSubprocess.kill()


def startEmulator(avd):
    # Emulator
    emulatorCommand = f"emulator -avd {avd} -no-boot-anim -no-snapshot"
    subprocessPopen(emulatorCommand, subprocess.DEVNULL)

    # Start adb
    subprocessRun('adb start-server', subprocess.DEVNULL)

    # Waiting for the emulator
    bootCompleted = False

    while not bootCompleted:
        time.sleep(5)
        result = subprocessCheckOutput('adb shell getprop sys.boot_completed')

        if result == '1':
            print('boot completed')
            bootCompleted = True


def stopEmulator():
    # Cleanup
    subprocessRun('adb emu kill', subprocess.DEVNULL)
    subprocessRun('adb kill-server', subprocess.DEVNULL)


def main(args):
    # Create output folder
    if args.output_folder == None:
        outputFolder = pathlib.Path('./output')
    else:
        outputFolder = pathlib.Path(args.output_folder)

    outputFolder.mkdir(parents=True, exist_ok=True)

    configFile = pathlib.Path(__file__).parent / 'stressConfigurations.json'
    testScript = args.test_script

    startEmulator(args.avd)

    if not args.no_stress:
        with open(configFile) as jsonFile:
            configurations = json.load(jsonFile)

        runTestWithStressNg(testScript, outputFolder, configurations)
    else:
        currentLogFile = outputFolder / f"no-stress.txt"
        runTest(testScript, currentLogFile)

    stopEmulator()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('avd',
                        help='specify Android Virtual Device')

    parser.add_argument('test_script', help='specify test script')

    parser.add_argument('--no-stress',
                        help="don't use stress-ng", action="store_true")

    parser.add_argument('-o', '--output-folder',
                        help="specify output folder")

    args = parser.parse_args()

    main(args)
