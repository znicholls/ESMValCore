"""Tests for the ICON on-the-fly CMORizer."""
import iris
import numpy as np
import pytest
from cf_units import Unit
from iris import NameConstraint
from iris.coords import AuxCoord, DimCoord
from iris.cube import Cube, CubeList

from esmvalcore._config import get_extra_facets
from esmvalcore.cmor._fixes.icon.icon import AllVars, Siconca
from esmvalcore.cmor.fix import Fix
from esmvalcore.cmor.table import get_var_info

# Note: test_data_path is defined in tests/integration/cmor/_fixes/conftest.py


@pytest.fixture
def cubes_2d(test_data_path):
    """2D sample cubes."""
    nc_path = test_data_path / 'icon_2d.nc'
    return iris.load(str(nc_path))


@pytest.fixture
def cubes_3d(test_data_path):
    """3D sample cubes."""
    nc_path = test_data_path / 'icon_3d.nc'
    return iris.load(str(nc_path))


@pytest.fixture
def cubes_grid(test_data_path):
    """Grid description sample cubes."""
    nc_path = test_data_path / 'icon_grid.nc'
    return iris.load(str(nc_path))


@pytest.fixture
def cubes_regular_grid():
    """Cube with regular grid."""
    time_coord = DimCoord([0], var_name='time', standard_name='time',
                          units='days since 1850-01-01')
    lat_coord = DimCoord([0.0, 1.0], var_name='lat', standard_name='latitude',
                         long_name='latitude', units='degrees_north')
    lon_coord = DimCoord([-1.0, 1.0], var_name='lon',
                         standard_name='longitude', long_name='longitude',
                         units='degrees_east')
    cube = Cube([[[0.0, 1.0], [2.0, 3.0]]], var_name='tas', units='K',
                dim_coords_and_dims=[(time_coord, 0),
                                     (lat_coord, 1),
                                     (lon_coord, 2)])
    return CubeList([cube])


@pytest.fixture
def cubes_2d_lat_lon_grid():
    """Cube with 2D latitude and longitude."""
    time_coord = DimCoord([0], var_name='time', standard_name='time',
                          units='days since 1850-01-01')
    lat_coord = AuxCoord([[0.0, 0.0], [1.0, 1.0]], var_name='lat',
                         standard_name='latitude', long_name='latitude',
                         units='degrees_north')
    lon_coord = AuxCoord([[0.0, 1.0], [0.0, 1.0]], var_name='lon',
                         standard_name='longitude', long_name='longitude',
                         units='degrees_east')
    cube = Cube([[[0.0, 1.0], [2.0, 3.0]]], var_name='tas', units='K',
                dim_coords_and_dims=[(time_coord, 0)],
                aux_coords_and_dims=[(lat_coord, (1, 2)),
                                     (lon_coord, (1, 2))])
    return CubeList([cube])


def get_allvars_fix(mip, short_name):
    """Get member of fix class."""
    vardef = get_var_info('ICON', mip, short_name)
    extra_facets = get_extra_facets('ICON', 'ICON', mip, short_name, ())
    fix = AllVars(vardef, extra_facets=extra_facets)
    return fix


def check_ta_metadata(cubes):
    """Check ta metadata."""
    assert len(cubes) == 1
    cube = cubes[0]
    assert cube.var_name == 'ta'
    assert cube.standard_name == 'air_temperature'
    assert cube.long_name == 'Air Temperature'
    assert cube.units == 'K'
    return cube


def check_tas_metadata(cubes):
    """Check tas metadata."""
    assert len(cubes) == 1
    cube = cubes[0]
    assert cube.var_name == 'tas'
    assert cube.standard_name == 'air_temperature'
    assert cube.long_name == 'Near-Surface Air Temperature'
    assert cube.units == 'K'
    return cube


def check_time(cube):
    """Check time coordinate of cube."""
    assert cube.coords('time', dim_coords=True)
    time = cube.coord('time', dim_coords=True)
    assert time.var_name == 'time'
    assert time.standard_name == 'time'
    assert time.long_name == 'time'
    assert time.units == Unit('days since 1850-01-01',
                              calendar='proleptic_gregorian')
    np.testing.assert_allclose(time.points, [54786.0])
    assert time.bounds is None
    assert time.attributes == {}


