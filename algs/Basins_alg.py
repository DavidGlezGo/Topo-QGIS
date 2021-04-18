from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import QgsProcessingAlgorithm, QgsProcessingParameterRasterLayer, QgsProcessingParameterRasterDestination, QgsProcessingParameterNumber
from .. import topopy
from ..topopy import DEM, Flow
from qgis import processing

class Get_Basins(QgsProcessingAlgorithm):
    # Constants used to refer to parameters and outputs They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.
    
    INPUT_DEM = 'INPUT_DEM'
    MIN_AREA = 'MIN_AREA'
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
        self.addParameter(QgsProcessingParameterRasterLayer(self.INPUT_DEM,  self.tr("Filled DEM")))
        self.addParameter(QgsProcessingParameterNumber(self.MIN_AREA, self.tr("Minimum area (%)"), QgsProcessingParameterNumber.Double, 0.5, True, 0.001, 100))
        self.addParameter(QgsProcessingParameterRasterDestination(self.OUTPUT_BAS, self.tr("Basins"), None, False))
 
    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        input_dem = self.parameterAsRasterLayer(parameters, self.INPUT_DEM, context)
        min_area = self.parameterAsDouble(parameters, self.MIN_AREA, context)
        output_bas = self.parameterAsOutputLayer(parameters, self.OUTPUT_BAS, context)
        
		
        dem = DEM(input_dem.source())
        fd = Flow(dem)
        area = min_area/100
        gbas = fd.get_drainage_basins(min_area=area)
        gbas.save(output_bas)
        
        results = {self.OUTPUT_BAS : output_bas, }
        return results