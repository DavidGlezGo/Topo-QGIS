# -*- coding: utf-8 -*-
"""
/***************************************************************************
 TopopyProfiler
								 A QGIS plugin
 This plugin shows the geomorphic index profile
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
							  -------------------
		begin				: 2021-03-31
		git sha			  : $Format:%H$
		copyright			: (C) 2021 by David
		email				: davidglezojgo@gmail.com
 ***************************************************************************/

/***************************************************************************
 *																		 *
 *	This program is free software; you can redistribute it and/or modify  *
 *	it under the terms of the GNU General Public License as published by  *
 *	the Free Software Foundation; either version 2 of the License, or	 *
 *	(at your option) any later version.									*
 *																		 *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import QAction, QFileDialog
# Initialize Qt resources from file resources.py
from .resources import *

# Import the code for the DockWidget
from .topopy_profiler_dockwidget import TopopyProfilerDockWidget
import os.path

from qgis.core import *
from qgis.gui import *

from . import topopy
from .topopy import *

from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure
from matplotlib.widgets import Button
import matplotlib
import matplotlib.pyplot as plt

import numpy as np
import random


from .qgs_topopy_provider import QgsTopopyProvider

class TopopyProfiler:
	"""QGIS Plugin Implementation."""

	def __init__(self, iface):
		"""Constructor.

		:param iface: An interface instance that will be passed to this class
			which provides the hook by which you can manipulate the QGIS
			application at run time.
		:type iface: QgsInterface
		"""
		# Save reference to the QGIS interface
		self.iface = iface

		# initialize plugin directory
		self.plugin_dir = os.path.dirname(__file__)

		# initialize locale
		locale = QSettings().value('locale/userLocale')[0:2]
		locale_path = os.path.join(
			self.plugin_dir,
			'i18n',
			'TopopyProfiler_{}.qm'.format(locale))

		if os.path.exists(locale_path):
			self.translator = QTranslator()
			self.translator.load(locale_path)
			QCoreApplication.installTranslator(self.translator)

		# Declare instance attributes
		self.actions = []
		self.menu = self.tr(u'&Topopy')
		# TODO: We are going to let the user set this up in a future iteration
		self.toolbar = self.iface.addToolBar(u'Topopy')
		self.toolbar.setObjectName(u'Topopy')

		# print "** INITIALIZING TopopyProfiler"

		self.pluginIsActive = False
		self.first_start = None
		# Declare UI variable
		self.dockwidget = TopopyProfilerDockWidget()
				
		# Set all layouts		
		LayoutsParam = matplotlib.figure.SubplotParams(left=0.05, bottom=0.19, right=0.99, top=0.98)
		
		self.Ecanvas = FigureCanvas(Figure(subplotpars = LayoutsParam))
		self.Ccanvas = FigureCanvas(Figure(subplotpars = LayoutsParam))
		self.Kcanvas = FigureCanvas(Figure(subplotpars = LayoutsParam))
		self.Scanvas = FigureCanvas(Figure(subplotpars = LayoutsParam))
		
		self.Eaxes = self.Ecanvas.figure.add_subplot()
		self.Caxes = self.Ccanvas.figure.add_subplot()
		self.Kaxes = self.Kcanvas.figure.add_subplot()
		self.Saxes = self.Scanvas.figure.add_subplot()
		
		self.ElevLayout = self.dockwidget.ElevProf.layout()
		self.ChiLayout = self.dockwidget.ChiProf.layout()
		self.KsnLayout = self.dockwidget.KsnProf.layout()
		self.SlopeLayout = self.dockwidget.SlopeProf.layout()
		
		self.ElevLayout.addWidget(self.Ecanvas)
		self.ChiLayout.addWidget(self.Ccanvas)
		self.KsnLayout.addWidget(self.Kcanvas)
		self.SlopeLayout.addWidget(self.Scanvas)

		# Set first channel to plot 
		self.graph = 0
		
		# Show the cursor as a cross 
		self.cursor = QCursor(Qt.CrossCursor)
		self.Ecanvas.setCursor(self.cursor)		
		self.Ccanvas.setCursor(self.cursor)	
		self.Kcanvas.setCursor(self.cursor)	
		self.Scanvas.setCursor(self.cursor)	
		
		# Selection buttons disabled 
		self.dockwidget.NextButton.setEnabled(False)
		self.dockwidget.PrevButton.setEnabled(False)
		self.dockwidget.GoButton.setEnabled(False)
		self.dockwidget.GoSpinBox.setEnabled(False)
		self.dockwidget.AllCheckBox.setEnabled(False)
		
		# Set the properties of the temporary layer
		self.rubberband = QgsRubberBand(self.iface.mapCanvas(), False)
		self.rubberband.setWidth(2)
		self.rubberband.setColor(QColor(Qt.red))
		
		# Set the properties of the temporary layer
		self.rubberpoint = QgsRubberBand(self.iface.mapCanvas(), False)
		self.rubberpoint.setWidth(10)
		self.rubberpoint.setColor(QColor(Qt.red))

		# Set the properties of the temporary layer
		self.rubberknick = QgsRubberBand(self.iface.mapCanvas(), False)
		self.rubberknick.setWidth(5)
		self.rubberknick.setColor(QColor(Qt.red))

		# Delete any temporary layer drawn
		self.rubberpoint.reset(QgsWkbTypes.PointGeometry)
		self.rubberband.reset(QgsWkbTypes.LineGeometry)
		
####-----------------------------------------------------------------------------####
		"""caja de herramientas"""
		self.provider = None
####-----------------------------------------------------------------------------####		

	# noinspection PyMethodMayBeStatic
	def tr(self, message):
		"""Get the translation for a string using Qt translation API.

		We implement this ourselves since we do not inherit QObject.

		:param message: String for translation.
		:type message: str, QString

		:returns: Translated version of message.
		:rtype: QString
		"""
		# noinspection PyTypeChecker,PyArgumentList,PyCallByClass
		return QCoreApplication.translate('TopopyProfiler', message)

	def add_action(self,
		icon_path,
		text,
		callback,
		enabled_flag=True,
		add_to_menu=True,
		add_to_toolbar=True,
		status_tip=None,
		whats_this=None,
		parent=None):
		"""Add a toolbar icon to the toolbar.

		:param icon_path: Path to the icon for this action. Can be a resource
			path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
		:type icon_path: str

		:param text: Text that should be shown in menu items for this action.
		:type text: str

		:param callback: Function to be called when the action is triggered.
		:type callback: function

		:param enabled_flag: A flag indicating if the action should be enabled
			by default. Defaults to True.
		:type enabled_flag: bool

		:param add_to_menu: Flag indicating whether the action should also
			be added to the menu. Defaults to True.
		:type add_to_menu: bool

		:param add_to_toolbar: Flag indicating whether the action should also
			be added to the toolbar. Defaults to True.
		:type add_to_toolbar: bool

		:param status_tip: Optional text to show in a popup when mouse pointer
			hovers over the action.
		:type status_tip: str

		:param parent: Parent widget for the new action. Defaults None.
		:type parent: QWidget

		:param whats_this: Optional text to show in the status bar when the
			mouse pointer hovers over the action.

		:returns: The action that was created. Note that the action is also
			added to self.actions list.
		:rtype: QAction
		"""

		icon = QIcon(icon_path)
		action = QAction(icon, text, parent)
		action.triggered.connect(callback)
		action.setEnabled(enabled_flag)

		if status_tip is not None:
			action.setStatusTip(status_tip)

		if whats_this is not None:
			action.setWhatsThis(whats_this)

		if add_to_toolbar:
			self.toolbar.addAction(action)

		if add_to_menu:
			self.iface.addPluginToMenu(
				self.menu,
				action)

		self.actions.append(action)

		return action

	def initGui(self):
		"""Create the menu entries and toolbar icons inside the QGIS GUI."""

		icon_path = ':/plugins/topopy_profiler/icon.png'
####-----------------------------------------------------------------------------####	
	###caja de herramientas"""
		self.initProcessing()
