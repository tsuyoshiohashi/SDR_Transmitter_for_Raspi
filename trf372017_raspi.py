#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# trf372017_raspi.py
#
# Data sheet: https://www.ti.com/product/TRF372017
#
# This program is for SDR_Transmit_Hat(My own work)
# set registers in trf372017 to control VCO and PLL
# 
# SPI and I2S port in raspi board must be enabled. 
#
# Required file: sdr_transmitter_raspi.py and psk_raspi.py in the same directory
#
# This implementation is for personal experiments.
#
# Copyright (c) 2022 Tsuyoshi Ohashi
# Released under the MIT license
# https://opensource.org/licenses/mit-license.php
# 

import spidev
import RPi.GPIO as GPIO
from time import sleep

class Trf372017:
    # lock detect port
    lock_detect_port = 4    # GPIO4,pin7
    # Frequency Range   10kHz Step
    nint_min = 43001    # 430.01 MHz
    nint_max = 43999    # 439.99 MHz
    freq_default = 43392    # 433.92MHz
    freq_step = 10000       # 10kHz
    # Register 1
    rdiv = 500      # 20MHz(fREF_OSC)/40kHz(fPFD) = 500
    ref_inv = 0     # up edge
    neg_vco = 1     # negative slope
    icp = 0b01010   # 0.97mA
    icpdouble = 0   # not double
    cal_clk_sel = 0x3   # Scaling Factor is 16 (Table.13)
                        # fPFD is 40kHz, CAL_CLK_FREQUENCY is 640kHz > 0.1MHz 
    rsv = 0
    # Register 2
    nint = 43392        # fRF=430-440MHz,fRFSTEPSIZE=10kHz
    pll_div_sel = 0b01  # PLL FREQUENCY DIVIDER is 2
    prsc_sel = 1    # 1, 1->8/9, 0->4/5
    vco_sel = 0b00  # lowest frequency
    vcosel_mode = 0 # Auto select vco and capacitor
    cal_acc = 0b00  # error count
    en_cal = 0      # Execute VCO auto-cal
    # Register 3 
    nfrac = 0x00    # disuse
    # Register 4
    pwd_pll = 0     # on
    pwd_cp = 0      # on
    pwd_vco = 0     # on
    pwd_vcomux = 0  # on
    pwd_div124 =0   # on
    pwd_presc = 0   # on
    pwd_out_buff = 1    # off  LO output buffer, disuse
    pwd_lo_div = 1  # off, disuse
    pwd_tx_div = 1  # off, 
    pwd_bb_vcm = 0  # OFF(1): VCM Disable, ON(0) VCM Enable
    pwd_dc_off = 1  # OFF
    en_ext_vco = 0  # disable
    en_isource = 0  # off fractional mode only
    ld_ana_prec = 0b11  # integer mode=00  # LOW(11) better??
    cp_tristate = 0b00  # Normal
    speedup = 0
    ld_dig_prec = 1 # 0: normal, 1:long time
    en_dith = 1     # 
    mod_ord = 0b01  # DISUSE
    dith_sel = 0
    del_sd_clk = 0b01   # DISUSE
    en_frac = 0     # No, 
    # Register 5
    vcobias_rtrim = 0b100
    pllbias_rtrim = 0b10
    vco_bias = 0b0101   # 400uA,VCC_VCO2=3.3V
    vcobuf_bias = 0b10
    vcomux_bias = 0b11
    bufout_bias = 0b00      # LO OUT
    vco_cal_ib = 0
    vco_cal_ref = 0b010
    vco_ampl_ctrl = 0b11
    vco_vb_ctrl = 0b00
    en_ld_isource = 0
    # Register 6
    ioff = 0x80
    qoff = 0x80
    vref_sel = 0b100    # recommended[100], 0.65V[000], 1V[111]
    tx_div_sel = 0b11   # Div8
    lo_div_sel = 0b11   # Div8
    tx_div_bias = 0b10  # 50uA
    lo_div_bias = 0b10  # 50uA
    # Register 7
    vco_trim = 0x20     # used in manual cal mode
    vco_test_mode = 0
    cal_bypass = 0
    mux_ctrl = 0b001    # Lock Detect pin5
    isource_sink = 0
    isource_trim = 0b100
    pd_tc = 0b00
    ib_vcm_sel = 0  # PTAT(Proportional To Absolute Temperature) recommended
    dcoffset_i = 0b10   # 150uA input DC offset
    vco_bias_sel = 1    #
    # Register 0
    count_mode_mux_sel = 0  # minimun frequency( target is 430MHz band)
    
    # CS4350 /RESET port
    cs_reset_port = 5   # GPIO5,pin29
    
    def __init__(self, bus=0, dev=0):
        
        try:
            self.spi = spidev.SpiDev()
            self.spi.open(bus, dev)
            self.spi.max_speed_hz = 100000  # 100khz
            self.spi.mode = 0
            print("SPI BUS:", bus, " DEV:", dev)
        except:
            print("SPI Error")
            exit(1)
            
        # port numbering, bcm mode
        GPIO.setmode(GPIO.BCM)
        # init lock detect io port
        GPIO.setup(self.lock_detect_port, GPIO.IN)
        
        # init CS4350 Reset port
        GPIO.setup(self.cs_reset_port, GPIO.OUT)
        sleep(0.5)
        GPIO.output(self.cs_reset_port, GPIO.LOW )
        sleep(0.5)
        GPIO.output(self.cs_reset_port, GPIO.HIGH )
        
        # set registers default 
        self.set_reg1()
        self.set_reg2()
        self.set_reg4()
        self.set_reg5()
        self.set_reg6()
        self.set_reg7()
    # Detect PLL Lock
    def get_ld(self):
        return( GPIO.input(self.lock_detect_port))
    # set register
    def set_reg1(self,debug=0):
        if(debug):
            print("set reg1")
        self.reg1 = 0x9 | \
            (self.rdiv << 5) | (self.ref_inv << 19) | (self.neg_vco << 20) | \
            (self.icp << 21) | (self.icpdouble << 26) | (self.cal_clk_sel << 27) | (self.rsv << 31)
        self.reg1_l = self.swapbit2byte(self.reg1)
        self.spi.xfer2(self.reg1_l)
    
    def set_reg2(self,debug=0):
        if(debug):
            print("set reg2")
        self.reg2 = 0xa | \
            (self.nint << 5) | (self.pll_div_sel << 21) | (self.prsc_sel << 23) | \
            (self.vco_sel << 26) | (self.vcosel_mode << 28) | (self.cal_acc << 29) | (self.en_cal << 31)
        self.reg2_l = self.swapbit2byte(self.reg2)
        self.spi.xfer2(self.reg2_l)
        
    def set_reg4(self,debug=0):
        if(debug):
            print("set reg4")
        self.reg4 = 0x0c | \
            (self.pwd_pll << 5) | (self.pwd_cp << 6) | ( self.pwd_vco << 7) | \
            (self.pwd_vcomux << 8) | (self.pwd_div124 << 9) | (self.pwd_presc << 10) | \
            (self.pwd_out_buff << 12) | (self.pwd_lo_div << 13) | (self.pwd_tx_div << 14) | \
            (self.pwd_bb_vcm << 15) | (self.pwd_dc_off << 16) | (self.en_ext_vco << 17) | \
            (self.en_isource << 18) | ( self.ld_ana_prec << 19) | (self.cp_tristate << 21) | \
            (self.speedup << 23) | (self.ld_dig_prec << 24) | (self.en_dith << 25) | \
            (self.mod_ord << 26) | (self.dith_sel << 28) | (self.del_sd_clk << 29) | \
            (self.en_frac << 31)
        self.reg4_l = self.swapbit2byte(self.reg4)
        self.spi.xfer2(self.reg4_l)
        
    def set_reg5(self,debug=0):
        if(debug):
            print("set reg5")
        self.reg5 = 0xd | \
            (self.vcobias_rtrim << 5) | (self.pllbias_rtrim << 8) | (self.vco_bias << 10) | \
            (self.vcobuf_bias << 14) | (self.vcomux_bias << 16) | (self.bufout_bias << 18) | \
            (1 << 21) | (self.vco_cal_ib << 22) | ( self.vco_cal_ref << 23) | \
            (self.vco_ampl_ctrl << 26) | (self.vco_vb_ctrl << 28) | (self.en_ld_isource << 31)
        self.reg5_l = self.swapbit2byte(self.reg5)
        self.spi.xfer2(self.reg5_l)
        
    def set_reg6(self,debug=0):
        if(debug):
            print("set reg6")
        self.reg6 = 0xe | \
            (self.ioff << 5) | (self.qoff << 13) | (self.vref_sel << 21) | (self.tx_div_sel << 24) | \
            (self.lo_div_sel << 26) | (self.tx_div_bias << 28) | (self.lo_div_bias << 30)
        self.reg6_l = self.swapbit2byte(self.reg6)
        self.spi.xfer2(self.reg6_l)
        
    def set_reg7(self,debug=0):
        if(debug):
            print("set reg7")
        self.reg7 = 0xf | \
            (self.vco_trim << 7) | (self.vco_test_mode << 14) | (self.cal_bypass << 15) | \
            (self.mux_ctrl << 16) | (self.isource_sink << 19) | (self.isource_trim << 20) | \
            (self.pd_tc << 23) | (self.ib_vcm_sel << 25 ) | (1 << 28 ) | (self.dcoffset_i << 29) | (self.vco_bias_sel) << 31
        self.reg7_l = self.swapbit2byte(self.reg7)
        self.spi.xfer2(self.reg7_l)
        
    ### ......can't read reg0.....
    def get_reg(self,reg_no,debug=0):
        self.reg_no = 0x07 & reg_no
        if(debug):
            print("get reg:",self.reg_no)
        self.reg0 = 0x8 | \
            (self.count_mode_mux_sel << 27) | (self.reg_no << 28) | (1 << 31)   # readback mode
        self.reg0_l = self.swapbit2byte(self.reg0)
        self.spi.xfer2(self.reg0_l)
        self.ret = self.spi.xfer2([0x00,0x00,0x00,0x00])
        return(self.ret)
        
    ########  set modulator/pll/vco parameters ########
    def set_icp(self, icp=10):
        self.icp = 0x1f & icp
        self.set_reg1()
        print("ICP=", self.icp )
    
    def set_frequency(self, freq):
        try:
            if(freq < self.nint_min or freq > self.nint_max):
                raise ValueError("Out of Range and 10kHz Step")
            else:
                self.nint = freq    # 10kHz STEP frequency
                self.set_reg2()
                sleep(0.5)
                print("NINT=", self.nint )
        except ValueError as e:
            print(e)
        
    def set_encal(self):
        self.en_cal = 1 # Resets automatically
        self.set_reg2()
        sleep(0.5)
        print("Execute VCO freq Auto-Calibration:", self.en_cal)
       
    # Reg4
    def set_pwr_pll(self,onoff,detail=False):
        self.pwd_pll = 1 if(onoff.lower() == "off") else 0   # 1=all pll blocks off
        self.set_reg4()
        sleep(0.5)
        if(detail):
            print("PWD_PLL:", self.pwd_pll)
    
    def set_pwr_cp(self,onoff,detail=False):
        self.pwd_cp = 1 if(onoff.lower() == "off") else 0   # 1=charge pump off
        self.set_reg4()
        sleep(0.5)
        if(detail):
            print("PWD_CP:", self.pwd_pll)
        
    def set_pwr_vco(self,onoff,detail=False):
        self.pwd_vco = 1 if(onoff.lower() == "off") else 0   # 1=vco off
        self.set_reg4()
        sleep(0.5)
        if(detail):
            print("PWD_VCO:", self.pwd_vco)
    
    def set_ld_ana_prec(self, prec):
        self.ld_ana_prec = 0x03 & prec
        self.set_reg4()
        print("LD_ANA_PREC:", self.ld_ana_prec)
    
    def set_ld_dig_prec(self, prec):
        self.ld_dig_prec = 0x01 & prec
        self.set_reg4()
        print("LD_DIG_PREC:", self.ld_dig_prec)
        
    def set_pwr_outbuff(self,onoff):
        self.pwd_out_buff = 1 if(onoff.lower() == "off") else 0   # 1=buff off
        self.set_reg4()
        print("PWD_OUT_BUFF:", self.pwd_out_buff)
    
    def set_pwr_lodiv(self,onoff):
        self.pwd_lo_div = 1 if(onoff.lower() == "off") else 0   # 1=tx off
        self.set_reg4()
        print("PWD_LO_DIV:", self.pwd_lo_div)
    
    def set_pwr_txdiv(self,onoff, detail=False):
        self.pwd_tx_div = 1 if(onoff.lower() == "off") else 0   # 1=tx off
        self.set_reg4()
        if(detail):
            print("PWD_TX_DIV:", self.pwd_tx_div)
                
    def set_pwr_bbvcm(self,onoff):
        self.pwd_bb_vcm = 1 if(onoff.lower() == "off") else 0   # 1=tx off
        self.set_reg4()
        print("PWD_BB_VCM:", self.pwd_bb_vcm)
        
    def set_dc_off(self,onoff):
        self.pwd_dc_off = 1 if(onoff.lower() == "off") else 0   # 1=dc offset off
        self.set_reg4()
        print("PWD_DC_OFF:", self.pwd_dc_off)
    # Reg6      
    def set_dc_off_i(self, offset):
        self.ioff = offset
        self.set_reg6()
        print("OFFSET_I: ", self.ioff)
    
    def set_dc_off_q(self, offset):
        self.qoff = offset
        self.set_reg6()
        print("OFFSET_Q: ", self.qoff)

    def get_freq_bits(self):
        print("NINT=", self.nint )
        print("RDIV=", self.rdiv )
    # swap bit order and set byte list
    def swapbit2byte(self, a, debug=0):
        # swap bit
        self.s = bin(a)[2:].zfill(32)
        if(debug):
            print(self.s)
        #print(len(self.s))
        self.ra = self.s[::-1]  # reverse!
        #print(ra)
        self.bytes= []
        for i in range(4):
            self.bits = self.ra[i*8:8+i*8].zfill(8)
            self.bits_i = int(self.bits,2)
            if(debug):
                print( self.bits )
                #print( bits_i )
            self.bytes.append( self.bits_i )
        return(self.bytes)
    
    def __del__(self):
        # Terminate trf operation
        self.set_pwr_txdiv("off")
        self.set_pwr_pll("off")
        self.set_pwr_cp("off")
        self.set_pwr_vco("off")
        # Close SPI
        self.spi.close()
        # Cleanup GPIO
        GPIO.cleanup(self.lock_detect_port)
        GPIO.cleanup(self.cs_reset_port)
        
