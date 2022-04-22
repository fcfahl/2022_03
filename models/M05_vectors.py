import wrapt
import logging as log
import grass.script as grass
import grass.script.setup as gsetup
from grass.pygrass.modules.shortcuts import vector as v
from grass.pygrass.modules import Module
from subprocess import PIPE

import models.M03_generic as gnr
from models.M03_generic import useIf


@wrapt.decorator
def run_module(wrapped, instance, args, kwargs):
    """ Decorator to log the grass modules
        Used wrapt library in order to preserve the signature of the caller function
        see: https://hynek.me/articles/decorators/
    """
    func_name = wrapped.__name__
    try:
        wrapped(*args, **kwargs)
        instance.grass_log(f"___ function -> [{func_name}] ___ ")
        if instance.run:
            instance.grass_log(instance.run)

    except Exception as ex:
        instance.grass_log(f"ERROR {str(ex)} on [{func_name.upper()}]")

    return wrapped


class Vector(gnr.Generic):

    def __init__(self, mapset, model='vector', in_file=None, layer=None, out_file=None, in_folder=None, out_folder=None, **kwargs):
        gnr.Generic.__init__(self, mapset=mapset, model=model, in_file=in_file, layer=layer, out_file=out_file, in_folder=in_folder, out_folder=out_folder, **kwargs)


    # _________________ Import methods

    @run_module
    def import_vector (self, input=None, output=None, layer=None, where=None, flags=''):
        log.info(f"input={input}, output={output}, layer={layer}")
        self.run = Module("v.in.ogr", input=useIf(self.in_file_path, value=input), output=useIf(self.layer, output), layer=useIf(self.layer, layer), where=where, snap=1e-13, flags=flags, overwrite=True, quiet=self.quiet)

    @run_module
    def import_vector_reproject (self, input=None, output=None, layer=None, db_layer=None, epsg=None, flags=''):
        self.run = Module("v.import", input=useIf(self.in_file_path, value=input), output=useIf(self.out_file, output), layer=useIf(self.db_layer, layer), epsg=useIf(self.epsg, epsg), flags=flags, overwrite=True, quiet=self.quiet)

    @run_module
    def import_vector_grass (self, db_location=None, db_mapset=None, db_layer=None, db_path=None, output=None):
        self.run = Module("v.proj", location=useIf(self.db_location, db_location), mapset=useIf(self.mapset, db_mapset), dbase=useIf(self.db_path, db_path), input=useIf(self.db_layer, db_layer), output=useIf(self.layer, output), overwrite=True, quiet=self.quiet)

    @run_module
    def import_postgres (self, pg_db, db_user, db_pwd, db_layer, output=None, flags=""):
        self.run = Module("v.in.ogr", input=f"PG:host=localhost dbname={pg_db} user={db_user} password={db_pwd}", layer=db_layer, output=self.output_(output), overwrite=True, flags=flags, quiet=self.quiet)

    @run_module
    def import_csv (self, input=None, output=None, x=1, y=2, cols=None, sep='comma', skip=1):
        self.run = Module("v.in.ascii", input=useIf(self.in_file_path, value=input), output=useIf(self.layer, value=output), x=x, y=y, separator=sep, columns=cols, skip=skip, overwrite=True, quiet=self.quiet)

    @run_module
    def pg_external_layer (self, user, pwd, db, layer):
        self.run = Module("v.external",  f'PG:host=localhost user={user} password={pwd} dbname={db}', layer=layer, overwrite=True, quiet=self.quiet)

    @run_module
    def import_table (self, input=None, output=None):
        self.run = Module("db.in.ogr", input=self.in_file_path_(input) , output=self.output_(output), overwrite=True, quiet=self.quiet)


    # Export methods
    # @run_module
    # def export_vector (self, input, output, layer_name=None, format='CSV', type_='auto', flags=''):
    #     self.run = Module('v.out.ogr', input=self.in_file_path_(input) , output=self.output_(output), format=format, type=type_, overwrite=True, flags=flags)

    # Query (DB) methods
    @run_module
    def query_Attribute (self, layer=None, columns=None, sql=None, separator='comma', flags='c'):
        self.run = Module('v.db.select', map=useIf(self.layer, value=layer), columns=columns, where=sql, separator=separator, flags=flags, overwrite=True, finish_=True,  stdout_=PIPE, quiet=self.quiet)
        return ( [x for x in run.outputs.stdout.split('\n') if x != ''][0].split(',')) # this is to return the output as list of strings

    @run_module
    def select_DB (self, sql, separator='pipe', vertical_separator='pipe', database="$GISDBASE/$LOCATION_NAME/$MAPSET/sqlite/sqlite.db", flags='c'):
        self.run =  Module('db.select', sql=sql, separator=separator, vertical_separator=vertical_separator, flags=flags, overwrite=True, finish_=True, database=database, stdout_=PIPE, quiet=self.quiet)
        return ( [ x for x in run.outputs.stdout.split('\n') if x != ''] ) # this is to return the output as list of strings

    @run_module
    def run_SQL (self, sql):
        self.run = Module('db.execute', sql=sql, database='$GISDBASE/$LOCATION_NAME/$MAPSET/sqlite/sqlite.db', quiet=self.quiet)

    @run_module
    def update_vector_attr (self, input=None, column=None, value=None, query_column=None, where=None, flags=''):
        self.run = Module('v.db.update', map=useIf(self.layer, value=input), column=column, value=value, query_column=query_column, where=where, flags=flags, quiet=self.quiet)

    @run_module
    def add_geom_attr (self, input=None, option='coor', columns='x,y', type='centroid', units=None, flags=''):
        self.run = Module("v.to.db",  map=useIf(self.layer, value=input), option=option, columns=columns, type=type, units=units, flags=flags, overwrite=True, quiet=self.quiet)

    @run_module
    def describe_table (self, in_table, flags='c'):
        self.run = Module("db.describe",  table=in_table, flags=flags)

    @run_module
    def query_rasters_from_points (self, vector=None, raster=None, column=None, query='', flags=''):
        self.run = Module('v.what.rast', map=useIf(self.layer, value=vector), raster=useIf(self.layer, value=raster), column=column, where=query, flags=flags, quiet=self.quiet)

    @run_module
    def query_rasters_stats (self, raster=None, column_prefix=None, method=['average,sum'], flags='c'):
        self.run = Module('v.rast.stats', map=self.layer, raster=raster, column_prefix=column_prefix, method=method, flags=flags, quiet=self.quiet)

    @run_module
    def query_vector_stats (self, points, areas, points_column, count_column, stats_column, method='sum', flags=''):
        self.run = Module('v.vect.stats', points=points, areas=areas, points_column=points_column, count_column=count_column, stats_column=stats_column, method=method, flags=flags, quiet=self.quiet)

    @run_module
    def get_vector_info (self, input=None, type='points', flags='t'):
        """ types: nodes, points, lines, boundaries, centroids, areas, islands, primitives, map3d"""

        # self.run = Module('v.info', map=useIf(self.layer, value=input), flags=flags, stdout_=PIPE, quiet=self.quiet)
        # result_dict =  {x.split('=')[0]:x.split('=')[1] for x in run.outputs.stdout.split('\n') if x != ''}
        # return result_dict.get(type)

        info = grass.parse_command("v.info",  map=useIf(self.layer, value=input), flags=flags)
        return (info[type])

    @run_module
    def get_vector_univar (self, input, column, type='point', sql=None, flags='g'):
        info = grass.parse_command("v.univar", map=useIf(self.layer, value=input), column=column, type=type, where=sql, flags=flags, quiet=self.quiet)
        return (info)


    ########## Processing methods
    @run_module
    def extract_vector (self, input=None, output=None, query=None, type='area', dissolve_column='cat', new=-1, flags=''):
        self.run =  Module("v.extract", input=useIf(self.layer, value=input), output=useIf(self.layer, value=output), where=query, type=type, dissolve_column=dissolve_column, new=new, overwrite=True,  flags=flags, quiet=self.quiet)
        print (run)

    @run_module
    def smooth_vector (self, input=None, output=None, method='douglas', threshold=1, angle_thresh=100, flags=''):
        self.run = Module("v.generalize", input=useIf(self.layer, value=input), output=useIf(self.layer, value=output), method=method, threshold=threshold, overwrite=True, flags=flags, quiet=self.quiet)

    @run_module
    def edit_vector (self, map=None, tool='create', flags=''):
        Module("v.edit", map=useIf(self.layer, value=map), tool=tool, overwrite=True, flags=flags, quiet=self.quiet)

    ########## Table methods
    @run_module
    def add_vector_table (self, input=None, columns=None, flags=''):
        self.run = Module("v.db.addtable", map=useIf(self.layer, value=input), columns=columns, flags=flags, quiet=self.quiet)

    @run_module
    def add_columns (self, input=None, columns=None):
        self.run = Module("v.db.addcolumn",  map=useIf(self.layer, value=input), columns=columns, quiet=self.quiet)

    @run_module
    def drop_columns (self, input=None, columns=None):
        self.run = Module("v.db.dropcolumn",  map=useIf(self.layer, value=input), columns=columns, quiet=self.quiet)

    @run_module
    def rename_columns (self, input=None, column=None):
        self.run = Module("v.db.renamecolumn",  map=useIf(self.layer, value=input), column=column, quiet=self.quiet)

    @run_module
    def join_table (self, input=None, in_table=None, vector_column=None, table_column=None, subset_columns=''):
        self.run = Module("v.db.join", map=useIf(self.layer, value=input), column=vector_column, other_table=in_table, other_column=table_column, subset_columns=subset_columns)

    @run_module
    def drop_table (self, table_name):
        self.run = Module("db.droptable",  table=useIf(self.layer, value=table_name), flags='f')

    @run_module
    def drop_vector_table (self, input):
        self.run = Module("v.db.droptable",  map=useIf(self.layer, value=input), flags='f')


    ########## Overlay
    @run_module
    def overlay_vectors (self, ainput, binput, output=None, operator='and', flags=''):
        self.run = Module("v.overlay", ainput=ainput, binput=binput, output=useIf(self.layer, value=output), operator=operator, flags=flags, overwrite=True, quiet=self.quiet)

    @run_module
    def patch_vector (self, in_files, output=None, flags=''):
        self.run = Module("v.patch",  input=in_files, output=useIf(self.layer, value=output), flags=flags, overwrite=True )

    @run_module
    def clip_vector (self, input=None, output=None, clip=None, flags=''):
        self.run = Module("v.clip", input=useIf(self.layer, value=input), clip=clip, output=useIf(self.layer, value=output), flags=flags, overwrite=True, quiet=self.quiet)

    @run_module
    def select_vector (self, ainput, atype, binput, btype, output=None, operator='within', flags=''):
        self.run = Module("v.select", ainput=useIf(self.layer, value=ainput), atype=atype, binput=binput, btype=btype, output=useIf(self.layer, value=output), operator=operator, flags=flags, overwrite=True, quiet=self.quiet)

    @run_module
    def vector_from_bbox (self, flags=''):
        self.run = Module("v.in.region", output=self.layer, flags=flags, overwrite=True, quiet=self.quiet)

    @run_module
    def vector_voronoi (self, input=None, output=None, flags=''):
        self.run = Module("v.voronoi", input=useIf(self.layer, value=input), output=useIf(self.layer, value=output), flags=flags, overwrite=True, quiet=self.quiet)

    ##########
    @run_module
    def dissolve_vector (self, input=None, output=None, column=None):
        self.run = Module("v.dissolve", input=useIf(self.layer, value=input), output=useIf(self.layer, value=output), column=column, overwrite=True, quiet=self.quiet)

    @run_module
    def buffer_vector (self, input=None, output=None, distance=None, flags=''):
        self.run = Module("v.buffer", input=useIf(self.layer, value=input), output=useIf(self.layer, value=output), distance=distance, flags=flags, overwrite=True, quiet=self.quiet)

    ##########
    @run_module
    def get_list_cats (self, input=None, option='print', cat=-1, flags=''):
        self.run =  Module('v.category', input=useIf(self.layer, value=input), option=option, cat=cat, flags=flags, stdout_=PIPE, quiet=self.quiet)
        result = [ int(x) for x in run.outputs.stdout.split('\n') if x != '']
        return ( sorted(result) ) # this is to return the output as list of strings

    @run_module
    def colors_vectors (self, input, use='attr', column=None, color='rainbow'):
        self.run = Module("v.colors", map=useIf(self.layer, value=input), use=use, column=column, color=color, quiet=self.quiet)


    # def make_grid (self, out_file, box, flags=''):
    #     self.run = Module("v.mkgrid", map=out_file, box=box, overwrite=True, flags=flags)


    ########## Topology
    @run_module
    def clean_vector (self, input=None, output=None, type='point', tool='rmdupl', threshold=None, flags=''):
        self.run = Module("v.clean", input=useIf(self.layer, value=input), output=useIf(self.layer, value=output), type=type, tool=tool, threshold=threshold, flags=flags, overwrite=True, quiet=self.quiet)

    @run_module
    def build_vector (self, input=None, flags=''):
        self.run = Module("v.build", map=useIf(self.layer, value=input), flags=flags, overwrite=True, quiet=self.quiet)

    @run_module
    def add_centroids (self, input=None, output=None, flags=''):
        self.run = Module("v.centroids",  input=useIf(self.layer, value=input), output=useIf(self.layer, value=output), flags=flags, overwrite=True )

    @run_module
    def convert_type (self, input=None, output=None, from_type='kernel', to_type='centroid', flags=''):
        self.run = Module("v.type", input=useIf(self.layer, value=input), output=useIf(self.layer, value=output), from_type=from_type, to_type=to_type, flags=flags, overwrite=True, quiet=self.quiet)


    ########## Postgres connection

    @run_module
    def pg_connect (self, db, driver='pg'):
        self.run = Module('db.connect', database=db, driver=driver)




    ########## Dissolve internal rings
    @run_module
    def dissolve_islands(self, input=None, output=None):
        """ it will merge the islands with the polugons
        https://gis.stackexchange.com/questions/43624/how-to-delete-rings-automatically-using-qgis-grass
        """
        tmp_1 = f'TMP_a_clean_{input}'
        tmp_2 = f'TMP_b_centroids_{input}'

        # ______________ optional before starting: clean features
        self.clean_vector (input=input, output=tmp_1, type='area', tool=['bpol','rmdup'])
        self.build_vector (input=tmp_1)

        #  ______________ 1. Add centroids to the holes
        self.add_centroids (input=tmp_1, output=tmp_2)

        #  ______________ 2. Drop the current table and and one that includes the areas that now have centroids and a value column that you will use to dissolve the areas
        self.drop_vector_table (input=tmp_2)
        self.add_table (input=tmp_2, columns='value INT')

        #   ______________ 3. Update this "value" column with the same value everywhere
        self.update_vector_attr(input=tmp_2, column='value', value=1)

        #  ______________ 4. Now combine the areas by dissolving them together
        self.dissolve_vector (input=tmp_2, output=output, column='value')

        #  ______________ 5. Clean tmps
        self.remove_layer(map=[tmp_1,tmp_2])

    ########## PANDAS
    @run_module
    def vector_to_pandas (self, vector_path):
        """ vector path of the /GRASSDB/LOCATION_NAME/MAPSET/vector/layername/head        
            it requires GDAL-GRASS-Plugin installed. see: https://www.mail-archive.com/grass-user@lists.osgeo.org/msg39905.html
            not working with debian - gdal plugin does not recognize the vector
        """

        import fiona
        import geopandas as gpd

        fiona.supported_drivers["OGR_GRASS"] = "r" 

        gdf = gpd.read_file(vector_path)

        return gdf

    @run_module
    def vector_to_pandas_by_sql(self,sql):
        """ https://pvanb.wordpress.com/2017/04/07/grass-and-pandas-from-attribute-table-to-pandas-dataframe/ 
            alternative for load grass table  to pandas              
        """

        import pandas as pd
        import sqlite3
        
        # Read in the attribute table
        sqlpath = grass.read_command("db.databases", driver="sqlite").replace('\n', '')
        con = sqlite3.connect(sqlpath)
  
        df = pd.read_sql_query(sql, con)
        con.close()

        return df
