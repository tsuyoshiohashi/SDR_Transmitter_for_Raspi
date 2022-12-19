#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: BPSK Transmitter
# Author: T.Ohashi
# GNU Radio version: 3.8.2.0

from distutils.version import StrictVersion

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print("Warning: failed to XInitThreads()")

from PyQt5 import Qt
from PyQt5.QtCore import QObject, pyqtSlot
from gnuradio import eng_notation
from gnuradio import qtgui
from gnuradio.filter import firdes
import sip
from gnuradio import audio
from gnuradio import blocks
import numpy
from gnuradio import digital
from gnuradio import filter
from gnuradio import gr
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio.qtgui import Range, RangeWidget
import epy_block_0

from gnuradio import qtgui

class BPSK_Transmitter(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "BPSK Transmitter")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("BPSK Transmitter")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except:
            pass
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "BPSK_Transmitter")

        try:
            if StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
                self.restoreGeometry(self.settings.value("geometry").toByteArray())
            else:
                self.restoreGeometry(self.settings.value("geometry"))
        except:
            pass

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 192000
        self.bit_rate = bit_rate = 64000
        self.sps = sps = int(samp_rate/bit_rate)
        self.samplespersymbol = samplespersymbol = sps
        self.rrc_filter_taps = rrc_filter_taps = firdes.root_raised_cosine(1.0, samp_rate,bit_rate/1, 0.35, 11*sps)
        self.psk = psk = digital.constellation_bpsk().base()
        self.ex_bw = ex_bw = 0.35
        self.data_chooser = data_chooser = 0
        self.bitrate = bitrate = bit_rate
        self.IQ_gain = IQ_gain = 0.5

        ##################################################
        # Blocks
        ##################################################
        # Create the options list
        self._data_chooser_options = (0, 1, )
        # Create the labels list
        self._data_chooser_labels = ('Vector Source', 'Random Source', )
        # Create the combo box
        self._data_chooser_tool_bar = Qt.QToolBar(self)
        self._data_chooser_tool_bar.addWidget(Qt.QLabel('Select Bit Data' + ": "))
        self._data_chooser_combo_box = Qt.QComboBox()
        self._data_chooser_tool_bar.addWidget(self._data_chooser_combo_box)
        for _label in self._data_chooser_labels: self._data_chooser_combo_box.addItem(_label)
        self._data_chooser_callback = lambda i: Qt.QMetaObject.invokeMethod(self._data_chooser_combo_box, "setCurrentIndex", Qt.Q_ARG("int", self._data_chooser_options.index(i)))
        self._data_chooser_callback(self.data_chooser)
        self._data_chooser_combo_box.currentIndexChanged.connect(
            lambda i: self.set_data_chooser(self._data_chooser_options[i]))
        # Create the radio buttons
        self.top_grid_layout.addWidget(self._data_chooser_tool_bar)
        self._IQ_gain_range = Range(0, 1, 0.1, 0.5, 200)
        self._IQ_gain_win = RangeWidget(self._IQ_gain_range, self.set_IQ_gain, 'IQ_gain', "counter_slider", float)
        self.top_grid_layout.addWidget(self._IQ_gain_win)
        self._samplespersymbol_tool_bar = Qt.QToolBar(self)

        if None:
            self._samplespersymbol_formatter = None
        else:
            self._samplespersymbol_formatter = lambda x: str(x)

        self._samplespersymbol_tool_bar.addWidget(Qt.QLabel('Samples/Symbol' + ": "))
        self._samplespersymbol_label = Qt.QLabel(str(self._samplespersymbol_formatter(self.samplespersymbol)))
        self._samplespersymbol_tool_bar.addWidget(self._samplespersymbol_label)
        self.top_grid_layout.addWidget(self._samplespersymbol_tool_bar)
        self.qtgui_time_sink_x_0_0 = qtgui.time_sink_f(
            32, #size
            samp_rate/sps, #samp_rate
            "Base", #name
            1 #number of inputs
        )
        self.qtgui_time_sink_x_0_0.set_update_time(0.10)
        self.qtgui_time_sink_x_0_0.set_y_axis(-1, 1)

        self.qtgui_time_sink_x_0_0.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0_0.enable_tags(True)
        self.qtgui_time_sink_x_0_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_0_0.enable_autoscale(True)
        self.qtgui_time_sink_x_0_0.enable_grid(False)
        self.qtgui_time_sink_x_0_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_0_0.enable_control_panel(False)
        self.qtgui_time_sink_x_0_0.enable_stem_plot(False)


        labels = ['Signal 1', 'Signal 2', 'Signal 3', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_time_sink_x_0_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_0_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_0_win = sip.wrapinstance(self.qtgui_time_sink_x_0_0.pyqwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_time_sink_x_0_0_win)
        self.qtgui_time_sink_x_0 = qtgui.time_sink_c(
            32*sps, #size
            samp_rate, #samp_rate
            "IQ", #name
            1 #number of inputs
        )
        self.qtgui_time_sink_x_0.set_update_time(0.10)
        self.qtgui_time_sink_x_0.set_y_axis(-1, 1)

        self.qtgui_time_sink_x_0.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0.enable_tags(True)
        self.qtgui_time_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_0.enable_autoscale(True)
        self.qtgui_time_sink_x_0.enable_grid(False)
        self.qtgui_time_sink_x_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_0.enable_control_panel(False)
        self.qtgui_time_sink_x_0.enable_stem_plot(False)


        labels = ['Signal 1', 'Signal 2', 'Signal 3', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(2):
            if len(labels[i]) == 0:
                if (i % 2 == 0):
                    self.qtgui_time_sink_x_0.set_line_label(i, "Re{{Data {0}}}".format(i/2))
                else:
                    self.qtgui_time_sink_x_0.set_line_label(i, "Im{{Data {0}}}".format(i/2))
            else:
                self.qtgui_time_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_win = sip.wrapinstance(self.qtgui_time_sink_x_0.pyqwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_time_sink_x_0_win)
        self.qtgui_const_sink_x_0 = qtgui.const_sink_c(
            1024, #size
            "", #name
            1 #number of inputs
        )
        self.qtgui_const_sink_x_0.set_update_time(0.10)
        self.qtgui_const_sink_x_0.set_y_axis(-1, 1)
        self.qtgui_const_sink_x_0.set_x_axis(-1, 1)
        self.qtgui_const_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, "")
        self.qtgui_const_sink_x_0.enable_autoscale(False)
        self.qtgui_const_sink_x_0.enable_grid(False)
        self.qtgui_const_sink_x_0.enable_axis_labels(True)


        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "red", "red", "red",
            "red", "red", "red", "red", "red"]
        styles = [0, 0, 0, 0, 0,
            0, 0, 0, 0, 0]
        markers = [0, 0, 0, 0, 0,
            0, 0, 0, 0, 0]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_const_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_const_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_const_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_const_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_const_sink_x_0.set_line_style(i, styles[i])
            self.qtgui_const_sink_x_0.set_line_marker(i, markers[i])
            self.qtgui_const_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_const_sink_x_0_win = sip.wrapinstance(self.qtgui_const_sink_x_0.pyqwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_const_sink_x_0_win)
        self.epy_block_0 = epy_block_0.blk(frequency=433920000)
        self.digital_symbol_sync_xx_0 = digital.symbol_sync_cc(
            digital.TED_MUELLER_AND_MULLER,
            sps,
            0.045,
            1.0,
            1.0,
            1.5,
            1,
            digital.constellation_qpsk().base(),
            digital.IR_MMSE_8TAP,
            128,
            [])
        self.digital_costas_loop_cc_0 = digital.costas_loop_cc(0.0628, 2, True)
        self.digital_constellation_modulator_0 = digital.generic_mod(
            constellation=psk,
            differential=False,
            samples_per_symbol=int(samp_rate/bit_rate),
            pre_diff_code=True,
            excess_bw=ex_bw,
            verbose=False,
            log=False)
        self.blocks_vector_source_x_0 = blocks.vector_source_b((1024*[0b01010011]), True, 1, [])
        self.blocks_unpack_k_bits_bb_0 = blocks.unpack_k_bits_bb(8)
        self.blocks_selector_1 = blocks.selector(gr.sizeof_char*1,data_chooser,0)
        self.blocks_selector_1.set_enabled(True)
        self.blocks_multiply_const_vxx_0_0 = blocks.multiply_const_cc(0.71)
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_cc(IQ_gain)
        self.blocks_complex_to_float_0 = blocks.complex_to_float(1)
        self.blocks_char_to_float_0 = blocks.char_to_float(1, 1)
        self._bitrate_tool_bar = Qt.QToolBar(self)

        if None:
            self._bitrate_formatter = None
        else:
            self._bitrate_formatter = lambda x: str(x)

        self._bitrate_tool_bar.addWidget(Qt.QLabel('Bit_Rate' + ": "))
        self._bitrate_label = Qt.QLabel(str(self._bitrate_formatter(self.bitrate)))
        self._bitrate_tool_bar.addWidget(self._bitrate_label)
        self.top_grid_layout.addWidget(self._bitrate_tool_bar)
        self.audio_sink_0 = audio.sink(samp_rate, 'plughw:0', True)
        self.analog_random_source_x_0 = blocks.vector_source_b(list(map(int, numpy.random.randint(0, 256, 10000))), True)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_random_source_x_0, 0), (self.blocks_selector_1, 1))
        self.connect((self.blocks_char_to_float_0, 0), (self.qtgui_time_sink_x_0_0, 0))
        self.connect((self.blocks_complex_to_float_0, 1), (self.audio_sink_0, 1))
        self.connect((self.blocks_complex_to_float_0, 0), (self.audio_sink_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.blocks_multiply_const_vxx_0_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.qtgui_time_sink_x_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0_0, 0), (self.blocks_complex_to_float_0, 0))
        self.connect((self.blocks_selector_1, 0), (self.blocks_unpack_k_bits_bb_0, 0))
        self.connect((self.blocks_selector_1, 0), (self.digital_constellation_modulator_0, 0))
        self.connect((self.blocks_unpack_k_bits_bb_0, 0), (self.blocks_char_to_float_0, 0))
        self.connect((self.blocks_vector_source_x_0, 0), (self.blocks_selector_1, 0))
        self.connect((self.digital_constellation_modulator_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.digital_constellation_modulator_0, 0), (self.digital_symbol_sync_xx_0, 0))
        self.connect((self.digital_costas_loop_cc_0, 0), (self.qtgui_const_sink_x_0, 0))
        self.connect((self.digital_symbol_sync_xx_0, 0), (self.digital_costas_loop_cc_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "BPSK_Transmitter")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_sps(int(self.samp_rate/self.bit_rate))
        self.qtgui_time_sink_x_0.set_samp_rate(self.samp_rate)
        self.qtgui_time_sink_x_0_0.set_samp_rate(self.samp_rate/self.sps)

    def get_bit_rate(self):
        return self.bit_rate

    def set_bit_rate(self, bit_rate):
        self.bit_rate = bit_rate
        self.set_bitrate(self._bitrate_formatter(self.bit_rate))
        self.set_sps(int(self.samp_rate/self.bit_rate))

    def get_sps(self):
        return self.sps

    def set_sps(self, sps):
        self.sps = sps
        self.set_samplespersymbol(self._samplespersymbol_formatter(self.sps))
        self.qtgui_time_sink_x_0_0.set_samp_rate(self.samp_rate/self.sps)

    def get_samplespersymbol(self):
        return self.samplespersymbol

    def set_samplespersymbol(self, samplespersymbol):
        self.samplespersymbol = samplespersymbol
        Qt.QMetaObject.invokeMethod(self._samplespersymbol_label, "setText", Qt.Q_ARG("QString", self.samplespersymbol))

    def get_rrc_filter_taps(self):
        return self.rrc_filter_taps

    def set_rrc_filter_taps(self, rrc_filter_taps):
        self.rrc_filter_taps = rrc_filter_taps

    def get_psk(self):
        return self.psk

    def set_psk(self, psk):
        self.psk = psk

    def get_ex_bw(self):
        return self.ex_bw

    def set_ex_bw(self, ex_bw):
        self.ex_bw = ex_bw

    def get_data_chooser(self):
        return self.data_chooser

    def set_data_chooser(self, data_chooser):
        self.data_chooser = data_chooser
        self._data_chooser_callback(self.data_chooser)
        self.blocks_selector_1.set_input_index(self.data_chooser)

    def get_bitrate(self):
        return self.bitrate

    def set_bitrate(self, bitrate):
        self.bitrate = bitrate
        Qt.QMetaObject.invokeMethod(self._bitrate_label, "setText", Qt.Q_ARG("QString", self.bitrate))

    def get_IQ_gain(self):
        return self.IQ_gain

    def set_IQ_gain(self, IQ_gain):
        self.IQ_gain = IQ_gain
        self.blocks_multiply_const_vxx_0.set_k(self.IQ_gain)





def main(top_block_cls=BPSK_Transmitter, options=None):

    if StrictVersion("4.5.0") <= StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()

    tb.show()

    def sig_handler(sig=None, frame=None):
        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    def quitting():
        tb.stop()
        tb.wait()

    qapp.aboutToQuit.connect(quitting)
    qapp.exec_()

if __name__ == '__main__':
    main()
