"""Unit tests for :mod:`esmvalcore.preprocessor._rolling_window`."""
import iris
import numpy as np
import pytest

from esmvalcore.preprocessor._rolling_window import rolling_window_statistics


def assert_masked_array_equal(arr_1, arr_2):
    """Check equality of two masked arrays."""
    arr_1 = np.ma.array(arr_1)
    arr_2 = np.ma.array(arr_2)
    mask_1 = np.ma.getmaskarray(arr_1)
    mask_2 = np.ma.getmaskarray(arr_2)
    np.testing.assert_allclose(mask_1, mask_2)
    data_1 = arr_1.filled(np.nan)
    data_2 = arr_2.filled(np.nan)
    np.testing.assert_allclose(data_1, data_2)


@pytest.fixture
def cube():
    """Fixture cube."""
    times = iris.coords.DimCoord([1.0, 2.0, 3.0, 4.0, 5.0],
                                 standard_name='time', units='yr')
    lats = iris.coords.DimCoord([0.0, 20.0], standard_name='latitude',
                                units='m')
    lons = iris.coords.DimCoord([500.0, 600.0], standard_name='longitude',
                                units='m')
    aux_coord = iris.coords.AuxCoord([[0.0, 0.0], [1.0, 1.0]], var_name='aux')
    cube_data = np.arange(5.0 * 2.0 * 2.0).reshape(5, 2, 2)
    cube_data[:3] = 0.0
    cube_data[2, 0, 0] = np.nan
    cube_data[3, 0, 0] = np.nan
    cube_data = np.ma.masked_invalid(cube_data)
    cube = iris.cube.Cube(cube_data.astype('float32'), var_name='x',
                          long_name='X', units='kg',
                          dim_coords_and_dims=[(times, 0), (lats, 1),
                                               (lons, 2)],
                          aux_coords_and_dims=[(aux_coord, (1, 2))])
    return cube


def test_rolling_window_statistics_invalid_op(cube):
    """Test rolling-window statistics with invalid operator."""
    with pytest.raises(ValueError):
        rolling_window_statistics(cube, 'time', 'invalid_op', 2)


def test_rolling_window_statistics_2d_coord(cube):
    """Test rolling-window statistics on 2D coordinate."""
    with pytest.raises(iris.exceptions.CoordinateMultiDimError):
        rolling_window_statistics(cube, 'aux', 'mean', 2)


def test_rolling_window_statistics_mean(cube):
    """Test rolling-window statistics with mean operator."""
    cube = rolling_window_statistics(cube, 'time', 'mean', 2)
    expected_data = np.ma.masked_invalid([[[0.0, 0.0],
                                           [0.0, 0.0]],
                                          [[0.0, 0.0],
                                           [0.0, 0.0]],
                                          [[np.nan, 6.5],
                                           [7.0, 7.5]],
                                          [[16.0, 15.0],
                                           [16.0, 17.0]]])
    assert cube.shape == (4, 2, 2)
    assert_masked_array_equal(cube.data, expected_data)


def test_rolling_window_statistics_sum(cube):
    """Test rolling-window statistics with sum operator."""
    cube = rolling_window_statistics(cube, 'time', 'sum', 4)
    expected_data = [[[0.0, 13.0],
                      [14.0, 15.0]],
                     [[16.0, 30.0],
                      [32.0, 34.0]]]
    assert cube.shape == (2, 2, 2)
    assert_masked_array_equal(cube.data, expected_data)
