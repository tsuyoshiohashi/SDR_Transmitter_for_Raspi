# SDR Transmitter for Raspi
RaspberryPi and an extension board (All mode transmitter HAT) perform modulation such as PSK/QPSK with SDR in the 430Mhz band and output high frequency.

## Confirmed environment
Raspi3B+　RaspberryPi OS(bullseye)

# HAT configuration and operation
## IQ signal
The IQ signal is output to Raspi's I2S and converted to a differential analog signal by the stereo DAC CS4350.
The CS4350 supports up to 192kHz sampling.

In the current version, there is a capacitor in the path of the IQ signal, so it is not possible to send DC.
In other words, it is not possible to send data that has a long series of 0's or 1's.
Usually there is an inversion for bit synchronization, so this shouldn't be a problem.

Since it is IQ modulation, the magnitude of the high frequency output can be changed according to the magnitude of the IQ signal.
The magnitude of the IQ signal can be set by software. (like volume)

If the IQ signal is made too large, it will be distorted, so please use it to make it smaller.

## Modulation/VCO/PLL

TI's trf372017 is used.
According to the datasheet, the trf372017 is an IC chip for 3G/4G with built-in IQ modulator, VCO, and PLL, and can obtain high-frequency signals modulated by IQ signals.
Control of trf372017 is via SPI.

Since the minimum frequency of VCO is 300MHz, transmission in the 144MHz band is not possible. (Upper spec is 4.8GHz, more than enough for me)
The 430MHz band can be transmitted in 10kHz steps.

Please refer to trf372017_PLL.png when changing the transmission frequency and step frequency.
The bandwidth of the IQ modulator is 160MHz, but it is used very little. 192k/160M=0.12%.....

I haven't measured the high frequency output, but it should be less than 10dBm. (P1dB=11dBm)

For details, see the circuit diagram and board diagram.

# Software
You can choose between Gnuradio version and python version for generating and transmitting modulated signals.

# python version
Required files:
sdr_transmitter_raspi.py trf372017_raspi.py psk_raspi.py

Run sdr_transmitter_raspi.py from the command line.
~~~
$ python sdr_transmitter_raspy.py
~~~

Once the initialization is done,You can enter commands when the frequency prompt appears. It will be green if the PLL is locked and red if it is unlocked. The numbers are the frequencies in steps of the transmission frequency.
You can use the history function.
"help" displays a list of commands.

In the python version, you can choose from 10 types from bpsk16kbps to qpsk128kbps.

The following is an example of operation.

~~~
$ python sdr_transmitter_raspi.py 
SDR Transmitter for Raspi(trf372017) 192k Rev.j
SPI BUS: 0  DEV: 0
dataExecute VCO freq Auto-Calibration: 1
NINT= 43392
43392>data r
Data type: random
43392>len 2048
bit length= 2048
43392>repeat 2
repeat= 2
43392>freq 43393
NINT= 43393
43393>tx bpsk32
modulation type: bpsk32
Tranmit w/ bpsk32 2048 bits 2 times
fs= 192000 sps= 6
bits= 2048 symbols= 2048 samples= 12353 time=  0.06433854166666667
fs= 192000 sps= 6
bits= 2048 symbols= 2048 samples= 12353 time=  0.06433854166666667
43393>q
Bye!

~~~

With the current settings, the transmission frequency can be set in 10kHz steps in the 430MHz band. (Integer Mode only)

You can change the frequency and steps by changing the settings, but in that case you may need to change the constants of the circuit. See the trf372017 datasheet for details.

Note that this software does not support read-back of SPI registers and cannot be read.

## Gnuradio version

I confirmed the operation with Ver3.8.

Required files:
bpsk.grc epy_block_0.py trf372017_raspi.py

Place the necessary files in any directory path set.

Open the flow graph bpsk.grc with Gnuradio. This is a sample to send at bpsk 64kbps.

Set trf372017 such as frequency with EmbeddedBlock(Ctrl trf372017).
Modify the sample project bpsk.grc or copy and paste EmbddedBlock(Ctrl trf372017) in your project.

Send the generated IQ signal to the Audio Sink, and set the Sample Rate to 48kHz, 96kHz, or 192kHz.

3 samples/symbol at 192kHz sampling results in 64k symbols/second.

# Installation instructions

## raspi
1. /boot/config.txt

Edit /boot/config.txt to enable SPI and I2S and enable I2S driver.

Relevant parts of /boot/config.txt
~~~
dtparam=i2s=on
dtoverlay=hifiberry-dac
dtparam=spi=on
~~~

In addition, it is a good idea to disable the headphone jack and HDMI output unless there is a particular reason.
You can make a sound for confirmation, but please turn down the volume.
(The IQ signal is high resolution, but it's not pleasant music! Please be careful not to damage your ears.)

Set the I2S output as the default for the sound device.
You can check the playback device with aplay -l.

If you have multiple playback devices, set the I2S output HifiBerry to default.

2. Module installation

    The python version requires the installation of libraries and modules
~~~
$ sudo apt install libatlas-base-dev 
$ sudo apt install libportaudio2 libportaudiocpp0 portaudio19-dev 
$ pip install spidev matplotlib scikit-commpy pyaudio sounddevice 
~~~

If you have a messege the version of numpy is different

~~~
$ sudo pip install numpy --upgrade 
~~~

For the Gnuradio version, first install Gnuradio.

~~~
sudo apt install gnuradio
~~~

3.8.2 entered in my environment.

Pass PYTHONPATH for Embedded Block.

~~~
$ cd
$ nano .profile
~~~

Add the following at the end (just an example)

~~~
# trf372017 python module path
export PYTHONPATH="/home/hogehoge/sdr_tx:$PYTHONPATH"
~~~ 

The required libraries and modules may differ depending on the environment.

Have A Fun!