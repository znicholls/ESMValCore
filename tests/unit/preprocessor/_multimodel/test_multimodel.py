"""Unit test for :func:`esmvalcore.preprocessor._multimodel`"""

from datetime import datetime

import iris
import numpy as np
import pytest
from cf_units import Unit
from iris.cube import Cube

import esmvalcore.preprocessor._multimodel as mm
from esmvalcore.preprocessor import multi_model_statistics

SPAN_OPTIONS = ('overlap', 'full')

FREQUENCY_OPTIONS = ('daily', 'monthly', 'yearly')  # hourly

CALENDAR_OPTIONS = ('360_day', '365_day', 'gregorian', 'proleptic_gregorian',
                    'julian')


def assert_array_almost_equal(this, other):
    """Assert that array `this` almost equals array `other`."""
    if np.ma.isMaskedArray(this) or np.ma.isMaskedArray(other):
        np.testing.assert_array_equal(this.mask, other.mask)

    np.testing.assert_array_almost_equal(this, other)


def timecoord(frequency,
              calendar='gregorian',
              offset='days since 1850-01-01',
              num=3):
    """Return a time coordinate with the given time points and calendar."""

    time_points = range(1, num + 1)

    if frequency == 'hourly':
        dates = [datetime(1850, 1, 1, i, 0, 0) for i in time_points]
    if frequency == 'daily':
        dates = [datetime(1850, 1, i, 0, 0, 0) for i in time_points]
    elif frequency == 'monthly':
        dates = [datetime(1850, i, 15, 0, 0, 0) for i in time_points]
    elif frequency == 'yearly':
        dates = [datetime(1850, 7, i, 0, 0, 0) for i in time_points]

    unit = Unit(offset, calendar=calendar)
    points = unit.date2num(dates)
    return iris.coords.DimCoord(points, standard_name='time', units=unit)


def generate_cube_from_dates(
    dates,
    calendar='gregorian',
    offset='days since 1850-01-01',
    fill_val=1,
    len_data=3,
    var_name=None,
):
    """Generate test cube from list of dates / frequency specification.

    Parameters
    ----------
    calendar : str or list
        Date frequency: 'hourly' / 'daily' / 'monthly' / 'yearly' or
        list of datetimes.
    offset : str
        Offset to use
    fill_val : int
        Value to fill the data with
    len_data : int
        Number of data / time points
    var_name : str
        Name of the data variable

    Returns
    -------
    iris.cube.Cube
    """
    if isinstance(dates, str):
        time = timecoord(dates, calendar, offset=offset, num=len_data)
    else:
        unit = Unit(offset, calendar=calendar)
        time = iris.coords.DimCoord(unit.date2num(dates),
                                    standard_name='time',
                                    units=unit)

    return Cube((fill_val, ) * len_data,
                dim_coords_and_dims=[(time, 0)],
                var_name=var_name)


def get_cubes_for_validation_test(frequency):
    """Set up cubes used for testing multimodel statistics."""

    # Simple 1d cube with standard time cord
    cube1 = generate_cube_from_dates(frequency)

    # Cube with masked data
    cube2 = cube1.copy()
    cube2.data = np.ma.array([5, 5, 5], mask=[True, False, False])

    # Cube with deviating time coord
    cube3 = generate_cube_from_dates(frequency,
                                     calendar='360_day',
                                     offset='days since 1950-01-01',
                                     len_data=2,
                                     fill_val=9)

    return [cube1, cube2, cube3]


VALIDATION_DATA_SUCCESS = (
    ('full', 'mean', (5, 5, 3)),
    ('full', 'std', (5.656854249492381, 4, 2.8284271247461903)),
    ('full', 'std_dev', (5.656854249492381, 4, 2.8284271247461903)),
    ('full', 'min', (1, 1, 1)),
    ('full', 'max', (9, 9, 5)),
    ('full', 'median', (5, 5, 3)),
    ('full', 'p50', (5, 5, 3)),
    ('full', 'p99.5', (8.96, 8.96, 4.98)),
    ('overlap', 'mean', (5, 5)),
    ('overlap', 'std', (5.656854249492381, 4)),
    ('overlap', 'std_dev', (5.656854249492381, 4)),
    ('overlap', 'min', (1, 1)),
    ('overlap', 'max', (9, 9)),
    ('overlap', 'median', (5, 5)),
    ('overlap', 'p50', (5, 5)),
    ('overlap', 'p99.5', (8.96, 8.96)),
    # test multiple statistics
    ('overlap', ('min', 'max'), ((1, 1), (9, 9))),
    ('full', ('min', 'max'), ((1, 1, 1), (9, 9, 5))),
)


