def calculate_ET0(obj):

    #_______________ topics 
    obj.adm()
    obj.terrain()
    obj.climate()
    obj.et0_layers()
   
    #_______________ objects
    mask = obj.mask
    et0  = obj.ET0    
    dem  = obj.dem
    lat  = obj.latitude_rad

    # _______________ climate
    tm   = obj.temperature
    rh   = obj.humidity
    wn   = obj.wind_2m
    sr   = obj.solar_rad
    pr   = obj.precipitation

    #_______________ mapset
    et0.set_mapset()
    mask.region(flags='ap')

    #_______________ parameters
    months = et0.get_months()  
    et0.set_ET0_terrain_layers(dem=dem.layer_at, lat=lat.layer_at)  

    # _______________ calculations for monthly layers
    for month in months:

        #_______________ ET0 input layers
        et0.set_ET0_layer(month)
        et0.set_ET0_temporary_layers(month) 
        et0.set_ET0_climate_layers(month, tm, rh, wn, sr, pr)
        et0.set_day_of_year(month)

        #_______________ Calculation
        et0.do_ET0_steps(mask.layer_at)
 
    # _______________ Remove temporary files
    et0.remove_pattern(pattern="TMP_*")   

def calculate_ETc(obj):

    #_______________ topics
    obj.adm()
    obj.climate()
    obj.et0_layers()
    obj.etc_layers()
    obj.et_validaton()

    #_______________ objects
    mask = obj.mask
    et0  = obj.ET0    
    etc  = obj.ETc   
    etv  = obj.valid   

    #_______________ mask
    etc.set_mask_attr(mask.layer_at)

    #_______________ parameters
    crop_names  = etc.get_crop_names()
    months      = etc.get_months() 
    ref_year    = etc.get_reference_year()

    print (et0.mapset)

    for crop in crop_names:

        #_______________ mapset
        etc.set_crop_name(crop)
        etc.set_crop_maspet()
        mask.region(flags='ap')

        #_______________ crop parameters
        etc.set_crop_stages()
        etc.set_crop_computed_stages()
        etc.set_crop_lengths()
        etc.set_start_crop_day()
        etc.set_end_crop_day()
        etc.set_etc_date_range()

        #_______________ layers
        etc.set_etc_aggregated_layers()  
        etc.set_crop_stage_layers()
     
        # # _______________ preliminary methods    
        etc.compute_kc_adjusted(obj.climates)
 
        # # _______________ ETc daily calculations
        etc.compute_ETc_steps(obj)
        etc.compute_ETc_aggregates(obj)


        

def calculate_ETs(obj):

    #_______________ topics
    obj.adm()
    obj.soil()
    obj.etc_layers()
    obj.ets_layers()

    #_______________ objects
    mask        = obj.mask
    etc         = obj.ETc   
    ets         = obj.ETs  
    moisture    = obj.moisture_vol
    capacity    = obj.field_capacity
    wilting     = obj.wilting_point
    root        = obj.rooting_depth   


    #_______________ mask
    ets.set_mask_attr(mask.layer_at)

    #_______________ parameters   
    for crop in ets.get_crop_names():

        #_______________ mapset
        ets.set_crop_name(crop)
        ets.set_crop_maspet()
        mask.region(flags='ap')

        #_______________ crop parameters
        ets.set_start_crop_day()
        ets.set_end_crop_day()
        ets.set_etc_date_range()

        ets.calculate_ETs_steps(moisture, capacity, wilting, root)
        ets.compute_ETc_adj_aggregates()



def do_validation(obj):

    #_______________ topics
    obj.adm()
    obj.climate()
    obj.soil()
    obj.et0_layers()
    obj.etc_layers()
    obj.ets_layers()
    obj.et_validaton()

    #_______________ objects
    mask        = obj.mask
    etv         = obj.valid  

    #_______________ mask
    etv.set_mask_attr(mask.layer_at)

    #_______________ parameters
    crop_names  = etv.get_crop_names()
    months      = etv.get_months() 
    ref_year    = etv.get_reference_year()

    for crop in crop_names:

        #_______________ mapset
        etv.set_crop_name(crop)
        etv.set_crop_maspet()
        mask.region(flags='ap')

        etv.compute_ET_validation(obj, crop)


def calculate_crop_yields(obj):

    #_______________ topics
    obj.adm()
    obj.etc_layers()
    obj.crop_yield_layers()

    #_______________ objects
    mask = obj.mask
    etc  = obj.ETc   
    yld  = obj.crop_yield   

    #_______________ mask
    yld.set_mask_attr(mask.layer_at)

    #_______________ parameters
    crop_names  = yld.get_crop_names()


    for crop in crop_names:

        # _______________ mapset
        yld.set_crop_name(crop)
        yld.set_crop_maspet()
        mask.region(flags='ap')

        # _______________ layers
        yld.set_prefix()  
        yld.set_etc_aggregated_layers()  
        yld.set_crop_yield_layers()  

        # _______________ calculations
        yld.compute_crop_yield(obj)

    # print (crop_names)

    # print (yld)

def clean_temp_raster(obj, exclude=None):


    #_______________ objects
    obj.etc_layers()
    etc  = obj.ETc   


    for crop in  etc.get_crop_names():

        # _______________ mapset
        etc.set_crop_name(crop)
        etc.set_crop_maspet()

        etc.clean_up_tmp('raster', exclude=exclude)



