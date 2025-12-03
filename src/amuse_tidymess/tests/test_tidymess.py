from amuse.support.testing.amusetest import TestWithMPI

from amuse.community.tidymess.interface import tidymessInterface, tidymess

class tidymessInterfaceTests(TestWithMPI):

    def test_echo_int(self):
        instance = tidymessInterface()
        result,error = instance.echo_int(12)
        self.assertEquals(error, 0)
        self.assertEquals(result, 12)
        instance.stop()