def check_height(cube, plev_has_bounds=True):
    """Check height coordinate of cube."""
    assert cube.coords('model level number', dim_coords=True)
    height = cube.coord('model level number', dim_coords=True)
    assert height.var_name == 'model_level'
    assert height.standard_name is None
    assert height.long_name == 'model level number'
    assert height.units == 'no unit'
    np.testing.assert_array_equal(height.points, np.arange(47))
    assert height.bounds is None
    assert height.attributes == {'positive': 'up'}

    assert cube.coords('air_pressure', dim_coords=False)
    plev = cube.coord('air_pressure', dim_coords=False)
    assert plev.var_name == 'plev'
    assert plev.standard_name == 'air_pressure'
    assert plev.long_name == 'pressure'
    assert plev.units == 'Pa'
    assert plev.attributes == {'positive': 'down'}
    assert cube.coord_dims('air_pressure') == (0, 1, 2)

    if plev_has_bounds:
        assert plev.bounds is not None
    else:
        assert plev.bounds is None


def check_heightxm(cube, height_value):
    """Check scalar heightxm coordinate of cube."""
    assert cube.coords('height')
    height = cube.coord('height')
    assert height.var_name == 'height'
    assert height.standard_name == 'height'
    assert height.long_name == 'height'
    assert height.units == 'm'
    assert height.attributes == {'positive': 'up'}
    np.testing.assert_allclose(height.points, [height_value])
    assert height.bounds is None


def check_lat_lon(cube):
    """Check latitude and longitude coordinates of cube."""
    assert cube.coords('latitude', dim_coords=False)
    lat = cube.coord('latitude', dim_coords=False)
    assert lat.var_name == 'lat'
    assert lat.standard_name == 'latitude'
    assert lat.long_name == 'latitude'
    assert lat.units == 'degrees_north'
    np.testing.assert_allclose(
        lat.points,
        [-45.0, -45.0, -45.0, -45.0, 45.0, 45.0, 45.0, 45.0],
        rtol=1e-5
    )
    np.testing.assert_allclose(
        lat.bounds,
        [
            [-90.0, 0.0, 0.0],
            [-90.0, 0.0, 0.0],
            [-90.0, 0.0, 0.0],
            [-90.0, 0.0, 0.0],
            [0.0, 0.0, 90.0],
            [0.0, 0.0, 90.0],
            [0.0, 0.0, 90.0],
            [0.0, 0.0, 90.0],
        ],
        rtol=1e-5
    )

    assert cube.coords('longitude', dim_coords=False)
    lon = cube.coord('longitude', dim_coords=False)
    assert lon.var_name == 'lon'
    assert lon.standard_name == 'longitude'
    assert lon.long_name == 'longitude'
    assert lon.units == 'degrees_east'
    np.testing.assert_allclose(
        lon.points,
        [-135.0, -45.0, 45.0, 135.0, -135.0, -45.0, 45.0, 135.0],
        rtol=1e-5
    )
    np.testing.assert_allclose(
        lon.bounds,
        [
            [-135.0, -90.0, -180.0],
            [-45.0, 0.0, -90.0],
            [45.0, 90.0, 0.0],
            [135.0, 180.0, 90.0],
            [-180.0, -90.0, -135.0],
            [-90.0, 0.0, -45.0],
            [0.0, 90.0, 45.0],
            [90.0, 180.0, 135.0],
        ],
        rtol=1e-5
    )

    assert cube.coords('first spatial index for variables stored on an '
                       'unstructured grid', dim_coords=True)
    i_coord = cube.coord('first spatial index for variables stored on an '
                         'unstructured grid', dim_coords=True)
    assert i_coord.var_name == 'i'
    assert i_coord.standard_name is None
    assert i_coord.long_name == ('first spatial index for variables stored on '
                                 'an unstructured grid')
    assert i_coord.units == '1'
    np.testing.assert_allclose(i_coord.points, [0, 1, 2, 3, 4, 5, 6, 7])
    assert i_coord.bounds is None

    assert len(cube.coord_dims(lat)) == 1
    assert cube.coord_dims(lat) == cube.coord_dims(lon)
    assert cube.coord_dims(lat) == cube.coord_dims(i_coord)


