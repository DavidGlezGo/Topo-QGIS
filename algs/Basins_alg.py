from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import QgsProcessingAlgorithm, QgsProcessingParameterRasterLayer, QgsProcessingParameterRasterDestination, QgsProcessingParameterNumber, QgsProcessingParameterFeatureSource, QgsProcessing
from .. import topopy
from ..topopy import DEM, Flow
from qgis import processing

class Get_Basins(QgsProcessingAlgorithm):
	# Constants used to refer to parameters and outputs They will be
	# used when calling the algorithm from another algorithm, or when
	# calling from the QGIS console.
	
	INPUT_FD = 'INPUT_FD'
	MIN_AREA = 'MIN_AREA'
	OUTLETS = 'OUTLETS'
	OUTPUT_BAS = 'OUTPUT_BAS'
 
	def __init__(self):
		super().__init__()

	def createInstance(self):
		return type(self)()
 
	def name(self):
		"""
		Rerturns the algorithm name, used to identify the algorithm.
		Must be unique within each provider and should contain lowercase alphanumeric characters only.
		"""
		return "getbasins"
	 
	def displayName(self):
		"""
		Returns the translated algorithm name, which should be used for any
		user-visible display of the algorithm name.
		"""
		return self.tr("Get Drainage Basins") 
	
	def groupId(self):
		"""
		Returns the unique ID of the group this algorithm belongs to.
		"""
		return "dem_processing"

	def group(self):
		"""
		Returns the name of the group this algoritm belongs to.
		"""
		return self.tr("DEM Processing")

	def shortHelpString(self):
		"""
		Returns a localised short helper string for the algorithm. 
		"""
		texto = """
					This function extracts the drainage basins for the Flow object and returns a Grid object that can be saved into the disk.
					
					Flow: Flow direccion raster

					Minimum area: Minimum area for basins to avoid very small basins. The area is given as a percentage of the total	number of cells (default 0.5%).
					
					Basins: Output basins raster.
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
		self.addParameter(QgsProcessingParameterRasterLayer(self.INPUT_FD,  self.tr("Flow Direction")))
		self.addParameter(QgsProcessingParameterNumber(self.MIN_AREA, self.tr("Minimum area (%)"), QgsProcessingParameterNumber.Double, 0.5, True, 0.001, 100))
		self.addParameter(QgsProcessingParameterFeatureSource(self.OUTLETS,  "Outlets", [QgsProcessing.TypeVectorPoint], optional = True))
		self.addParameter(QgsProcessingParameterRasterDestination(self.OUTPUT_BAS, self.tr("Basins"), None, False))
 
	def processAlgorithm(self, parameters, context, feedback):
		"""
		Here is where the processing itself takes place.
		"""
		input_fd = self.parameterAsRasterLayer(parameters, self.INPUT_FD, context)
		min_area = self.parameterAsDouble(parameters, self.MIN_AREA, context)
		outlets = self.parameterAsSource(parameters, self.OUTLETS, context)
		output_bas = self.parameterAsOutputLayer(parameters, self.OUTPUT_BAS, context)

		fd = Flow()
		fd.load(input_fd.source())
		
		area = min_area/100
		
		if outlets != None:
			features = outlets.getFeatures()
			out_arr = []
			for feature in features:
				geom = feature.geometry()
				P = geom.asPoint()
				out_arr.append(P)
			
		gbas = fd.get_drainage_basins(outlets=outlets, min_area=area)
		gbas.save(output_bas)
		
		results = {self.OUTPUT_BAS : output_bas, }
		return results