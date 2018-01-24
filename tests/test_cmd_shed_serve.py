import functools
import os
import threading
import time

from planemo import network_util
from .test_utils import (
    CliTestCase,
    skip_if_environ,
    TEST_REPOS_DIR,
)


class ShedServeTestCase(CliTestCase):

    @skip_if_environ("PLANEMO_SKIP_GALAXY_TESTS")
    def test_serve(self):
        port = network_util.get_free_port()
        serve = functools.partial(self._run, port)
        t = threading.Thread(target=serve)
        t.daemon = True
        t.start()
        time.sleep(15)
        assert network_util.wait_net_service("127.0.0.1", port)

    def _run(self, port):
        fastqc_path = os.path.join(TEST_REPOS_DIR, "fastqc")
        test_cmd = [
            "shed_serve",
            "--install_galaxy",
            "--shed_target", "toolshed",
            "--port",
            str(port),
            fastqc_path,
        ]
        self._check_exit_code(test_cmd)
