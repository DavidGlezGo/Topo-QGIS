from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import QgsProcessingAlgorithm, QgsProcessingParameterFile, QgsProcessingParameterVectorDestination
from .. import topopy
from ..topopy import *
from qgis import processing
import numpy as np
import ogr, osr

class Channel2Vector(QgsProcessingAlgorithm):
	# Constants used to refer to parameters and outputs They will be
	# used when calling the algorithm from another algorithm, or when
	# calling from the QGIS console.
	
	INPUT_CHs = 'INPUT_CHs'	
	OUTPUT_CHs = 'OUTPUT_CHs'
	OUTPUT_KPs = 'OUTPUT_KPs'
 
	def __init__(self):
		super().__init__()

	def createInstance(self):
		return type(self)()
 
	def name(self):
		"""
		Rerturns the algorithm name, used to identify the algorithm.
		Must be unique within each provider and should contain lowercase alphanumeric characters only.
		"""
		return "getorders"
	 
	def displayName(self):
		"""
		Returns the translated algorithm name, which should be used for any
		user-visible display of the algorithm name.
		"""
		return self.tr("Channels to Vectorial") 
	
	def groupId(self):
		"""
		Returns the unique ID of the group this algorithm belongs to.
		"""
		return "drainage_net_processing"

	def group(self):
		"""
		Returns the name of the group this algoritm belongs to.
		"""
		return self.tr("Drainage Network Processing")

	def shortHelpString(self):
		"""
		Returns a localised short helper string for the algorithm. 
		"""
		texto = """
					This script extract streams orderded by strahler or shreeve. Cell values will have a value acording with the order of the segment they belong.
					
					Flow: Flow direccion raster.

					Method: Select the method for calculating the stream order.
					
					Stream Order: Output raster with streams ordered.
					"""
		return texto
	
	def tr(self, string):
		return QCoreApplication.translate('Processing', string)

	def helpUrl(self):
		return "https://qgis.org"
		 

	def initAlgorithm(self, config=None):
		"""
		Here we define the inputs and output of the algorithm, along
		with some other properties.
		"""
		self.addParameter(QgsProcessingParameterFile(self.INPUT_CHs,  "Input Channels", extension="npy"))
		self.addParameter(QgsProcessingParameterVectorDestination(self.OUTPUT_CHs, self.tr("Channels")))
		self.addParameter(QgsProcessingParameterVectorDestination(self.OUTPUT_KPs, self.tr("Knickpoints")))
 
	def processAlgorithm(self, parameters, context, feedback):
		"""
		Here is where the processing itself takes place.
		"""
		filename = self.parameterAsFile(parameters, self.INPUT_CHs, context)
		output_ch = self.parameterAsOutputLayer(parameters, self.OUTPUT_CHs, context)
		
		Channels =  np.load(str(filename), allow_pickle=True)
		# Create shapefile
		driver = ogr.GetDriverByName("ESRI Shapefile")
		dataset = driver.CreateDataSource(output_ch)

		sp = osr.SpatialReference()
		sp.ImportFromWkt(Channels[0]._proj)	
		layer = dataset.CreateLayer("Channels", sp, geom_type=ogr.wkbLineString25D)
		
		# Add fields
		campos = ["id_profile", "L", "area_e6", "z", "chi", "ksn", "slope"]
		tipos = [0, 2, 2, 2, 2, 2, 2]
		for n in range(len(campos)):
			layer.CreateField(ogr.FieldDefn(campos[n], tipos[n]))
			
		id = 0
		unic = []
		id_profile = 0
		
		KP = False
		for CH in Channels:
			if len(CH._knickpoints) > 0:
				KP = True
				
		if KP == True:
			output_kp = self.parameterAsOutputLayer(parameters, self.OUTPUT_KPs, context)
			kpdataset = driver.CreateDataSource(output_kp)
			kplayer = kpdataset.CreateLayer("Knickpoints", sp, geom_type=ogr.wkbPoint25D)	
			
			campos = ['id', 'channel', 'z', 'chi', 'ksn', 'rksn', 'slope', 'rslope']
			tipos = [0, 0, 2, 2, 2, 2, 2, 2]
			for n in range(len(campos)):
				kplayer.CreateField(ogr.FieldDefn(campos[n], tipos[n]))	
		else:
			feedback.setProgressText('**This channel file does not have Knickpoints**')
	
		for CH in Channels:
			id_profile += 1
			ind = 0
			Ich = len(CH._ax)
			feedback.setProgressText(str(int((id_profile/len(Channels))*100)) + '% of Channels converted')
			XY = CH.get_xy()
			processing = True
			while processing:			
				if ind < Ich-3:	
					if tuple(XY[ind]) in unic:
						processing = False
						continue
					else:
						dx = np.mean([CH._dx[ind], CH._dx[ind+1]])
						zx = np.mean([CH._zx[ind], CH._zx[ind+1]])
						chi = np.mean([CH._chi[ind], CH._chi[ind+1]])
						slope = np.mean([CH._slp[ind], CH._slp[ind+1]])
						ksn = np.mean([CH._ksn[ind],CH._ksn[ind+1]])
						area = np.mean([CH._ax[ind],CH._ax[ind+1]])

						feat = ogr.Feature(layer.GetLayerDefn())
						feat.SetField("id_profile", int(id_profile))
						feat.SetField("L", float(dx))
						feat.SetField("area_e6", float(area/1000000))
						feat.SetField("z", float(zx))
						feat.SetField("chi", float(chi))
						feat.SetField("ksn", float(ksn))
						feat.SetField("slope", float(slope))
						
						# Create geometry
						geom = ogr.Geometry(ogr.wkbLineString25D)
						geom.AddPoint(XY[ind][0], XY[ind][1], CH._zx[ind])
						geom.AddPoint(XY[ind+1][0],XY[ind+1][1], CH._zx[ind+1])
						unic.append(tuple(XY[ind]))
					
					feat.SetGeometry(geom)
					# Add segment feature to the shapefile
					layer.CreateFeature(feat)
					
					ind += 1
					
				else:				
					processing = False
					continue
					
			if KP == True:
				for n in CH._knickpoints:
					id +=1
					feat = ogr.Feature(kplayer.GetLayerDefn())
					feat.SetField('id', int(id))
					feat.SetField('channel', int(id_profile))					
					feat.SetField('z', float(CH._zx[n]))
					feat.SetField('chi', float(CH._chi[n]))
					feat.SetField('ksn', float(CH._ksn[n]))
					feat.SetField('rksn', float(CH._R2ksn[n]))
					feat.SetField('slope', float(CH._slp[n]))
					feat.SetField('rslope', float(CH._R2slp[n]))
					
					# Create geometry
					geom = ogr.Geometry(ogr.wkbPoint25D)
					geom.AddPoint(CH.get_xy()[n][0], CH.get_xy()[n][1], CH._zx[n])
					feat.SetGeometry(geom)			
					kplayer.CreateFeature(feat)
						
		if KP == True:
			results = {self.OUTPUT_CHs : output_ch, self.OUTPUT_KPs : output_kp, }
		else:
			results = {self.OUTPUT_CHs : output_ch, }			
		return results