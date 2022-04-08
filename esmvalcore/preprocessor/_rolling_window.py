"""Rolling-window operations on cubes."""

import logging

from ._shared import get_iris_analysis_operation

logger = logging.getLogger(__name__)


def rolling_window_statistics(cube, coordinate, operator, window_length):
    """Compute rolling-window statistics over a coordinate.

    Parameters
    ----------
    cube : iris.cube.Cube
        Input cube.
    coordinate : str
        Coordinate over which the rolling-window statistics is calculated. Must
        be 1D.
    operator : str
        Select operator to apply. Available operators: ``'mean'``,
        ``'median'``, ``'std_dev'``, ``'sum'``, ``'variance'``, ``'min'``,
        ``'max'``, ``'rms'``.
    window_length : int
        Size of the window to use.

    Returns
    -------
    iris.cube.Cube
        Rolling-window statistics cube.

    Raises
    ------
    iris.exceptions.CoordinateMultiDimError
        Coordinate has more than one dimensions.
    ValueError
        Invalid ``'operator'`` given.

    """
    operation = get_iris_analysis_operation(operator)
    cube = cube.rolling_window(coordinate, operation, window_length)
    return cube