# Test areacella (for extra_facets, and grid_latitude and grid_longitude
# coordinates)


def test_get_areacella_fix():
    """Test getting of fix."""
    fix = Fix.get_fixes('ICON', 'ICON', 'fx', 'areacella')
    assert fix == [AllVars(None)]


def test_areacella_fix(cubes_grid):
    """Test fix."""
    fix = get_allvars_fix('fx', 'areacella')
    fixed_cubes = fix.fix_metadata(cubes_grid)

    assert len(fixed_cubes) == 1
    cube = fixed_cubes[0]
    assert cube.var_name == 'areacella'
    assert cube.standard_name == 'cell_area'
    assert cube.long_name == 'Grid-Cell Area for Atmospheric Grid Variables'
    assert cube.units == 'm2'

    check_lat_lon(cube)


# Test clwvi (for extra_facets)


def test_get_clwvi_fix():
    """Test getting of fix."""
    fix = Fix.get_fixes('ICON', 'ICON', 'Amon', 'clwvi')
    assert fix == [AllVars(None)]


def test_clwvi_fix(cubes_2d):
    """Test fix."""
    fix = get_allvars_fix('Amon', 'clwvi')
    fixed_cubes = fix.fix_metadata(cubes_2d)

    assert len(fixed_cubes) == 1
    cube = fixed_cubes[0]
    assert cube.var_name == 'clwvi'
    assert cube.standard_name == ('atmosphere_mass_content_of_cloud_'
                                  'condensed_water')
    assert cube.long_name == 'Condensed Water Path'
    assert cube.units == 'kg m-2'

    check_time(cube)
    check_lat_lon(cube)


# Test siconca (for extra_facets, extra fix and typesi coordinate)


def test_get_siconca_fix():
    """Test getting of fix."""
    fix = Fix.get_fixes('ICON', 'ICON', 'SImon', 'siconca')
    assert fix == [Siconca(None), AllVars(None)]


def test_siconca_fix(cubes_2d):
    """Test fix."""
    vardef = get_var_info('ICON', 'SImon', 'siconca')
    extra_facets = get_extra_facets('ICON', 'ICON', 'SImon', 'siconca', ())
    siconca_fix = Siconca(vardef, extra_facets=extra_facets)
    allvars_fix = get_allvars_fix('SImon', 'siconca')

    fixed_cubes = siconca_fix.fix_metadata(cubes_2d)
    fixed_cubes = allvars_fix.fix_metadata(fixed_cubes)

    assert len(fixed_cubes) == 1
    cube = fixed_cubes[0]
    assert cube.var_name == 'siconca'
    assert cube.standard_name == 'sea_ice_area_fraction'
    assert cube.long_name == 'Sea-Ice Area Percentage (Atmospheric Grid)'
    assert cube.units == '%'

    check_time(cube)
    check_lat_lon(cube)
    assert cube.coords('area_type')
    typesi = cube.coord('area_type')
    assert typesi.var_name == 'type'
    assert typesi.standard_name == 'area_type'
    assert typesi.long_name == 'Sea Ice area type'
    assert typesi.units.is_no_unit()
    np.testing.assert_array_equal(typesi.points, ['sea_ice'])
    assert typesi.bounds is None

    np.testing.assert_allclose(
        cube.data,
        [[10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0]],
    )


# Test ta (for height and plev coordinate)


def test_get_ta_fix():
    """Test getting of fix."""
    fix = Fix.get_fixes('ICON', 'ICON', 'Amon', 'ta')
    assert fix == [AllVars(None)]


def test_ta_fix(cubes_3d):
    """Test fix."""
    fix = get_allvars_fix('Amon', 'ta')
    fixed_cubes = fix.fix_metadata(cubes_3d)

    cube = check_ta_metadata(fixed_cubes)
    check_time(cube)
    check_height(cube)
    check_lat_lon(cube)


