from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import QgsProcessingAlgorithm, QgsProcessingParameterRasterLayer, QgsProcessingParameterEnum, QgsProcessingParameterVectorDestination, QgsProcessingParameterNumber
from .. import topopy
from ..topopy import DEM, Flow, Network
from qgis import processing
import ogr, osr
import numpy as np

class Chi_shp(QgsProcessingAlgorithm):
    # Constants used to refer to parameters and outputs They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.
    
    INPUT_DEM = 'INPUT_DEM'
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
        return "CHIshp"
     
    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr("CHI") 
    
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
                    This script finds points of interest of the drainage network.
                    
                    Flow: Flow direccion raster.
                    
                    Threshold: Flow accumulation threshold to extract stream POI (in number of cells). Default 0.25% of    the total number of cells.
                    
                    Kind: Kind of point of interest to return.
                    
                    Output Point Shape: Shape type point with POI
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
        self.addParameter(QgsProcessingParameterNumber(self.THRESHOLD, self.tr("Threshold"), QgsProcessingParameterNumber.Integer, optional=True,  minValue=1))
        self.addParameter(QgsProcessingParameterNumber(self.THETAREF, self.tr("Thetaref"), QgsProcessingParameterNumber.Double, 0.45,  optional=True,  minValue=0))
        self.addParameter(QgsProcessingParameterNumber(self.NPOINTS, self.tr("npoints"), QgsProcessingParameterNumber.Integer, 5, optional=True,  minValue=1))
        self.addParameter(QgsProcessingParameterNumber(self.DIST, self.tr("Distance"), QgsProcessingParameterNumber.Double, optional=True,  minValue=0.01))
        self.addParameter(QgsProcessingParameterVectorDestination(self.OUTPUT_SHP, "CHI"))
 
    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        input_dem = self.parameterAsRasterLayer(parameters, self.INPUT_DEM, context)
        threshold = self.parameterAsInt(parameters, self.THRESHOLD, context)
        thetaref = self.parameterAsDouble(parameters, self.THETAREF, context)
        npoints = self.parameterAsInt(parameters, self.NPOINTS, context)
        dist = self.parameterAsDouble(parameters, self.DIST, context)
        output_shp = self.parameterAsOutputLayer(parameters, self.OUTPUT_SHP, context)
        
        dem = DEM(input_dem.source())
        fd = Flow(dem)
        nt = Network(fd, threshold, thetaref, npoints, gradients=True)
        nt.get_chi_shapefile(output_shp, dist)
        
        
        
        results = {self.OUTPUT_SHP : output_shp, }
        return results