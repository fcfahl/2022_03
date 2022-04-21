#!/usr/bin/python
import os, requests
import logging as log
from tqdm import tqdm
from bs4 import BeautifulSoup


def load_vectors(obj):

    obj.set_mapset()

    if hasattr(obj, 'epsg'):
        obj.import_vector_reproject(output=obj.layer)
    else:
        obj.import_vector(output=obj.layer, layer=obj.db_layer)

def do_raster_reprojection(obj):

    obj.set_mapset()

    if hasattr(obj, 'epsg'):
        obj.import_raster_reproject()
    else:
        print (obj)
        obj.import_raster()

def import_vectors(obj):

    #_______________ topics
    obj.adm()


    for layer in obj.vectors.values():

        print (layer)

        if not hasattr(layer, 'ext'):
            continue

        elif not layer.ext:
            continue

        elif layer.ext == 'gpkg':
            load_vectors(layer)

        # elif layer.ext in ['gpkg','shp','pg']:
        #     load_vectors(layer)

        # elif layer.ext in ['gpkg','shp','pg']:
        #     load_vectors(layer)

        elif layer.ext == 'grass':
            print ("\n______",layer)
            # layer.set_mapset()
            # layer.import_Grass()


    # _______________ Topics
    obj.adm()

def import_rasters(obj):

    for raster in obj.rasters.values():

        # ________________ import raster
        if not hasattr(raster, 'ext'):
            continue

        elif not raster.ext:
            continue

        elif raster.ext == 'tif':
            do_raster_reprojection(raster)

        elif raster.ext == 'grass':
            pass

        # ________________ clip raster if needed
        if  hasattr(raster, 'clip'):
            raster.clip_raster_with_vector(vector=raster.clip)

def import_LULC(obj):

    #_______________ topics
    obj.adm()
    obj.lulc()

    #_______________ objects
    mask        = obj.mask
    utl         = obj.get_utl()
    esa         = obj.esa

    #_______________ mapset
    esa.set_mapset()
    mask.region(flags='ap')

    #_______________ files
    zip_file    = esa.in_folder.joinpath(esa.zip_file)
    netcdf_file = esa.in_folder.joinpath(esa.netcdf)
    reproj_file = str(esa.in_folder.joinpath(esa.in_file))

    #_______________ parameters
    bbox = obj.get_bbox(latlon=False)['extent'] ### bbox of the target src

    #_______________ reproject
    utl.extract_zip(zip_file, dst_path=esa.in_folder)
    utl.reproject_netcdf(in_file=netcdf_file, band=esa.band, out_file=reproj_file, in_proj=4326, out_proj=3035, bbox=bbox, res=201.9)

    #_______________ methods
    esa.import_raster()
    esa.clip_raster(in_mask=mask.layer_at) 
    esa.set_colors (rules=str(esa.in_folder.parents[0].joinpath('colors', esa.color)))
    esa.set_cats (rules=str(esa.in_folder.parents[0].joinpath('colors', esa.cats)))

    #_______________ clean up
    utl.delete_file(reproj_file)
    utl.delete_file(netcdf_file)
  
def import_DEM(obj):

    #_______________ topics
    obj.adm()
    obj.terrain()

    #_______________ objects
    mask        = obj.mask
    utl         = obj.get_utl()
    dem         = obj.dem

    #_______________ mapset
    dem.set_mapset()
    mask.region(flags='ap')

    #_______________ file names
    reproject_name = f"{dem.in_file}_EPSG3035.tif"
    reproject_file = f"{dem.in_folder}/{reproject_name}"

    #_______________ reproject
    utl.run_bash_reproject(
        path=obj.dem.in_folder,
        script='reproject_GMTED.sh',
        in_file=f'{obj.dem.in_file_path}.vrt',
        out_file=reproject_file,
        in_proj='EPSG:4326',
        out_proj='EPSG:3035')

    #_______________ methods
    dem.import_raster(input=reproject_file)
    dem.clip_raster(in_mask=mask.layer_at)         
    dem.remove_layer(tmp=True)

    # _______________ clean up
    utl.delete_file(reproject_file)

