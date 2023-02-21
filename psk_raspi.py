#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# psk_raspi.py
#
# This program is for SDR_Transmit_Hat(My own work, See hat directory)
# Generate/transmit BPSK, QPSK, pi/2 Shift BPSK, pi/4 Shift QPSK, OQPSK
# Symbol rate is (192k)/N (N>=3, 2 might work).
# Sampling rate is 192kHz.
# I/Q signal is provided through i2s on raspi
# I2S port in raspi board must be enabled and set default sound device. 
#
# Required file: trf372017_raspy.py and ctrl_trf372017.py in the same directory.
#
# This implementation is for personal experiments.
#
# Copyright (c) 2022-2023 Tsuyoshi Ohashi
# Released under the MIT license
# https://opensource.org/licenses/mit-license.php
#  

import numpy as np
import sys
import os
import matplotlib.pyplot as plt
import commpy as cp

#import pyaudio
import sounddevice as sd
#import threading

class PskMod:

    gain_default = 0.5
    
    def __init__(self,gain=0.5, mod="bpsk",fs=192000,sps=6,alpha=0.35,n_tap=11):
        self.gain = gain    # IQ signal is about 0.4V at trf372
        self.fs = fs         # sampling frequency (48000,96000,192000)
        self.sps = sps       # samples per symbol
        self.aplha = alpha  
        self.tap = n_tap*sps
        self.ts = 1/fs*sps  # symbol period
        self.sr = int(fs/sps)    # symbol rate
        self.mod = mod
        if(self.mod=="bpsk"):
            # bpsk modulator has 2 symbols
            self.psk_mod = cp.modulation.PSKModem(2)
        elif(self.mod=="qpsk"):
            # qpsk modulator has 4 symbols
            self.psk_mod = cp.modulation.PSKModem(4)
    
    def set_gain(self, gain):
        if(gain>=0 and gain <=1):
            self.gain = gain
    
    def __call__(self,bits,disp_l):
        self.modulate(bits,disp_l)
    
    # oqpsk modulator
    def oq_mod(self, bits):
        self.bits = bits
        self.len = np.sqrt(2)/2
        self.symbols = np.array([], dtype=np.complex64)    # array for modulation symbols
        
        self.sym = 1 + 1j # start with dummy symbol 
        self.symbols = np.append(self.symbols, self.sym)
        for i in range(0, len(self.bits), 2):
            if(self.bits[i]==0 ):
                self.sym = 1 + self.symbols[-1].imag*1j
            else:
                self.sym = -1 + self.symbols[-1].imag*1j
            self.symbols = np.append(self.symbols, self.sym)
            #print(i, self.bits[i], self.sym)
            
            if(self.bits[i+1]==0 ):
                self.sym = self.symbols[-1].real +1j
            else:
                self.sym = self.symbols[-1].real -1j
            self.symbols = np.append(self.symbols, self.sym)
            #print(i+1, self.bits[i+1], self.sym)
        return(self.symbols)
        
    # pi/4 shift qpsk modulator
    def pi4_mod(self, bits):
        self.bits = bits
        self.len = np.sqrt(2)/2
        self.sym_table = {0:1, 1:(1+1j)*self.len, 2:1j, 3:(-1+1j)*self.len, 4:-1, 5:(-1-1j)*self.len, 6:-1j, 7:(1-1j)*self.len}
        self.symbols = np.array([])    # array for modulation symbols

        self.phase = 0  # Phase absolute location
        for i in range(0, len(self.bits), 2):
            if(self.bits[i]==0 and self.bits[i+1]==0):      # 1/4
                self.phase += 1
            elif(self.bits[i]==0 and self.bits[i+1]==1):    # 3/4
                self.phase += 3
            elif(self.bits[i]==1 and self.bits[i+1]==0):    # -1/4
                self.phase += 7
            else:                                           # -3/4
                self.phase += 5
            self.phase = self.phase % 8
            self.sym = self.sym_table[self.phase]
            #print(self.bits[i],self.bits[i+1], self.phase, self.sym)
            self.symbols = np.append(self.symbols, self.sym)
        return(self.symbols)

    # pi/2 shift bpsk modulator
    def pi2_mod(self,bits):
        self.bits = bits
        
        self.sym_table = {0:1, 1:1j, 2:-1, 3:-1j}
        self.symbols = np.array([])    # array for modulation symbols

        self.phase = 0  # Phase absolute location
        for i in range(0, len(self.bits)):
            if(self.bits[i]==0):      # 1/2
                self.phase += 1
            else:                     # -1/2
                self.phase += 3
            self.phase = self.phase % 4
            self.sym = self.sym_table[self.phase]
            #print(self.bits[i], self.phase, self.sym)
            self.symbols = np.append(self.symbols, self.sym)
        return(self.symbols)

    # make symbol / up sampling / rrc filter / transmit through sound / display wave, constellation
    def modulate(self, bits, disp_l=0):
        self.bits = bits
        self.disp_l = disp_l
        #print(self.bits)
        
        # bpsk/ qpsk
        if(self.mod=="bpsk" or self.mod=="qpsk"):
            # modulate bit into IQ symbols
            self.symbols = self.psk_mod.modulate(self.bits)
        # pi/2 shift bpsk
        elif(self.mod=="pi2bpsk"):
            self.symbols = self.pi2_mod(self.bits)
        # pi/4 shift qpsk
        elif(self.mod=="pi4qpsk"):
            self.symbols = self.pi4_mod(self.bits)
        # oqpsk
        elif(self.mod=="oqpsk"):
            self.symbols = self.oq_mod(self.bits)
        else:
            print("unkown modulation type")
            return(False)
        # up-conversion
        #self.symbols_upsampled = np.zeros(self.sps*(len(self.symbols)-1)+1,dtype = np.complex64) 
        #self.symbols_upsampled[::self.sps] = self.symbols
        self.symbols_upsampled = cp.utilities.upsample(self.symbols, self.sps)
        #print(len(self.symbols))
        #print(self.symbols_upsampled)
        
        # RRC filter
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
        print("fs=", self.fs, "sps=", self.sps, "symbol_rate=", self.sr)
        print("bits=", len(self.bits), "symbols=", len(self.symbols), "samples=", len(self.sig_i), "time= {:.6f}".format(play_seconds))
        
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
        # display Constellation
        if(self.disp_l):
            plt.scatter(self.sig_i, self.sig_q, marker=".", alpha=0.5)
            plt.title("constellation")
            #plt.legend()
            plt.show()
            
    def __del__(self):
        pass
        #print(".")
        

