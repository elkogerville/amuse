from amuse.support.testing.amusetest import TestWithMPI

from amuse.community.uclchem.interface import uclchemInterface, uclchem

class uclchemInterfaceTests(TestWithMPI):

    def test_echo_int(self):
        instance = uclchemInterface()
        result,error = instance.echo_int(12)
        self.assertEquals(error, 0)
        self.assertEquals(result, 12)
        instance.stop()
