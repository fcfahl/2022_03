import math

import grass.script as grass
import grass.script.setup as gsetup
from grass.pygrass.modules.shortcuts import raster as r
from grass.pygrass.modules import Module

import models.M03_generic as gnr
from models.M03_generic import useIf



class Raster(gnr.Generic):

    def __init__(self, mapset, model='raster', in_file=None, layer=None, out_file=None, in_folder=None, out_folder=None, **kwargs):

        gnr.Generic.__init__(self, mapset=mapset, model=model, in_file=in_file, layer=layer, out_file=out_file, in_folder=in_folder, out_folder=out_folder, **kwargs)

        # print(self)

    def run_module(func):
        func_name = func.__name__

        def __init__(self, label: str = None):
            self.label = label

        def __call__(self, func):
            if self.label is None:  # Label was not provided
                self.label = func.__name__  # Use function's name.
            return super().__call__(func)

            print(func_name)

        # self.log =



    # _________________ Import methods
    @run_module
    def import_raster (self, input=None, output=None, band=1, flags=''):
        self.run = Module("r.in.gdal", input=useIf(self.in_file_path, value=input), output=useIf(self.layer, output), band=band, overwrite=True, flags=flags)

    @run_module
    def import_raster_reproject (self, input=None, output=None, band=1, resolution='region', extent='region', resample='nearest', resolution_value=None, flags=''):
        self.run = Module("r.import", input=useIf(self.in_file_path, value=input), output=useIf(self.layer, output), band=band, resample=resample, extent=extent, resolution=resolution, resolution_value=resolution_value, flags=flags, overwrite=True, quiet=self.quiet)

    def import_raster_grass (self, db_location=None, db_mapset=None, db_layer=None, db_path=None, output=None):
        self.run = Module("r.proj", location=useIf(self.db_location, db_location), mapset=useIf(self.db_mapset, db_mapset), dbase=useIf(self.db_path, db_path), input=useIf(self.db_layer, db_layer), output=useIf(self.layer, output), overwrite=True, quiet=self.quiet)

    def import_netcdf_unscale(self, netcdf, output, band, scale, offset):

        tmp = f"TMP_{output}"

        self.import_raster (input=netcdf, output=tmp, band=band, flag='eo')
        self.region(input=tmp)
        self.raster_calculator (f"{output}  = {tmp} * {scale} + {offset}")

        self.remove_file(map=tmp)



    # _________________ Conversio methods
    def vectorize_raster(self, input=None, output=None, band=1, type='area', column=None, flags=''):
        self.run = Module("r.to.vect", input=useIf(self.layer, value=input), output=useIf(self.layer, output), type=type, column=column, flags=flags, overwrite=True, quiet=self.quiet)


    # _________________ Process methods
    def clip_raster_with_vector (self, layer=None, vector=None):

        in_file_ = useIf(self.layer, layer)
        tmp_file = f"TMP_{in_file_}"

        self.region(flags='ap')

        self.copy_layer('raster', in_file_, tmp_file) # duplicate raster

        self.rasterize_vector (input=vector, layer=self.mask)

        self.raster_calculator(f"{in_file_} = if({self.mask}, {tmp_file}, null())  ") # clip raster
        self.remove_layer(map=tmp_file)
        self.remove_layer(map=self.mask)

    def clip_raster (self, in_file=None, in_mask=None, mapset=None):

        in_file_ = useIf(self.layer, in_file)
        tmp_file = f"TMP_{in_file_}"

        self.region(flags='ap')

        self.copy_layer('raster', in_file_, tmp_file) # duplicate raster
        self.raster_calculator(f"{in_file_} = if({in_mask}, {tmp_file}, null())  ") # clip raster
        self.remove_layer(map=tmp_file)

    def rasterize_vector (self, input=input, layer=None, type='area', use='cat', value=None, column=None, label=None):

        if use == "cat":
            self.run = Module("v.to.rast", input=useIf(self.in_file, value=input), output=useIf(self.layer, layer), type=type, use='cat', label_column=label, overwrite=True, quiet=self.quiet)
        elif use == "val":
            self.run = Module("v.to.rast", input=useIf(self.in_file, value=input), output=useIf(self.layer, layer), type=type, use='val', value=value, overwrite=True, quiet=self.quiet)
        else:
            self.run = Module("v.to.rast", input=useIf(self.in_file, value=input), output=useIf(self.layer, layer), type=type, use=use, attribute_column=column, label_column=label, overwrite=True, quiet=self.quiet)

    def raster_null (self, input=None, setnull=None, null=None, flags=''):

        if setnull:
            self.run = Module("r.null",  map=useIf(self.layer, value=input), setnull=setnull, flags=flags, quiet=self.quiet)
        elif null:
            self.run = Module("r.null",  map=useIf(self.layer, value=input), null=null, flags=flags, quiet=self.quiet)
        else:
            print('NO parameters defined for r.null')

    def raster_calculator (self, formula):
        self.run = Module("r.mapcalc", expression=formula, overwrite=True, quiet=self.quiet)

    def raster_cluster (self, input=None, output=None, title=None, threshold=0.001, minsize=10, flags='d'):
        self.run = Module("r.clump", input=useIf(self.layer, value=input), output=useIf(self.layer, value=output), title=title, threshold=threshold, minsize=minsize, flags=flags, overwrite=True, quiet=self.quiet)

    def raster_cost (self, input=None, output=None, start_raster=None, start_points=None, flags='k'):
        self.run = Module("r.cost", input=useIf(self.layer, value=input), output=useIf(self.layer, value=output), start_raster=start_raster, start_points=start_points, flags=flags, overwrite=True, quiet=self.quiet)

    def patch_rasters (self, input=None, output=None):
        self.run = Module("r.patch", input=input, output=useIf(self.layer, value=output), overwrite=True, quiet=self.quiet)
    
    def raster_grow_cells (self, input=None, output=None, radius=None, flags=''):
        self.run = Module("r.grow",  input=useIf(self.layer, value=input), output=useIf(self.layer, value=output), radius=radius, flags=flags, overwrite=True, quiet=self.quiet)

    def raster_grow_distance (self, input=None, distance=None, value=None, metric='euclidean', flags='m'):
        self.run = Module("r.grow.distance",  input=useIf(self.layer, value=input), distance=useIf(self.layer, value=distance), value=value, metric=metric, flags=flags, overwrite=True, quiet=self.quiet)
    
    def raster_resample (self, input=None, output=None, flags=''):
        self.run = Module("r.resample", input=useIf(self.layer, value=input), output=useIf(self.layer, value=output), overwrite=True, flags=flags, quiet=self.quiet)
    
    def raster_resample_interp (self, input=None, output=None, method='nearest', flags=''):
        self.run = Module("r.resamp.interp", input=useIf(self.layer, value=input), output=useIf(self.layer, value=output), method=method, overwrite=True, flags=flags, quiet=self.quiet)
    
    def raster_resample_bspline (self, input=None, output=None, mask=None, flags=''):
        self.run = Module("r.resamp.bspline", input=useIf(self.layer, value=input), output=useIf(self.layer, value=output), mask=mask, overwrite=True, flags=flags, quiet=self.quiet)

    def set_colors (self, layer=None, color='bcyr', rules=None, flags=''):

        if rules:
            self.run = Module("r.colors", map=useIf(self.layer, value=layer), rules=rules, flags=flags, quiet=self.quiet)
        else:
            self.run = Module("r.colors", map=useIf(self.layer, value=layer), color=color, flags=flags, quiet=self.quiet)

    def set_cats (self, layer=None, rules=None, separator='pipe'):
        self.run = Module("r.category", map=useIf(self.layer, value=layer), rules=rules, separator=separator)

    def raster_contours (self, input=None, output=None, step=None, levels=None, minlevel=None, maxlevel=None, flags=''):
        self.run = Module("r.contour", input=useIf(self.layer, value=input), output=useIf(self.layer, value=output), step=step, levels=levels, minlevel=minlevel, maxlevel=maxlevel, overwrite=True, flags=flags, quiet=self.quiet)
    
    def raster_univar (self, input=None, output=None, zones=None, separator='comma', flags='t'):
        self.run = Module("r.univar",  map=useIf(self.layer, value=input), output=useIf(self.layer, value=output), zones=zones, flags=flags, separator=separator, overwrite=True, quiet=self.quiet )

    def raster_stats_zonal (self, base, cover, output=None, method='sum', flags=''):
        """ Options: count, sum, min, max, range, average, avedev, variance, stddev, skewness, kurtosis, variance2, stddev2, skewness2, kurtosis2 """
        self.run = Module("r.stats.zonal",  base=base, cover=cover, output=self.layer, method=method, flags=flags, overwrite=True, quiet=self.quiet )

    def raster_series (self, in_files, output=None, method='sum'):
        self.run = Module("r.series",  input=[in_files], output=useIf(self.layer, value=output), method=method, overwrite=True, quiet=self.quiet )

    def set_raster_mask (self, action=None, in_file=None):
        """ old name: set_mask. renamed to avoid confusion"""
    
        if action:            
            try:
                self.run = Module("r.mask", raster=in_file, flags="r")
            except:
                print ('No MASK')
        else:
            self.run = Module("r.mask", raster=in_file, maskcats="*", overwrite=True)


    def raster_latlon (self, input=None, output=None, flags=''):
        self.run = Module("r.latlong",  input=useIf(self.layer, value=input), output=useIf(self.layer, value=output), flags=flags, overwrite=True, quiet=self.quiet)

    def deg2rad(self, degree):
        """ Convert angular degrees to radians """
        self.raster_calculator (f'{self.layer} = {degree} * ({math.pi}/180.0)')


    def query_raster_by_coord (self, input=None, x=None, y=None, flags=''):
        """ Query raster layer by coordinate values"""

        return round(float(str(grass.read_command("r.what",  map=useIf(self.layer, value=input), coordinates=[x,y], flags=flags, overwrite=True, quiet=self.quiet )).rstrip('\r\n').split('|')[3]),2)
 
    def get_raster_stats (self, input=None, type='max'):
        """ types: n, null_cells, cells, min, max, range, mean, mean_of_abs, stddev, variance, coeff_va, sum"""

        univar = grass.parse_command("r.univar",  map=useIf(self.layer, value=input), flags='g')
        return (univar[type])
       
    def raster_from_bbox (self, output=None, flags=''):

        tmp_layer = 'TMP_bbox'
        Module("v.in.region", output=tmp_layer, overwrite=True, quiet=self.quiet)
        self.rasterize_vector (input=tmp_layer, layer=useIf(self.layer, value=output), type='area', use='val', value=1)
        self.remove_layer(map=tmp_layer, type_='vector')

    def raster_neighbors (self, input=None, output=None, method='average', selection=None, size=3, flags=''):
        run = Module("r.neighbors",  input=useIf(self.layer, value=input), output=useIf(self.layer, value=output), method=method, size=size, selection=selection, flags=flags, overwrite=True )

    def raster_buffer (self,  input=None, output=None, distances=10, units=None):
        run = Module("r.buffer", input=useIf(self.layer, value=input), output=useIf(self.layer, value=output), distances=distances, units=units, overwrite=True)
