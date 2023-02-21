# Changes
psk_raspi.py : 変調方式に pi/2 shift BPSK, pi/4 shift QPSK, OQPSK を追加しました．

sdr_transmitter_raspy.py : psk_raspi.py の変更に合わせました．

readme.md / readme_JP.md : 記述の見直しと変調方式の追加に合わせて更新しました．

# SDR Transmitter for Raspi
RaspberryPiと拡張基板（All mode transmitter HAT、自作）で430Mhz帯等でSDRでPSK/QPSKなどの変調を行い高周波を出力します．

## 動作確認した環境
Raspi3B+　Raspberry Pi OS(bullseye)

# HATの構成と動作
## IQ信号
IQ信号をRaspiのI2Sに出力してステレオDAC CS4350により差動アナログ信号に変換します．
CS4350は192kHzサンプリングまで対応しています．

現在のバージョンではIQ信号のパスにコンデンサが入っているので直流を送ることはできません．
つまり、0の連続、1の連続が長く続くデータの送信はできません．
通常はビット同期をとるための反転があるので問題になることはないでしょう．
また、直流分を必要とする変調も出来ません．（例えば位相変位が１８０度より小さなBPSKとか）

IQ変調なのでIQ信号の大きさにより高周波出力の大きさを変えることができます．
IQ信号の大きさはソフトで設定できます．（音量ボリュームのように）

IQ信号を大きくしすぎると歪んでしまうので小さくする方に使ってください．

## 変調/VCO/PLL

TIのtrf372017を使っています．
trf372017はデータシートによればIQ変調器、VCO、PLLを内蔵している3G/4G向けのICチップでIQ信号により変調された高周波信号が得られます．
trf372017の制御はSPI経由です．

VCOの最低周波数は300MHzですので144MHz帯での送信はできません．（仕様の上限は4.8GHzです．私にとっては十分過ぎます）
430MHz帯を10kHzステップで送信できるようになっています．

送信周波数やステップ周波数を変更する場合はtrf372017_PLL.pngを参考にしてください．
IQ変調器の帯域は160MHzありますがごくわずかしか使っていません．192k/160M=0.12% .....orz

高周波出力は測定していませんが10dBm以下でしょう．(P1dB=11dBm)

詳しくは回路図や基板図を見てください．

# ソフトウェア
変調信号の生成と送信するソフトはGnuradio版とpython版があります．
同一ではありません．

## python版
sdr_transmitter_raspi.py　をコマンドラインから実行してください．

~~~
$ python sdr_transmitter_raspy.py
~~~

周波数プロンプトが表示されたらコマンドを入力できます．PLLがロックしていればD2 LEDが緑色、ロックが外れていれば赤色になります．数字は送信周波数をステップ単位にした周波数です．
"help" でコマンドのリストを表示します．

python版ではbpsk16kbpsからqpsk128kbps までの10種類に加えて、pi/2 shift bpsk、pi/4 shift qpsk の各速度とOQPSKを選べます．OQPSKではスタガリングのために64kbps(64kSymbol/Sec)に制限されます．

次は操作の一例です.

~~~
$ python sdr_transmitter_raspi.py
SDR Transmitter for Raspi(trf372017) 192k sampling, pi shift Rev.k
SPI BUS: 0  DEV: 0
Execute VCO freq Auto-Calibration: 1
NINT= 43392
43392>data r
Data type: random
43392>len 4096
bit length= 4096
43392>repeat 2
repeat= 2
43392>freq 43393
NINT= 43393
43393>tx bpsk32
modulation type: bpsk32
Tranmit w/ bpsk32 4096 bits 2 times
fs= 192000 sps= 6
bits= 4096 symbols= 4096 samples= 24641 time=  0.12833854166666667
fs= 192000 sps= 6
bits= 4096 symbols= 4096 samples= 24641 time=  0.12833854166666667
43393>tx pi4qpsk64
modulation type: pi4qpsk64
Tranmit w/ pi4qpsk64 4096 bits 2 times
fs= 192000 sps= 6
bits= 4096 symbols= 2048 samples= 12353 time=  0.06433854166666667
fs= 192000 sps= 6
bits= 4096 symbols= 2048 samples= 12353 time=  0.06433854166666667
43393>q
Bye!

~~~

現在の設定では送信周波数は430MHz帯で10kHzステップで設定できます．( Integer Modeのみです)

設定を変更することで周波数やステップを変更できますがその場合は回路の定数の変更が必要になるかも知れません．詳しくはtrf372017のデータシートを参照してください．

なお、このソフトはSPIのレジスタのread-backには対応しておらず、読み出しはできません．

psk_raspi.py 単独でも動かすことができます．trf372017での送信はしませんがIQ波形などを表示します．詳しくはソースを見てください．

## Gnuradio版
Ver3.8で動作を確認しました．

フローグラフ bpsk.grc をGnuradioで開いてください．bpsk 64kbpsで送信するサンプルです．

周波数などtrf372017の設定はEmbddedBlock(Ctrl trf372017)で行います．
あなたのプロジェクトではサンプルプロジェクトbpsk.grcを改変するかEmbddedBlock(Ctrl trf372017)をコピー＆ペーストしてください．

生成したIQ信号はAudio Sinkに流し込みます.Sample Rateは48kHz、96kHz、192kHzのいずれかにしてください．

192kHzサンプリングで 3 samples/symbolの場合、64k symbols/secondになります．

# インストール手順
## raspi
1. /boot/config.txt
編集してSPIとI2Sを有効にしてI2S のドライバを有効にします．

/boot/config.txt　の関係する箇所
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

2. モジュールのインストール
    python版ではライブラリ、モジュールのインストールが必要です
~~~
$ sudo apt install libatlas-base-dev 
$ sudo apt install libportaudio2 libportaudiocpp0 portaudio19-dev 
$ pip install spidev matplotlib scikit-commpy pyaudio sounddevice 
~~~

numpy のバージョンが違うと言われたら

~~~
$ sudo pip install numpy --upgrade 
~~~

Gnuradio版ではまずGnuradioをインストールします．

~~~
sudo apt install gnuradio
~~~
自分の環境では3.8.2が入りました．

Embedded Block のためにPYTHONPATH を通します．

~~~
$ cd
$ nano .profile
~~~

下記を最後に追加します（一例です）
~~~
# trf372017 python module path
export PYTHONPATH="/home/hogehoge/sdr_tx:$PYTHONPATH"
~~~ 

環境により必要なライブラリやモジュールは違うことがあるかも知れません．

# 実行
    
## Gnuradioの場合
パスを通した任意のディレクトリに必要なファイルを置きます．

必要なファイル：
bpsk.grc epy_block_0.py trf372017_raspi.py

Gnuradio-Companion からbpsk.grc を開き、実行します．

## Pythonの場合
必要なファイル：
sdr_transmitter_raspi.py trf372017_raspi.py psk_raspi.py

ターミナルで sdr_transmitter_raspi.py を実行します．

~~~
$ python sdr_transmitter_raspi.py
~~~
初期化ができてプロンプトが表示されたらコマンドを入力して設定や送信ができます．
コマンドリストはhelp で表示されます．
ヒストリ機能が使えます．(ホームディレクトリに.ctrl_trf_history ファイルができます)

Have A Fun!