####-----------------------------------------------------------------------------####	
		self.add_action(
			icon_path,
			text=self.tr(u'Geomophological profiler'),
			callback=self.run,
			parent=self.iface.mainWindow())
			
		self.first_start = True
		
	#--------------------------------------------------------------------------

	def onClosePlugin(self):
		"""Cleanup necessary items here when plugin dockwidget is closed"""

		#print "** CLOSING TopopyProfiler"

		# disconnects
		self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)

		# remove this statement if dockwidget is to remain
		# for reuse if plugin is reopened
		# Commented next statement since it causes QGIS crashe
		# when closing the docked window:
		# self.dockwidget = None

		self.pluginIsActive = False
		
		#Clean the plugin
		self.dockwidget.PrevButton.setEnabled(False)
		self.dockwidget.NextButton.setEnabled(False)
		self.dockwidget.GoButton.setEnabled(False)
		self.dockwidget.GoSpinBox.setEnabled(False)
		self.dockwidget.AllCheckBox.setEnabled(False)
		self.dockwidget.AllCheckBox.setChecked(False)
		self.all = False
		self.clear_graph()
		self.draw_graph()
		self.graph = 0
		self.rubberband.reset(QgsWkbTypes.LineGeometry)
		self.rubberpoint.reset(QgsWkbTypes.PointGeometry)
		self.iface.mainWindow().statusBar().showMessage( "" )


	def unload(self):
		"""Removes the plugin menu item and icon from QGIS GUI."""

		#print "** UNLOAD TopopyProfiler"

		for action in self.actions:
			self.iface.removePluginMenu(
				self.tr(u'&Topopy Profiler'),
				action)
			self.iface.removeToolBarIcon(action)
		# remove the toolbar
		del self.toolbar
		
		# Delete any temporary layer drawn
		self.rubberband.reset(QgsWkbTypes.LineGeometry)
		self.rubberpoint.reset(QgsWkbTypes.PointGeometry)
		self.rubberknick.reset(QgsWkbTypes.PointGeometry)
