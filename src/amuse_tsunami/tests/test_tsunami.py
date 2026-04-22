from amuse.support.testing.amusetest import TestWithMPI

from amuse_tsunami.interface import TsunamiInterface, Tsunami

class TestTsunamiInterface(TestWithMPI):

    def test_echo_int(self):
        instance = TsunamiInterface()

        instance.stop()


class TestTsunami(TestWithMPI):
