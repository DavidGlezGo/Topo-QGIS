from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import QgsProcessingAlgorithm, QgsProcessingParameterFeatureSource, QgsProcessingParameterField, QgsProcessingParameterFile, QgsProcessingParameterFileDestination, QgsProcessing
from .. import topopy
from ..topopy import DEM, Flow, Network
from qgis import processing
import processing
import numpy as np

class Get_Channels(QgsProcessingAlgorithm):
	# Constants used to refer to parameters and outputs They will be
	# used when calling the algorithm from another algorithm, or when
	# calling from the QGIS console.
	
	INPUT_CH = 'INPUT_CH'
	ID_FIELD = 'ID_FIELD'
	INPUT_NT = 'INPUT_NT'
	OUTPUT_CH = 'OUTPUT_CH'
 
	def __init__(self):
		super().__init__()

	def createInstance(self):
		return type(self)()
 
	def name(self):
		"""
		Rerturns the algorithm name, used to identify the algorithm.
		Must be unique within each provider and should contain lowercase alphanumeric characters only.
		"""
		return "getchannels"
	 
	def displayName(self):
		"""
		Returns the translated algorithm name, which should be used for any
		user-visible display of the algorithm name.
		"""
		return self.tr("Channel Info") 
	
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
					This scrip saves channel information as Channel objects.
					
					Input Streams: polyline type layer of the streams to be saved.

					Input Network: .dat file with Network information.
					
					Channels Output: Output .npy file channels information.
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
		self.addParameter(QgsProcessingParameterFeatureSource(self.INPUT_CH,  "Input Streams", [QgsProcessing.TypeVectorLine]))
		self.addParameter(QgsProcessingParameterFile(self.INPUT_NT,  "Input Network", extension="dat"))
		self.addParameter(QgsProcessingParameterFileDestination(self.OUTPUT_CH, "Channels Output", 'NPY files (*.npy)'))
 
	def processAlgorithm(self, parameters, context, feedback):
		"""
		Here is where the processing itself takes place.
		"""

		input_ch = self.parameterAsSource(parameters, self.INPUT_CH, context)
		network = self.parameterAsFile(parameters, self.INPUT_NT, context)
		output_ch = self.parameterAsFileOutput(parameters, self.OUTPUT_CH, context)
		
		feedback.setProgressText('(1/3) Obtaining extremes of polylines.')
		try:
			explode = processing.run("native:explodelines", {'INPUT': parameters[self.INPUT_CH], 'OUTPUT': 'memory:' })['OUTPUT']
		except:
			feedback.setProgressText('¡¡¡¡¡ERROR!!!!! The input layer is not a polyline ')
			

		features = explode.getFeatures()

		unic=[]
		rep = []
		for feature in features:
			
			geom = feature.geometry()
			geom.length()
			L = geom.asPolyline()
			for X in L:
				if X in unic :
					unic.remove(X)
					rep.append(X)
				else:
					unic.append(X)
		for r in rep:
			
			if r in unic:
				unic.remove(r)
				
		feedback.setProgressText('(2/3) Classifying extremes.')
##----------------------------------------------------
		N = Network()
		N._load(network)
		H = N.get_stream_poi("heads", "IND")
##----------------------------------------------------
		
		heads = []
		mouths = []
		
		Channels = []
		for u in unic:
			
			cell = N.xy_2_cell(u[0],u[1])
			ind = N.cell_2_ind(cell[0],cell[1])
			
			if ind in H:
				heads.append((u[0],u[1]))
			else:
				mouths.append((u[0],u[1]))

		feedback.setProgressText('(3/3) Calculating and organizing channels, (if there are many channels it may take a bit).')	

		Dicc_L = {}
		Dicc_CH = {}
		
		for head in heads:
			for mouth in mouths:
				
				CH = N.get_channel(head, mouth)
				
				if not head in Dicc_L.keys():
					Dicc_L.update({head:CH.get_length()})
					Dicc_CH.update({head:CH})
				elif CH.get_length() < Dicc_L[head]:
					Dicc_L.update({head:CH.get_length()})
					Dicc_CH.update({head:CH})
					

		
		Channels = tuple(Dicc_CH.values())
		
		feedback.setProgressText("- HEADS: " + str(len(heads)))			
		feedback.setProgressText("- MOUTHS: " + str(len(mouths)))
		feedback.setProgressText( "- CHANNELS: " + str(len(Channels)))
		
		np.save(output_ch, Channels)
		
		
		results = {self.OUTPUT_CH : output_ch, }
		return results