####-----------------------------------------------------------------------------####	
	###caja de herramientas"""
		QgsApplication.processingRegistry().removeProvider(self.provider)
####-----------------------------------------------------------------------------####			

	def run(self):
		"""Run method that loads and starts the plugin"""

		
		if not self.pluginIsActive:
			self.pluginIsActive = True

			#print "** STARTING TopopyProfiler"

			# dockwidget may not exist if:
			#	first run of plugin
			#	removed on close (see self.onClosePlugin method)
			#if self.dockwidget == None:
				# Create the dockwidget (after translation) and keep reference


			# connect to provide cleanup on closing of dockwidget
			self.dockwidget.closingPlugin.connect(self.onClosePlugin)
			

		# Clear the contents of the comboBox from previous runs
		self.dockwidget.FileLineEdit.clear()
		
		# Button actions
		self.dockwidget.AddButton.clicked.connect(self.calculate_channels)
		self.dockwidget.NextButton.clicked.connect(self.next_graph)
		self.dockwidget.PrevButton.clicked.connect(self.prev_graph)
		self.dockwidget.GoButton.clicked.connect(self.go_graph)
		self.dockwidget.AllCheckBox.clicked.connect(self.all_channels)
		self.dockwidget.SaveButton.clicked.connect(self.save)

		# Help message at the bottom of the QGis window
		self.iface.mainWindow().statusBar().showMessage( "Set CHANNELS file (.npy), then click on \"READ\" to display the profiles." )

		self.all = False
		
		# show the dockwidget
		# TODO: fix to allow choice of dock location
		self.iface.addDockWidget(Qt.BottomDockWidgetArea, self.dockwidget)
		self.dockwidget.show()
		if self.first_start == True:
			self.first_start = False
			self.dockwidget.PathButton.clicked.connect(self.select_output_file)
			
		
	def calculate_channels(self):
		""" Calculate all elements of topopy """
		filename = self.dockwidget.FileLineEdit.text()
		self.CHs = np.load(str(filename), allow_pickle=True)

		# Set first channel to plot 
		self.graph = 0
		
		self.change_graph()
		
		# Turn on the buttons and display the number of channels 
		self.dockwidget.GoSpinBox.setMaximum(int(len(self.CHs)))
		self.dockwidget.NcLabelValue.setText(str(len(self.CHs)))
		self.dockwidget.NextButton.setEnabled(True)
		self.dockwidget.GoButton.setEnabled(True)
		self.dockwidget.GoSpinBox.setEnabled(True)
		self.dockwidget.AllCheckBox.setEnabled(True)

		self.iface.mainWindow().statusBar().showMessage( "" )

		
		self.d_all = []
		self.z_all = []
		self.chi_all = []
		self.ksn_all = []
		self.slp_all = []
		
	def change_graph(self):
		""" Change the plotted channel """
		
		# Clear the profiles
		self.clear_graph()
		
		# Call the channel 
		self.channel = self.CHs[self.graph]
		
		self.single_channels()

		# Update the channel selector 
		self.dockwidget.GoSpinBox.setValue(int(self.graph)+1)

		self.Epoint = self.Ecanvas.mpl_connect('motion_notify_event', self.D_move)
		self.Cpoint = self.Ccanvas.mpl_connect('motion_notify_event', self.C_move)
		self.Kpoint = self.Kcanvas.mpl_connect('motion_notify_event', self.D_move)
		self.Spoint = self.Scanvas.mpl_connect('motion_notify_event', self.D_move)
		
		self.Eknick = self.Ecanvas.mpl_connect('button_press_event', self.D_knpoint)
		self.Cknick = self.Ccanvas.mpl_connect('button_press_event', self.D_knpoint)
		self.Kknick = self.Kcanvas.mpl_connect('button_press_event', self.D_knpoint)
		self.Sknick = self.Scanvas.mpl_connect('button_press_event', self.D_knpoint)
		
		# Show the profiles
		self.draw_graph()
		
		# Create a temporary polyline of the selected channel
		self.rubberband.reset(QgsWkbTypes.LineGeometry)
		self.rubberpoint.reset(QgsWkbTypes.PointGeometry)
		self.rubberknick.reset(QgsWkbTypes.PointGeometry)
		
		for x, y in self.channel.get_xy():
			self.rubberband.addPoint(QgsPointXY(x, y))		

		self.show_knickpoints(self.channel)			

	def next_graph(self):
		""" Select the next channel """
		
		# Advance to the next channel
		if self.graph < (len(self.CHs)-1):
			self.graph += 1
		
		# Disable the "Next>" button if the channel is the last
		if self.graph == (len(self.CHs)-1):
			self.dockwidget.NextButton.setEnabled(False)
		
		# Enable the "<Prev" button if the channel is the second 
		if self.graph == 1:
			self.dockwidget.PrevButton.setEnabled(True)
		
		# Change channel
		self.change_graph()
		self.dockwidget.lineEdit.setText(str(self.graph))	
		
	def prev_graph(self):
		""" Select the previous channel """
		
		# Go back to the previous channel
		if self.graph > 0:
			self.graph -= 1
			
		# Disable the "<Prev" button if the channel is the first
		if self.graph == 0:
			self.dockwidget.PrevButton.setEnabled(False)
			
		# Enable the "Next>" button if the channel is the penultimate
		if self.graph == (len(self.CHs)-2):
			self.dockwidget.NextButton.setEnabled(True)

		# Change channel
		self.change_graph()
		self.dockwidget.lineEdit.setText(str(self.graph))
		
	def go_graph(self):
		""" Select a specific channel """
		
		# Select the channel number 	
		self.graph = self.dockwidget.GoSpinBox.value() - 1
	
		# Disable the "Next>" button if the channel is the last, else enable it
		if self.graph == (len(self.CHs)-1):
			self.dockwidget.NextButton.setEnabled(False)
		else:
			self.dockwidget.NextButton.setEnabled(True)
			
		# Disable the "<Prev" button if the channel is the first, else enable it
		if self.graph == 0:
			self.dockwidget.PrevButton.setEnabled(False)
		else:
			self.dockwidget.PrevButton.setEnabled(True)
			

		
		# Change channel	
		self.change_graph()



	def single_channels(self):
		# Set the Profiles
		# Elevation profile
		self.Eaxes.plot(self.channel.get_d(head=False), self.channel.get_z(), color="r", ls="-", c="0.3", lw=1)
		self.Eaxes.set_xlim(xmin=0, xmax=max(self.channel.get_d()))
		# Chi profile
		self.Caxes.plot(self.channel.get_chi(), self.channel.get_z(), color="r", ls="-", c="0.3", lw=1)
		self.Caxes.set_xlim(xmin=min(self.channel.get_chi()), xmax=max(self.channel.get_chi()))
		# Ksn profile
		self.Kaxes.plot(self.channel.get_d(head=False), self.channel.get_ksn(),  color="0", ls="None", marker=".", ms=1)
		self.Kaxes.set_xlim(xmin=0, xmax=max(self.channel.get_d()))
		# Slope profile
		self.Saxes.plot(self.channel.get_d(head=False), self.channel.get_slope(),  color="0", ls="None", marker=".", ms=1)
		self.Saxes.set_xlim(xmin=0, xmax=max(self.channel.get_d()))		

	def all_channels(self):
		"""Show all channels"""
		
		if 	self.all == False:
			self.all = True
			# Clear the profiles
			self.clear_graph()
			
			if len(self.d_all) == 0:
				for n in np.arange(len(self.CHs)-1):

					self.d_all += list(self.CHs[n].get_d(head=False))
					self.z_all += list(self.CHs[n].get_z())
					self.ksn_all += list(self.CHs[n].get_ksn())
					self.chi_all += list(self.CHs[n].get_chi())
					self.slp_all += list(self.CHs[n].get_slope())

			# Set the Profiles
			# Elevation profile
			self.Eaxes.plot(self.d_all, self.z_all, color="0", ls="None", marker="o", ms=1)
			self.Eaxes.set_xlim(xmin=0, xmax=max(self.d_all))
			# Chi profile
			self.Caxes.plot(self.chi_all, self.z_all, color="0", ls="None", marker="o", ms=1)
			self.Caxes.set_xlim(xmin=min(self.chi_all), xmax=max(self.chi_all))
			# Ksn profile
			self.Kaxes.plot(self.d_all, self.ksn_all,  color="0", ls="None", marker="o", ms=1)
			self.Kaxes.set_xlim(xmin=0, xmax=max(self.d_all))
			# Slope profile
			self.Saxes.plot(self.d_all, self.slp_all,  color="0", ls="None", marker="o", ms=1)
			self.Saxes.set_xlim(xmin=0, xmax=max(self.d_all))

			# Show the profiles
			self.draw_graph()
			self.dockwidget.lineEdit_3.setText(str(self.all))
			self.rubberband.reset(QgsWkbTypes.LineGeometry)

			self.dockwidget.PrevButton.setEnabled(False)
			self.dockwidget.NextButton.setEnabled(False)
			self.dockwidget.GoButton.setEnabled(False)
			self.dockwidget.GoSpinBox.setEnabled(False)

			self.rubberpoint.reset(QgsWkbTypes.PointGeometry)
			self.rubberknick.reset(QgsWkbTypes.PointGeometry)	
			
			self.Ecanvas.mpl_disconnect(self.Epoint)
			self.Ccanvas.mpl_disconnect(self.Cpoint)
			self.Kcanvas.mpl_disconnect(self.Kpoint)
			self.Scanvas.mpl_disconnect(self.Spoint)

			self.Ecanvas.mpl_disconnect(self.Eknick)
			self.Ccanvas.mpl_disconnect(self.Cknick)
			self.Kcanvas.mpl_disconnect(self.Kknick)
			self.Scanvas.mpl_disconnect(self.Sknick)			
			
		else:
			self.all = False
			# Change channel
			self.change_graph()
			self.dockwidget.lineEdit_3.setText(str(self.all))
			if self.graph < (len(self.CHs)-1):
				self.dockwidget.NextButton.setEnabled(True)
			if self.graph > 0:
				self.dockwidget.PrevButton.setEnabled(True)

			self.dockwidget.GoButton.setEnabled(True)
			self.dockwidget.GoSpinBox.setEnabled(True)

	def clear_graph(self):
		""" Clear all graphs """
		
		self.Eaxes.clear()
		self.Caxes.clear()
		self.Kaxes.clear()
		self.Saxes.clear()
	
	def draw_graph(self):
		""" Draw all graphs """
		
		self.Eaxes.set_xlabel("Distance to mouth [m]")
		self.Eaxes.set_ylabel("Elevation [m]")
		self.Caxes.set_xlabel("χ [m]")		
		self.Caxes.set_ylabel("Elevation [m]")
		self.Kaxes.set_xlabel("Distance to mouth [m]")
		self.Kaxes.set_ylabel("ksn")
		self.Saxes.set_xlabel("Distance to mouth [m]")
		self.Saxes.set_ylabel("Slope [%]")
		
		self.Ecanvas.draw()
		self.Ccanvas.draw()
		self.Kcanvas.draw()
		self.Scanvas.draw()



