from pathlib import Path

import iris

import esmvalcore._config
from esmvalcore._ancestry import ParentFinderCMIP5, ParentFinderCMIP6

CFG_DEVELOPER = esmvalcore._config.read_config_developer_file()
esmvalcore._config._config.CFG = CFG_DEVELOPER

def test_scratch():
    rootpath = Path("/Users/znicholls/Documents/AGCEC/netCDF-SCM/netcdf-scm/tests/test-data/cmip6output")
    in_file = "/Users/znicholls/Documents/AGCEC/netCDF-SCM/netcdf-scm/tests/test-data/cmip6output/CMIP6/GeoMIP/MOHC/UKESM1-0-LL/G6solar/r1i1p1f2/Lmon/npp/gn/v20191031/npp_Lmon_UKESM1-0-LL_G6solar_r1i1p1f2_gn_202001-204912.nc"

    start = iris.load_cube(in_file)

    res = ParentFinderCMIP6(start).get_parent_metadata()
    res = ParentFinderCMIP6(start).find_local_parent(rootpath, "ESGF")
    assert False, "make test"

def test_scratch_cmip5():
    rootpath = Path("/Users/znicholls/Documents/AGCEC/netCDF-SCM/netcdf-scm/tests/test-data/marble-cmip5/cmip5/")
    in_file = "/Users/znicholls/Documents/AGCEC/netCDF-SCM/netcdf-scm/tests/test-data/marble-cmip5/cmip5/rcp45/Amon/tas/NorESM1-M/r1i1p1/tas_Amon_NorESM1-M_rcp45_r1i1p1_200601-230012.nc"

    start = iris.load_cube(in_file)

    res = ParentFinderCMIP5(start).get_parent_metadata()
    res = ParentFinderCMIP5(start).find_local_parent(rootpath, "ETHZ")
    assert False, "make test"
