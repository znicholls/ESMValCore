from abc import ABC, abstractmethod

import pytest

from esmvalcore._ancestry import _get_local_dataset


class BaseAncestryChecker(ABC):
    @property
    @abstractmethod
    def _project(self):
        pass

    # @property
    # @abstractmethod
    # def _expected_parent_id_keys(self):
    #     pass

    # def test_get_parent_id_keys(self):
    #     assert (
    #         _get_local_dataset(self._project)._parent_id_keys
    #         == self._expected_parent_id_keys
    #     )

    @abstractmethod
    def test_get_parent_ids(self, data_attributes, expected_ids):
        """
        Test finding of parent search ids

        Parameters
        ----------
        data_attributes : dict[str: str]
            Data attributes from which to generate the parent search ids,
            should match the attribute structure of the data from the given
            project.

        expected_ids : dict[str: str]
            A dictionary of ids (following ESMValTool nomenclature) and
            expected values for the parent dataset (given the value of
            ``mock_ds``).
        """
        assert (
            _get_local_dataset(self._project).get_parent_ids(data_attributes)
            == expected_ids
        )


class TestAncestryCMIP5(BaseAncestryChecker):
    _project = "CMIP5"

    @pytest.mark.parametrize(
        "data_attributes,expected_ids",
        (
            (
                {
                    "parent_experiment": "piControl",
                    "parent_experiment_id": "piControl",
                    "parent_experiment_rip": "r1i1p1",
                    "other_meta": "something",
                },
                {
                    "parent_experiment_id": "piControl",
                    "parent_experiment_rip": "r1i1p1",
                },
            ),
        )
    )
    def test_get_parent_ids(self, data_attributes, expected_ids):
        super().test_get_parent_ids(data_attributes, expected_ids)


class TestAncestryCMIP6(BaseAncestryChecker):
    _project = "CMIP6"

    @pytest.mark.parametrize(
        "data_attributes,expected_ids",
        (
            (
                {
                    "parent_activity_id": "CMIP",
                    "parent_experiment_id": "historical",
                    "parent_mip_era": "CMIP6",
                    "parent_source_id": "UoM",
                    "parent_variant_label": "r1i1p1f1",
                    "other_meta": "something",
                },
                {
                    "parent_activity_id": "CMIP",
                    "parent_experiment_id": "historical",
                    "parent_mip_era": "CMIP6",
                    "parent_source_id": "UoM",
                    "parent_variant_label": "r1i1p1f1",
                },
            ),
            # Test with spaces, an IPSL bug
            # Perhaps not needed given ESMValTool's cleaning of metadata
            # elsewhere
            (
                {
                    "parent_activity_id": "C M I P",
                    "parent_experiment_id": "p i C o n t r o l",
                    "parent_mip_era": "C M I P 6",
                    "parent_source_id": "C N R M - C M6-1-H R",
                    "parent_variant_label": "r 1i1p1f 2",
                },
                {
                    "parent_activity_id": "CMIP",
                    "parent_experiment_id": "piControl",
                    "parent_mip_era": "CMIP6",
                    "parent_source_id": "CNRM-CM6-1-HR",
                    "parent_variant_label": "r1i1p1f2",
                },
            ),
        )
    )
    def test_get_parent_ids(self, data_attributes, expected_ids):
        super().test_get_parent_ids(data_attributes, expected_ids)
