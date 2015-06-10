#!/usr/bin/env python

"""
Get the number of bytes received and sent from a network interface.
"""

import appindicator
import gtk
import os.path
import signal
import subprocess
import sys

# Catch CTRL+C
def signal_handler(signal, frame):
  print('\nAborted!')
  sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
sys.tracebacklimit = 0


class RxTxBytes():
	"""
	Bytes received and sent Object
	"""
	PATH = "/sys/class/net/"
	PATH_STATS = "/statistics/"
	FILE_SUFFIX = "_bytes"

	PING_FREQUENCY = 1 # every 1 second

	bytesData = {}

	def __init__(self, interface):
		"""
		Constructor
		"""
		self.bytesData['rx'] = self.PATH + interface + self.PATH_STATS + 'rx' + self.FILE_SUFFIX;
		self.bytesData['tx'] = self.PATH + interface + self.PATH_STATS + 'tx' + self.FILE_SUFFIX;

		# AppIndicator
		self.ind = appindicator.Indicator(
			"RxTx",
			"utilities-system-monitor",
		appindicator.CATEGORY_APPLICATION_STATUS)
		self.ind.set_status(appindicator.STATUS_ACTIVE)
		#self.ind.set_attention_icon("utilities-system-monitor")
		self.ind.set_label("Loading ...")

		# Set menu
		self.menu_setup()
		self.ind.set_menu(self.menu)

	def getBytes(self, mode):
		"""
		Get the bytes received or sent
		@param	String [ The mode (tx or rx) ]
		@return	Integer [ Size ], Message [ If error ]
		"""
		if not mode in self.bytesData:
			return 0, "Error: the mode is invalid"

		filename = self.bytesData[mode]

		if not os.path.isfile(filename):
			return 0, "The " + filename + " cannot be found"

		p = subprocess.Popen(['cat', filename],
				stdout=subprocess.PIPE, 
				stderr=subprocess.PIPE
			 )
		out, err = p.communicate()
		return int(out), err

	def getHumanReadableBytes(self, size, suffix = 'B'):
		"""
		Get the human readable version of bytes received or sent
		@param	size [ The size ]
		@return	String [ Human readable version]
		"""
		if not isinstance(size, ( int, long )):
			return "Error"
		for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
			if abs(size) < 1024.0:
				return "%3.4f %s%s" % (size, unit, suffix)
			size /= 1024.0
		return "%.4f %s%s" % (size, 'Yi', suffix)

	def main(self):
		self.fetch()
		gtk.timeout_add(self.PING_FREQUENCY * 1000, self.fetch)
		gtk.main()

	def fetch(self):
		"""
		Fetch the data from the statistic files
		"""
		rx, rxErr = self.getBytes('rx')
		tx, txErr = self.getBytes('tx')
		msg = ""

		if rxErr:
			msg += rxErr

		if txErr:
			msg += txErr

		if not msg:
			msg += self.getHumanReadableBytes(rx) + ' / ' + self.getHumanReadableBytes(tx)

		self.ind.set_label(msg)
		return True

	# App Indicator methods

	def menu_setup(self):
		"""
		Setup the AppIndicator Menu
		"""
		self.menu = gtk.Menu()

		quit_item = gtk.MenuItem("Quit")
		quit_item.connect("activate", self.quit)
		quit_item.show()
		self.menu.append(quit_item)

		#separator = gtk.SeparatorMenuItem()
		#separator.show()
		#self.menu.append(separator)

	def quit(self, which):
		"""
		Close the program
		"""
		sys.exit(0)

if __name__ == "__main__":
	indicator = RxTxBytes('eth0')
	indicator.main()
