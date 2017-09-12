"""
Unit tests for the :func:`esmvaltool.backend.regrid._create_cube` function.

"""

from __future__ import (absolute_import, division, print_function)
from six.moves import (filter, input, map, range, zip)  # noqa
import six  # noqa

import numpy as np
import unittest

import tests
from tests.unit.regrid import _make_vcoord, _make_cube
from esmvaltool.interface_scripts.regrid import _create_cube as create_cube


class Test(tests.Test):
    def setUp(self):
        shape = (3, 2, 1)
        self.dtype = np.dtype('int8')
        self.cube = _make_cube(shape, dtype=self.dtype)

    def test_invalid_shape__data_mismatch_with_levels(self):
        levels = np.array([0, 1])
        emsg = 'Mismatch between data and levels'
        with self.assertRaisesRegexp(ValueError, emsg):
            create_cube(self.cube, self.cube.data, levels)

    def test(self):
        shape = (2, 2, 1)
        data = np.empty(shape)
        levels = np.array([10, 20])
        result = create_cube(self.cube, data, levels)
        expected = _make_cube(data, aux_coord=False, dim_coord=False)
        vcoord = _make_vcoord(levels)
        expected.add_dim_coord(vcoord, 0)
        self.assertEqual(result, expected)

    def test_non_monotonic(self):
        shape = (2, 2, 1)
        data = np.empty(shape)
        levels = np.array([10, 10])
        result = create_cube(self.cube, data, levels)
        expected = _make_cube(data, aux_coord=False, dim_coord=False)
        vcoord = _make_vcoord(levels)
        expected.add_aux_coord(vcoord, 0)
        self.assertEqual(result, expected)

    def test_collapse(self):
        shape = (1, 2, 1)
        data = np.empty(shape)
        levels = np.array([123])
        result = create_cube(self.cube, data, levels)
        expected = _make_cube(data, aux_coord=False, dim_coord=False)[0]
        vcoord = _make_vcoord(levels)
        expected.add_aux_coord(vcoord)
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
