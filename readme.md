# SDR Transmitter for Raspi
RaspberryPiと拡張基板（All mode transmitter HAT）で430Mhz帯でSDRでPSK/QPSKなどの変調を行い高周波を出力します．

RaspberryPi and an extension board (All mode transmitter HAT) perform modulation such as PSK/QPSK with SDR in the 430Mhz band and output high frequency.

## 動作確認した環境
## Confirmed environment
Raspi3B+　RaspberryPi OS(bullseye)

# HATの構成と動作
# HAT configuration and operation
## IQ信号
## IQ signal
IQ信号をRaspiのI2Sに出力してステレオDAC CS4350により差動アナログ信号に変換します．
CS4350は192kHzサンプリングまで対応しています．

The IQ signal is output to Raspi's I2S and converted to a differential analog signal by the stereo DAC CS4350.
The CS4350 supports up to 192kHz sampling.

現在のバージョンではIQ信号のパスにコンデンサが入っているので直流を送ることはできません．
つまり、0の連続、1の連続が長く続くデータの送信はできません．
通常はビット同期をとるための反転があるので問題になることはないでしょう．

In the current version, there is a capacitor in the path of the IQ signal, so it is not possible to send DC.
In other words, it is not possible to send data that has a long series of 0's or 1's.
Usually there is an inversion for bit synchronization, so this shouldn't be a problem.

IQ変調なのでIQ信号の大きさにより高周波出力の大きさを変えることができます．
IQ信号の大きさはソフトで設定できます．（音量ボリュームのように）

Since it is IQ modulation, the magnitude of the high frequency output can be changed according to the magnitude of the IQ signal.
The magnitude of the IQ signal can be set by software. (like volume)

IQ信号を大きくしすぎると歪んでしまうので小さくする方に使ってください．

If the IQ signal is made too large, it will be distorted, so please use it to make it smaller.


## 変調/VCO/PLL
## Modulation/VCO/PLL

TIのtrf372017を使っています．
trf372017はデータシートによればIQ変調器、VCO、PLLを内蔵している3G/4G向けのICチップでIQ信号により変調された高周波信号が得られます．
trf372017の制御はSPI経由です．

TI's trf372017 is used.
According to the datasheet, the trf372017 is an IC chip for 3G/4G with built-in IQ modulator, VCO, and PLL, and can obtain high-frequency signals modulated by IQ signals.
Control of trf372017 is via SPI.

VCOの最低周波数は300MHzですので144MHz帯での送信はできません．（仕様の上限は4.8GHzです．私にとっては十分過ぎます）
430MHz帯を10kHzステップで送信できるようになっています．

Since the minimum frequency of VCO is 300MHz, transmission in the 144MHz band is not possible. (Upper spec is 4.8GHz, more than enough for me)
The 430MHz band can be transmitted in 10kHz steps.


送信周波数やステップ周波数を変更する場合はtrf372017_PLL.pngを参考にしてください．
IQ変調器の帯域は160MHzありますがごくわずかしか使っていません．192k/160M=0.12% .....

Please refer to trf372017_PLL.png when changing the transmission frequency and step frequency.
The bandwidth of the IQ modulator is 160MHz, but it is used very little. 192k/160M=0.12%.....

高周波出力は測定していませんが0dBm以下でしょう．

I haven't measured the high frequency output, but it should be less than 0dBm.

詳しくは回路図や基板図を見てください．

For details, see the circuit diagram and board diagram.

# ソフトウェア
# Software

変調信号の生成と送信するソフトはGnuradio版とpython版があります．

You can choose between Gnuradio version and python version for generating and transmitting modulated signals.

## python版
# python version

sdr_transmitter_raspi.py　をコマンドラインから実行してください．

Run sdr_transmitter_raspi.py from the command line.
~~~
$ python sdr_transmitter_raspy.py
~~~

周波数プロンプトが表示されたらコマンドを入力できます．PLLがロックしていれば緑色、ロックが外れていれば赤色になります．数字は送信周波数をステップ単位にした周波数です．
"help" でコマンドのリストを表示します．

You can enter commands when the frequency prompt appears. It will be green if the PLL is locked and red if it is unlocked. The numbers are the frequencies in steps of the transmission frequency.
"help" displays a list of commands.

python版ではbpsk16kbpsからqpsk128kbpsまでの10種類から選べます．

In the python version, you can choose from 10 types from bpsk16kbps to qpsk128kbps.

次は操作の一例です.

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

現在の設定では送信周波数は430MHz帯で10kHzステップで設定できます．( Integer Modeのみです)

設定を変更することで周波数やステップを変更できますがその場合は回路の定数の変更が必要になるかも知れません．詳しくはtrf372017のデータシートを参照してください．

With the current settings, the transmission frequency can be set in 10kHz steps in the 430MHz band. (Integer Mode only)

You can change the frequency and steps by changing the settings, but in that case you may need to change the constants of the circuit. See the trf372017 datasheet for details.

