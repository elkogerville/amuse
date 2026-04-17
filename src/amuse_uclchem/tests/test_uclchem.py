from amuse.support.testing.amusetest import TestWithMPI

from amuse_uclchem.interface import UclchemInterface, Uclchem
#from amuse_uclchem import Uclchem

class UclchemInterfaceTests(TestWithMPI):

    def test_echo_int(self):
        instance = UclchemInterface()
        print(instance.current_time)
