#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# sdr_transmitter_raspi.py
#
# This program is for SDR_Transmit_Hat(My own work, See  ***)
# set registers in trf372017 to control VCO/PLL and generate/transmit PSK signal
# 
# I/Q signal is provided through i2s on raspi (Max 192k sample/sec)
# SPI and I2C port in raspi board must be enabled. 
#
# Required file: trf372017_raspy.py and psk_raspi.py in same directory
# 
# Terminate the RF output in the experiment.　;-)
#
# This implementation is for personal experiments.
#
# Copyright (c) 2022 Tsuyoshi Ohashi
# Released under the MIT license
# https://opensource.org/licenses/mit-license.php
#

import readline
import os
import numpy as np
from time import sleep
import trf372017_raspi as trf372017
import psk_raspi as pskmod

on = "on"
off = "off"
    
def show_help(trf):
    print("\033[31m Red \033[0m prompt is PLL unlock, \033[32m Green \033[0m is locked.")   
    print("Command List:")
    print("[f | freq] [", trf.nint_min , "-", trf.nint_max, "] -> set frequency") 
    print("+/-", "\t\t -> {:.0f}kHz up/down".format(trf.freq_step/1000))
    print("number   \t -> frequency(10kHz step)")
    print("tx modulator", "\t -> transmit data")
    print("\t\t with modulator(bpsk16/bpsk32/bpsk48/bpsk64/qpsk32/qpsk64/qpsk96/qpsk128)")
    print("data [f | m | r]", "\t -> data pattern, fixed/monotonic/random")
    print("len N", "\t\t -> data length N bits")
    print("disp L", "\t\t -> display IQ wave form during L symbols, 0 means no display")
    print("\t\t\t to move on, press the x in upper right")
    print("repeat N", "\t -> set repeat times of tx")
    print("gain g", "\t\t -> set IQ signal gain (0-1) around 0.5 ")
    
    print("init",  "\t\t -> Restart TRF and DAC chip")
    print("? | help | h ",  "\t\t -> Show this help")
    print("q | e | quit | exit ",  "\t -> Terminate program")
    ### rarely use ### 
    print("encal", "\t\t -> VCO Freq. Auto Calibration" )
    print("icp [0-31]" ,"\t -> 1.94mA-0.47mA")
    print("ldana [0-3]", "\t -> LD_ANA_PREC, 0:high, 3:low" )
    print("lddig [0-1]", "\t -> LD_DIG_PREC, 0:short, 1:long time" )
    print("pwdpll on|off", "\t -> power pll on/off")
    print("pwdcp on|off", "\t -> power charge pump on/off")
    print("pwdvco on|off",  "\t -> power vco on/off")
    print("pwdtx on|off",  "\t -> power tx_div on/off")
    print("ioff  [0-255]", "\t -> I DC offset")
    print("qoff  [0-255]",  "\t -> Q DC offset")
    
def start_trf(trf,freq):
    # VCO auto calibration
    trf.set_encal()
    trf.set_frequency( freq)

