# -*- coding: utf-8 -*-
# !/usr/bin/python
#
# Copyright (c) 2020 Seagate Technology LLC and/or its Affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# For any questions about this software or licensing,
# please email opensource@seagate.com or cortx-questions@seagate.com.
#
"""Module for handling the yaml config and DB config and combine them"""

import os
import logging
from urllib.parse import quote_plus
import yaml
from pymongo import MongoClient
from commons.utils import config_utils
from commons import pswdmanager
from commons.params import SETUPS_FPATH, DB_HOSTNAME, DB_NAME, SYS_INFO_COLLECTION

LOG = logging.getLogger(__name__)

def get_config_yaml(fpath: str) -> dict:
    """Reads the config and decrypts the passwords

    :param fpath: configuration file path
    :return [type]: dictionary containing config data
    """
    with open(fpath) as fin:
        LOG.debug("Reading details from file : %s", fpath)
        data = yaml.safe_load(fin)
        data['end'] = 'end'
        LOG.debug("Decrypting password from file : %s", fpath)
        pswdmanager.decrypt_all_passwd(data)
    return data


def get_config_db(setup_query: dict, drop_id: bool=True):
    """Reads the configuration from the database

    :param setup_query:collection which will be read eg: {"setupname":"automation"}
    """
    sys_coll = _get_collection_obj()
    LOG.debug("Finding the setup details: %s", setup_query)
    cursor = sys_coll.find(setup_query)
    docs = {}
    for doc in cursor:
        if drop_id:
            LOG.debug("IDs fields from MongoDB will be dropped")
            doc.pop('_id')
        if "setupname" in doc.keys():
            LOG.debug("Reading the -- %s --setup details", doc['setupname'])
            docs.update({doc['setupname']: doc})
    return docs


def _get_collection_obj():
    LOG.debug("Database hostname: %s", DB_HOSTNAME)
    LOG.debug("Database name: %s", DB_NAME)
    LOG.debug("Collection name: %s", SYS_INFO_COLLECTION)
    db_creds = pswdmanager.get_secrets(secret_ids=['DB_USER', 'DB_PASSWORD'])
    mongodburi = "mongodb://{0}:{1}@{2}"
    uri = mongodburi.format(
        quote_plus(db_creds['DB_USER']), quote_plus(db_creds['DB_PASSWORD']), DB_HOSTNAME)
    LOG.debug("URI : %s", uri)
    client = MongoClient(uri)
    setup_db = client[DB_NAME]
    collection_obj = setup_db[SYS_INFO_COLLECTION]
    LOG.debug("Collection obj for DB interaction %s", collection_obj)
    return collection_obj


def update_config_db(setup_query: dict, data: dict) -> dict:
    """update the setup details in the database

    :param setup_query: Query for setup eg: {"setupname":"automation"}
    :return [type]:
    """
    sys_coll = _get_collection_obj()
    LOG.debug("Setup query : %s", setup_query)
    LOG.debug("Data to be updated : %s", data)
    rdata = sys_coll.update_many(setup_query, data)
    LOG.debug("Data is updated successfully")
    return rdata


def get_config_wrapper(**kwargs):
    """Get the configuration from the database as well as yaml and merge.
    It is expected that duplicate data should not be present between DB and yaml
    :param target: if targetis given than it will append the target details to the config.
    :param fpath: if fpath is given than it will fetch the details from yaml file
    :param target_key : allows us to fetch smaller portion of the complete yaml file
    :param config_key : allows us to fetch smaller portion of the complete target details
    """
    flag = False
    data = {}
    if "fpath" in kwargs:
        flag = True
        LOG.debug("Reading config from yaml file: %s", kwargs['fpath'])
        config_details = get_config_yaml(fpath=kwargs['fpath'])
        if "config_key" in kwargs:
            config_details = config_details[kwargs["config_key"]]
        data.update(config_details)

    if "target" in kwargs and kwargs['target'] is not None:
        target = kwargs['target']
        flag = True
        if os.path.exists(SETUPS_FPATH):
            LOG.debug("Reading config from setups.json for setup: %s", target)
            setup_details = config_utils.read_content_json(SETUPS_FPATH, mode='rb')[target]
        else:
            setup_query = {"setupname": kwargs['target']}
            LOG.debug("Reading config from DB for setup: %s", target)
            setup_details = get_config_db(setup_query=setup_query)[target]
        if "target_key" in kwargs:
            setup_details = setup_details[kwargs["target_key"]]
        data.update(setup_details)
    if not flag:
        LOG.error("Invalid keyword argument")
        raise ValueError("Invalid argument")
    return data