from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import QgsProcessingAlgorithm, QgsProcessingParameterRasterLayer, QgsProcessingParameterVectorDestination, QgsProcessingParameterBoolean
from .. import topopy
from ..topopy import DEM, Flow, Network
from qgis import processing

class Streams2shp(QgsProcessingAlgorithm):
    # Constants used to refer to parameters and outputs They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.
    
    INPUT_DEM = 'INPUT_DEM'
    CON = 'CON'
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
        return "Channels2shp"
     
    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr("Extract Streams") 
    
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
                    
                    Flow: Flow accumulation raster.

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
        self.addParameter(QgsProcessingParameterRasterLayer(self.INPUT_DEM,  self.tr("Flow Accumulation")))
        self.addParameter(QgsProcessingParameterBoolean(self.CON, "Segmented Streams", False))
        self.addParameter(QgsProcessingParameterVectorDestination(self.OUTPUT_SHP, self.tr("Streams")))
 
    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        input_dem = self.parameterAsRasterLayer(parameters, self.INPUT_DEM, context)
        con = self.parameterAsBool(parameters, self.CON, context)
        output_shp = self.parameterAsOutputLayer(parameters, self.OUTPUT_SHP, context)
       
        dem = DEM(input_dem.source())
        fd = Flow(dem)
        nt = Network(fd)
        if con == 0:
            shp = nt.export_to_shp(output_shp, True)
           
        if con == 1:
            shp = nt.export_to_shp(output_shp)
        
        
        results = {self.OUTPUT_SHP : output_shp, }
        return results