import subprocess as sp
import os.path
import time
import logging
import shutil
import paramiko
from paramiko.ssh_exception import SSHException
import re
import json

class RunStatus:
    SCHEDULED = "scheduled"
    STARTED = "started"
    FINISHED = "finished"
    FAILED = "failed"
    STOPPED = "stopped"

    def is_alive(status):
        return not status in [RunStatus.FAILED, RunStatus.STOPPED, RunStatus.FINISHED]

class RunEnvironment:
    def start(self, identifier, command):
        raise NotImpementedError()

    def stop(self, identifier):
        raise NotImpementedError()

    def clean(self, identifier):
        raise NotImpementedError()

    def get_status(self, identifier):
        raise NotImplementedError()

    def get_file(self, identifier, path):
        raise NotImplementedError()

    def get_stdout(self, identifier):
        raise NotImplementedError()

    def get_stderr(self, identifier):
        raise NotImplementedError()

    def wait(self, identifiers, interval = 1.0, limit = None):
        try:
            iter(identifiers)
        except TypeError:
            identifiers = [identifiers]

        remaining = list(identifiers)
        wait_time = 0.0

        while True:
            for identifier in remaining[:]:
                if not RunStatus.is_alive(self.get_status(identifier)):
                    remaining.remove(identifier)

            if len(remaining) == 0:
                return True

            if not limit is None and wait_time > limit:
                return False

            time.sleep(interval)
            wait_time += interval

class LocalEnvironment(RunEnvironment):
    def __init__(self, runtime_directory):
        self.runtime_directory = runtime_directory

        self.processes = {}
        self.status = {}

        self.logger = logging.getLogger("remote.environment.LocalEnvironment")

        if not self.runtime_directory.startswith("/"):
            raise RuntimeError("Runtime directory should be absolute: %s" % runtime_directory)

        if not os.path.exists(self.runtime_directory):
            raise RuntimeError("Local directory does not exist: %s" % runtime_directory)

    def start(self, identifier, command):
        run_path = "%s/%s" % (self.runtime_directory, identifier)
        runtime_path = "%s/run" % run_path

        os.mkdir(run_path)
        os.mkdir(runtime_path)

        stdout = open("%s/stdout.log" % run_path, "w+")
        stderr = open("%s/error.log" % run_path, "w+")

        self.processes[identifier] = sp.Popen(command, stdout = stdout, stderr = stderr, cwd = runtime_path)
        self.status[identifier] = RunStatus.STARTED
        self.logger.info("Started run %s" % identifier)

        return True

    def _ping(self):
        updates = {}

        for identifier, status in self.status.items():
            if RunStatus.is_alive(status):
                process = self.processes[identifier]
                return_code = process.poll()

                if not return_code is None:
                    if return_code == 0:
                        updates[identifier] = RunStatus.FINISHED
                    else:
                        updates[identifier] = RunStatus.FAILED

        for identifier, status in updates.items():
            self.logger.info("Updated status of run %s to %s" % (identifier, status))

        self.status.update(updates)

    def stop(self, identifier):
        self._ping()

        if RunStatus.is_alive(self.status[identifier]):
            self.processes[identifier].terminate()
            self.status[identifier] = RunStatus.STOPPED

        logger.info("Stopped run %s" % identifier)

    def clean(self, identifier):
        self._ping()

        if RunStatus.is_alive(self.status[identifier]):
            self.stop(identifier)

        run_path = "%s/%s" % (self.runtime_directory, identifier)
        shutil.rmtree(run_path)

        del self.status[identifier]
        del self.processes[identifier]

        self.logger.info("Cleaned run %s" % identifier)

    def get_status(self, identifier):
        self._ping()
        return self.status[identifier]

    def get_stdout(self, identifier):
        run_path = "%s/%s" % (self.runtime_directory, identifier)
        return open("%s/stdout.log" % run_path, "rb")

    def get_stderr(self, identifier):
        run_path = "%s/%s" % (self.runtime_directory, identifier)
        return open("%s/stderr.log" % run_path, "rb")

    def get_file(self, path, mode = "r"):
        runtime_path = "%s/%s/run" % (self.runtime_directory, identifier)
        return open("%s/%s" % (runtime_path, path), mode)