### 
def main():
    
    # 192 sampling version
    print("SDR Transmitter for Raspi(trf372017) 192k Rev.j")
    
    # initialize/set default trf372017 registers 
    trf = trf372017.Trf372017(0,0)      # SPI bus=0,device=0
    # set frequency
    freq = trf.freq_default
    #
    start_trf(trf,freq)
    
    # various psk modulators 
    # sps : sample per symbol
    #       
    ### QPSK ####          bps = fs/sps*log2(mod)
    # 32kbps
    qpsk32 = pskmod.PskMod(mod=4, fs=192000, sps=12) 
    # 48kbps
    qpsk48 = pskmod.PskMod(mod=4, fs=192000, sps=8)    
    ## 64kbps
    qpsk64 = pskmod.PskMod(mod=4, fs=192000, sps=6) 
    ## 96kbps
    qpsk96 = pskmod.PskMod(mod=4, fs=192000, sps=4) 
    ## 128kbps
    qpsk128 = pskmod.PskMod(mod=4, fs=192000, sps=3)  
      
    ### BPSK
    # 16kbps
    bpsk16 = pskmod.PskMod(mod=2, fs=192000, sps=12)
    # 24kbps
    bpsk24 = pskmod.PskMod(mod=2, fs=192000, sps=8)
    # 32kbps
    bpsk32 = pskmod.PskMod(mod=2, fs=192000, sps=6) 
    # 48kbps
    bpsk48 = pskmod.PskMod(mod=2, fs=192000, sps=4) 
    # 64kbps
    bpsk64 = pskmod.PskMod(mod=2, fs=192000, sps=3) 
    
    # modulators
    modulators = [bpsk16,bpsk24,bpsk32,bpsk48,bpsk64,qpsk32,qpsk48,qpsk64,qpsk96,qpsk128] 
    modulator_list = ["bpsk16","bpsk24","bpsk32","bpsk48","bpsk64","qpsk32","qpsk48","qpsk64","qpsk96","qpsk128"]  

    gain = modulators[0].gain_default
    #print("gain=", gain)
    
    # command history
    HISTORY_FILE = os.path.expanduser('~/.ctrl_trf_history')
    if os.path.exists(HISTORY_FILE):
        readline.read_history_file(HISTORY_FILE)
    # display IQ wave?
    disp_l = 0  # no display, if set, number of samples(ex.1024)
    # tx repeat count
    repeat = 1
    # modulation bits type
    data_type = "random"
    # length of bits
    len_bits_default = 1024
    len_bits = len_bits_default
    # In detail ?
    detail = False
    # Lets' go!
    while(1):
        # PLL lock detect
        ld = trf.get_ld()
        #print("LD:",ld)
        p_start = "\033[32m" if (trf.get_ld()) else "\033[31m"   # Lock:Green/ Unlock:Red 
        p_end = "\033[0m"
        p1 = trf.nint   # 10kHz frequency
        p2 = ">"
        
        cmd_line = input( p_start + str(p1) + p2 + p_end)
        readline.write_history_file(HISTORY_FILE)
        cmd = cmd_line.split()
        if( len(cmd)==0):
            pass
        # frequency
        elif(cmd[0] == "freq" or cmd[0]=="f"):
            try:
                freq = int(cmd[1])
                trf.set_frequency(freq)
            except:
                print("Usage: >freq frequency(10kHzstep)")            
        elif(cmd[0] == "+"):
            freq += 1
            trf.set_frequency(freq)
        elif(cmd[0] == "-"):
            freq -= 1
            trf.set_frequency(freq)
        elif(cmd[0].isdecimal()):
            freq = int(cmd[0])
            trf.set_frequency(freq)
        # PLL
        elif(cmd[0] == "icp"): # 0=1.94mA, 31=0.47mA, 10=0.97mA
            try:
                trf.set_icp( int(cmd[1]))
            except:
                print("icp: ", trf.icp)
        elif(cmd[0]=="encal"):
            trf.set_encal()
        elif(cmd[0]=="ldana"):
            try:
                trf.set_ld_ana_prec( int(cmd[1]))
            except:
                print("ldana: ", trf.ld_ana_prec)
        elif(cmd[0]=="lddig"):
            try:
                trf.set_ld_dig_prec( int(cmd[1]))
            except:
                print("lddig: ", trf.ld_dig_prec)
        # power down
        elif(cmd[0]=="pwdpll"):
            try:
                trf.set_pwr_pll(on if(cmd[1]=="on") else off)
                #print("pwd_pll=", cmd[1])
            except:
                print("pwd_pll: ", trf.pwd_pll)
        # power down
        elif(cmd[0]=="pwdcp"):
            try:
                trf.set_pwr_cp(on if(cmd[1]=="on") else off)
                #print("pwd_cp=", cmd[1])
            except:
                print("pwd_cp: ", trf.pwd_cp)
        elif(cmd[0]=="pwdvco"):
            try:
                trf.set_pwr_vco(on if(cmd[1]=="on") else off)
                #print("pwd_vco=", cmd[1])
            except:
                print("pwd_vco: ", trf.pwd_vco)
        elif(cmd[0]=="pwdtx"):
            try:
                trf.set_pwr_txdiv(on if(cmd[1]=="on") else off)
                #print("pwd_txdiv=", cmd[1])
            except:
                print("pwd_txdiv: ", trf.pwd_tx_div)
        # I/Q dc offset
        elif(cmd[0] == "ioff"): # Iref DC offset
            try:
                ioff = 0xff & int(cmd[1])
                trf.set_dc_off_i(ioff)
                print("i_off=", ioff)
            except:
                print("i_off=", trf.ioff)
        elif(cmd[0] == "qoff"): # Iref DC offset
            try:
                qoff = 0xff & int(cmd[1])
                trf.set_dc_off_q(qoff)
                print("q_off=", qoff)
            except:
                print("q_off=", trf.qoff)
        # Modulate and transmit data 
        elif(cmd[0] == "tx"):
            try:
                mod_type = cmd[1]
                if(mod_type not in modulator_list):
                    mod_type = modulator_list[0]    # default    
                
            except:
                mod_type = modulator_list[0]
            # 
            print("modulation type:", mod_type)
            
            # data type
            def access_bit(data, num):
                base = int(num // 8)
                shift = int(num % 8)
                # reverse order (MSB first)
                #return (1 if(data[base] << shift & 0x80) else 0  )
                return (data[base] >> shift) & 0x1

            if(data_type=="monotonic"):
                data_bytes = bytes([i%256 for i in range(len_bits//8)])
                bits = [access_bit(data_bytes,i) for i in range(len(data_bytes)*8)]      
                #print(data_bytes)
                
            elif(data_type=="fixed"):
                ### Can't send pure DC ### 
                bits = np.tile([0,1,0,1,0,0,1,1], len_bits//8)
            else:
                bits = np.random.randint(0, 2, len_bits)  
            #print("bits:", bits)
            
            # Now start transmit
            trf.set_pwr_txdiv(on, detail)    
            counter = repeat
            for i, mod_can in enumerate(modulator_list):
                if(mod_type == mod_can):  # found modulator type
                    print("Tranmit w/", mod_type, len_bits, "bits", repeat, "times")
                    modulators[i].set_gain(gain)
                    counter = repeat
                    while(counter):
                        modulators[i].modulate(bits,disp_l=disp_l)
                        counter -=1
                        sleep(0.5)
            # done!
            trf.set_pwr_txdiv(off)
            
        # data pattern
        elif(cmd[0]=="data"):
            if(cmd[1][0]=="f"):
                data_type = "fixed"
            elif(cmd[1][0]=="m"):
                data_type = "monotonic"
            else:
                data_type = "random"
            print("Data type:", data_type)    
        # bits length
        elif(cmd[0]=="len"):
            try:
                len_bits = int(cmd[1])
                if(len_bits < 8):
                    len_bits = 8
            except:
                len_bits = len_bits_default
                
            print("bit length=",len_bits)      
                
        # display IQ wave disp_l samples
        elif(cmd[0]=="disp"):
            try:
                disp_l = int(cmd[1])
            except:
                print("display qty=",disp_l)
        # repeat tx number of times
        elif(cmd[0]=="repeat"):
            try:
                repeat = int(cmd[1])
            except:
                repeat = 1
            print("repeat=",repeat)
        # gain for IQ signal
        elif(cmd[0]=="gain"):
            try:
                gain = float(cmd[1])
            except:
                pass    
            print("gain=", gain)
        # help
        elif(cmd[0]=="?" or cmd[0]=="help" or cmd[0]=="h"):
            show_help(trf)
        elif(cmd[0]=="init"):
            del trf
            trf = trf372017.Trf372017(0,0)      # Reborn
            freq = trf.freq_default
            start_trf(trf,freq)
            
        # Read Register # NOT WORK....
        elif(cmd[0]=="read" or cmd[0]=="rd"):
            try:
                reg_read = int(cmd[1])
            except:
                reg_read = 0
            print("Read reg:", reg_read)
            reg_data = trf.get_reg(reg_read)
            print("Reg Data:", reg_data)
        ## quit/exit
        elif(cmd[0]=="quit" or cmd[0]=="exit" or cmd[0]=="q" or cmd[0]=="e"):
            print("Bye!")
            exit()
        elif(cmd[0]=="detail"):
            detail = True
        elif(cmd[0]=="regulaor"):
            detail = False
        # unknown command
        else:
            print("Sorry,not in command list.")
            show_help(trf)

if __name__ == '__main__':
    
    main()