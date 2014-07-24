
#Install pyvisa, use easy_install for example:
#easy_install pyvisa
import visa

class DP832(object):
    def __init__(self):
        pass

    def conn(self, constr="USB0::0x1AB1::0x0E11::DP8xxxxxxxxxx::INSTR"):
        """Attempt to connect to instrument"""
        self.inst = visa.instrument(constr)

    def identify(self):
        """Return identify string which has serial number"""
        return self.inst.ask("*IDN?")

    def readings(self, channel="CH1"):
        """Read voltage/current/power from CH1/CH2/CH3"""       
        resp = self.inst.ask("MEAS:ALL? %s"%channel)
        resp = resp.split(',')
        dr = {"v":float(resp[0]), "i":float(resp[1]), "p":float(resp[2])}
        return dr

    def dis(self):
        del self.inst

        
if __name__ == '__main__':
    test = DP832()

    #Insert your serial number here / confirm via Ultra Sigma GUI
    test.conn("USB0::0x1AB1::0x0E11::DP8xxxxxxxxxx::INSTR")
    
    print test.readings()
