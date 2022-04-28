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


    def adm(self):

        self.europa_border  = self.add_vector(mapset='adm', layer='Europa_Border', db_layer='Europa_Border', db_location=str(self.grass_location['crop_yield']['location']), db_path=str(self.path.gis_projects.joinpath(str(self.grass_location['crop_yield']['db_path']))), ext='grass')
        self.nuts_0  = self.add_vector(mapset='adm', layer='NUTS_0', db_layer='NUTS_0', db_location=str(self.grass_location['crop_yield']['location']), db_path=str(self.path.gis_projects.joinpath(str(self.grass_location['crop_yield']['db_path']))), ext='grass')
        self.nuts_2  = self.add_vector(mapset='adm', layer='NUTS_2', db_layer='NUTS_2', db_location=str(self.grass_location['crop_yield']['location']), db_path=str(self.path.gis_projects.joinpath(str(self.grass_location['crop_yield']['db_path']))), ext='grass')

        self.mask  = self.add_raster(mapset='adm', layer='Europa_MASK_1000m', in_file='Europa_MASK_1000m.pack', in_folder=str(self.path.gis_projects.joinpath(str(self.grass_location['crop_yield']['path']),'01_Data','02_Raster','pack')), ext='pack' )


################

    # ____________________ print attributes
    def __str__(self):
        return  '\n'.join((f'\n____________ {key} ____________\n{value}' for key, value in self.__dict__.items()))
