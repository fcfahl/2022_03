import logging
import grass.script as grass
import grass.script.setup as gsetup
from grass.pygrass.modules.shortcuts import general as g
from grass.pygrass.modules import Module

import models.M02_layers as lyr


class Generic(lyr.Layer):

    def __init__(self, mapset, model=None, layer=None, in_file=None, out_file=None, in_folder=None, out_folder=None,
                 **kwargs):

        lyr.Layer.__init__(self, mapset=mapset, model=model, layer=layer, in_file=in_file, out_file=out_file,
                           in_folder=in_folder, out_folder=out_folder, **kwargs)

    ################## MAPSET
    def get_current_mapset(self):
        return (grass.gisenv()['MAPSET'])

    def set_mapset(self, mapset=None, flags='c'):
        if (self.mapset != self.get_current_mapset()): g.mapset(mapset=self.mapset, flags=flags)

    def add_mapset_to_layer(self, layer=None):
        self.layer_at = f"{useIf(self.layer, value=layer)}@{self.mapset}"

        ################## REGION

    def get_region(self):
        return (grass.region())

    def get_nsres(self, input=None):
        return float(grass.region()['nsres'])

    def get_ewres(self, input=None):
        return float(grass.region()['ewres'])

    def set_region(self, format=None, in_file=None, in_raster=None, north=None, south=None, west=None, east=None,
                   res=None, flags='a'):

        if format == 'vector':
            g.region(vector=useIf(self.layer, value=in_file), align=in_raster, res=res, flags=flags, quiet=self.quiet)
        elif format == 'raster':
            g.region(raster=in_file, flags=flags, quiet=self.quiet)
        elif format == 'bounds':
            g.region(n=north, s=south, w=west, e=east, res=res, flags=flags, quiet=self.quiet)
        elif format == 'resolution':
            g.region(nsres=res, ewres=res, flags=flags, quiet=self.quiet)
        else:
            print(f"{in_file} <- unable to set region")

    def region(self, flags=''):
        """ simplified method to get the region"""
        g.region(raster=self.layer_at, flags=flags, quiet=self.quiet)

    ################## RESOLUTION    

    def set_resolution(self, nsres=None, ewres=None, flag='a'):
        g.region(nsres=nsres, ewres=ewres, flags=flag, quiet=self.quiet)

    def get_pixel_area_m2(self, input=None):
        return self.get_nsres() * self.get_ewres()

    def get_pixel_area_ha(self, input=None):
        return self.get_pixel_area_m2() / 10000

    ################## LAYERS

    def set_tmp(self):
        self.tmp = f'TMP_{self.layer}'
        # self.tmp_at = f"{self.tmp}@{self.mapset}"   

    def copy_layer(self, type=None, in_file=None, out_file=None):

        copy = f"{in_file},{out_file}"

        if self.model == "vector" or type == "vector":
            g.copy(vector=[copy], overwrite=True)

        elif self.model == "raster" or type == "raster":
            g.copy(raster=[copy], overwrite=True)
        else:
            print("none to copy")

    def remove_layer(self, map=None, tmp=False):
        if tmp:
            g.remove(type=self.model, name=self.tmp, flags='f')
        else:
            g.remove(type=self.model, name=map, flags='f')

    def remove_pattern(self, type_=None, pattern=None, exclude=None):
        g.remove(type=useIf(self.model, value=type_), pattern=pattern, exclude=exclude, flags='f')

    def select_files(self, type, pattern, exclude="", mapset="PERMANENT"):
        return str(grass.read_command('g.list', type=type, mapset=mapset, pattern=pattern, exclude=exclude, sep=',',
                                      flags='m')).rstrip('\r\n')

    def rename_file(self, old, new):

        in_files = f"{old},{new}"

        if self.model == 'vector':
            g.rename(vector=[in_files], overwrite=True)
        elif self.model == 'raster':
            g.rename(raster=[in_files], overwrite=True)
        else:
            print('unable to rename ', old)

    def clean_up_tmp(self, type_, pattern='TMP_*', exclude=None):
        self.remove_pattern(type_=useIf(self.model, value=type_), pattern=pattern, exclude=exclude)

    ##################  Generic layer description
    def set_source(self, source):
        self.source = source

    def set_description(self, description):
        self.description = description

    def set_unit(self, unit):
        self.unit = unit

    def set_native_projection(self, proj):
        self.native_projection = proj

    ##################  Pixel area

    def get_pixel_area(self, unit='meters'):

        pixel_area = self.get_resolution() ** 2

        if unit == 'hectares' or unit == 'hectare' or unit == 'ha':
            return pixel_area / 10000
        elif unit == 'meters' or unit == 'meter' or unit == 'm':
            return pixel_area
        elif unit == 'kilometers' or unit == 'kilometer' or unit == 'km':
            return pixel_area / 1000000
        else:
            print('unit of area not defined')


# ____________________ Overwrite IO parameters
def useIf(attr, value=None):
    return (value if value else attr)
