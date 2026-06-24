from amuse.support.testing.amusetest import TestWithMPI

from amuse.community.arepo.interface import ArepoInterface, Arepo

class ArepoInterfaceTests(TestWithMPI):

    def test_echo_int(self):
        instance = ArepoInterface()
        result,error = instance.echo_int(12)
        self.assertEquals(error, 0)
        self.assertEquals(result, 12)
        instance.stop()