############## for test ##################################
def main():
    
    if(len(sys.argv) == 3):
        # bpsk
        if(sys.argv[1]=="bpsk32"):      # 32kbps / 32ksps
            sps = 6
            modulator = PskMod(mod="bpsk",fs=192000, sps=sps)
        #qpsk
        elif(sys.argv[1]=="qpsk32"):    # 32kbps / 16ksps
            sps = 12
            modulator = PskMod(mod="qpsk",fs=192000, sps=sps)
        elif(sys.argv[1]=="qpsk64"):    # 64kbps / 32ksps
            sps = 6
            modulator = PskMod(mod="qpsk",fs=192000, sps=sps)
        # pi/2 shift bpsk
        elif(sys.argv[1]=="pi2bpsk16"):      # 16kbps / 16ksps
            sps = 12
            modulator = PskMod(mod="pi2bpsk",fs=192000, sps=sps) 
        elif(sys.argv[1]=="pi2bpsk32"):    # 32kbps / 32ksps 
            sps = 6
            modulator = PskMod(mod="pi2bpsk",fs=192000, sps=sps) 
        # pi/4 shift qpsk
        elif(sys.argv[1]=="pi4qpsk32"):    # 32kbps / 16ksps
            sps = 12
            modulator = PskMod(mod="pi4qpsk",fs=192000, sps=sps) 
        elif(sys.argv[1]=="pi4qpsk64"):     # 64kbps / 32ksps
            sps = 6
            modulator = PskMod(mod="pi4qpsk", fs=192000, sps=sps)
        # OQPSK Offset QPSK
        elif(sys.argv[1]=="oqpsk16"):    # 16kbps / 16ksps
            sps = 12
            modulator = PskMod(mod="oqpsk",fs=192000, sps=sps)
        elif(sys.argv[1]=="oqpsk32"):    # 32kbps / 32ksps
            sps = 6
            modulator = PskMod(mod="oqpsk",fs=192000, sps=sps)
        elif(sys.argv[1]=="oqpsk64"):    # 64kbps / 64ksps
            sps = 3
            modulator = PskMod(mod="oqpsk",fs=192000, sps=sps) 
        else:
            print("unknown modulator type.")
            exit()

        N = int(sys.argv[2])    # bits length
    else:       # Other argc, set 
        print("Usage:",  os.path.basename(__file__) , " modulator(bpsk32/qpsk64...oqpsk64) N(bit length)")
        exit()
    
    bits = np.random.randint(0, 2, N)
    print("Data: ", bits)
    # display all samples=N*sps
    modulator.modulate(bits,disp_l=N*sps)

if __name__ == '__main__':
    main()
    
# End of psk_raspi.py