def test_ta_fix_no_plev_bounds(cubes_3d):
    """Test fix."""
    fix = get_allvars_fix('Amon', 'ta')
    cubes = CubeList([
        cubes_3d.extract_cube(NameConstraint(var_name='ta')),
        cubes_3d.extract_cube(NameConstraint(var_name='pfull')),
    ])
    fixed_cubes = fix.fix_metadata(cubes)

    cube = check_ta_metadata(fixed_cubes)
    check_time(cube)
    check_height(cube, plev_has_bounds=False)
    check_lat_lon(cube)


# Test tas (for height2m coordinate)


def test_get_tas_fix():
    """Test getting of fix."""
    fix = Fix.get_fixes('ICON', 'ICON', 'Amon', 'tas')
    assert fix == [AllVars(None)]


def test_tas_fix(cubes_2d):
    """Test fix."""
    fix = get_allvars_fix('Amon', 'tas')
    fixed_cubes = fix.fix_metadata(cubes_2d)

    cube = check_tas_metadata(fixed_cubes)
    check_time(cube)
    check_lat_lon(cube)
    check_heightxm(cube, 2.0)


def test_tas_scalar_height2m_already_present(cubes_2d):
    """Test fix."""
    fix = get_allvars_fix('Amon', 'tas')

    # Scalar height (with wrong metadata) already present
    height_coord = AuxCoord(2.0, var_name='h', standard_name='height')
    cube = cubes_2d.extract_cube(NameConstraint(var_name='tas'))
    cube.add_aux_coord(height_coord, ())
    fixed_cubes = fix.fix_metadata(cubes_2d)

    assert len(fixed_cubes) == 1
    cube = fixed_cubes[0]
    check_heightxm(cube, 2.0)


def test_tas_dim_height2m_already_present(cubes_2d):
    """Test fix."""
    fix = get_allvars_fix('Amon', 'tas')

    # Dimensional coordinate height (with wrong metadata) already present
    height_coord = AuxCoord(2.0, var_name='h', standard_name='height')
    cube = cubes_2d.extract_cube(NameConstraint(var_name='tas'))
    cube.add_aux_coord(height_coord, ())
    cube = iris.util.new_axis(cube, scalar_coord='height')
    cube.transpose((1, 0, 2))
    cubes = CubeList([cube])
    fixed_cubes = fix.fix_metadata(cubes)

    assert len(fixed_cubes) == 1
    cube = fixed_cubes[0]
    check_heightxm(cube, 2.0)


# Test uas (for height10m coordinate)


def test_get_uas_fix():
    """Test getting of fix."""
    fix = Fix.get_fixes('ICON', 'ICON', 'Amon', 'uas')
    assert fix == [AllVars(None)]


def test_uas_fix(cubes_2d):
    """Test fix."""
    fix = get_allvars_fix('Amon', 'uas')
    fixed_cubes = fix.fix_metadata(cubes_2d)

    assert len(fixed_cubes) == 1
    cube = fixed_cubes[0]
    assert cube.var_name == 'uas'
    assert cube.standard_name == 'eastward_wind'
    assert cube.long_name == 'Eastward Near-Surface Wind'
    assert cube.units == 'm s-1'

    check_time(cube)
    check_lat_lon(cube)
    assert cube.coords('height')
    height = cube.coord('height')
    assert height.var_name == 'height'
    assert height.standard_name == 'height'
    assert height.long_name == 'height'
    assert height.units == 'm'
    assert height.attributes == {'positive': 'up'}
    np.testing.assert_allclose(height.points, [10.0])
    assert height.bounds is None


def test_uas_scalar_height10m_already_present(cubes_2d):
    """Test fix."""
    fix = get_allvars_fix('Amon', 'uas')

    # Scalar height (with wrong metadata) already present
    height_coord = AuxCoord(10.0, var_name='h', standard_name='height')
    cube = cubes_2d.extract_cube(NameConstraint(var_name='uas'))
    cube.add_aux_coord(height_coord, ())
    fixed_cubes = fix.fix_metadata(cubes_2d)

    assert len(fixed_cubes) == 1
    cube = fixed_cubes[0]
    check_heightxm(cube, 10.0)