def import_climate(obj):

    def import_bands(month, band_name):

        tmp_grow = f'TMP_grow_{month}'

        climate.import_raster(input=band_name, output=climate.tmp,  flags='o')
        climate.set_region(format='raster', in_file=climate.tmp, flags='ap')
        climate.raster_grow_cells(input=climate.tmp, output=tmp_grow, radius=4) #fill the cells close to the ocean (missing values)

        mask.region(flags='ap')
        climate.raster_resample_interp(input=tmp_grow, method='bicubic') # bilinear to smooth the results
        climate.clip_raster(in_mask=mask.layer_at)
        climate.remove_layer([climate.tmp, tmp_grow])

    def fix_negative_humidity(layer):
        """ There are negative numbers on rh min, which should be removed
        https://ftp.cpc.ncep.noaa.gov/wd51we/reanal/random_notes/negative.h2o
        """

        tmp = f"TMP_{layer}"

        climate.raster_calculator(f"{tmp} = if({layer} <0, 0, {layer})")
        climate.rename_file(old=tmp, new=layer)

    def reproject_netcdf():

        utl.run_bash_reproject(
            path=era5_folder,
            script='reproject_era5.sh',
            in_file=climate.in_file_path,
            out_file=reproject_file,
            in_proj='EPSG:4326',
            out_proj='EPSG:3035')
          
    def do_wind_2m():
        """ Wind speed (u2)
            Formula from FAO Irrigation and Drainage Paper No. 56 -> pag 47
        """

        wind_2m = climate.layer
        wind_10m = climate.get_climate_layer_name_by_prefix('wind_10m', stats, month)

        z = 10 ## height of the wind dataset
        climate.raster_calculator(f"{wind_2m} = {wind_10m} * 4.87 / log(67.8 * {z} - 5.42)")
        climate.remove_layer(wind_10m)


    #####################

    # _______________ topics
    obj.adm()
    obj.climate()

    # _______________ objects
    mask        = obj.mask
    clm         = obj.climates   
    utl         = obj.get_utl()
    path        = obj.path

    # _______________ parameters
    era5_folder = path.climate['Europa'].joinpath('ERA5')

    # _______________ region
    mask.get_region()

    # _______________ mask parameters
    for climate in clm.values():

        climate.set_mapset()     

        for stats in climate.stats:

            # _______________ climate parameters
            climate.get_ERA5_input_file(stats)
            reproject_name = f"EPSG3035_{climate.prefix}_{stats}.nc"
            reproject_file = f"{era5_folder}/{reproject_name}"     

            for month in climate.get_months():

                # _______________ layer parameters
                climate.set_climate_layer(stats, month)
                climate.set_tmp()
                band_name = f'NETCDF:"{reproject_file}":Band{month}'        

                # _______________ Import ERA5 layers
                if climate.source == 'ERA5':

                    print (climate)
                    reproject_netcdf() 
                    import_bands(month, band_name)                                 
                    if stats =='min' and climate.prefix == 'rh': # Fix negative numbers of rh_min
                        fix_negative_humidity(climate.layer)   


                elif climate.source == 'wind_calculation':          
                    do_wind_2m()

                else:
                    print ('NO LAYER TO BE IMPORTED')

            # _______________ clean up
            utl.delete_file(reproject_file)


######################## METHODS RHMin
def compute_RHMin(obj):

    # _______________ topics
    obj.adm()
    obj.climate()

    # _______________ objects
    mask        = obj.mask
    clm         = obj.climates   

    # _______________ layes
    rhmin = clm.get('rhmin_calc')

    #_______________ mapset
    rhmin.set_mapset()
    mask.region(flags='ap')


    # # _______________ calculations for monthly layers
    for month in obj.get_months():


        #_______________ Layers
        tdew_mean   = obj.climates['tdew_2m'].get_climate_layer(month=month, at=False)['mean']
        temp_max    = obj.climates['temp_2m'].get_climate_layer(month=month, at=False)['max']
        rhmin_calc  = obj.climates['rhmin_calc'].get_climate_layer(month=month, at=False)['min'] 
        etdew       = obj.climates['etdew'].get_climate_layer(month=month, at=False)['min'] 
        etmax       = obj.climates['etmax'].get_climate_layer(month=month, at=False)['max'] 

        #_______________ calculations
        formula_eTdew = f"{etdew} = 0.6108*exp((17.27*{tdew_mean})/({tdew_mean} + 237.3))"
        formula_eTmax = f"{etmax} = 0.6108*exp((17.27*{temp_max})/({temp_max} + 237.3))"
        formula_rhmin = f"{rhmin_calc} = {etdew}/{etmax}*100"

        for formula in [formula_eTdew, formula_eTmax, formula_rhmin]:
            rhmin.raster_calculator(formula)

        

    # print (self)

##########################

    
def create_reference_mask(obj):
    """ Create a mask layer to be used as reference for extension and resolution """

    #_______________ topics
    obj.adm()

    #_______________ objects
    mask =   obj.mask
    vector = obj.nuts_2

    #_______________ mapset
    vector.set_mapset()
    vector.set_region(format='vector', res=obj.get_resolution(), flags='ap')

    #_______________ methods
    mask.rasterize_vector (input=vector.layer_at, label='ISO3_CODE')

def create_latitude_layers(obj):
    """ Create a raster with latitude values in radians and degrees  """

    #_______________ topics
    obj.adm()

    #_______________ objects
    mask    = obj.mask
    vector  = obj.europa_border
    deg     = obj.latitude_deg
    rad     = obj.latitude_rad

    #_______________ mapset
    vector.set_mapset()
    mask.region(flags='ap')

    #_______________ methods
    deg.raster_latlon(input=mask.layer_at)
    deg.clip_raster(in_mask=mask.layer_at)      
    rad.deg2rad(degree=deg.layer)

