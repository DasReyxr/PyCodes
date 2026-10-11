import pyvisa

#rm = pyvisa.ResourceManager()   # en Linux sin NI-VISA: pyvisa.ResourceManager('@py')
rm = pyvisa.ResourceManager('@py')
osc = rm.open_resource('ASRL/dev/ttyUSB0::INSTR')
osc.baud_rate = 19200
osc.data_bits = 8
osc.parity = pyvisa.constants.Parity.none
osc.stop_bits = pyvisa.constants.StopBits.one
osc.flow_control = pyvisa.constants.ControlFlow.rts_cts
osc.read_termination = '\n'
osc.write_termination = '\n'
osc.timeout = 5000

print(osc.query('*IDN?'))