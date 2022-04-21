import logging, wrapt
# import models.utils.log as log
import grass.script as grass
import grass.script.setup as gsetup
from grass.pygrass.modules.shortcuts import raster as r
from grass.pygrass.modules import Module

import models.M04_rasters as rst
from models.M03_generic import useIf

class Soil(rst.Raster):

    def __init__(self, mapset, prefix=None, band=None, layer=None, file_prefix=None, in_file=None, in_folder=None, period=None, unit=None, stats=None, nodata=-9999, source=None, **kwargs):

        rst.Raster.__init__(self, mapset=mapset, layer=layer, prefix=prefix, in_file=in_file, in_folder=in_folder, file_prefix=file_prefix, **kwargs)

        self.layer=layer
        self.period=period
        self.null_value=nodata
        self.set_source(source)
        # self.set_description(f'Soil monthly average values for [{layer}]')
        self.set_unit(unit)
        self.set_native_projection('EPSG:4326')
        self.stats=stats        

    def get_soil_layer_name(self, stats, month, day=None):
        if self.layer:
            layer =  self.layer
        else:
            layer =  f'{self.prefix}_{self.unit}_{stats}_{month:0>2}_{self.get_month_name(month)}'

        return layer

    def get_soil_layer_name_at(self, stats, month, day=None):
        return f'{self.get_soil_layer_name(stats, month)}@{self.mapset}'

    def get_soil_layer_name_by_prefix(self, prefix, stats, month, day=None):
        return f'{prefix}_{self.unit}_{stats}_{month:0>2}_{self.get_month_name(month)}'

    def get_soil_input_file(self, stats, month):

        try:
            self.in_file_path = str(self.in_folder.joinpath(stats, f'{self.file_prefix}_{stats}_{month:02d}.nc'))
        except:
            self.in_file_path = None

    def set_soil_layer(self, stats, month, day=None):

        self.month = month   
        self.stat = stats

        self.layer = self.get_soil_layer_name(stats, month)
        self.add_mapset_to_layer()

    def get_soil_layer(self, month, day=None, at=True):

        layer = dict()

        for stat in self.stats:
            if at:
                layer[stat] = self.get_soil_layer_name_at(stat, month)
            else:
                layer[stat] = self.get_soil_layer_name(stat, month)

        return layer





