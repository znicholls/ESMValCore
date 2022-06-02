from pathlib import Path

import iris.cube

import esmvalcore._config
from esmvalcore._ancestry import ParentFinderCMIP5, ParentFinderCMIP6

CFG_DEVELOPER = esmvalcore._config.read_config_developer_file()
esmvalcore._config._config.CFG = CFG_DEVELOPER

def test_scratch():
    # If you want to try on actual data
    # rootpath = Path("root")
    # in_file = rootpath /CMIP6/GeoMIP/MOHC/UKESM1-0-LL/G6solar/r1i1p1f2/Lmon/npp/gn/v20191031/npp_Lmon_UKESM1-0-LL_G6solar_r1i1p1f2_gn_202001-204912.nc"
    # start = iris.load_cube(in_file)

    # Mocking (TODO: do this properly)
    start = iris.cube.Cube([0])
    start.attributes = {'CDI': 'Climate Data Interface version 1.9.7.1 (http://mpimet.mpg.de/cdi)', 'history': '2019-10-30T10:10:26Z altered by CMOR: replaced missing value flag (-1.07374e+09) with standard missing value (1e+20).', 'source': 'UKESM1.0-LL (2018): \naerosol: UKCA-GLOMAP-mode\natmos: MetUM-HadGEM3-GA7.1 (N96; 192 x 144 longitude/latitude; 85 levels; top level 85 km)\natmosChem: UKCA-StratTrop\nland: JULES-ES-1.0\nlandIce: none\nocean: NEMO-HadGEM3-GO6.0 (eORCA1 tripolar primarily 1 deg with meridional refinement down to 1/3 degree in the tropics; 360 x 330 longitude/latitude; 75 levels; top grid cell 0-1 m)\nocnBgchem: MEDUSA2\nseaIce: CICE-HadGEM3-GSI8 (eORCA1 tripolar primarily 1 deg; 360 x 330 longitude/latitude)', 'institution': 'Met Office Hadley Centre, Fitzroy Road, Exeter, Devon, EX1 3PB, UK', 'Conventions': 'CF-1.7 CMIP-6.2', 'activity_id': 'GeoMIP', 'branch_method': 'standard', 'branch_time_in_child': 61200.0, 'branch_time_in_parent': 61200.0, 'creation_date': '2019-10-30T10:10:26Z', 'cv_version': '6.2.37.5', 'data_specs_version': '01.00.29', 'experiment': 'total solar irradiance reduction to reduce net forcing from SSP585 to SSP245', 'experiment_id': 'G6solar', 'external_variables': 'areacella', 'forcing_index': 2, 'frequency': 'mon', 'further_info_url': 'https://furtherinfo.es-doc.org/CMIP6.MOHC.UKESM1-0-LL.G6solar.none.r1i1p1f2', 'grid': 'Native N96 grid; 192 x 144 longitude/latitude', 'grid_label': 'gn', 'initialization_index': 1, 'institution_id': 'MOHC', 'mip_era': 'CMIP6', 'mo_runid': 'u-bg157', 'nominal_resolution': '250 km', 'parent_activity_id': 'ScenarioMIP', 'parent_experiment_id': 'ssp585', 'parent_mip_era': 'CMIP6', 'parent_source_id': 'UKESM1-0-LL', 'parent_time_units': 'days since 1850-01-01', 'parent_variant_label': 'r1i1p1f2', 'physics_index': 1, 'product': 'model-output', 'realization_index': 1, 'realm': 'land', 'source_id': 'UKESM1-0-LL', 'source_type': 'AOGCM AER BGC CHEM', 'sub_experiment': 'none', 'sub_experiment_id': 'none', 'table_id': 'Lmon', 'table_info': 'Creation Date:(13 December 2018) MD5:f0588f7f55b5732b17302f8d9d0d7b8c', 'title': 'UKESM1-0-LL output prepared for CMIP6', 'variable_id': 'npp', 'variable_name': 'npp', 'variant_label': 'r1i1p1f2', 'license': 'CMIP6 model data produced by the Met Office Hadley Centre is licensed under a Creative Commons Attribution-ShareAlike 4.0 International License (https://creativecommons.org/licenses). Consult https://pcmdi.llnl.gov/CMIP6/TermsOfUse for terms of use governing CMIP6 output, including citation requirements and proper acknowledgment. Further information about this data, including some limitations, can be found via the further_info_url (recorded as a global attribute in this file) and at https://ukesm.ac.uk/cmip6. The data producers and data providers make no warranty, either express or implied, including, but not limited to, warranties of merchantability and fitness for a particular purpose. All liabilities arising from the supply of the information (including any liability arising in negligence) are excluded to the fullest extent permitted by law.', 'cmor_version': '3.4.0', 'tracking_id': 'hdl:21.14100/d68e4d81-edc8-4eff-b528-a5074ed0659e', 'CDO': 'Climate Data Operators version 1.9.7.1 (http://mpimet.mpg.de/cdo)', 'comment': "'Production of carbon' means the production of biomass expressed as the mass of carbon which it contains. Net primary production is the excess of gross primary production (rate of synthesis of biomass from inorganic precursors) by autotrophs ('producers'), for example, photosynthesis in plants or phytoplankton, over the rate at which the autotrophs themselves respire some of this biomass. 'Productivity' means production per unit area. The phrase 'expressed_as' is used in the construction A_expressed_as_B, where B is a chemical constituent of A. It means that the quantity indicated by the standard name is calculated solely with respect to the B contained in A, neglecting all other chemical constituents of A.", 'original_name': 'mo: (stash: m01s19i102, lbproc: 128) / ((SECONDS_IN_DAY: 86400.) * (DAYS_IN_YEAR: 360.))'}

    res = ParentFinderCMIP6(start).get_parent_metadata()
    res = ParentFinderCMIP6(start).find_esgf_parent()
    # needs actual data
    # res = ParentFinderCMIP6(start).find_local_parent(rootpath, "ESGF")
    assert False, "actually write a test"