class SSHEnvironment(RunEnvironment):
    def __init__(self, client, runtime_directory):
        self.runtime_directory = runtime_directory

        if not self.runtime_directory.startswith("/"):
            raise RuntimeError("Runtime directory should be absolute: %s" % runtime_directory)

        self.pids = {}
        self.status = {}

        self.logger = logging.getLogger("remote.environment.SSHEnvironment")

        self.client = client
        self.sftp = None

        return_code, output, error = self._call(["ls", self.runtime_directory], False)

        if return_code != 0:
            raise RuntimeError("Remote directory does not exist: %s" % self.runtime_directory)

        self._recover_state()

    def _recover_state(self):
        return_code, output, error = self._call(["cat", "state.json"], raise_error = False)

        if return_code == 0:
            state = json.loads(output)
            self.status = state["status"]
            self.pids = state["pids"]

    def _update_state(self):
        state = dict(pids = self.pids, status = self.status)
        state = json.dumps(state)
        self._call(["echo", state], pipe_path = "state.json")

    def _escape(self, command):
        if command.strip() == "&":
            return command.strip()

        if command.strip() == "|":
            return command.strip()

        return '"' + command.replace('"', '\\"') + '"'

    def _call(self, command, raise_error = True, cwd = None, pipe_path = None, pipe_append = False):
        command = " ".join(map(self._escape, command))
        command = "cd \"%s\" && %s" % (self.runtime_directory if cwd is None else cwd, command)

        if pipe_path is not None:
            command += " >> " if pipe_append else " > "
            command += "\"%s\"" % pipe_path

        channel = self.client.get_transport().open_session()
        channel.exec_command(command)

        # Useful for debugging
        # print(command)

        stdout = b""
        while True:
            chunk = channel.recv(1024)
            stdout += chunk
            if len(chunk) == 0: break

        stderr = b""
        while True:
            chunk = channel.recv_stderr(1024)
            stderr += chunk
            if len(chunk) == 0: break

        return_code = channel.recv_exit_status()

        if return_code != 0 and raise_error:
            raise RuntimeError("Error: %s" % stderr)

        return return_code, stdout, stderr

    def start(self, identifier, command):
        # Prepare directory
        self._call(["mkdir", "-p", "%s/run" % identifier])

        # Prepare run script
        command = " ".join(map(self._escape, command))
        runtime_path = "%s/%s/run" % (self.runtime_directory, identifier)

        self._call([
            "echo", "%s 1> ../stdout.log 2> ../stderr.log" % command
        ], pipe_path = "run.sh", cwd = runtime_path)

        self._call([
            "echo", 'echo \\$? > ../return_code'
        ], pipe_path = "run.sh", cwd = runtime_path, pipe_append = True)

        # Start run script
        return_code, output, error = self._call([
            "sh", "run.sh", "&", "echo", "$!"
        ], cwd = runtime_path)

        self.pids[identifier] = int(output)
        self.status[identifier] = RunStatus.STARTED
        self._update_state()

    def _ping(self):
        updates = {}

        for identifier, status in self.status.items():
            if RunStatus.is_alive(status):
                pid = self.pids[identifier]
                return_code, output, error = self._call(["kill", "-0", str(pid)], raise_error = False)

                if return_code != 0: # Not running anymore (or no permission)
                    runtime_path = "%s/%s" % (self.runtime_directory, identifier)
                    _, output, error = self._call(["cat", "return_code"], cwd = runtime_path)
                    return_code = int(output)

                    if return_code == 0:
                        updates[identifier] = RunStatus.FINISHED
                    else:
                        updates[identifier] = RunStatus.FAILED

        for identifier, status in updates.items():
            self.logger.info("Updated status of run %s to %s" % (identifier, status))

        self.status.update(updates)
        if len(updates) > 0: self._update_state()

    def stop(self, identifier):
        self._ping()

        if RunStatus.is_alive(self.status[identifier]):
            self._call(["kill", "-9", str(self.pids[identifier])])
            self.status[identifier] = RunStatus.STOPPED
            self._update_state()

        logger.info("Stopped run %s" % identifier)

    def clean(self, identifier):
        self._ping()

        if RunStatus.is_alive(self.status[identifier]):
            self.stop(identifier)

        self._call(["rm", "-rf", "./%s" % identifier])

        del self.status[identifier]
        del self.pids[identifier]

        self.logger.info("Cleaned run %s" % identifier)
        self._update_state()

    def get_status(self, identifier):
        self._ping()
        return self.status[identifier]

    def _open(self, path, mode = "r", cwd = None):
        if self.sftp is None:
            self.sftp = self.client.open_sftp()

        path = "%s/%s" % (self.runtime_directory if cwd is None else cwd, path)
        return self.sftp.file(path, mode)

    def get_stdout(self, identifier):
        return self._open("stdout.log", cwd = "%s/%s" % (self.runtime_directory, identifier))

    def get_stderr(self, identifier):
        return self._open("stderr.log", cwd = "%s/%s" % (self.runtime_directory, identifier))

    def get_file(self, path, mode = "r"):
        return self._open(path, cwd = "%s/%s/run" % (self.runtime_directory, identifier))

