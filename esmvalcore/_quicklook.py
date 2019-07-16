"""
Creates recipes for EMAC simulation.

"""

import datetime
import glob
import logging
import os
import re
from pathlib import Path, PurePath

import yaml

from ._config import (get_project_config, read_config_developer_file,
                      read_config_user_file)

logger = logging.getLogger(__name__)


def create_recipe(cfg):
    start = cfg['quicklook'].get('start')
    end = cfg['quicklook'].get('end')
    # TODO: We should rename "recipes" to "diagnostics" in this context
    recipes = cfg['quicklook'].get('recipes')
    run_id = cfg['quicklook'].get('dataset-id')
    output_dir = os.path.join(cfg['quicklook'].get('output_dir'), run_id)
    recipe_dir = cfg['quicklook'].get('recipe_dir')

    logger.debug("Creating directory %s", output_dir)
    os.makedirs(output_dir, exist_ok=True)
    all_diagnostics = dict()
    for recipe in recipes:
        recipe_name = 'diagnostics_{0}.yml'.format(recipe)
        with open(os.path.join(recipe_dir, recipe_name)) as stream:
            all_diagnostics = {
                **all_diagnostics,
                **yaml.load(stream, Loader=yaml.FullLoader).get('diagnostics')
            }
    with open(os.path.join(recipe_dir, 'general.yml')) as stream:
        out = {**yaml.load(stream, Loader=yaml.FullLoader)}

    out['diagnostics'] = d
    out['datasets'] = [{
        'dataset': 'EMAC',
        'project': 'EMAC',
        'exp': run_id,
        'start_year': start,
        'end_year': end
    }]
    path_to_recipe = os.path.join(output_dir, 'recipe_quicklook.yml')
    with open(path_to_recipe, 'w') as stream:
        logger.debug("Writing %s to  %s", recipe_name, output_dir)
        stream.write(yaml.dump(out))
    return path_to_recipe