####-----------------------------------------------------------------------------####	
	"""caja de herramientas"""
	def initProcessing(self):
		"""Init Processing provider for QGIS >= 3.8."""
		self.provider = QgsTopopyProvider()
		QgsApplication.processingRegistry().addProvider(self.provider)
####-----------------------------------------------------------------------------####


	def select_output_file(self):
	  filename, _filter = QFileDialog.getOpenFileName(self.dockwidget, "Select Channels file ","", 'NPY files (*.npy)')
	  self.dockwidget.FileLineEdit.setText(filename)


	def D_move(self, event):
		# get the x and y pixel coords
		x, y = event.x, event.y
		if event.inaxes:
			self.dockwidget.lineEdit_2.setText('data coords %f %f' % (event.xdata, event.ydata))
			self.rubberpoint.reset(QgsWkbTypes.PointGeometry)
			i = np.abs(list(self.channel.get_d(head=False)) - event.xdata).argmin()
			xy = self.channel.get_xy()[i]
			self.rubberpoint.addPoint(QgsPointXY(xy[0], xy[1]))	  
	
	def C_move(self, event):
		# get the x and y pixel coords
		x, y = event.x, event.y
		if event.inaxes:
			self.dockwidget.lineEdit_2.setText('data coords %f %f' % (event.xdata, event.ydata))
			self.rubberpoint.reset(QgsWkbTypes.PointGeometry)
			i = np.abs(list(self.channel.get_d(head=False)) - event.xdata).argmin()
			xy = self.channel.get_xy()[i]
			self.rubberpoint.addPoint(QgsPointXY(xy[0], xy[1]))	
	
	def D_knpoint(self, event):
		# get the x and y pixel coords
		x, y = event.x, event.y
		
		if event.inaxes:

			if event.button == 1:
				i = np.abs(list(self.channel.get_d(head=False)) - event.xdata).argmin()
				self.CHs[self.graph]._knickpoints.append(i)

			if event.button == 3:
				i = np.abs(list(self.channel.get_d(head=False)) - event.xdata).argmin()
				self.dockwidget.lineEdit_3.setText(str(i))	
				
				i = np.abs(list(self.CHs[self.graph]._knickpoints) - i).argmin()

				self.CHs[self.graph]._knickpoints.pop(i)

				
			self.rubberknick.reset(QgsWkbTypes.PointGeometry)
			
			

			self.show_knickpoints(self.channel)		



	def C_knpoint(self, event):
		# get the x and y pixel coords
		x, y = event.x, event.y
		if event.inaxes:
			kpoints = self.channel._knickpoints
			if event.button == 1:
				final_value = self.near(list(self.channel.get_chi()), event.xdata, float("inf"))
				i = list(self.channel.get_chi()).index(final_value)
				kpoints.append(i)

			if event.button == 3:
				final_value = self.near(list(self.channel.get_chi()), event.xdata, float("inf"))
				i = list(self.channel.get_chi()).index(final_value)
				xy = self.channel.get_xy()[i]
				self.dockwidget.lineEdit_3.setText(str(i))	
	
				value = self.near(list(kpoints), i, int(2+len(self.channel.get_chi())*0.025))	
				self.dockwidget.lineEdit_2.setText(str(int(2+len(self.channel.get_chi())*0.025)))			
				kpoints.pop(kpoints.index(value))
				self.rubberknick.reset(QgsWkbTypes.PointGeometry)
				
			self.rubberknick.reset(QgsWkbTypes.PointGeometry)
			
			
			self.dockwidget.lineEdit.setText(str(kpoints)+ str(len(kpoints)))
			self.show_knickpoints(self.channel)	


	def show_knickpoints(self, channel):
		kpoints = channel._knickpoints		
		self.clear_graph()
		self.single_channels()
		for kp in kpoints:
			xy = channel.get_xy()[kp]
			self.rubberknick.addPoint(QgsPointXY(xy[0], xy[1]))		
			
			self.dockwidget.lineEdit_2.setText(str(list(self.channel.get_d(head=False))[kp])+ '/' +str(kp))	
			
			self.Eaxes.plot(self.channel.get_d(head=False)[kp], self.channel.get_z()[kp], color="b", ls="None", marker="d", ms=10)
			# Chi profile
			self.Caxes.plot(self.channel.get_chi()[kp], self.channel.get_z()[kp], color="b", ls="None", marker="d", ms=10)
			# Ksn profile
			self.Kaxes.plot(self.channel.get_d(head=False)[kp], self.channel.get_ksn()[kp],  color="r", ls="None", marker="d", ms=10)
			# # Slope profile
			self.Saxes.plot(self.channel.get_d(head=False)[kp], self.channel.get_slope()[kp],  color="r", ls="None", marker="d", ms=10)
		self.draw_graph()

	def save (self):
		
		with open('C:/Users/david/Desktop/CHs.npy', 'wb') as f:
			np.save(f, self.CHs)
			
	