class LSFEnvironment(SSHEnvironment):
    def __init__(self, client, runtime_directory):
        SSHEnvironment.__init__(self, client, runtime_directory)

    def start(self, identifier, command):
        # Prepare directory
        self._call(["mkdir", "-p", "%s/run" % identifier])

        # Prepare run script
        command = " ".join(map(self._escape, command))
        runtime_path = "%s/%s/run" % (self.runtime_directory, identifier)

        self._call([
            "echo", "%s 1> ../stdout.log 2> ../stderr.log" % command
        ], pipe_path = "run.sh", cwd = runtime_path)

        self._call([
            "echo", 'echo \\$? > ../return_code'
        ], pipe_path = "run.sh", cwd = runtime_path, pipe_append = True)

        # Schedule run script
        return_code, output, error = self._call([
            "bsub", "-J", "eqasim:%s" % identifier, "sh", "run.sh"
        ], cwd = runtime_path)

        match = re.match("Job <([0-9]+)>", output.decode("utf-8"))

        if not match:
            raise RuntimeError("Could not recover job id from Euler")

        self.pids[identifier] = int(match.group(1))
        self.status[identifier] = RunStatus.SCHEDULED
        self._update_state()

    def _ping(self):
        updates = {}

        for identifier, status in self.status.items():
            _, bjobs, _ = self._call(["bjobs", str(self.pids[identifier])], raise_error = False)
            identifier_status = self.status[identifier]

            if identifier_status == RunStatus.SCHEDULED:
                if not b"PEND" in bjobs:
                    updates[identifier] = RunStatus.STARTED
                    identifier_status = RunStatus.STARTED

            if RunStatus.is_alive(identifier_status):
                if not b"PEND" in bjobs and not b"RUN" in bjobs:
                    runtime_path = "%s/%s/run" % (self.runtime_directory, identifier)
                    return_code, output, error = self._call([
                        "cat", "lsf.o%d" % self.pids[identifier],
                        "|", "grep", "Successfully completed.",
                        "|", "wc", "-l"
                    ], cwd = runtime_path)

                    euler_ok = int(output) == 1

                    return_code, output, error = self._call([
                        "cat", "../return_code"
                    ], cwd = runtime_path)

                    run_ok = int(output) == 0

                    if run_ok and euler_ok:
                        updates[identifier] = RunStatus.FINISHED
                    else:
                        updates[identifier] = RunStatus.FAILED

        for identifier, status in updates.items():
            self.logger.info("Updated status of run %s to %s" % (identifier, status))

        self.status.update(updates)
        if len(updates) > 0: self._update_state()

    def stop(self, identifier):
        self._ping()

        if RunStatus.is_alive(self.status[identifier]):
            self._call(["bkill", str(self.pids[identifier])])
            self.status[identifier] = RunStatus.STOPPED
            self._update_state()

        logger.info("Stopped run %s" % identifier)
