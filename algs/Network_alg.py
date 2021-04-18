from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import QgsProcessingAlgorithm, QgsProcessingParameterRasterLayer, QgsProcessingParameterNumber, QgsProcessingParameterFileDestination, QgsProcessing
from .. import topopy
from ..topopy import DEM, Flow, Network
from qgis import processing
import processing

class Get_Network(QgsProcessingAlgorithm):
    # Constants used to refer to parameters and outputs They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.
    
    INPUT_DEM = 'INPUT_DEM'
    THRESHOLD = 'THRESHOLD'
    THETAREF = 'THETAREF'
    NPOINTS = 'NPOINTS'
    OUTPUT_N = 'OUTPUT_N'
 
    def __init__(self):
        super().__init__()

    def createInstance(self):
        return type(self)()
 
    def name(self):
        """
        Rerturns the algorithm name, used to identify the algorithm.
        Must be unique within each provider and should contain lowercase alphanumeric characters only.
        """
        return "getnetwork"
     
    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr("Network Info") 
    
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
                    This script saves the Network instance to disk. It will be saved as a numpy array in text format with a header.
					The first three lines will have the information of the raster:
					Line1::   xsize; ysize; cx; cy; ULx; ULy; Tx; Ty
					Line2::   thetaref; threshold; slp_np; ksn_np
					Line3::   String with the projection (WKT format)
					xsize, ysize >> Dimensions of the raster
					cx, cy >> Cellsizes in X and Y
					Tx, Ty >> Rotation factors (for geotransformation matrix)
					ULx, ULy >> X and Y coordinates of the corner of the upper left pixel of the raster
					thetaref >>  m/n coeficient to calculate chi values in each channel cell
					threshold >> Number the cells to initiate a channel
					slp_np, ksn_np >> Number of points to calculate ksn and slope by regression. Window of {npoints * 2 + 1}
                    -------- INPUTS --------
                    Input filled DEM : Input pit-filled Digital Elevation Model (DEM).
					
					Threshold: Flow accumulation threshold to extract stream POI (in number of cells). Default 0.25% of    the total number of cells.

					Thetaref: m/n coeficient to calculate chi values in each channel cell . 
					
					Npoints: Number of points to calculate slope and ksn in each cell.
					
					Network Output: Output Netfork file .dat format.
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
        self.addParameter(QgsProcessingParameterFileDestination(self.OUTPUT_N, "Network Output", 'DAT files (*.dat)'))
 
    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        input_dem = self.parameterAsRasterLayer(parameters, self.INPUT_DEM, context)
        threshold = self.parameterAsInt(parameters, self.THRESHOLD, context)
        thetaref = self.parameterAsDouble(parameters, self.THETAREF, context)
        npoints = self.parameterAsInt(parameters, self.NPOINTS, context)
        output_n = self.parameterAsFileOutput(parameters, self.OUTPUT_N, context)

        dem = DEM(input_dem.source())
        fd = Flow(dem)
        nt = Network(fd, threshold, thetaref, npoints, gradients=True)
        nt.save(output_n)
        
        
        results = {self.OUTPUT_N : output_n, }
        return results