def test_scratch_cmip5():
    # If you want to try on actual data
    # rootpath = Path("root")
    # in_file = rootpath/rcp45/Amon/tas/NorESM1-M/r1i1p1/tas_Amon_NorESM1-M_rcp45_r1i1p1_200601-230012.nc
    # start = iris.load_cube(in_file)

    # Mocking (TODO: do this properly)
    start = iris.cube.Cube([0])
    start.attributes = {'CDI': 'Climate Data Interface version 1.9.8 (https://mpimet.mpg.de/cdi)', 'Conventions': 'CF-1.4', 'history': "2011-06-04T22:38:39Z altered by CMOR: Treated scalar dimension: 'height'. 2011-06-04T22:38:40Z altered by CMOR: Converted type from 'd' to 'f'.", 'institution': 'Norwegian Climate Centre', 'institute_id': 'NCC', 'experiment_id': 'rcp45', 'model_id': 'NorESM1-M', 'forcing': 'GHG, SA, Oz, Sl, BC, OC', 'parent_experiment_id': 'historical', 'parent_experiment_rip': 'r1i1p1', 'branch_time': 56940.0, 'contact': 'Please send any requests or bug reports to noresm-ncc@met.no.', 'initialization_method': 1, 'physics_version': 1, 'tracking_id': 'a327250e-ca23-4880-9a82-04344c30d5cd', 'product': 'output', 'experiment': 'RCP4.5', 'frequency': 'mon', 'creation_date': '2011-06-04T22:38:40Z', 'project_id': 'CMIP5', 'table_id': 'Table Amon (27 April 2011) a5a1c518f52ae340313ba0aada03f862', 'title': 'NorESM1-M model output prepared for CMIP5 RCP4.5', 'parent_experiment': 'historical', 'modeling_realm': 'atmos', 'realization': 1, 'cmor_version': '2.6.0', 'CDO': 'Climate Data Operators version 1.9.8 (https://mpimet.mpg.de/cdo)', 'associated_files': 'baseURL: http://cmip-pcmdi.llnl.gov/CMIP5/dataLocation gridspecFile: gridspec_atmos_fx_NorESM1-M_rcp45_r0i0p0.nc areacella: areacella_fx_NorESM1-M_rcp45_r0i0p0.nc', 'original_name': 'TREFHT'}
    start.var_name = "tas"
    # Setting mip in advance, this could be done in pre-processing/fixes
    start.attributes["mip"] = "Amon"

    res = ParentFinderCMIP5(start).get_parent_metadata()
    res = ParentFinderCMIP5(start).find_esgf_parent()
    # needs actual data
    # res = ParentFinderCMIP5(start).find_local_parent(rootpath, "ETHZ")
    assert False, "actually write a test"