def extract_cropland(obj):
    """ Extract cropland from LULC """

    #_______________ topics 
    obj.adm()
    obj.lulc()

    #_______________ objects
    mask     = obj.mask
    esa      = obj.esa
    cropland = obj.cropland

    #_______________ mapset
    cropland.set_mapset()
    mask.region(flags='ap')

    #_______________ methods
    cropland.raster_calculator (f"{cropland.layer} = if({esa.layer} >=10 && {esa.layer} <=30, 1, null())")
    cropland.set_colors (color='aspect')


def import_soil_moisture(obj):

    def reproject_netcdf(in_file, out_file, in_proj='EPSG:4326', out_proj='EPSG:3035', script_name=None, script_path=None):

        utl.run_bash_reproject(
            # path=script_path,
            # path='/media/fcf/Data/03_Datasets/Global/Soil/Soil_Moisture/SMAP/Scripts/',
            path=f'{obj.path.world}/Soil/Soil_Moisture/SMAP/Scripts/',
            script=script_name,
            in_file=in_file,
            out_file=out_file,
            in_proj=in_proj,
            out_proj=out_proj,
        )       

    # _______________ topics
    obj.adm()
    obj.soil()

    # _______________ objects
    mask        = obj.mask
    # sol         = obj.soils   
    utl         = obj.get_utl()
    path        = obj.path
    moisture    = obj.moisture_vol

    # _______________ region
    mask.get_region()

    # # _______________ parameters
    months = obj.get_month_numbers()

    moisture.set_mapset()   

    for stats in moisture.stats:

        for month in months:

            # _______________ soil parameters
            moisture.layer = None
            moisture.get_soil_input_file(stats, month)
            moisture.set_soil_layer(stats, month)
            moisture.set_tmp()
            reproject_name = f"EPSG3035_{moisture.prefix}_{stats}_{month}.tif"
            reproject_file = str(moisture.in_folder.joinpath(stats, reproject_name))

            mask.region()

            #_______________ methods
            reproject_netcdf(
                in_file=moisture.in_file_path, 
                out_file=reproject_file, 
                in_proj='EPSG:4326', 
                out_proj='EPSG:3035', 
                script_name='reproject_soil_moisture.sh',
                script_path=moisture.in_folder                   
                )
  
            moisture.import_raster(input=reproject_file, output=moisture.tmp)
            moisture.raster_grow_cells (input=moisture.tmp, radius=1.1)
            moisture.clip_raster(in_mask=mask.layer_at)              

            # # _______________ clean up
            utl.delete_file(reproject_file)

            # print ('___________')
  

def import_soil_layers(obj):

    def reproject_layer(layer, reprojec_file):

        utl = obj.get_utl()        
        ymin, ymax, xmin, xmax, extent=layer.get_bbox(latlon=True).values()

        if layer == root:

            # /mnt/Data/03_Datasets/Europa/Soil/JRC/Scripts/

            utl.run_bash_reproject_bbox(
                path=f"{obj.path.dataset}/scripts/",
                script='reproject_BBOX.sh',
                in_file=layer.in_file_path,
                out_file=reprojec_file,
                in_proj='EPSG:4326',
                out_proj='EPSG:3035',
                xmin=xmin, 
                ymin=ymin, 
                xmax=xmax, 
                ymax=ymax,
            )

        else:

            utl.run_bash_reproject(
                # path=layer.in_folder,
                path=f"{obj.path.dataset}/scripts/",
                script='reproject_raster.sh',
                in_file=layer.in_file_path,
                out_file=reprojec_file,
                in_proj='EPSG:4326',
                out_proj='EPSG:3035', 
            )                

    


    def rescale_layer(layer):

        scale_factor = 100.0
        tmp_layer = f"TMP_{layer.layer}"

        formula = f"{tmp_layer} = {layer.layer} / {scale_factor} " 

        layer.raster_calculator (formula) 
        layer.rename_file(old=tmp_layer, new=layer.layer)    


    def compute_water_availability(water_avail, capacity, wilting):
        """  
            water available to plant (field capacity – wilting point) [mm/m] 

            not sure about the units - the input data has the following units 
            field_capacity = cm3/cm3
            wilting_point  = cm3/cm3     

            1 cubic centimeter / cubic centimeter = 1000 millimeters / meter
        
        """        

       
        formula = f"{water_avail.layer} = ({capacity.layer} - {wilting.layer}) * 1000 " 

        water_avail.raster_calculator (formula)     

        print (f'\t formula: {formula}') 


    # _______________ topics
    obj.adm()
    obj.soil()

    # _______________ objects
    mask        = obj.mask
    capacity    = obj.field_capacity   
    wilting     = obj.wilting_point    
    water_avail = obj.water_avail 
    root        = obj.rooting_depth   

    
    capacity.set_mapset()          

    for layer in [capacity, wilting]:

        mask.get_region()

        reprojec_file = str(layer.in_folder.joinpath(f"{layer.tmp}.tif"))
        

        reproject_layer(layer, reprojec_file)
        layer.import_raster(input=reprojec_file, flags='o')      
        layer.clip_raster(in_mask=mask.layer_at) 

        if layer != root:
            rescale_layer(layer)

        layer.set_colors (color='viridis')

        obj.get_utl().delete_file(reprojec_file)

    # compute_water_availability(water_avail, capacity, wilting)

