"""
Embedded Python Blocks:

Each time this file is saved, GRC will instantiate the first class it finds
to get ports and parameters of your block. The arguments to __init__  will
be the parameters. All of them are required to have default values!
"""

import numpy as np
from gnuradio import gr
import trf372017_raspi as trf372017


class blk(gr.sync_block):  # other base classes are basic_block, decim_block, interp_block
    """Embedded Python Block example - a simple multiply const"""

    def __init__(self, frequency=433920000):  # only default arguments here
        """arguments to this function show up as parameters in GRC"""
        gr.sync_block.__init__(
            self,
            name='Ctrl trf372017',   # will show up in GRC
            in_sig=None,
            out_sig=None
        )
        # if an attribute with the same name as a parameter is found,
        # a callback is registered (properties work, too).
        self.freq = int(frequency/10000)  # 10kHz step
        self.trf = trf372017.Trf372017(0,0)      # SPI bus=0,device=0
        # VCO auto calibration
        self.trf.set_encal()
        # tx on
        self.trf.set_pwr_txdiv("on")
        self.trf.set_frequency( self.freq)
        

    def work(self, input_items, output_items):
        pass
        
    def __del__(self):
        del self.trf
