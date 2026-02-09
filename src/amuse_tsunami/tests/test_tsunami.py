from amuse.support.testing.amusetest import TestWithMPI

from amuse.community.tsunami.interface import tsunamiInterface, tsunami

class tsunamiInterfaceTests(TestWithMPI):

    def test_echo_int(self):
        instance = tsunamiInterface()
        result,error = instance.echo_int(12)
        self.assertEquals(error, 0)
        self.assertEquals(result, 12)
        instance.stop()