def test_uas_dim_height10m_already_present(cubes_2d):
    """Test fix."""
    fix = get_allvars_fix('Amon', 'uas')

    # Dimensional coordinate height (with wrong metadata) already present
    height_coord = AuxCoord(10.0, var_name='h', standard_name='height')
    cube = cubes_2d.extract_cube(NameConstraint(var_name='uas'))
    cube.add_aux_coord(height_coord, ())
    cube = iris.util.new_axis(cube, scalar_coord='height')
    cube.transpose((1, 0, 2))
    cubes = CubeList([cube])
    fixed_cubes = fix.fix_metadata(cubes)

    assert len(fixed_cubes) == 1
    cube = fixed_cubes[0]
    check_heightxm(cube, 10.0)


# Test fix with regular grid and 2D latitudes and longitude


def test_regular_grid_fix(cubes_regular_grid):
    """Test fix."""
    fix = get_allvars_fix('Amon', 'tas')
    fixed_cubes = fix.fix_metadata(cubes_regular_grid)

    cube = check_tas_metadata(fixed_cubes)
    assert cube.coords('time', dim_coords=True, dimensions=0)
    assert cube.coords('latitude', dim_coords=True, dimensions=1)
    assert cube.coords('longitude', dim_coords=True, dimensions=2)
    assert cube.coords('height', dim_coords=False, dimensions=())


def test_2d_lat_lon_grid_fix(cubes_2d_lat_lon_grid):
    """Test fix."""
    fix = get_allvars_fix('Amon', 'tas')
    fixed_cubes = fix.fix_metadata(cubes_2d_lat_lon_grid)

    cube = check_tas_metadata(fixed_cubes)
    assert cube.coords('time', dim_coords=True, dimensions=0)
    assert cube.coords('latitude', dim_coords=False, dimensions=(1, 2))
    assert cube.coords('longitude', dim_coords=False, dimensions=(1, 2))
    assert cube.coords('height', dim_coords=False, dimensions=())


# Test fix with empty standard_name


def test_empty_standard_name_fix(cubes_2d):
    """Test fix."""
    # We know that tas has a standard name, but this being native model output
    # there may be variables with no standard name. The code is designed to
    # handle this gracefully and here we test it with an artificial, but
    # realistic case.
    vardef = get_var_info('ICON', 'Amon', 'tas')
    original_standard_name = vardef.standard_name
    vardef.standard_name = ''
    extra_facets = get_extra_facets('ICON', 'ICON', 'Amon', 'tas', ())
    fix = AllVars(vardef, extra_facets=extra_facets)
    fixed_cubes = fix.fix_metadata(cubes_2d)

    assert len(fixed_cubes) == 1
    cube = fixed_cubes[0]
    assert cube.var_name == 'tas'
    assert cube.standard_name is None
    assert cube.long_name == 'Near-Surface Air Temperature'
    assert cube.units == 'K'

    # Restore original standard_name of tas
    vardef.standard_name = original_standard_name


# Test automatic addition of missing coordinates


def test_add_time(cubes_2d):
    """Test fix."""
    # Remove time from tas cube to test automatic addition
    tas_cube = cubes_2d.extract_cube(NameConstraint(var_name='tas'))
    uas_cube = cubes_2d.extract_cube(NameConstraint(var_name='uas'))
    tas_cube = tas_cube[0]
    tas_cube.remove_coord('time')
    cubes = CubeList([tas_cube, uas_cube])

    fix = get_allvars_fix('Amon', 'tas')
    fixed_cubes = fix.fix_metadata(cubes)

    cube = check_tas_metadata(fixed_cubes)
    assert cube.shape == (1, 8)
    check_time(cube)


def test_add_time_fails():
    """Test fix."""
    fix = get_allvars_fix('Amon', 'ta')
    cube = Cube(1, var_name='ta', units='K')
    cubes = CubeList([
        cube,
        Cube(1, var_name='tas', units='K'),
    ])
    msg = "Cannot add required coordinate 'time' to variable 'ta'"
    with pytest.raises(ValueError, match=msg):
        fix._add_time(cube, cubes)


# Test with single-dimension cubes


