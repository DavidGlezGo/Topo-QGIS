from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import QgsProcessingAlgorithm, QgsProcessingParameterFile, QgsProcessingParameterRasterLayer, QgsProcessingParameterVectorDestination, QgsProcessingParameterBoolean, QgsProcessingParameterFileDestination
from .. import topopy
from ..topopy import DEM, Flow, Network
from qgis import processing

class Network2csv(QgsProcessingAlgorithm):
    # Constants used to refer to parameters and outputs They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.
    
    INPUT_NT = 'INPUT_NT'
    OUTPUT_CSV = 'OUTPUT_CSV'
 
    def __init__(self):
        super().__init__()

    def createInstance(self):
        return type(self)()
 
    def name(self):
        """
        Rerturns the algorithm name, used to identify the algorithm.
        Must be unique within each provider and should contain lowercase alphanumeric characters only.
        """
        return "Network2csv"
     
    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr("Network to CSV") 
    
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
                    
                    Network: .dat file with Network information..

                    Segmented Streams: [Checked] the Strahler and Shreeve order are calculated, [Not Checked] only Strahler order.
                    
                    Stream Order: Output polylineas 25D with streams order.
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
        self.addParameter(QgsProcessingParameterFileDestination(self.OUTPUT_CSV, "Network Output", 'CSV files (*.csv)'))
 
    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        input_nt = self.parameterAsFile(parameters, self.INPUT_NT, context)
        output_csv = self.parameterAsFileOutput(parameters, self.OUTPUT_CSV, context)
               
        nt = Network()
        nt._load(input_nt)
        
        nt.export_to_points(output_csv)
        
        
        results = {self.OUTPUT_CSV : output_csv, }
        return results