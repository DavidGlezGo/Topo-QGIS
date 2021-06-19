from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import QgsProcessingAlgorithm, QgsProcessingParameterFile, QgsProcessingParameterRasterLayer, QgsProcessingParameterEnum, QgsProcessingParameterVectorDestination, QgsProcessingParameterNumber
from .. import topopy
from ..topopy import DEM, Flow, Network
from qgis import processing
import ogr, osr
import numpy as np

class Net_shp(QgsProcessingAlgorithm):
	# Constants used to refer to parameters and outputs They will be
	# used when calling the algorithm from another algorithm, or when
	# calling from the QGIS console.
	
	INPUT_NT = 'INPUT_NT'   
	THRESHOLD = 'THRESHOLD'
	THETAREF = 'THETAREF'
	NPOINTS = 'NPOINTS'
	DIST = 'DIST'
	OUTPUT_SHP = 'OUTPUT_SHP'
 
	def __init__(self):
		super().__init__()

	def createInstance(self):
		return type(self)()
 
	def name(self):
		"""
		Rerturns the algorithm name, used to identify the algorithm.
		Must be unique within each provider and should contain lowercase alphanumeric characters only.
		"""
		return "Network_vectorial"
	 
	def displayName(self):
		"""
		Returns the translated algorithm name, which should be used for any
		user-visible display of the algorithm name.
		"""
		return self.tr("Network to polylines") 
	
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
					This script extract streams CHI values.
					
					Input Network: .dat file with Network information.
					
					Distance: Flow accumulation threshold to extract stream POI (in number of cells). Default 0.25% of	the total number of cells.
					
					Output Point Shape: Shape type polyline with:
						- id_profile : Profile identifier. Profiles are calculated from heads until outlets or  
						- L : Lenght from the middle point of the segment to the profile head
						- area_e6 : Drainage area in the segment mouth (divided by E6, to avoide large numbers) 
						- z : Elevation of the middle point of the segment
						- chi : Mean chi of the segment 
						- ksn : Ksn of the segment (calculated by linear regression)
						- slope : slope of the segment (calculated by linear regression)
						- rksn : R2 of the ksn linear regression
						- rslope : R2 of the slope linear regression
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
		self.addParameter(QgsProcessingParameterFile(self.INPUT_NT,  "Input Network", extension="dat"))
		self.addParameter(QgsProcessingParameterNumber(self.DIST, self.tr("Distance"), QgsProcessingParameterNumber.Double, optional=True,  minValue=0.01))
		self.addParameter(QgsProcessingParameterVectorDestination(self.OUTPUT_SHP, "CHI"))
 
	def processAlgorithm(self, parameters, context, feedback):
		"""
		Here is where the processing itself takes place.
		"""
		network = self.parameterAsFile(parameters, self.INPUT_NT, context)
		dist = self.parameterAsDouble(parameters, self.DIST, context)
		output_shp = self.parameterAsOutputLayer(parameters, self.OUTPUT_SHP, context)
  
		N = Network()
		N._load(network)
  
		N.get_chi_shapefile(output_shp, dist)
		
		
		
		results = {self.OUTPUT_SHP : output_shp, }
		return results