def test_only_time():
    """Test fix."""
    # We know that ta has dimensions time, plev19, latitude, longitude, but the
    # ICON CMORizer is designed to check for the presence of each dimension
    # individually. To test this, remove all but one dimension of ta to create
    # an artificial, but realistic test case.
    vardef = get_var_info('ICON', 'Amon', 'ta')
    original_dimensions = vardef.dimensions
    vardef.dimensions = ['time']
    extra_facets = get_extra_facets('ICON', 'ICON', 'Amon', 'ta', ())
    fix = AllVars(vardef, extra_facets=extra_facets)

    # Create cube that does not contain time to test automatic addition of time
    # dimension from other cube in file
    time_coord = DimCoord([0.0, 1.0], var_name='time', standard_name='time',
                          long_name='time', units='days since 1850-01-01')
    cubes = CubeList([
        Cube([1, 1], var_name='ta', units='K',
             dim_coords_and_dims=[(time_coord, 0)]),
    ])
    fixed_cubes = fix.fix_metadata(cubes)

    # Check cube metadata
    cube = check_ta_metadata(fixed_cubes)

    # Check cube data
    assert cube.shape == (2,)
    np.testing.assert_equal(cube.data, [1, 1])

    # Check time metadata
    assert cube.coords('time')
    new_time_coord = cube.coord('time')
    assert new_time_coord.var_name == 'time'
    assert new_time_coord.standard_name == 'time'
    assert new_time_coord.long_name == 'time'
    assert new_time_coord.units == 'days since 1850-01-01'

    # Check time data
    np.testing.assert_allclose(new_time_coord.points, [0.0, 1.0])
    np.testing.assert_allclose(new_time_coord.bounds,
                               [[-0.5, 0.5], [0.5, 1.5]])

    # Restore original dimensions of ta
    vardef.dimensions = original_dimensions


def test_only_height():
    """Test fix."""
    # We know that ta has dimensions time, plev19, latitude, longitude, but the
    # ICON CMORizer is designed to check for the presence of each dimension
    # individually. To test this, remove all but one dimension of ta to create
    # an artificial, but realistic test case.
    vardef = get_var_info('ICON', 'Amon', 'ta')
    original_dimensions = vardef.dimensions
    vardef.dimensions = ['plev19']
    extra_facets = get_extra_facets('ICON', 'ICON', 'Amon', 'ta', ())
    fix = AllVars(vardef, extra_facets=extra_facets)

    # Create cube that does not contain time to test automatic addition of time
    # dimension from other cube in file
    height_coord = DimCoord([1000.0, 100.0], var_name='height',
                            standard_name='height', units='cm')
    cubes = CubeList([
        Cube([1, 1], var_name='ta', units='K',
             dim_coords_and_dims=[(height_coord, 0)]),
    ])
    fixed_cubes = fix.fix_metadata(cubes)

    # Check cube metadata
    cube = check_ta_metadata(fixed_cubes)

    # Check cube data
    assert cube.shape == (2,)
    np.testing.assert_equal(cube.data, [1, 1])

    # Check height metadata
    assert cube.coords('height')
    new_height_coord = cube.coord('height')
    assert new_height_coord.var_name == 'height'
    assert new_height_coord.standard_name == 'height'
    assert new_height_coord.long_name == 'height'
    assert new_height_coord.units == 'm'
    assert new_height_coord.attributes == {'positive': 'up'}

    # Check height data
    np.testing.assert_allclose(new_height_coord.points, [1.0, 10.0])
    assert new_height_coord.bounds is None

    # Restore original dimensions of ta
    vardef.dimensions = original_dimensions


# Test variable not available in file


def test_var_not_available(cubes_2d):
    """Test fix."""
    fix = get_allvars_fix('Amon', 'pr')
    msg = "Variable 'pr' used to extract 'pr' is not available in input file"
    with pytest.raises(ValueError, match=msg):
        fix.fix_metadata(cubes_2d)


# Test fix with invalid time units


def test_invalid_time_units(cubes_2d):
    """Test fix."""
    fix = get_allvars_fix('Amon', 'tas')
    for cube in cubes_2d:
        cube.coord('time').attributes['invalid_units'] = 'month as %Y%m%d.%f'
    msg = "Expected time units"
    with pytest.raises(ValueError, match=msg):
        fix.fix_metadata(cubes_2d)
