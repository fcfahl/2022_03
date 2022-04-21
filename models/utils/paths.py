import os
import platform
from pathlib import Path

""" Path definition """


class PathDefinition:

    def __init__(self):

        self.script = Path(__file__).parent.parent.parent.absolute()
        self.project = self.script.parent.parent.parent.absolute()
        self.project_name = self.project.name

        self.data = self.project.joinpath('01_Data').absolute()
        self.vector = self.data.joinpath('01_Vector').absolute()
        self.raster = self.data.joinpath('02_Raster').absolute()
        self.table = self.data.joinpath('03_Tables').absolute()
        self.grass = self.data.joinpath('04_GRASS_DB').absolute()

        self.results = self.project.joinpath('02_Results').absolute()
        self.workspace = self.project.joinpath('04_Workspaces').absolute()
        self.documents = self.project.joinpath('05_Documents').absolute()

        self.tmp = self.project.joinpath('TMP').absolute()
        self.log = self.script.joinpath('logs').absolute()
        self.config = self.script.joinpath('config').absolute()

        self.__create_paths__()
        self.__datasets__()

    def __datasets__(self):

        import getpass
        user = getpass.getuser()

        self.home = Path(str(Path.home().absolute()))

        if platform.node() == 'REEW028':  # JRC
            self.dataset = self.home.joinpath('GIS', '03_Datasets')

        if platform.node() == 'csr-mjr':  # Home manjaro
            self.home = Path(str(Path.home().absolute()).replace('csr', 'fcf'))
            self.dataset = Path(f'/run/media/{user}/Data/03_Datasets')  # Manjaro
        if platform.node() == 'MX.station':  # Opensuse
            self.home = Path(str(Path.home().absolute()).replace('fer', 'fcf'))
            self.dataset = Path(f'/mnt/Data/03_Datasets')  # Manjaro
        else:
            self.dataset = Path(f'/media/{user}/Data/03_Datasets')  # Ubuntu / MX
        self.world = self.dataset.joinpath('Global')
        self.africa = self.dataset.joinpath('Africa')
        self.europa = self.dataset.joinpath('Europa')

        self.__regions__()

    def __regions__(self):

        regions = ['Africa', 'Europa', 'Global']
        params = ['Administrative', 'Agriculture', 'Climate', 'DEM', 'Hydro', 'Infrastructure', 'Land_Use', 'OSM',
                  'Population', 'Reference_Data', 'Soil']

        for item in params:
            setattr(self, item.lower(), {region: self.dataset.joinpath(region, item) for region in regions})

    def __create_paths__(self):

        for path in [self.vector, self.raster, self.table, self.grass, self.results, self.workspace, self.documents,
                     self.tmp]:

            if not os.path.exists(path):
                os.makedirs(path)

    # ____________________ print attributes
    def __str__(self):
        return '\n'.join((f'{key:<20s} = {value}' for key, value in self.__dict__.items()))
