from remote.environment import LocalEnvironment, SSHEnvironment, LSFEnvironment
from remote.environment import RunStatus

import os.path
import shutil
import pytest
import time
import paramiko

@pytest.fixture()
def runtime_directory(tmpdir_factory):
    directory = tmpdir_factory.mktemp('test_tmp')
    yield directory
    shutil.rmtree(str(directory))

def _test_generic_environment(environment, interval):
    environment.start("id1", ["echo", "test message"])
    assert environment.wait(["id1"], interval = interval)

    assert environment.get_stdout("id1").read() == b"test message\n"
    assert environment.get_status("id1") == RunStatus.FINISHED
    environment.clean("id1")

    environment.start("id2", ["sh", "$/54"])
    assert environment.wait(["id2"], interval = interval)
    assert environment.get_status("id2") == RunStatus.FAILED
    environment.clean("id2")

    environment.clean_assets("cid1")
    assert not environment.has_asset("cid1", "path/to/my_remote_asset.txt")
    environment.add_asset("cid1", "path/to/my_remote_asset.txt", "my_asset.txt")
    assert environment.has_asset("cid1", "path/to/my_remote_asset.txt")

    environment.start("id3", ["cat", environment.get_asset("cid1", "path/to/my_remote_asset.txt")])
    assert environment.wait(["id3"], interval = interval)
    assert environment.get_stdout("id3").read() == b"This is my asset.\n"

def test_local_environment(runtime_directory):
    environment = LocalEnvironment(str(runtime_directory))
    _test_generic_environment(environment, 1e-3)

def test_ssh_environment():
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.connect("ivt-nama.ethz.ch")

    try:
        environment = SSHEnvironment(client, "/nas/shoerl/envtest")
        _test_generic_environment(environment, 1e-3)
    finally:
        client.close()

def test_euler_environment():
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.connect("euler")

    try:
        environment = LSFEnvironment(client, "/cluster/home/shoerl/envtest")
        _test_generic_environment(environment, 1.0)
    finally:
        client.close()











#
