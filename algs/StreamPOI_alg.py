from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import QgsProcessingAlgorithm, QgsProcessingParameterRasterLayer, QgsProcessingParameterEnum, QgsProcessingParameterVectorDestination, QgsProcessingParameterNumber
from .. import topopy
from ..topopy import DEM, Flow, Grid
from qgis import processing
import ogr, osr
import numpy as np

class Stream_POI(QgsProcessingAlgorithm):
    # Constants used to refer to parameters and outputs They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.
    
    INPUT_DEM = 'INPUT_DEM'
    THRESHOLD = 'THRESHOLD'
    KIND = 'KIND'
    KIND_LIST = ['All', 'Heads', 'Confluences', 'Outlets']
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
        return "streampoi"
     
    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr("Stream POI") 
    
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
        self.addParameter(QgsProcessingParameterEnum(self.KIND, "Point Of Interest", self.KIND_LIST, False, 0))
        self.addParameter(QgsProcessingParameterVectorDestination(self.OUTPUT_SHP, "POIs"))
 
    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        input_dem = self.parameterAsRasterLayer(parameters, self.INPUT_DEM, context)
        threshold = self.parameterAsInt(parameters, self.THRESHOLD, context)
        points = self.parameterAsInt(parameters, self.KIND, context)
        output_shp = self.parameterAsOutputLayer(parameters, self.OUTPUT_SHP, context)
        
        dem = DEM(input_dem.source())
        fd = Flow(dem)

        if threshold == 0:
            threshold = int(fd.get_ncells() * 0.0025)
            
        driver = ogr.GetDriverByName('ESRI Shapefile')
        dataset = driver.CreateDataSource(output_shp)
        sp = osr.SpatialReference()
        sp.ImportFromWkt(fd._proj)
        layer = dataset.CreateLayer("POIs", sp, ogr.wkbPoint)      
        layer.CreateField(ogr.FieldDefn("Type", ogr.OFTString))

        def save_POI(flow, threshold, kind):
            poi = flow.get_stream_poi(threshold, kind, "XY")
            for i in range(len(poi)):
                point = ogr.Geometry(ogr.wkbPoint)
                point.AddPoint((poi[i])[0], (poi[i])[1])
                feat = ogr.Feature(layer.GetLayerDefn())
                feat.SetGeometry(point)
                value = kind.replace("s","")
                feat.SetField("Type", kind)
                layer.CreateFeature(feat) 
                
        if points == 0:        
            save_POI(fd, threshold, "heads")
            save_POI(fd, threshold, "confluences")
            save_POI(fd, threshold, "outlets")
            
        if points == 1:
            save_POI(fd, threshold, "heads")
           
        if points == 2:
            save_POI(fd, threshold, "confluences")
            
        if points == 3:
            save_POI(fd, threshold, "outlets")
        
        results = {self.OUTPUT_SHP : output_shp, }
        return results