なお、このソフトはSPIのレジスタのread-backには対応しておらず、読み出しはできません．

Note that this software does not support read-back of SPI registers and cannot be read.

## Gnuradio版
## Gnuradio version
Ver3.8で動作を確認しました．

I confirmed the operation with Ver3.8.

フローグラフ bpsk.grc をGnuradioで開いてください．bpsk 64kbpsで送信するサンプルです．

Open the flow graph bpsk.grc with Gnuradio. This is a sample to send at bpsk 64kbps.

周波数などtrf372017の設定はEmbddedBlock(Ctrl trf372017)で行います．
あなたのプロジェクトではサンプルプロジェクトbpsk.grcを改変するかEmbddedBlock(Ctrl trf372017)をコピー＆ペーストしてください．

生成したIQ信号はAudio Sinkに流し込みます.Sample Rateは48kHz、96kHz、192kHzのいずれかにしてください．

Set trf372017 such as frequency with EmbeddedBlock(Ctrl trf372017).
Modify the sample project bpsk.grc or copy and paste EmbddedBlock(Ctrl trf372017) in your project.

Send the generated IQ signal to the Audio Sink, and set the Sample Rate to 48kHz, 96kHz, or 192kHz.


192kHzサンプリングで 3 samples/symbolの場合、64k symbols/secondになります．

3 samples/symbol at 192kHz sampling results in 64k symbols/second.

# インストール手順
# Installation instructions

## raspi
1. /boot/config.txt
編集してSPIとI2Sを有効にしてI2S のドライバを有効にします．

Edit /boot/config.txt to enable SPI and I2S and enable I2S driver.

/boot/config.txt　の関係する箇所

Relevant parts of /boot/config.txt
~~~
dtparam=i2s=on
dtoverlay=hifiberry-dac
dtparam=spi=on
~~~

なお、ヘッドホンジャックやHDMI出力は特に理由がない限り無効にしておくのがよさげです．
確認のために音を出して確認するのはできますが音量を絞っておいてください．
（IQ信号はハイレゾですが心地よい音楽とは言えません！　耳を傷めないように注意してください．）

I2S出力はサウンドデバイスのdefaultとしてください．
再生デバイスは aplay -l　で確認できます．

複数の再生デバイスがある場合、I2S出力HifiBerryをdefaultにしてください．

In addition, it is a good idea to disable the headphone jack and HDMI output unless there is a particular reason.
You can make a sound for confirmation, but please turn down the volume.
(The IQ signal is high resolution, but it's not pleasant music! Please be careful not to damage your ears.)

Set the I2S output as the default for the sound device.
You can check the playback device with aplay -l.

If you have multiple playback devices, set the I2S output HifiBerry to default.

2. モジュールのインストール
    
    Module installation

    python版ではライブラリ、モジュールのインストールが必要です

    The python version requires the installation of libraries and modules

~~~
$ sudo apt install libatlas-base-dev 
$ sudo apt install libportaudio2 libportaudiocpp0 portaudio19-dev 
$ pip install spidev matplotlib scikit-commpy pyaudio sounddevice 
~~~

numpy のバージョンが違うと言われたら

If you have a messege the version of numpy is different

~~~
$ sudo pip install numpy --upgrade 
~~~

Gnuradio版ではまずGnuradioをインストールします．

For the Gnuradio version, first install Gnuradio.

~~~
sudo apt install gnuradio
~~~
自分の環境では3.8.2が入りました．

3.8.2 entered in my environment.

Embedded Block のためにPYTHONPATH を通します．

Pass PYTHONPATH for Embedded Block.

~~~
$ cd
$ nano .profile
~~~

下記を最後に追加します（一例です）

Add the following at the end (just an example)

~~~
# trf372017 python module path
export PYTHONPATH="/home/hogehoge/sdr_tx:$PYTHONPATH"
~~~ 

環境により必要なライブラリやモジュールは違うことがあるかも知れません．

The required libraries and modules may differ depending on the environment.

# 実行
# Execution
    
    
## Gnuradioの場合
##  For Gnuradio
パスを通した任意のディレクトリに必要なファイルを置きます．

Place the necessary files in any directory path set.

必要なファイル：

Required files:

bpsk.grc epy_block_0.py trf372017_raspi.py

Gnuradio-Companion からbpsk.grc を開き、実行します．

Open bpsk.grc from Gnuradio-Companion and run it.

## Pythonの場合
## For Python
必要なファイル：

Required files:

sdr_transmitter_raspi.py trf372017_raspi.py psk_raspi.py

ターミナルで sdr_transmitter_raspi.py を実行します．
Open a terminal and run sdr_transmitter_raspi.py.

~~~
$ python sdr_transmitter_raspi.py
~~~
初期化ができてプロンプトが表示されたらコマンドを入力して設定や送信ができます．
コマンドリストはhelp で表示されます．
ヒストリ機能が使えます．

Once the initialization is complete and the prompt appears, you can enter commands to configure and send.
The command list is displayed by help.
You can use the history function.

Have A Fun!