########
def show_help(trf):
    print("Red prompt is PLL unlock, Green is lock")   
    print("Command List")
    print("icp [0-31]" ,"-> 1.94mA-0.47mA")
    print("freq [", trf.nint_min , "-", trf.nint_max, "]") 
    print("+/-", " -> 10kHz up/down")
    print("tx on|off", "-> tx on/off")
    print("encal", " -> VCO freq Auto Calibration" )
    print("ldana [0-3]", " -> LD_ANA_PREC, 0:high, 3:low" )
    print("lddig [0-1]", " -> LD_DIG_PREC, 0:short, 3:long time" )
    print("pwdpll on|off", "-> power pll on/off")
    print("pwdvco on|off",  "-> power vco on/off")
    print("ioffset  [0-255]", "-> I DC offset")
    print("qoffset  [0-255]",  "-> Q DC offset")

def main():
    on = "on"
    off = "off"
    print("SDR Transmitter starting. rev.f")
    trf = Trf372017(0,0)      # SPI bus=0,device=0
    
    # VCO auto calibration
    trf.set_encal()
    # tx on
    trf.set_pwr_txdiv(on)
    freq = 43300
    trf.set_frequency( freq)
    sleep(1)
    
    # Test
    while(1):
        ld = trf.get_ld()
        #print("LD:",ld)
        p_start = "\033[32m" if (trf.get_ld()) else "\033[31m"   # Lock:Green/ Unlock:Red 
        p_end = "\033[0m"
        p1 = freq
        p2 = ">"
        cmd_line = input( p_start + str(freq) + p2 + p_end)
        cmd = cmd_line.split()

        # frequency
        if( len(cmd)==0):
            pass
        elif(cmd[0] == "freq"):
            freq = int(cmd[1])
            trf.set_frequency(freq)
        elif(cmd[0] == "+"):
            freq += 1
            trf.set_frequency(freq)
        elif(cmd[0] == "-"):
            freq -= 1
            trf.set_frequency(freq)
        # tx on/off
        elif(cmd[0] == "tx"):
            trf.set_pwr_txdiv(on if(cmd[1]=="on") else off)
            print("To generate carrier, I/Q signal is required. For example, play sin/cos sound.")
        # PLL
        elif(cmd[0] == "icp"): # 0=1.94mA, 31=0.47mA, 10=0.97mA
            trf.set_icp( int(cmd[1]))
        elif(cmd[0]=="encal"):
            trf.set_en_cal()
        elif(cmd[0]=="ldana"):
            trf.set_ld_ana_prec( int(cmd[1]))
        # power
        elif(cmd[0]=="pwdpll"):
            trf.set_pwr_pll(on if(cmd[1]=="on") else off)
            print("pwd_pll=", cmd[1])
        elif(cmd[0]=="pwdvco"):
            trf.set_pwr_vco(on if(cmd[1]=="on") else off)
            print("pwd_vco=", cmd[1])
        # I/Q
        elif(cmd[0] == "ioff"): # Iref DC offset
            ioff = 0xff & int(cmd[1])
            trf.set_dc_off_i(ioff)
            print("i_off=", ioff)
        elif(cmd[0] == "qoff"): # Iref DC offset
            qoff = 0xff & int(cmd[1])
            trf.set_dc_off_q(qoff)
            print("q_off=", qoff)
        #
        elif(cmd[0] == "qoff"): # Iref DC offset
            qoff = 0xff & int(cmd[1])
            trf.set_dc_off_q(qoff)
            print("q_off=", qoff)
        # help
        elif(cmd[0]=="?" or cmd[0]=="help" or cmd[0]=="h"):
            show_help(trf)
        # re-start
        elif(cmd[0]=="init"):
            del trf
            sleep(1)
            trf = Trf372017(0,0)      # Re-born
        # Quit
        elif(cmd[0]=="quit" or cmd[0]=="exit" or cmd[0]=="q" or cmd[0]=="e"):
            del trf
            print("Bye!")
            exit()
        else:
            print("???")
            show_help(trf)
    
if __name__ == '__main__':    
    main()

# end of trf372017_raspi.py