@pytest.mark.parametrize('frequency', FREQUENCY_OPTIONS)
@pytest.mark.parametrize('span, statistics, expected', VALIDATION_DATA_SUCCESS)
def test_multimodel_statistics(frequency, span, statistics, expected):
    """High level test for multicube statistics function.

    - Should work for multiple data frequencies
    - Should be able to deal with multiple statistics
    - Should work for both span arguments
    - Should deal correctly with different mask options
    - Return type should be a dict with all requested statistics as keys
    """
    cubes = get_cubes_for_validation_test(frequency)

    if isinstance(statistics, str):
        statistics = (statistics, )
        expected = (expected, )

    result = multi_model_statistics(cubes, span, statistics)

    assert isinstance(result, dict)
    assert set(result.keys()) == set(statistics)

    for i, statistic in enumerate(statistics):
        result_cube = result[statistic]
        expected_data = np.ma.array(expected[i], mask=False)
        assert_array_almost_equal(result_cube.data, expected_data)


VALIDATION_DATA_FAIL = (
    ('percentile', ValueError),
    ('wpercentile', ValueError),
    ('count', TypeError),
    ('peak', TypeError),
    ('proportion', TypeError),
)


@pytest.mark.parametrize('statistic, error', VALIDATION_DATA_FAIL)
def test_unsupported_statistics_fail(statistic, error):
    """Check that unsupported statistics raise an exception."""
    cubes = get_cubes_for_validation_test('monthly')
    span = 'overlap'
    statistics = (statistic, )
    with pytest.raises(error):
        _ = multi_model_statistics(cubes, span, statistics)


@pytest.mark.parametrize('calendar1, calendar2, expected', (
    ('360_day', '360_day', '360_day'),
    ('365_day', '365_day', '365_day'),
    ('365_day', '360_day', 'gregorian'),
    ('360_day', '365_day', 'gregorian'),
    ('gregorian', '365_day', 'gregorian'),
    ('proleptic_gregorian', 'julian', 'gregorian'),
    ('julian', '365_day', 'gregorian'),
))
def test_get_consistent_time_unit(calendar1, calendar2, expected):
    """Test same calendar returned or default if calendars differ.

    Expected behaviour: If the calendars are the same, return that one.
    If the calendars are not the same, return 'gregorian'.
    """
    cubes = (
        generate_cube_from_dates('monthly', calendar=calendar1),
        generate_cube_from_dates('monthly', calendar=calendar2),
    )

    result = mm._get_consistent_time_unit(cubes)
    assert result.calendar == expected


def generate_resolve_span_cases(valid):
    """Generate test cases for _resolve_span."""
    points_1 = (1, 2, 3)
    points_2 = (2, 3, 4)
    points_3 = (3, 4, 5)
    points_4 = (4, 5, 6)
    empty_tuple = ()

    if valid:
        yield from (
            ((points_1, ), 'overlap', points_1),
            ((points_1, ), 'full', points_1),
            ((points_1, points_2), 'overlap', (2, 3)),
            ((points_1, points_2), 'full', (1, 2, 3, 4)),
            ((points_1, points_2, points_3), 'overlap', (3, )),
            ((points_1, points_2, points_3), 'full', (1, 2, 3, 4, 5)),
            ((points_1, points_4), 'full', (1, 2, 3, 4, 5, 6)),
        )
    else:
        yield from (
            (empty_tuple, 'overlap', TypeError),
            (empty_tuple, 'full', TypeError),
            ((points_1, points_4), 'overlap', ValueError),
        )


@pytest.mark.parametrize('points, span, expected',
                         generate_resolve_span_cases(True))
def test_resolve_span(points, span, expected):
    """Check that resolve_span returns the correct union/intersection."""
    result = mm._resolve_span(points, span=span)
    assert isinstance(result, np.ndarray)
    np.testing.assert_equal(result, expected)


@pytest.mark.parametrize('points, span, error',
                         generate_resolve_span_cases(False))
def test_resolve_span_fail(points, span, error):
    """Test failing case for _resolve_span."""
    with pytest.raises(error):
        mm._resolve_span(points, span=span)


@pytest.mark.parametrize('span', SPAN_OPTIONS)
def test_align(span):
    """Test _align function."""

    # TODO --> check that if a cube is extended,
    #          the extended points are masked (not NaN!)

    len_data = 3

    cubes = []

    for calendar in CALENDAR_OPTIONS:
        cube = generate_cube_from_dates('monthly',
                                        calendar=calendar,
                                        len_data=3)
        cubes.append(cube)

    result_cubes = mm._align(cubes, span)

    calendars = set(cube.coord('time').units.calendar for cube in result_cubes)

    assert len(calendars) == 1
    assert list(calendars)[0] == 'gregorian'

    shapes = set(cube.shape for cube in result_cubes)

    assert len(shapes) == 1
    assert tuple(shapes)[0] == (len_data, )


@pytest.mark.parametrize('span', SPAN_OPTIONS)
def test_combine_same_shape(span):
    """Test _combine with same shape of cubes."""
    len_data = 3
    num_cubes = 5
    test_dim = 'test_dim'
    cubes = []

    for i in range(num_cubes):
        cube = generate_cube_from_dates('monthly',
                                        '360_day',
                                        fill_val=i,
                                        len_data=len_data)
        cubes.append(cube)

    result_cube = mm._combine(cubes, dim=test_dim)

    dim_coord = result_cube.coord(test_dim)
    assert dim_coord.var_name == test_dim
    assert result_cube.shape == (num_cubes, len_data)

    desired = np.linspace((0, ) * len_data,
                          num_cubes - 1,
                          num=num_cubes,
                          dtype=int)
    np.testing.assert_equal(result_cube.data, desired)


