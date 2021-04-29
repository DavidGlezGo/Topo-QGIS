from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import QgsProcessingAlgorithm, QgsProcessingParameterFile, QgsProcessingParameterRasterLayer, QgsProcessingParameterRasterDestination, QgsProcessingParameterEnum
from .. import topopy
from ..topopy import DEM, Flow, Network
from qgis import processing

class Get_Orders(QgsProcessingAlgorithm):
	# Constants used to refer to parameters and outputs They will be
	# used when calling the algorithm from another algorithm, or when
	# calling from the QGIS console.
	
	INPUT_NT = 'INPUT_NT'	
	KIND = 'KIND'
	KIND_LIST = ['Strahler', 'Shreeve']
	OUTPUT_ORDER = 'OUTPUT_ORDER'
 
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
		return self.tr("Get Stream Orders") 
	
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
		self.addParameter(QgsProcessingParameterFile(self.INPUT_NT,  "Input Network", extension="dat"))
		self.addParameter(QgsProcessingParameterEnum(self.KIND, "Stream Order", self.KIND_LIST, False, 0))
		self.addParameter(QgsProcessingParameterRasterDestination(self.OUTPUT_ORDER, self.tr("Stream Order"), None, False))
 
	def processAlgorithm(self, parameters, context, feedback):
		"""
		Here is where the processing itself takes place.
		"""
		network = self.parameterAsFile(parameters, self.INPUT_NT, context)
		order = self.parameterAsInt(parameters, self.KIND, context)
		output_order = self.parameterAsOutputLayer(parameters, self.OUTPUT_ORDER, context)
	   
		N = Network()
		N._load(network)
		
		if order == 0:
			outo = N.get_stream_orders()
		   
		if order == 1:
			outo = N.get_stream_orders('shreeve')
		
		outo.save(output_order)
		
		results = {self.OUTPUT_ORDER : output_order, }
		return results