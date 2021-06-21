from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import QgsProcessingAlgorithm, QgsProcessingParameterFile, QgsProcessingParameterVectorDestination, QgsProcessingParameterString, QgsProcessingParameterRasterLayer, QgsProcessingParameterNumber, QgsProcessingParameterFileDestination
from .. import topopy
from ..topopy import *
from qgis import processing
import numpy as np
import ogr, osr

class Basin_Channels(QgsProcessingAlgorithm):
	# Constants used to refer to parameters and outputs They will be
	# used when calling the algorithm from another algorithm, or when
	# calling from the QGIS console.
	
	INPUT_NT = 'INPUT_NT'	
	BASINS = 'BASINS'
	ID = 'ID'
	OUTPUT_CHs = 'OUTPUT_CHs'
 
	def __init__(self):
		super().__init__()

	def createInstance(self):
		return type(self)()
 
	def name(self):
		"""
		Rerturns the algorithm name, used to identify the algorithm.
		Must be unique within each provider and should contain lowercase alphanumeric characters only.
		"""
		return "basinchannels"
	 
	def displayName(self):
		"""
		Returns the translated algorithm name, which should be used for any
		user-visible display of the algorithm name.
		"""
		return self.tr("Basins Channels") 
	
	def groupId(self):
		"""
		Returns the unique ID of the group this algorithm belongs to.
		"""
		return "drainage_ch_processing"

	def group(self):
		"""
		Returns the name of the group this algoritm belongs to.
		"""
		return self.tr("Drainage Channel Processing")

	def shortHelpString(self):
		"""
		Returns a localised short helper string for the algorithm. 
		"""
		texto = """
					this script converts channels from .npy format to vectorial format.
					
					Input Channels: .npy file with the channels inside.

					Channels: polyline 25D ShapeFile with channels information.
					
					Knickpoints: point 25D ShapeFile with channels knickpoint information.
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
		self.addParameter(QgsProcessingParameterFile(self.INPUT_NT,  self.tr("Network"), extension="dat"))
		self.addParameter(QgsProcessingParameterRasterLayer(self.BASINS,  self.tr("Basins")))
		self.addParameter(QgsProcessingParameterNumber(self.ID,  self.tr("ID basin"), QgsProcessingParameterNumber.Integer,  minValue=1))
		self.addParameter(QgsProcessingParameterFileDestination(self.OUTPUT_CHs, "Channels Output", 'NPY files (*.npy)'))


	def processAlgorithm(self, parameters, context, feedback):
		"""
		Here is where the processing itself takes place.
		"""
		network = self.parameterAsFile(parameters, self.INPUT_NT, context)
		basins = self.parameterAsRasterLayer(parameters, self.BASINS, context)
		id = self.parameterAsInt(parameters, self.ID, context)
		output_ch = self.parameterAsFileOutput(parameters, self.OUTPUT_CHs, context)
		
		nt = Network()
		nt._load(network)		
		
		bs = Grid(basins.source())
		
		bn = BNetwork(net=nt, basingrid=bs, bid=id)
		
		print(bn._heads)

		
		Channels = bn.get_channels(aschannel=True)
		
		np.save(output_ch, Channels)

		results = {self.OUTPUT_CHs : output_ch, }			
		return results