def test_combine_different_shape_fail():
    """Test _combine with inconsistent data."""
    num_cubes = 5
    test_dim = 'test_dim'
    cubes = []

    for num in range(1, num_cubes + 1):
        cube = generate_cube_from_dates('monthly', '360_day', len_data=num)
        cubes.append(cube)

    with pytest.raises(iris.exceptions.MergeError):
        _ = mm._combine(cubes, dim=test_dim)


def test_combine_inconsistent_var_names_fail():
    """Test _combine with inconsistent var names."""
    num_cubes = 5
    test_dim = 'test_dim'
    cubes = []

    for num in range(num_cubes):
        cube = generate_cube_from_dates('monthly',
                                        '360_day',
                                        var_name=f'test_var_{num}')
        cubes.append(cube)

    with pytest.raises(iris.exceptions.MergeError):
        _ = mm._combine(cubes, dim=test_dim)


@pytest.mark.parametrize('span', SPAN_OPTIONS)
def test_edge_case_different_time_offsets(span):
    cubes = (
        generate_cube_from_dates('monthly',
                                 '360_day',
                                 offset='days since 1888-01-01'),
        generate_cube_from_dates('monthly',
                                 '360_day',
                                 offset='days since 1899-01-01'),
    )

    statistic = 'min'
    statistics = (statistic, )

    result = multi_model_statistics(cubes, span, statistics)

    result_cube = result[statistic]

    time_coord = result_cube.coord('time')

    assert time_coord.units.calendar == 'gregorian'
    assert time_coord.units.origin == 'days since 1850-01-01'

    desired = np.array((14., 45., 73.))
    np.testing.assert_array_equal(time_coord.points, desired)

    # input cubes are updated in-place
    for cube in cubes:
        np.testing.assert_array_equal(cube.coord('time').points, desired)


def generate_cubes_with_non_overlapping_timecoords():
    """Generate sample data where time coords do not overlap."""
    time_points = range(1, 4)
    dates1 = [datetime(1850, i, 15, 0, 0, 0) for i in time_points]
    dates2 = [datetime(1950, i, 15, 0, 0, 0) for i in time_points]

    return (
        generate_cube_from_dates(dates1),
        generate_cube_from_dates(dates2),
    )


def test_edge_case_time_no_overlap_fail():
    """Test case when time coords do not overlap using span='overlap'.

    Expected behaviour: `multi_model_statistics` should fail if time
    points are not overlapping.
    """
    cubes = generate_cubes_with_non_overlapping_timecoords()

    statistic = 'min'
    statistics = (statistic, )

    with pytest.raises(ValueError):
        _ = multi_model_statistics(cubes, 'overlap', statistics)


def test_edge_case_time_no_overlap_success():
    """Test case when time coords do not overlap using span='full'.

    Expected behaviour: `multi_model_statistics` should use all
    available time points.
    """
    cubes = generate_cubes_with_non_overlapping_timecoords()

    statistic = 'min'
    statistics = (statistic, )

    result = multi_model_statistics(cubes, 'full', statistics)
    result_cube = result[statistic]

    assert result_cube.coord('time').shape == (6, )


@pytest.mark.parametrize('span', SPAN_OPTIONS)
def test_edge_case_time_not_in_middle_of_months(span):
    """Test case when time coords are not on 15th for monthly data.

    Expected behaviour: `multi_model_statistics` will set all dates to
    the 15th.
    """
    time_points = range(1, 4)
    dates1 = [datetime(1850, i, 12, 0, 0, 0) for i in time_points]
    dates2 = [datetime(1850, i, 25, 0, 0, 0) for i in time_points]

    cubes = (
        generate_cube_from_dates(dates1),
        generate_cube_from_dates(dates2),
    )

    statistic = 'min'
    statistics = (statistic, )

    result = multi_model_statistics(cubes, span, statistics)
    result_cube = result[statistic]

    time_coord = result_cube.coord('time')

    desired = np.array((14., 45., 73.))
    np.testing.assert_array_equal(time_coord.points, desired)

    # input cubes are updated in-place
    for cube in cubes:
        np.testing.assert_array_equal(cube.coord('time').points, desired)


@pytest.mark.parametrize('span', SPAN_OPTIONS)
def test_edge_case_sub_daily_data_fail(span):
    """Test case when cubes with sub-daily time coords are passed."""
    cube = generate_cube_from_dates('hourly')
    cubes = (cube, cube)

    statistic = 'min'
    statistics = (statistic, )

    with pytest.raises(ValueError):
        _ = multi_model_statistics(cubes, span, statistics)
