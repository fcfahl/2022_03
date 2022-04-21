import logging


import models.M01_base as bse
import models.M04_rasters as rst
import models.M05_vectors as vct


class Controller(bse.Base):

    vectors = dict()
    rasters = dict()

    def __init__(self):

        bse.Base.__init__(self)

        self.path = self.get_path()
        self.utl = self.get_utl()

        self.reset_logs()
        self.get_logger(self.path, self.utl)


    ####################

    def add_vector(self, mapset, layer, in_file=None, db_layer=None, in_folder=None, ext=None, **kwargs):

        self.vectors[layer] = vct.Vector(mapset=mapset, layer=layer, in_file=in_file, db_layer=db_layer, in_folder=in_folder, ext=ext, **kwargs)
        return self.vectors[layer]

    def add_raster(self, mapset, layer, in_file=None, in_folder=None, ext=None, **kwargs):

        self.rasters[layer] = rst.Raster(mapset=mapset, layer=layer, in_file=in_file, in_folder=in_folder, ext=ext, **kwargs)
        return self.rasters[layer]


    def adm(self, iso3code=None):

        self.europa_border  = self.add_vector(mapset='adm', layer='Europa_Border',  in_file='ref-coastline-2016-EPSG3035.gpkg', db_layer='EU_COAS_RG_20M_2016', in_folder=self.path.administrative['Europa'].joinpath('Eurostat', '03_EU_Coast_lines', 'Eurostat'), ext='gpkg')
        self.nuts_0         = self.add_vector(mapset='adm', layer='NUTS_0',         in_file='NUTS_2021_1M_EPSG3035_Europa_Extension.gpkg', db_layer='NUTS_0_Europa_No_Turkey', in_folder=self.path.administrative['Europa'].joinpath('Eurostat', '02_Europa_Extended'), ext='gpkg')
        self.nuts_2         = self.add_vector(mapset='adm', layer='NUTS_2',         in_file='NUTS_2021_1M_EPSG3035_Europa_Extension.gpkg', db_layer='NUTS_2_Europa_No_Turkey', in_folder=self.path.administrative['Europa'].joinpath('Eurostat', '02_Europa_Extended'), ext='gpkg')

        self.mask           = self.add_raster(mapset='adm', layer=f'Europa_MASK_{self.resolution}m', resolution=self.resolution)

        if iso3code:
            self.country  = self.add_vector(mapset='adm', layer=f'Country_{iso3code}')


################

    # ____________________ print attributes
    def __str__(self):
        return  '\n'.join((f'\n____________ {key} ____________\n{value}' for key, value in self.__dict__.items()))
