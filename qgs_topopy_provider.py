# -*- coding: utf-8 -*-

"""
/***************************************************************************
 QgsTopopy
                                 A QGIS plugin
 Analysis and evaluation of topography and drainage networks
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2021-03-17
        copyright            : (C) 2021 by J. Vicente Pérez Peña
        email                : vperez@go.ugr.es / geolovic@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

__author__ = 'J. Vicente Pérez Peña'
__date__ = '2021-03-17'
__copyright__ = '(C) 2021 by J. Vicente Pérez Peña'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from qgis.core import QgsProcessingProvider
from .algs.Fill_alg import Fill
from .algs.FlowDir_alg import FlowDir
from .algs.FlowAcc_alg import FlowAccumulation
from .algs.StreamPOI_alg import Stream_POI
from .algs.Basins_alg import Get_Basins
from .algs.Ch2Vector import Channel2Vector
from .algs.StreamSHP_alg import Streams2shp
from .algs.Chishp_alg import Net_shp
from .algs.Channels_alg import Get_Channels
from .algs.Network_alg import Get_Network
from .algs.Network2csv_alg import Network2csv
from .algs.Network2points_alg import Network2points
class QgsTopopyProvider(QgsProcessingProvider):

    def __init__(self):
        """
        Default constructor.
        """
        QgsProcessingProvider.__init__(self)

    def unload(self):
        """
        Unloads the provider. Any tear-down steps required by the provider
        should be implemented here.
        """
        pass

    def loadAlgorithms(self):
        """
        Loads all algorithms belonging to this provider.
        """
        self.algs = [Fill(),
                    FlowDir(),
                    FlowAccumulation(),
                    Stream_POI(),
                    Get_Basins(),
                    Channel2Vector(),
                    Streams2shp(),
                    Net_shp(),
                    Get_Channels(),
                    Get_Network(),
                    Network2csv(),
                    Network2points(),
					
                    ]
                    
        # add additional algorithms here
        # self.addAlgorithm(MyOtherAlgorithm())
        
        for alg in self.algs:
            self.addAlgorithm( alg )

    def id(self):
        """
        Returns the unique provider id, used for identifying the provider. This
        string should be a unique, short, character only string, eg "qgis" or
        "gdal". This string should not be localised.
        """
        return 'Qgs Topopy'

    def name(self):
        """
        Returns the provider name, which is used to describe the provider
        within the GUI.

        This string should be short (e.g. "Lastools") and localised.
        """
        return self.tr('Qgs Topopy')

    def icon(self):
        """
        Should return a QIcon which is used for your provider inside
        the Processing toolbox.
        """
        return QgsProcessingProvider.icon(self)

    def longName(self):
        """
        Returns the a longer version of the provider name, which can include
        extra details such as version numbers. E.g. "Lastools LIDAR tools
        (version 2.2.1)". This string should be localised. The default
        implementation returns the same string as name().
        """
        return self.name()
