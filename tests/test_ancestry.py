import re
from abc import ABC, abstractmethod
from pathlib import Path

import iris.cube
import pytest
from unittest import mock

import esmvalcore._config
from esmvalcore._ancestry import (
    NoLocalParentError,
    ParentFinder,
    ParentFinderCMIP5,
    ParentFinderCMIP6,
)

# read developer file so drs works
CFG_DEVELOPER = esmvalcore._config.read_config_developer_file()
esmvalcore._config._config.CFG = CFG_DEVELOPER


all_finders = pytest.mark.parametrize(
    "finder",
    (ParentFinderCMIP5, ParentFinderCMIP6)
)


def test_base_is_abstract():
    err_msg = "Can't instantiate abstract class ParentFinder"
    with pytest.raises(TypeError, match=err_msg):
        ParentFinder("inp")


@all_finders
@pytest.mark.parametrize("inp", (1, "str", [1, 2, 3]))
def test_init_wrong_type(finder, inp):
    err_msg = re.escape(
        f"`cube` must be an :obj:`iris.cube.Cube`, received {type(inp)}"
    )
    with pytest.raises(TypeError, match=err_msg):
        finder(inp)


class _ParentFinderTester(ABC):
    @property
    @abstractmethod
    def _test_class(self):
        """:obj:`ParentFinder`: Class to test"""

    @abstractmethod
    def test_get_parent_metadata(self):
        # should like something like the below
        # get mock cube
        # res = self._test_class(mock_cube).get_parent_metadata()
        # assert res == exp
        pass

    @staticmethod
    def _mock_cube():
        return iris.cube.Cube([0])

    def test_find_local_parent(self):
        # TODO: work out how to do integration test for this
        rootpath = Path("/here/there")
        drs = "ESGF"
        get_parent_metadata_return_value = "parent_metadata"
        _find_parent_files_return_value = ["a", "b", "/c/d"]

        runner = FindLocalParentRunner()
        mock_get_parent_metadata, mock_find_parent_files = runner.get_mocks(
            get_parent_metadata_return_value,
            _find_parent_files_return_value,
        )

        res = runner.run_find_local_parent_call(
            self,
            rootpath,
            drs,
            mock_get_parent_metadata,
            mock_find_parent_files,
        )

        mock_get_parent_metadata.assert_called_once()
        mock_find_parent_files.assert_called_once_with(
            get_parent_metadata_return_value,
            rootpath,
            drs,
        )
        assert res == [Path(v) for v in _find_parent_files_return_value]

    def test_find_local_parent_no_found_files(self):
        # TODO: work out how to do integration test for this
        rootpath = Path("/here/there")
        drs = "ESGF"
        get_parent_metadata_return_value = "parent_metadata"
        _find_parent_files_return_value = []
        esmval_ids = {"this": "that"}

        runner = FindLocalParentRunner()
        mock_get_parent_metadata, mock_find_parent_files = runner.get_mocks(
            get_parent_metadata_return_value,
            _find_parent_files_return_value,
        )
        mock_get_esmval_data_ids = mock.Mock(return_value=esmval_ids)

        err_msg = re.escape(
            f"Could not find parents for {esmval_ids}, we searched in "
            f"rootpath `{rootpath}` with drs `{drs}` for "
            f"{get_parent_metadata_return_value}"
        )
        with pytest.raises(NoLocalParentError, match=err_msg):
            runner.run_find_local_parent_call(
                self,
                rootpath,
                drs,
                mock_get_parent_metadata,
                mock_find_parent_files,
                mock_get_esmval_data_ids=mock_get_esmval_data_ids,
            )


class FindLocalParentRunner:
    def get_mocks(
        self,
        get_parent_metadata_return_value,
        _find_parent_files_return_value,
    ):
        mock_get_parent_metadata = mock.Mock(
            return_value=get_parent_metadata_return_value
        )
        mock_find_parent_files = mock.Mock(
            return_value=_find_parent_files_return_value
        )

        return mock_get_parent_metadata, mock_find_parent_files

    def run_find_local_parent_call(
        self,
        parent_finder_tester,
        rootpath,
        drs,
        mock_get_parent_metadata,
        mock_find_parent_files,
        mock_get_esmval_data_ids=None,
    ):
        with mock.patch.multiple(
            parent_finder_tester._test_class,
            get_parent_metadata=mock_get_parent_metadata,
            _find_parent_files=mock_find_parent_files,
            _get_esmval_data_ids=mock_get_esmval_data_ids,
        ):
            res = (
                parent_finder_tester
                ._test_class(parent_finder_tester._mock_cube())
                .find_local_parent(rootpath, drs)
            )

        return res


class TestParentFinderCMIP6(_ParentFinderTester):
    _test_class = ParentFinderCMIP6

    def test_get_parent_metadata(self):
        mock_cube = self._mock_cube()

        attributes_child = {
            "hi": "Bye",
            'activity_id': 'GeoMIP',
            'experiment_id': 'G6solar',
            'grid_label': 'gn',
            'institution_id': 'MOHC',
            'mip_era': 'CMIP6',
            'source_id': 'UKESM1-0-LL',
            'table_id': 'Lmon',
            'variable_id': 'npp',
            'variant_label': 'r1i1p1f2',
            'parent_activity_id': 'ScenarioMIP',
            'parent_experiment_id': 'ssp585',
            'parent_mip_era': 'CMIP6',
            'parent_source_id': 'UKESM1-0-LL',
            'parent_variant_label': 'r1i1p1f2',
        }
        mock_cube.attributes = attributes_child

        exp = {
            "activity": "ScenarioMIP",
            'exp': 'ssp585',
            "grid": "gn",
            "institute": "MOHC",
            "project": "CMIP6",
            "dataset": "UKESM1-0-LL",
            "mip": "Lmon",
            "short_name": "npp",
            "ensemble": "r1i1p1f2",
        }

        res = self._test_class(mock_cube).get_parent_metadata()
        assert res == exp


class TestParentFinderCMIP5(_ParentFinderTester):
    _test_class = ParentFinderCMIP5

    def test_get_parent_metadata(self):
        mock_cube = iris.cube.Cube([0])

        mock_cube.var_name = "tas"
        attributes_child = {
            "hi": "Bye",
            'experiment': 'rcp45',
            "initialization_method": 1,
            'institute_id': 'NCC',
            "model_id": "NorESM1-M",
            "physics_version": 1,
            'project_id': 'CMIP5',
            "realization": 1,
            'parent_experiment': 'historical',
            'parent_experiment_rip': 'r1i1p1',
        }
        # depends on how we want to keep this information around for downstream
        # users, see previous discussions
        attributes_child["mip"] = "Amon"

        mock_cube.attributes = attributes_child

        exp = {
            'exp': 'historical',
            "institute": "NCC",
            "project": "CMIP5",
            "dataset": "NorESM1-M",
            "short_name": "tas",
            "ensemble": "r1i1p1",
            "mip": "Amon",
        }

        res = self._test_class(mock_cube).get_parent_metadata()
        assert res == exp
