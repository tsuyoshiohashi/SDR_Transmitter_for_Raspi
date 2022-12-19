#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# psk_raspi.py
#
# This program is for SDR_Transmit_Hat(My own work)
# generate/transmit PSK signal
# 
# I/Q signal is provided through i2s on raspi
# I2S port in raspi board must be enabled. 
# 
# Required file: trf372017_raspy.py and ctrl_trf372017.py in same directory
# 
# This implementation is for personal experiments.
#
# Copyright (c) 2022 Tsuyoshi Ohashi
# Released under the MIT license
# https://opensource.org/licenses/mit-license.php
#

import numpy as np
import sys
import os
import matplotlib.pyplot as plt
import commpy as cp

import pyaudio
import sounddevice as sd
import threading

class PskMod:

    gain_default = 0.5
    
    def __init__(self,gain=0.5, mod=2,fs=192000,sps=6,alpha=0.35,n_tap=11):
        self.gain = gain    # IQ signal is about 0.4V at trf372
        self.fs = fs         # sampling frequency (48000,96000,192000)
        self.sps = sps       # samples per symbol
        self.aplha = alpha  
        self.tap = n_tap*sps
        self.ts = 1/fs*sps  # symbol period
        self.sr = fs/sps    # symbol rate
        # bpsk modulator has 2 symbols
        # qpsk modulator has 4 symbols
        self.psk_mod = cp.modulation.PSKModem(mod)
        self.list_modulation = [2,4]
    
    def set_gain(self, gain):
        if(gain>0 and gain <1):
            self.gain = gain
    
    def __call__(self,bits,disp_l):
        self.modulate(bits,disp_l)
            
    def modulate(self, bits, disp_l=0):
        self.bits = bits
        self.disp_l = disp_l
        #print(self.bits)
        # modulate bit into IQ symbols
        self.symbols = self.psk_mod.modulate(self.bits)
        # up-conversion
        #self.symbols_upsampled = np.zeros(self.sps*(len(self.symbols)-1)+1,dtype = np.complex64) 
        #self.symbols_upsampled[::self.sps] = self.symbols
        self.symbols_upsampled = cp.utilities.upsample(self.symbols, self.sps)
        #print(len(self.symbols))
        #print(self.symbols_upsampled)
        
        # RRF filter
        self.rrc_filter = cp.filters.rrcosfilter(self.tap, alpha=self.aplha, Ts=self.ts, Fs=self.fs)[1]
        # Complex signal
        self.signal = np.convolve(self.rrc_filter, self.symbols_upsampled)
        # get IQ signal and adjust gain
        self.sig_i = self.signal.real * self.gain
        self.sig_q = self.signal.imag * self.gain

        # convert 2-channel data to sounddevice stereo form
        self.sig_iq = np.column_stack((self.sig_i, self.sig_q))
        
        # Now we play IQ signal
        play_seconds = len(self.sig_i)/self.fs
        print("fs=", self.fs, "sps=", self.sps)
        print("bits=", len(self.bits), "symbols=", len(self.symbols), "samples=", len(self.sig_i), "time= ", play_seconds)
        
        #### sounddevice, simple ####
        sd.default.device = 0   # BCM283 I2S PLAYBACK HARDWARE
        sd.play(self.sig_iq, self.fs)
        sd.wait()
        ##########################################################
        
        #### py audio Callback mode ####
        """
        #### py audio Blocking Mode ####
        chunk = 512    #   1024
        #CHANNELS = 2
        #RATE = self.fs
        
        self.sig_iq32 = self.sig_iq.astype(np.float32)  # upto 32
        
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paFloat32,
                        channels=2,
                        rate=self.fs,
                        input=False,
                        output=True,
                        output_device_index=0,  #BCM2835 playback device
                        frames_per_buffer=chunk)

        for i in range(0, int(self.fs / chunk * play_seconds)):
            stream.write(self.sig_iq32, chunk)

        stream.stop_stream()
        stream.close()
        p.terminate()
        """
        """
        #### sound device callback ####
        sd.default.device = 0   # BCM2835 playback hardware
        sd.default.blocksize = 1024
        #print("play time:", self.ts * len(self.sig_iq)/self.sps)
        event = threading.Event()
        try:
            self.current_frame = 0
            time = len(self.sig_i)*self.ts
            ####
            def callback(outdata, frames, time, status):
                #if status:
                #    print(status)
                chunksize = min(len(self.sig_iq) - self.current_frame, frames)
                outdata[:chunksize] = self.sig_iq[self.current_frame:self.current_frame + chunksize]
                if chunksize < frames:
                    outdata[chunksize:] = 0
                    raise sd.CallbackStop()
                self.current_frame += chunksize

            stream = sd.OutputStream(
                samplerate=self.fs, channels=2, callback=callback, finished_callback=event.set)
            with stream:
                event.wait()  # Wait until playback is finished
        except:
            print(type(e).__name__ + ': ' + str(e))
        """
        ##############################################################
        # display IQ wave
        if(self.disp_l):
            self.x = np.arange(len(self.sig_i))
            plt.plot(self.x[:self.disp_l],self.sig_i[:self.disp_l], label="I sig")
            plt.plot(self.x[:self.disp_l],self.sig_q[:self.disp_l], label="Q sig")
            plt.legend()
            plt.show()
    def __del__(self):
        pass
        #print(".")
################################################
def main():
    
    if(len(sys.argv) == 3):
        if(sys.argv[1]=="bpsk32"):      # 32kbps
            sps = 6
            modulator = PskMod(mod=2,fs=192000, sps=sps) 
        elif(sys.argv[1]=="bpsk48"):    # 48kbps
            sps = 4
            modulator = PskMod(mod=2,fs=192000, sps=sps) 
        elif(sys.argv[1]=="bpsk64"):     # 64kbps
            sps = 3
            modulator = PskMod(fs=192000, sps=sps)    
        elif(sys.argv[1]=="bpsk16"):    # 16kbps
            modulator = PskMod(mod=2,fs=96000, sps=6)    
        elif(sys.argv[1]=="bpsk24"):    # 24kbps
            modulator = PskMod(mod=2,fs=96000, sps=4)    
        elif(sys.argv[1]=="qpsk64"):    # QPSK64kbps
            modulator = PskMod(mod=4,fs=192000, sps=6)
        else:
            # set others 16kbps
            modulator = PskMod(fs=96000, sps=6)    
        
        N = int(sys.argv[2])    # bits length
    else:       # Other argc, set 
        print("Usage:",  os.path.basename(__file__) , " modulator(bpsk32/qpsk64...S) N(bit length)")
        exit()
    
    bits = np.random.randint(0, 2, N)
    print("Data: ", bits)
    # display all samples=N*sps
    modulator.modulate(bits,disp_l=N*sps)

if __name__ == '__main__':
    main()
    
# End of psk_raspi.py