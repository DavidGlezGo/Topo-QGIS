# -*- coding: utf-8 -*-
from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import QgsProcessingAlgorithm, QgsProcessingParameterRasterLayer, QgsProcessingParameterRasterDestination, QgsProcessingParameterBoolean
from .. import topopy
from ..topopy import DEM
from qgis import processing

class Fill(QgsProcessingAlgorithm):
    # Constants used to refer to parameters and outputs They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    INPUT_DEM = 'INPUT_DEM'
    OUTPUT_FILL = 'OUTPUT_FILL'
    ALTERNATIVE = 'ALTERNATIVE'
 
    def __init__(self):
        super().__init__()

    def createInstance(self):
        return type(self)()
 
    def name(self):
        """
        Rerturns the algorithm name, used to identify the algorithm.
        Must be unique within each provider and should contain lowercase alphanumeric characters only.
        """
        return "fill"
     
    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr("Fill") 
    
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
                    This script fills the pits of a Digital Elevacion Model (DEM)
                    
                    Input DEM : Input Digital Elevation Model (DEM).
                    
                    Use alternate fill: Alternative calculation algorithm.
                    
                    Filled DEM : Output pi-filled DEM.
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
        self.addParameter(QgsProcessingParameterRasterLayer(self.INPUT_DEM,  self.tr("Input DEM")))
        self.addParameter(QgsProcessingParameterBoolean(self.ALTERNATIVE, "Use alternate fill", False))
        self.addParameter(QgsProcessingParameterRasterDestination(self.OUTPUT_FILL, "Filled DEM", None, False))

 
    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        input_dem = self.parameterAsRasterLayer(parameters, self.INPUT_DEM, context)
        alternative = self.parameterAsBool(parameters, self.ALTERNATIVE, context)
        output_fill = self.parameterAsOutputLayer(parameters, self.OUTPUT_FILL, context)
        
        dem = DEM(input_dem.source())
        feedback.setProgressText(str(type(dem)))
        if alternative:
            feedback.setProgressText("Alternative Fill")
            fill = dem.fill_sinks2()
        else:
            fill = dem.fill_sinks()
            
        feedback.setProgressText(str(type(fill)))
        fill.save(output_fill)
        
        results = {self.OUTPUT_FILL : output_fill}
        return results