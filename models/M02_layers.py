import pathlib
from datetime import datetime
import models.utils.paths as pth
import models.utils.utilities as utl

import models.M01_base as bse

class Layer(bse.Base): #

    model      = None
    mapset     = "PERMANET"
    layer      = None
    layer_at    = f'{layer}@{mapset}'
    in_file     = None
    out_file    = None

    def __init__(self, mapset=None, layer=None, model=None, in_file=None, out_file=None, in_folder=None, out_folder=None, **kwargs):

        bse.Base.__init__(self)

        self.mapset     = mapset
        self.layer  	= layer
        self.layer_at   = f'{self.layer}@{self.mapset}'
        self.tmp        = f'TMP_{self.layer}'
        self.mask       = f'MASK_{self.layer}'

        if model:
            self.model = model

        if in_file:
            self.in_file = in_file

        if layer:
            self.layer = layer

        if out_file:
            self.out_file = out_file

        if in_folder:
            self.in_folder = pathlib.Path(in_folder)

        if out_folder:
            self.out_folder = pathlib.Path(out_folder)

        if in_file != None and in_folder != None:
            self.in_file_path = str(self.in_folder.joinpath(self.in_file).absolute())

        if out_file != None and out_folder != None:
            self.out_file_path = str(self.out_folder.joinpath(self.out_file).absolute())

        # ____________________ kwargs
        self.__dict__.update(kwargs)


    ################## ATTRIBUTES

    def set_attribute(self, attr, value, at=False, dict_=True):
        setattr(self, attr, value)
        if at:
            if dict:
                setattr(self, f"{attr}_at", {key: f"{layer}@{self.mapset}" for key, layer in value.items()})
            else:
                setattr(self, f"{attr}_at", f"{value}@{self.mapset}")

    def get_obj_attribute(self, attr, at=False):

        if at:
            return getattr(self, f"{attr}_at")
        else:
            return getattr(self, attr)




