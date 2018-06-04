#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Frontend DSLWP RX UHD
# Generated: Sat May 26 09:30:26 2018
##################################################

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print "Warning: failed to XInitThreads()"

from PyQt4 import Qt
from gnuradio import analog
from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import filter
from gnuradio import gr
from gnuradio import gr, blocks
from gnuradio import qtgui
from gnuradio import uhd
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from gnuradio.qtgui import Range, RangeWidget
from optparse import OptionParser
import math
import sip
import sys
import time
from gnuradio import qtgui


class frontend_dslwp_rx_uhd(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Frontend DSLWP RX UHD")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Frontend DSLWP RX UHD")
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

        self.settings = Qt.QSettings("GNU Radio", "frontend_dslwp_rx_uhd")
        self.restoreGeometry(self.settings.value("geometry").toByteArray())

        ##################################################
        # Variables
        ##################################################
        self.waterfall_ch_min = waterfall_ch_min = -100
        self.waterfall_ch_max = waterfall_ch_max = -50
        self.samp_rate_2 = samp_rate_2 = 40000
        self.samp_rate = samp_rate = 2000000
        self.rx_gain = rx_gain = 50
        self.fc = fc = 436e6
        self.f_offset = f_offset = 0
        self.audio_rate = audio_rate = 48000

        ##################################################
        # Blocks
        ##################################################
        self.tab3 = Qt.QTabWidget()
        self.tab3_widget_0 = Qt.QWidget()
        self.tab3_layout_0 = Qt.QBoxLayout(Qt.QBoxLayout.TopToBottom, self.tab3_widget_0)
        self.tab3_grid_layout_0 = Qt.QGridLayout()
        self.tab3_layout_0.addLayout(self.tab3_grid_layout_0)
        self.tab3.addTab(self.tab3_widget_0, 'Waterfall')
        self.tab3_widget_1 = Qt.QWidget()
        self.tab3_layout_1 = Qt.QBoxLayout(Qt.QBoxLayout.TopToBottom, self.tab3_widget_1)
        self.tab3_grid_layout_1 = Qt.QGridLayout()
        self.tab3_layout_1.addLayout(self.tab3_grid_layout_1)
        self.tab3.addTab(self.tab3_widget_1, 'Spectrum')
        self.top_grid_layout.addWidget(self.tab3, 5,0,1,2)
        self.tab2 = Qt.QTabWidget()
        self.tab2_widget_0 = Qt.QWidget()
        self.tab2_layout_0 = Qt.QBoxLayout(Qt.QBoxLayout.TopToBottom, self.tab2_widget_0)
        self.tab2_grid_layout_0 = Qt.QGridLayout()
        self.tab2_layout_0.addLayout(self.tab2_grid_layout_0)
        self.tab2.addTab(self.tab2_widget_0, 'BJ1SN')
        self.top_grid_layout.addWidget(self.tab2, 4,0,1,2)
        self._rx_gain_range = Range(0, 73, 1, 50, 200)
        self._rx_gain_win = RangeWidget(self._rx_gain_range, self.set_rx_gain, 'RX Gain', "counter_slider", float)
        self.top_grid_layout.addWidget(self._rx_gain_win, 0,0,1,1)
        self._f_offset_tool_bar = Qt.QToolBar(self)
        self._f_offset_tool_bar.addWidget(Qt.QLabel('Frequency Offset'+": "))
        self._f_offset_line_edit = Qt.QLineEdit(str(self.f_offset))
        self._f_offset_tool_bar.addWidget(self._f_offset_line_edit)
        self._f_offset_line_edit.returnPressed.connect(
        	lambda: self.set_f_offset(eng_notation.str_to_num(str(self._f_offset_line_edit.text().toAscii()))))
        self.top_grid_layout.addWidget(self._f_offset_tool_bar, 0,1,1,1)
        self.uhd_usrp_source_0 = uhd.usrp_source(
        	",".join(("", "")),
        	uhd.stream_args(
        		cpu_format="fc32",
        		channels=range(1),
        	),
        )
        self.uhd_usrp_source_0.set_subdev_spec('A:B', 0)
        self.uhd_usrp_source_0.set_samp_rate(samp_rate)

        # GPSDO-USRP Sync
        ##################################################
        INFO = "[\033[32mINFO\033[0m]"
        ERROR = "[\033[31mERROR\033[0m]"
        SUCCESS = "[\033[32mSUEECSS\033[0m]"
        WARNING = "[\033[33mWARNING\033[0m]"
        GPS_debug = False

        print 
        print "##################################################"
        print "#                GPSDO Time Sync                 #"
        print "##################################################"

        #Set the sources
        self.uhd_usrp_source_0.set_clock_source('gpsdo', 0)
        self.uhd_usrp_source_0.set_time_source('gpsdo', 0)
        print INFO,"the default 10 MHz Reference and 1 PPS signals are now from the GPSDO."

        #Wait for Reference locked
        time.sleep(1)

        #Check Reference status
        if (self.uhd_usrp_source_0.get_mboard_sensor("ref_locked",0).value == "true"):
            print INFO,"Reference Locked."
        else:
            print ERROR,"Reference Unlocked."
            exit()

        #Check GPS status
        if (self.uhd_usrp_source_0.get_mboard_sensor("gps_locked",0).value == "true"):
            print INFO,"GPS Locked."
        else:
            print ERROR,"GPS Unlocked."
            if not GPS_debug :
                exit()

        #Print GPS info
        print INFO,"GPS INFO"
        print "       Time:",self.uhd_usrp_source_0.get_mboard_sensor("gps_time",0).value
        print "       GPGGA:",self.uhd_usrp_source_0.get_mboard_sensor("gps_gpgga",0).value 
        print "       GPRMC:",self.uhd_usrp_source_0.get_mboard_sensor("gps_gprmc",0).value

        #GPSDO-USRP Sync
        gps_time = int(self.uhd_usrp_source_0.get_mboard_sensor("gps_time",0))
        self.uhd_usrp_source_0.set_time_next_pps(uhd.time_spec(gps_time + 1))
        
        #Wait for it to apply
        #The wait is 2 seconds because USRP has a issue where
        #the time at the last PPS does not properly update at the PPS edge
        #when the time is actually set.
        print INFO,"Synchronizing the time"
        time.sleep (2)


        #Check the time
        gps_time = uhd.time_spec(int(self.uhd_usrp_source_0.get_mboard_sensor("gps_time",0)))
        usrp_time =  self.uhd_usrp_source_0.get_time_last_pps()
        print INFO,"Time INFO"
        print "       GPS time:     ","%.09f"%gps_time.get_real_secs()
        print "       USRP time:    ","%.09f"%usrp_time.get_real_secs()
        print "       Computer time:","%.09f"%time.time()
        if (gps_time.get_real_secs() == usrp_time.get_real_secs()):
            print SUCCESS,"USRP time synchronized to GPS time."
        else:
            print ERROR,"Failed to synchronize USRP time to GPS time."
        ##################################################

        self.uhd_usrp_source_0.set_center_freq(fc, 0)
        self.uhd_usrp_source_0.set_gain(rx_gain, 0)
        self.uhd_usrp_source_0.set_antenna('RX2', 0)
        self.rational_resampler_xxx_0_0_2 = filter.rational_resampler_ccc(
                interpolation=1,
                decimation=50,
                taps=None,
                fractional_bw=None,
        )
        self.rational_resampler_xxx_0_0 = filter.rational_resampler_ccc(
                interpolation=1,
                decimation=50,
                taps=None,
                fractional_bw=None,
        )
        self.qtgui_waterfall_sink_x_0_0_0_0_0 = qtgui.waterfall_sink_c(
        	1024, #size
        	firdes.WIN_BLACKMAN_hARRIS, #wintype
        	436.4e6, #fc
        	40e3, #bw
        	"B1", #name
                1 #number of inputs
        )
        self.qtgui_waterfall_sink_x_0_0_0_0_0.set_update_time(0.10)
        self.qtgui_waterfall_sink_x_0_0_0_0_0.enable_grid(False)
        self.qtgui_waterfall_sink_x_0_0_0_0_0.enable_axis_labels(True)

        if not True:
          self.qtgui_waterfall_sink_x_0_0_0_0_0.disable_legend()

        if "complex" == "float" or "complex" == "msg_float":
          self.qtgui_waterfall_sink_x_0_0_0_0_0.set_plot_pos_half(not True)

        labels = ['', '', '', '', '',
                  '', '', '', '', '']
        colors = [2, 0, 0, 0, 0,
                  0, 0, 0, 0, 0]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
                  1.0, 1.0, 1.0, 1.0, 1.0]
        for i in xrange(1):
            if len(labels[i]) == 0:
                self.qtgui_waterfall_sink_x_0_0_0_0_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_waterfall_sink_x_0_0_0_0_0.set_line_label(i, labels[i])
            self.qtgui_waterfall_sink_x_0_0_0_0_0.set_color_map(i, colors[i])
            self.qtgui_waterfall_sink_x_0_0_0_0_0.set_line_alpha(i, alphas[i])

        self.qtgui_waterfall_sink_x_0_0_0_0_0.set_intensity_range(waterfall_ch_min, waterfall_ch_max)

        self._qtgui_waterfall_sink_x_0_0_0_0_0_win = sip.wrapinstance(self.qtgui_waterfall_sink_x_0_0_0_0_0.pyqwidget(), Qt.QWidget)
        self.tab2_grid_layout_0.addWidget(self._qtgui_waterfall_sink_x_0_0_0_0_0_win, 0,1)
        self.qtgui_waterfall_sink_x_0_0_0 = qtgui.waterfall_sink_c(
        	1024, #size
        	firdes.WIN_BLACKMAN_hARRIS, #wintype
        	435.4e6, #fc
        	40e3, #bw
        	"B0", #name
                1 #number of inputs
        )
        self.qtgui_waterfall_sink_x_0_0_0.set_update_time(0.10)
        self.qtgui_waterfall_sink_x_0_0_0.enable_grid(False)
        self.qtgui_waterfall_sink_x_0_0_0.enable_axis_labels(True)

        if not True:
          self.qtgui_waterfall_sink_x_0_0_0.disable_legend()

        if "complex" == "float" or "complex" == "msg_float":
          self.qtgui_waterfall_sink_x_0_0_0.set_plot_pos_half(not True)

        labels = ['', '', '', '', '',
                  '', '', '', '', '']
        colors = [2, 0, 0, 0, 0,
                  0, 0, 0, 0, 0]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
                  1.0, 1.0, 1.0, 1.0, 1.0]
        for i in xrange(1):
            if len(labels[i]) == 0:
                self.qtgui_waterfall_sink_x_0_0_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_waterfall_sink_x_0_0_0.set_line_label(i, labels[i])
            self.qtgui_waterfall_sink_x_0_0_0.set_color_map(i, colors[i])
            self.qtgui_waterfall_sink_x_0_0_0.set_line_alpha(i, alphas[i])

        self.qtgui_waterfall_sink_x_0_0_0.set_intensity_range(waterfall_ch_min, waterfall_ch_max)

        self._qtgui_waterfall_sink_x_0_0_0_win = sip.wrapinstance(self.qtgui_waterfall_sink_x_0_0_0.pyqwidget(), Qt.QWidget)
        self.tab2_grid_layout_0.addWidget(self._qtgui_waterfall_sink_x_0_0_0_win, 0,0)
        self.qtgui_waterfall_sink_x_0 = qtgui.waterfall_sink_c(
        	1024, #size
        	firdes.WIN_BLACKMAN_hARRIS, #wintype
        	fc, #fc
        	samp_rate, #bw
        	"Waterfall", #name
                1 #number of inputs
        )
        self.qtgui_waterfall_sink_x_0.set_update_time(0.10)
        self.qtgui_waterfall_sink_x_0.enable_grid(False)
        self.qtgui_waterfall_sink_x_0.enable_axis_labels(True)

        if not True:
          self.qtgui_waterfall_sink_x_0.disable_legend()

        if "complex" == "float" or "complex" == "msg_float":
          self.qtgui_waterfall_sink_x_0.set_plot_pos_half(not True)

        labels = ['', '', '', '', '',
                  '', '', '', '', '']
        colors = [0, 0, 0, 0, 0,
                  0, 0, 0, 0, 0]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
                  1.0, 1.0, 1.0, 1.0, 1.0]
        for i in xrange(1):
            if len(labels[i]) == 0:
                self.qtgui_waterfall_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_waterfall_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_waterfall_sink_x_0.set_color_map(i, colors[i])
            self.qtgui_waterfall_sink_x_0.set_line_alpha(i, alphas[i])

        self.qtgui_waterfall_sink_x_0.set_intensity_range(-100, 0)

        self._qtgui_waterfall_sink_x_0_win = sip.wrapinstance(self.qtgui_waterfall_sink_x_0.pyqwidget(), Qt.QWidget)
        self.tab3_grid_layout_0.addWidget(self._qtgui_waterfall_sink_x_0_win, 0,0)
        self.qtgui_freq_sink_x_0 = qtgui.freq_sink_c(
        	8192, #size
        	firdes.WIN_BLACKMAN_hARRIS, #wintype
        	fc, #fc
        	samp_rate, #bw
        	"Spectrum", #name
        	1 #number of inputs
        )
        self.qtgui_freq_sink_x_0.set_update_time(0.10)
        self.qtgui_freq_sink_x_0.set_y_axis(-140, 10)
        self.qtgui_freq_sink_x_0.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_0.enable_autoscale(False)
        self.qtgui_freq_sink_x_0.enable_grid(False)
        self.qtgui_freq_sink_x_0.set_fft_average(1.0)
        self.qtgui_freq_sink_x_0.enable_axis_labels(True)
        self.qtgui_freq_sink_x_0.enable_control_panel(False)

        if not True:
          self.qtgui_freq_sink_x_0.disable_legend()

        if "complex" == "float" or "complex" == "msg_float":
          self.qtgui_freq_sink_x_0.set_plot_pos_half(not True)

        labels = ['', '', '', '', '',
                  '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
                  1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
                  "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
                  1.0, 1.0, 1.0, 1.0, 1.0]
        for i in xrange(1):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_x_0_win = sip.wrapinstance(self.qtgui_freq_sink_x_0.pyqwidget(), Qt.QWidget)
        self.tab3_grid_layout_1.addWidget(self._qtgui_freq_sink_x_0_win, 0,0)
        self.blocks_udp_sink_0_1_1 = blocks.udp_sink(gr.sizeof_gr_complex*1, '127.0.0.1', 7177, 1472, True)
        self.blocks_udp_sink_0_1 = blocks.udp_sink(gr.sizeof_gr_complex*1, '127.0.0.1', 7161, 1472, True)
        self.blocks_multiply_xx_0_0_1 = blocks.multiply_vcc(1)
        self.blocks_multiply_xx_0_0 = blocks.multiply_vcc(1)
        self.blocks_file_meta_sink_0_1_0 = blocks.file_meta_sink(gr.sizeof_gr_complex*1, './Meta/meta_B_436.raw', samp_rate_2, 0.02, blocks.GR_FILE_FLOAT, True, samp_rate_2, "", False)
        self.blocks_file_meta_sink_0_1_0.set_unbuffered(False)
        self.blocks_file_meta_sink_0_0 = blocks.file_meta_sink(gr.sizeof_gr_complex*1, './Meta/meta_B_435.raw', samp_rate_2, 0.02, blocks.GR_FILE_FLOAT, True, samp_rate_2, "", False)
        self.blocks_file_meta_sink_0_0.set_unbuffered(False)
        self.analog_sig_source_x_0_0_1 = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, -400e3+f_offset, 1, 0)
        self.analog_sig_source_x_0_0 = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, 600e3+f_offset, 1, 0)

        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_sig_source_x_0_0, 0), (self.blocks_multiply_xx_0_0, 1))
        self.connect((self.analog_sig_source_x_0_0_1, 0), (self.blocks_multiply_xx_0_0_1, 1))
        self.connect((self.blocks_multiply_xx_0_0, 0), (self.rational_resampler_xxx_0_0, 0))
        self.connect((self.blocks_multiply_xx_0_0_1, 0), (self.rational_resampler_xxx_0_0_2, 0))
        self.connect((self.rational_resampler_xxx_0_0, 0), (self.blocks_file_meta_sink_0_0, 0))
        self.connect((self.rational_resampler_xxx_0_0, 0), (self.blocks_udp_sink_0_1, 0))
        self.connect((self.rational_resampler_xxx_0_0, 0), (self.qtgui_waterfall_sink_x_0_0_0, 0))
        self.connect((self.rational_resampler_xxx_0_0_2, 0), (self.blocks_file_meta_sink_0_1_0, 0))
        self.connect((self.rational_resampler_xxx_0_0_2, 0), (self.blocks_udp_sink_0_1_1, 0))
        self.connect((self.rational_resampler_xxx_0_0_2, 0), (self.qtgui_waterfall_sink_x_0_0_0_0_0, 0))
        self.connect((self.uhd_usrp_source_0, 0), (self.blocks_multiply_xx_0_0, 0))
        self.connect((self.uhd_usrp_source_0, 0), (self.blocks_multiply_xx_0_0_1, 0))
        self.connect((self.uhd_usrp_source_0, 0), (self.qtgui_freq_sink_x_0, 0))
        self.connect((self.uhd_usrp_source_0, 0), (self.qtgui_waterfall_sink_x_0, 0))

    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "frontend_dslwp_rx_uhd")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_waterfall_ch_min(self):
        return self.waterfall_ch_min

    def set_waterfall_ch_min(self, waterfall_ch_min):
        self.waterfall_ch_min = waterfall_ch_min
        self.qtgui_waterfall_sink_x_0_0_0_0_0.set_intensity_range(self.waterfall_ch_min, self.waterfall_ch_max)
        self.qtgui_waterfall_sink_x_0_0_0.set_intensity_range(self.waterfall_ch_min, self.waterfall_ch_max)

    def get_waterfall_ch_max(self):
        return self.waterfall_ch_max

    def set_waterfall_ch_max(self, waterfall_ch_max):
        self.waterfall_ch_max = waterfall_ch_max
        self.qtgui_waterfall_sink_x_0_0_0_0_0.set_intensity_range(self.waterfall_ch_min, self.waterfall_ch_max)
        self.qtgui_waterfall_sink_x_0_0_0.set_intensity_range(self.waterfall_ch_min, self.waterfall_ch_max)

    def get_samp_rate_2(self):
        return self.samp_rate_2

    def set_samp_rate_2(self, samp_rate_2):
        self.samp_rate_2 = samp_rate_2

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.uhd_usrp_source_0.set_samp_rate(self.samp_rate)
        self.qtgui_waterfall_sink_x_0.set_frequency_range(self.fc, self.samp_rate)
        self.qtgui_freq_sink_x_0.set_frequency_range(self.fc, self.samp_rate)
        self.analog_sig_source_x_0_0_1.set_sampling_freq(self.samp_rate)
        self.analog_sig_source_x_0_0.set_sampling_freq(self.samp_rate)

    def get_rx_gain(self):
        return self.rx_gain

    def set_rx_gain(self, rx_gain):
        self.rx_gain = rx_gain
        self.uhd_usrp_source_0.set_gain(self.rx_gain, 0)


    def get_fc(self):
        return self.fc

    def set_fc(self, fc):
        self.fc = fc
        self.uhd_usrp_source_0.set_center_freq(self.fc, 0)
        self.qtgui_waterfall_sink_x_0.set_frequency_range(self.fc, self.samp_rate)
        self.qtgui_freq_sink_x_0.set_frequency_range(self.fc, self.samp_rate)

    def get_f_offset(self):
        return self.f_offset

    def set_f_offset(self, f_offset):
        self.f_offset = f_offset
        Qt.QMetaObject.invokeMethod(self._f_offset_line_edit, "setText", Qt.Q_ARG("QString", eng_notation.num_to_str(self.f_offset)))
        self.analog_sig_source_x_0_0_1.set_frequency(-400e3+self.f_offset)
        self.analog_sig_source_x_0_0.set_frequency(600e3+self.f_offset)

    def get_audio_rate(self):
        return self.audio_rate

    def set_audio_rate(self, audio_rate):
        self.audio_rate = audio_rate


def main(top_block_cls=frontend_dslwp_rx_uhd, options=None):

    from distutils.version import StrictVersion
    if StrictVersion(Qt.qVersion()) >= StrictVersion("4.5.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()
    tb.start()
    tb.show()

    def quitting():
        tb.stop()
        tb.wait()
    qapp.connect(qapp, Qt.SIGNAL("aboutToQuit()"), quitting)
    qapp.exec_()


if __name__ == '__main__':
    main()
