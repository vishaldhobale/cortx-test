#!/usr/bin/python
# -*- coding: utf-8 -*-
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

"""This file contains test related to Bucket Tagging."""

import os
import time
import logging
import pytest

from commons.ct_fail_on import CTFailOn
from commons.errorcodes import error_handler
from commons.exceptions import CTException
from commons.utils.config_utils import read_yaml
from commons.utils.assert_utils import assert_true
from commons.utils.assert_utils import assert_in
from commons.utils.assert_utils import assert_equal
from commons.utils.assert_utils import assert_is_not_none
from commons.utils.assert_utils import assert_false
from commons.utils.system_utils import make_dirs
from commons.utils.system_utils import path_exists
from commons.utils.system_utils import remove_dirs
from libs.s3.s3_test_lib import S3TestLib
from libs.s3.s3_tagging_test_lib import S3TaggingTestLib

S3_OBJ = S3TestLib()
TAG_OBJ = S3TaggingTestLib()
TEST_CONF = read_yaml("config/s3/test_bucket_tagging.yaml")[1]


class TestBucketTagging():
    """Bucket Tagging Testsuite."""

    @classmethod
    def setup_class(cls):
        """
        Function will be invoked prior to each test case.

        It will perform all prerequisite test suite steps if any.
        """
        cls.log = logging.getLogger(__name__)
        cls.log.info("STARTED: setup test suite operations.")
        cls.test_file = "obj_tag.txt"
        cls.test_dir_path = os.path.join(
            os.getcwd(), "testdata", "buckettagging")
        cls.test_file_path = os.path.join(cls.test_dir_path, cls.test_file)
        if not path_exists(cls.test_dir_path):
            make_dirs(cls.test_dir_path)
            cls.log.info("Created path: %s", cls.test_dir_path)
        cls.log.info("Test file path: %s", cls.test_file_path)
        cls.log.info("ENDED: setup test suite operations.")

    @classmethod
    def teardown_class(cls):
        """
        Function will be invoked after completion of all test case.

        It will clean up resources which are getting created during test suite setup.
        """
        cls.log.info("STARTED: teardown test suite operations.")
        if path_exists(cls.test_dir_path):
            remove_dirs(cls.test_dir_path)
        cls.log.info("Remove test directory: %s", cls.test_dir_path)
        cls.log.info("ENDED: teardown test suite operations.")

    def setup_method(self):
        """Function to perform the clean up if any before each test."""
        self.log.info("STARTED: Test setup operations.")
        resp = S3_OBJ.bucket_list()
        pref_list = [
            each_bucket for each_bucket in resp[1] if each_bucket.startswith(
                TEST_CONF["bucket_tag"]["bkt_name_prefix"])]
        if pref_list:
            self.log.info("Bucket list: %s", pref_list)
            status, resp = S3_OBJ.delete_multiple_buckets(pref_list)
            assert_true(status, resp)
        self.log.info("ENDED: Test setup operations.")

    def teardown_method(self):
        """Function to perform the clean up after each test."""
        self.log.info("STARTED: Test teardown operations.")
        resp = S3_OBJ.bucket_list()
        pref_list = [
            each_bucket for each_bucket in resp[1] if each_bucket.startswith(
                TEST_CONF["bucket_tag"]["bkt_name_prefix"])]
        if pref_list:
            self.log.info("Bucket list: %s", pref_list)
            status, resp = S3_OBJ.delete_multiple_buckets(pref_list)
            assert_true(status, resp)
        self.log.info("ENDED: Test teardown operations.")

    @pytest.mark.s3_ops
    @pytest.mark.tags("TEST-5514")
    @CTFailOn(error_handler)
    def test_2432(self):
        """Verify PUT Bucket tagging."""
        self.log.info("STARTED: Verify PUT Bucket tagging")
        bucket_name = "{}{}".format(TEST_CONF["test_2432"]["bucket_name"],
                                    str(int(time.time())))
        self.log.info("Step 1: Creating a bucket: %s", bucket_name)
        resp = S3_OBJ.create_bucket(bucket_name)
        assert_true(resp[0], resp[1])
        assert_equal(
            resp[1],
            bucket_name,
            resp[1])
        self.log.info("Step 1: Created a bucket: %s ", bucket_name)
        self.log.info("Step 2: Setting tag for bucket")
        resp = TAG_OBJ.set_bucket_tag(
            bucket_name,
            TEST_CONF["test_2432"]["key"],
            TEST_CONF["test_2432"]["value"])
        assert_true(resp[0], resp[1])
        self.log.info("Step 2: Tag is set for bucket")
        self.log.info("Step 3: Retrieving tag of a bucket")
        resp = TAG_OBJ.get_bucket_tags(
            bucket_name)
        assert_true(resp[0], resp[1])
        tag_key = f"{TEST_CONF['test_2432']['key']}{TEST_CONF['test_2432']['tag_id']}"
        tag_value = f"{TEST_CONF['test_2432']['value']}{TEST_CONF['test_2432']['tag_id']}"
        assert_equal(resp[1][0]["Key"], tag_key, tag_key)
        assert_equal(resp[1][0]["Value"], tag_value, tag_value)
        self.log.info("Step 3: Retrieved tag of a bucket")
        self.log.info("ENDED: Verify PUT Bucket tagging")

    @pytest.mark.s3_ops
    @pytest.mark.tags("TEST-5517")
    @CTFailOn(error_handler)
    def test_2433(self):
        """Verify GET Bucket tagging."""
        self.log.info("STARTED: Verify GET Bucket tagging")
        bucket_name = "{}{}".format(TEST_CONF["test_2433"]["bucket_name"],
                                    str(int(time.time())))
        self.log.info("Step 1: Creating a bucket: %s ", bucket_name)
        resp = S3_OBJ.create_bucket(bucket_name)
        assert_true(resp[0], resp[1])
        assert_equal(
            resp[1],
            bucket_name,
            resp[1])
        self.log.info("Step 1: Created a bucket: %s", bucket_name)
        self.log.info("Step 2: Setting tag for a bucket")
        resp = TAG_OBJ.set_bucket_tag(
            bucket_name,
            TEST_CONF["test_2433"]["key"],
            TEST_CONF["test_2433"]["value"])
        assert_true(resp[0], resp[1])
        self.log.info("Step 2: Tag is set for a bucket")
        self.log.info("Step 3: Retrieving tag of a bucket")
        resp = TAG_OBJ.get_bucket_tags(bucket_name)
        assert_true(resp[0], resp[1])
        tag_key = f"{TEST_CONF['test_2433']['key']}{TEST_CONF['test_2433']['tag_id']}"
        tag_value = f"{TEST_CONF['test_2433']['value']}{TEST_CONF['test_2433']['tag_id']}"
        assert_equal(resp[1][0]["Key"], tag_key, tag_key)
        assert_equal(resp[1][0]["Value"], tag_value, tag_value)
        self.log.info("Step 3: Retrieved tag of a bucket")
        self.log.info("ENDED: Verify GET Bucket tagging")

    @pytest.mark.s3_ops
    @pytest.mark.tags("TEST-5519")
    @CTFailOn(error_handler)
    def test_2434(self):
        """Verify DELETE Bucket tagging."""
        self.log.info("STARTED: Verify DELETE Bucket tagging")
        bucket_name = "{}{}".format(TEST_CONF["test_2434"]["bucket_name"],
                                    str(int(time.time())))
        self.log.info("Step 1: Creating a bucket: %s", bucket_name)
        resp = S3_OBJ.create_bucket(bucket_name)
        assert_true(resp[0], resp[1])
        assert_equal(
            resp[1],
            bucket_name,
            resp[1])
        self.log.info("Step 1: Created a bucket: %s ", bucket_name)
        self.log.info("Step 2: Setting tag for a bucket")
        resp = TAG_OBJ.set_bucket_tag(
            bucket_name,
            TEST_CONF["test_2434"]["key"],
            TEST_CONF["test_2434"]["value"])
        assert_true(resp[0], resp[1])
        self.log.info("Step 2: Tag is set for a bucket")
        self.log.info("Step 3: Deleting tag of a bucket")
        resp = TAG_OBJ.delete_bucket_tagging(
            bucket_name)
        assert_true(resp[0], resp[1])
        self.log.info("Step 3: Deleted tag of a bucket")
        self.log.info("Step 4: Retrieving tag of same bucket")
        try:
            resp = TAG_OBJ.get_bucket_tags(bucket_name)
            assert_false(resp[0], resp[1])
        except CTException as error:
            assert_in(
                TEST_CONF["test_2434"]["err_message"], str(
                    error.message), error.message)
        self.log.info(
            "Step 4: Retrieving bucket tag failed with %s",
            TEST_CONF["test_2434"]["err_message"])
        self.log.info("ENDED: Verify DELETE Bucket tagging")

    @pytest.mark.s3_ops
    @pytest.mark.tags("TEST-5533")
    @CTFailOn(error_handler)
    def test_2435(self):
        """Create a tag whose key is up to 128 Unicode characters in length."""
        self.log.info(
            "STARTED: Create a tag whose key is up to 128 Unicode characters in length")
        bucket_name = "{}{}".format(TEST_CONF["test_2435"]["bucket_name"],
                                    str(int(time.time())))
        self.log.info("Step 1: Creating a bucket: %s", bucket_name)
        resp = S3_OBJ.create_bucket(bucket_name)
        assert_true(resp[0], resp[1])
        assert_equal(
            resp[1],
            bucket_name,
            resp[1])
        self.log.info("Step 1: Created a bucket: %s ", bucket_name)
        self.log.info("Step 2: Setting tag for a bucket")
        resp = TAG_OBJ.set_bucket_tag(
            bucket_name,
            TEST_CONF["test_2435"]["key"],
            TEST_CONF["test_2435"]["value"])
        assert_true(resp[0], resp[1])
        self.log.info("Step 2: Tag is set for a bucket")
        self.log.info("Step 2: Retrieving tag of a bucket")
        resp = TAG_OBJ.get_bucket_tags(
            bucket_name)
        assert_true(resp[0], resp[1])
        tag_key = f"{TEST_CONF['test_2435']['key']}{TEST_CONF['test_2435']['tag_id']}"
        tag_value = f"{TEST_CONF['test_2435']['value']}{TEST_CONF['test_2435']['tag_id']}"
        assert_equal(resp[1][0]["Key"], tag_key, tag_key)
        assert_equal(resp[1][0]["Value"], tag_value, tag_value)
        self.log.info("Step 2: Retrieved tag of a bucket")
        self.log.info(
            "ENDED: Create a tag whose key is up to 128 Unicode characters in length")

    @pytest.mark.s3_ops
    @pytest.mark.tags("TEST-5534")
    @CTFailOn(error_handler)
    def test_2436(self):
        """
        Create a tag whose key is more than 128 Unicode characters in length.

        This is negative testing
        """
        self.log.info(
            "STARTED: Create a tag whose key is more than 128 Unicode characters in length")
        bucket_name = "{}{}".format(TEST_CONF["test_2436"]["bucket_name"],
                                    str(int(time.time())))
        self.log.info("Step 1: Creating a bucket: %s", bucket_name)
        resp = S3_OBJ.create_bucket(bucket_name)
        assert_true(resp[0], resp[1])
        assert_equal(
            resp[1],
            bucket_name,
            resp[1])
        self.log.info("Step 1: Created a bucket: %s", bucket_name)
        self.log.info("Step 2: Setting tag for a bucket")
        try:
            resp = TAG_OBJ.set_bucket_tag(
                bucket_name,
                TEST_CONF["test_2436"]["key"],
                TEST_CONF["test_2436"]["value"])
            assert_false(resp[0], resp[1])
        except CTException as error:
            assert_in(
                TEST_CONF["test_2436"]["err_message"], str(
                    error.message), error.message)
        self.log.info(
            "Step 2: Setting tag for a bucket failed with %s",
            TEST_CONF["test_2436"]["err_message"])
        self.log.info(
            "ENDED: Create a tag whose key is more than 128 Unicode characters in length")

    @pytest.mark.s3_ops
    @pytest.mark.tags("TEST-5535")
    @CTFailOn(error_handler)
    def test_2437(self):
        """Create a tag having values up to 256 Unicode characters in length."""
        self.log.info(
            "STARTED: Create a tag having values up to 256 Unicode characters in length")
        bucket_name = "{}{}".format(TEST_CONF["test_2437"]["bucket_name"],
                                    str(int(time.time())))
        self.log.info("Step 1: Creating a bucket: %s", bucket_name)
        resp = S3_OBJ.create_bucket(bucket_name)
        assert_true(resp[0], resp[1])
        assert_equal(
            resp[1],
            bucket_name,
            resp[1])
        self.log.info("Step 1: Created a bucket: %s", bucket_name)
        self.log.info("Step 2: Setting tag for a bucket")
        resp = TAG_OBJ.set_bucket_tag(
            bucket_name,
            TEST_CONF["test_2437"]["key"],
            TEST_CONF["test_2437"]["value"])
        assert_true(resp[0], resp[1])
        self.log.info("Step 2: Tag is set for a bucket")
        self.log.info("Step 3: Retrieving tag of a bucket")
        resp = TAG_OBJ.get_bucket_tags(bucket_name)
        assert_true(resp[0], resp[1])
        tag_key = f"{TEST_CONF['test_2437']['key']}{TEST_CONF['test_2437']['tag_id']}"
        tag_value = f"{TEST_CONF['test_2437']['value']}{TEST_CONF['test_2437']['tag_id']}"
        assert_equal(resp[1][0]["Key"], tag_key, tag_key)
        assert_equal(resp[1][0]["Value"], tag_value, tag_value)
        self.log.info("Step 3: Retrieved tag of a bucket")
        self.log.info(
            "ENDED: Create a tag having values up to 256 Unicode characters in length")

    @pytest.mark.s3_ops
    @pytest.mark.tags("TEST-5536")
    @CTFailOn(error_handler)
    def test_2438(self):
        """
        Create a tag having values more than 512 Unicode characters in length.

        info - This is negative testing
        """
        self.log.info(
            "STARTED: Create a tag having values more than 512 Unicode characters in length")
        bucket_name = "{}{}".format(TEST_CONF["test_2438"]["bucket_name"],
                                    str(int(time.time())))
        self.log.info("Step 1: Creating a bucket: %s", bucket_name)
        resp = S3_OBJ.create_bucket(bucket_name)
        assert_true(resp[0], resp[1])
        assert_equal(
            resp[1],
            bucket_name,
            resp[1])
        self.log.info("Step 1: Created a bucket: %s", bucket_name)
        self.log.info("Step 2: Setting tag for a bucket")
        try:
            resp = TAG_OBJ.set_bucket_tag(
                bucket_name,
                TEST_CONF["test_2438"]["key"],
                TEST_CONF["test_2438"]["value"])
            assert_false(resp[0], resp[1])
        except CTException as error:
            assert_in(
                TEST_CONF["test_2438"]["err_message"], str(
                    error.message), error.message)
        self.log.info(
            "Step 2: Setting tag for a bucket failed with %s", bucket_name)
        self.log.info(
            "ENDED: Create a tag having values more than 512 Unicode characters in length")

    @pytest.mark.s3_ops
    @pytest.mark.tags("TEST-5528")
    @CTFailOn(error_handler)
    def test_2439(self):
        """Create Bucket tags, up to 50."""
        self.log.info("STARTED: Create Bucket tags, up to 50")
        bucket_name = "{}{}".format(TEST_CONF["test_2439"]["bucket_name"],
                                    str(int(time.time())))
        self.log.info("Step 1: Creating a bucket: %s", bucket_name)
        resp = S3_OBJ.create_bucket(bucket_name)
        assert_true(resp[0], resp[1])
        assert_equal(
            resp[1],
            bucket_name,
            resp[1])
        self.log.info("Step 1: Created a bucket: %s", bucket_name)
        self.log.info("Step 2: Setting %s tags for a bucket", bucket_name)
        resp = TAG_OBJ.set_bucket_tag(
            bucket_name,
            TEST_CONF["test_2439"]["key"],
            TEST_CONF["test_2439"]["value"],
            TEST_CONF["test_2439"]["tag_count"])
        assert_true(resp[0], resp[1])
        self.log.info(
            "Step 2: %d tags are set for a bucket",
            TEST_CONF["test_2439"]["tag_count"])
        self.log.info("Step 3: Retrieving tags of a bucket")
        resp = TAG_OBJ.get_bucket_tags(bucket_name)
        sorted_tags = sorted(resp[1], key=lambda x: int(
            x["Key"][len(TEST_CONF["test_2439"]["key"]):]))
        self.log.info(sorted_tags)
        assert_true(resp[0], resp[1])
        for num in range(TEST_CONF["test_2439"]["tag_count"]):
            tag_key = f"{TEST_CONF['test_2439']['key']}{num}"
            tag_value = f"{TEST_CONF['test_2439']['value']}{num}"
            assert_equal(sorted_tags[num]["Key"], tag_key, tag_key)
            assert_equal(sorted_tags[num]["Value"], tag_value, tag_value)
        self.log.info("Step 3: Retrieved tags of a bucket")
        self.log.info("ENDED: Create Bucket tags, up to 50")

    @pytest.mark.s3_ops
    @pytest.mark.tags("TEST-5529")
    @CTFailOn(error_handler)
    def test_2440(self):
        """Create Bucket tags, more than 50."""
        self.log.info("STARTED: Create Bucket tags, more than 50")
        bucket_name = "{}{}".format(TEST_CONF["test_2440"]["bucket_name"],
                                    str(int(time.time())))
        self.log.info("Step 1: Creating a bucket: %s", bucket_name)
        resp = S3_OBJ.create_bucket(bucket_name)
        assert_true(resp[0], resp[1])
        assert_equal(
            resp[1],
            bucket_name,
            resp[1])
        self.log.info("Step 1: Created a bucket: %s", bucket_name)
        self.log.info(
            "Step 2: Setting %d tags for a bucket",
            TEST_CONF["test_2440"]["tag_count"])
        try:
            resp = TAG_OBJ.set_bucket_tag(
                bucket_name,
                TEST_CONF["test_2440"]["key"],
                TEST_CONF["test_2440"]["value"],
                TEST_CONF["test_2440"]["tag_count"])
            assert_false(resp[0], resp[1])
        except CTException as error:
            assert_in(
                TEST_CONF["test_2440"]["err_message"], str(
                    error.message), error.message)
        self.log.info(
            "Setting %d tags for a bucket failed with %s",
            TEST_CONF["test_2440"]["tag_count"],
            TEST_CONF["test_2440"]["err_message"])
        self.log.info("ENDED: Create Bucket tags, more than 50")

    @pytest.mark.s3_ops
    @pytest.mark.tags("TEST-5521")
    @CTFailOn(error_handler)
    def test_2441(self):
        """Verify bucket Tag Keys with case sensitive labels."""
        self.log.info(
            "STARTED: Verify bucket Tag Keys with case sensitive labels")
        bucket_name = "{}{}".format(TEST_CONF["test_2441"]["bucket_name"],
                                    str(int(time.time())))
        self.log.info("Step 1: Creating a bucket: %s", bucket_name)
        resp = S3_OBJ.create_bucket(bucket_name)
        assert_true(resp[0], resp[1])
        assert_equal(
            resp[1],
            bucket_name,
            resp[1])
        self.log.info("Step 1: Created a bucket: %s", bucket_name)
        self.log.info(
            "Step 2 : Setting tag for a bucket with case sensitive tag keys")
        resp = TAG_OBJ.set_bucket_tag(
            bucket_name,
            TEST_CONF["test_2441"]["key"],
            TEST_CONF["test_2441"]["value"])
        assert_true(resp[0], resp[1])
        self.log.info(
            "Step 2 : Tag is set for a bucket with case sensitive tag keys")
        self.log.info("Step 3: Retrieving tag of a bucket")
        resp = TAG_OBJ.get_bucket_tags(
            bucket_name)
        assert_true(resp[0], resp[1])
        tag_key = f"{TEST_CONF['test_2441']['key']}{TEST_CONF['test_2441']['tag_id']}"
        tag_value = f"{TEST_CONF['test_2441']['value']}{TEST_CONF['test_2441']['tag_id']}"
        assert_equal(resp[1][0]["Key"], tag_key, tag_key)
        assert_equal(resp[1][0]["Value"], tag_value, tag_value)
        self.log.info("Step 3: Retrieved tag of a bucket")
        self.log.info(
            "ENDED: Verify bucket Tag Keys with case sensitive labels")

    @pytest.mark.s3_ops
    @pytest.mark.tags("TEST-5520")
    @CTFailOn(error_handler)
    def test_2442(self):
        """Verify bucket tag Values with case sensitive labels."""
        self.log.info(
            "STARTED: Verify bucket tag Values with case sensitive labels")
        bucket_name = "{}{}".format(TEST_CONF["test_2442"]["bucket_name"],
                                    str(int(time.time())))
        self.log.info("Step 1: Creating a bucket: %s", bucket_name)
        resp = S3_OBJ.create_bucket(bucket_name)
        assert_true(resp[0], resp[1])
        assert_equal(
            resp[1],
            bucket_name,
            resp[1])
        self.log.info("Step 1: Created a bucket: %s", bucket_name)
        self.log.info(
            "Step 2: Setting tag for a bucket with case sensitive tag values")
        resp = TAG_OBJ.set_bucket_tag(
            bucket_name,
            TEST_CONF["test_2442"]["key"],
            TEST_CONF["test_2442"]["value"])
        assert_true(resp[0], resp[1])
        self.log.info(
            "Step 2: Tag is set for a bucket with case sensitive tag values")
        self.log.info("Step 3: Retrieving tag of a bucket")
        resp = TAG_OBJ.get_bucket_tags(bucket_name)
        assert_true(resp[0], resp[1])
        tag_key = f"{TEST_CONF['test_2442']['key']}{TEST_CONF['test_2442']['tag_id']}"
        tag_value = f"{TEST_CONF['test_2442']['value']}{TEST_CONF['test_2442']['tag_id']}"
        assert_equal(resp[1][0]["Key"], tag_key, tag_key)
        assert_equal(resp[1][0]["Value"], tag_value, tag_value)
        self.log.info("Step 3: Retrieved tag of a bucket")
        self.log.info(
            "ENDED: Verify bucket tag Values with case sensitive labels")

    @pytest.mark.s3_ops
    @pytest.mark.tags("TEST-5526")
    @CTFailOn(error_handler)
    def test_2443(self):
        """Create multiple tags with tag keys having special characters."""
        self.log.info(
            "STARTED: Create multiple tags with tag keys having special characters")
        bucket_name = "{}{}".format(TEST_CONF["test_2443"]["bucket_name"],
                                    str(int(time.time())))
        self.log.info("Step 1: Creating a bucket: %s", bucket_name)
        resp = S3_OBJ.create_bucket(bucket_name)
        assert_true(resp[0], resp[1])
        assert_equal(
            resp[1],
            bucket_name,
            resp[1])
        self.log.info("Step 1: Created a bucket: %s", bucket_name)
        self.log.info(
            "Step 2: Setting multiple tags with tag keys having special characters")
        for char in TEST_CONF["test_2443"]["spl_chars_list"]:
            tag_key = "{0}{1}{2}".format(
                char, TEST_CONF["test_2443"]["key"], char)
            resp = TAG_OBJ.set_bucket_tag(
                bucket_name,
                tag_key,
                TEST_CONF["test_2443"]["value"])
            assert_true(resp[0], resp[1])
            resp = TAG_OBJ.get_bucket_tags(bucket_name)
            assert_true(resp[0], resp[1])
            updated_key = f"{tag_key}{TEST_CONF['test_2443']['tag_id']}"
            updated_val = f"{TEST_CONF['test_2443']['value']}{TEST_CONF['test_2443']['tag_id']}"
            assert_equal(resp[1][0]["Key"], updated_key, updated_key)
            assert_equal(resp[1][0]["Value"], updated_val, updated_val)
        self.log.info(
            "Step 2: Set multiple tags with tag keys having special characters")
        self.log.info(
            "ENDED: Create multiple tags with tag keys having special characters")

    @pytest.mark.s3_ops
    @pytest.mark.tags("TEST-5527")
    @CTFailOn(error_handler)
    def test_2444(self):
        """Create multiple tags with tag keys having invalid special characters."""
        self.log.info(
            "STARTED: Create multiple tags with tag keys having invalid special characters")
        bucket_name = "{}{}".format(TEST_CONF["test_2444"]["bucket_name"],
                                    str(int(time.time())))
        self.log.info("Step 1: Creating a bucket %s", bucket_name)
        resp = S3_OBJ.create_bucket(bucket_name)
        assert_true(resp[0], resp[1])
        assert_equal(resp[1],
                     bucket_name,
                     resp[1])
        self.log.info("Step 1: Created a bucket %s", bucket_name)
        self.log.info(
            "Step 2: Setting tags for a bucket with tag keys having invalid special characters")
        for char in TEST_CONF["test_2444"]["spl_chars_list"]:
            key = "{0}{1}{2}".format(
                char, TEST_CONF["test_2444"]["key"], char)
            try:
                resp = TAG_OBJ.set_bucket_tag(
                    bucket_name,
                    key,
                    TEST_CONF["test_2444"]["value"])
                assert_false(resp[0], resp[1])
            except CTException as error:
                assert_in(
                    TEST_CONF["test_2444"]["err_message"], str(
                        error.message), error.message)
        self.log.info("Step 2: Could not set tags for a bucket with tag keys "
                      "having invalid special characters")
        self.log.info("ENDED: Create multiple tags with tag keys having"
                      " invalid special characters")

    @pytest.mark.s3_ops
    @pytest.mark.tags("TEST-5524")
    @CTFailOn(error_handler)
    def test_2445(self):
        """Create multiple tags with tag values having invalid special character."""
        self.log.info("STARTED: Create multiple tags with tag values having "
                      "invalid special character")
        bucket_name = "{}{}".format(TEST_CONF["test_2445"]["bucket_name"],
                                    str(int(time.time())))
        self.log.info("Step 1: Creating a bucket %s", bucket_name)
        resp = S3_OBJ.create_bucket(bucket_name)
        assert_true(resp[0], resp[1])
        assert_equal(
            resp[1],
            bucket_name,
            resp[1])
        self.log.info("Step 1: Created a bucket %s", bucket_name)
        self.log.info("Step 2: Setting multiple tags with tag values having "
                      "invalid special character")
        for char in TEST_CONF["test_2445"]["spl_chars_list"]:
            value = "{0}{1}{2}".format(
                char, TEST_CONF["test_2445"]["value"], char)
            try:
                resp = TAG_OBJ.set_bucket_tag(
                    bucket_name,
                    TEST_CONF["test_2445"]["key"],
                    value)
                assert_false(resp[0], resp[1])
            except CTException as error:
                assert_in(
                    TEST_CONF["test_2445"]["err_message"], str(
                        error.message), error.message)
        self.log.info("Step 2: Could not set multiple tags with tag values"
                      " having invalid special character")
        self.log.info("ENDED: Create multiple tags with tag values having "
                      "invalid special character")

    @pytest.mark.s3_ops
    @pytest.mark.tags("TEST-5531")
    @CTFailOn(error_handler)
    def test_2446(self):
        """Create bucket tags with duplicate keys."""
        self.log.info("STARTED: Create bucket tags with duplicate keys")
        bucket_name = "{}{}".format(TEST_CONF["test_2446"]["bucket_name"],
                                    str(int(time.time())))
        self.log.info("Step 1: Creating a bucket: %s", bucket_name)
        resp = S3_OBJ.create_bucket(bucket_name)
        assert_true(resp[0], resp[1])
        assert_equal(
            resp[1],
            bucket_name,
            resp[1])
        self.log.info("Step 1: Created a bucket: %s", bucket_name)
        self.log.info("Step 2: Setting bucket tags with duplicate keys")
        try:
            resp = TAG_OBJ.set_bucket_tag_duplicate_keys(
                bucket_name,
                TEST_CONF["test_2446"]["key"],
                TEST_CONF["test_2446"]["value"])
            assert_false(resp[0], resp[1])
        except CTException as error:
            assert_in(
                TEST_CONF["test_2446"]["err_message"], str(
                    error.message), error.message)
        self.log.info(
            "Step 2: Setting bucket tags with duplicate keys failed with %s",
            TEST_CONF["test_2446"]["err_message"])
        self.log.info("ENDED: Create bucket tags with duplicate keys")

    @pytest.mark.s3_ops
    @pytest.mark.tags("TEST-5512")
    @CTFailOn(error_handler)
    def test_2447(self):
        """verify values in a tag set should be unique."""
        self.log.info("STARTED: verify values in a tag set should be unique")
        bucket_name = "{}{}".format(TEST_CONF["test_2447"]["bucket_name"],
                                    str(int(time.time())))
        self.log.info("Step 1: Creating a bucket %s", bucket_name)
        resp = S3_OBJ.create_bucket(bucket_name)
        assert_true(resp[0], resp[1])
        assert_equal(
            resp[1],
            bucket_name,
            resp[1])
        self.log.info("Step 1: Created a bucket %s", bucket_name)
        self.log.info("Step 2: Setting bucket tags with unique tag values")
        resp = TAG_OBJ.set_bucket_tag(
            bucket_name,
            TEST_CONF["test_2447"]["key"],
            TEST_CONF["test_2447"]["value"],
            TEST_CONF["test_2447"]["tag_count"])
        assert_true(resp[0], resp[1])
        resp = TAG_OBJ.set_bucket_tag(
            bucket_name,
            TEST_CONF["test_2447"]["key"],
            TEST_CONF["test_2447"]["value"],
            TEST_CONF["test_2447"]["tag_count"])
        assert_true(resp[0], resp[1])
        self.log.info("Step 2: Set bucket tags with unique tag values")
        self.log.info("Step 3: Retrieving tag of a bucket")
        resp = TAG_OBJ.get_bucket_tags(bucket_name)
        assert_true(resp[0], resp[1])
        for num in range(TEST_CONF["test_2447"]["tag_count"]):
            updated_key = f"{TEST_CONF['test_2447']['key']}{num}"
            updated_val = f"{TEST_CONF['test_2447']['value']}{num}"
            assert_equal(resp[1][num]["Key"], updated_key, updated_key)
            assert_equal(resp[1][num]["Value"], updated_val, updated_val)
        self.log.info("Step 3: Retrieved tag of a bucket")
        self.log.info("ENDED: verify values in a tag set should be unique")

    @pytest.mark.s3_ops
    @pytest.mark.tags("TEST-5530")
    @CTFailOn(error_handler)
    def test_2448(self):
        """Create bucket tags with invalid special characters."""
        self.log.info("STARTED: Create bucket tags with invalid "
                      "(characters outside the allowed set) special characters")
        bucket_name = "{}{}".format(TEST_CONF["test_2448"]["bucket_name"],
                                    str(int(time.time())))
        self.log.info("Step 1: Creating a bucket %s", bucket_name)
        resp = S3_OBJ.create_bucket(bucket_name)
        assert_true(resp[0], resp[1])
        assert_equal(
            bucket_name,
            resp[1])
        self.log.info("Step 1: Created a bucket %s", bucket_name)
        self.log.info(
            "Step 2: Setting a bucket tag with invalid special characters")
        resp = TAG_OBJ.set_bucket_tag_invalid_char(
            bucket_name,
            TEST_CONF["test_2448"]["key"],
            TEST_CONF["test_2448"]["value"])
        assert_true(resp[0], resp[1])
        self.log.info(
            "Step 2: Set a bucket tag with invalid special characters")
        self.log.info("Step 3: Retrieving tag of a bucket")
        resp = TAG_OBJ.get_bucket_tags(bucket_name)
        assert_true(resp[0], resp[1])
        self.log.info("Step 3: Retrieved tag of a bucket")
        self.log.info("ENDED: Create bucket tags with invalid "
                      "(characters outside the allowed set) special characters")

    @pytest.mark.s3_ops
    @pytest.mark.tags("TEST-5523")
    @CTFailOn(error_handler)
    def test_2449(self):
        """Delete Bucket having tags associated with Bucket and its Objects."""
        self.log.info(
            "STARTED: Delete Bucket having tags associated with Bucket and its Objects")
        bucket_name = "{}{}".format(TEST_CONF["test_2449"]["bucket_name"],
                                    str(int(time.time())))
        obj_name = "{}{}".format(TEST_CONF["test_2449"]["obj_name"],
                                 str(int(time.time())))
        self.log.info(
            "Step 1: Creating a bucket %s and uploading an object %s",
            bucket_name, obj_name)
        resp = S3_OBJ.create_bucket_put_object(
            bucket_name,
            obj_name,
            self.test_file_path,
            TEST_CONF["test_2449"]["mb_count"])
        assert_true(resp[0], resp[1])
        self.log.info(
            "Step 1:  Created a bucket %s and uploaded an object %s",
            bucket_name, obj_name)
        self.log.info(
            "Step 2: Setting tag for a bucket %s", bucket_name)
        resp = TAG_OBJ.set_bucket_tag(
            bucket_name,
            TEST_CONF["test_2449"]["bkt_key"],
            TEST_CONF["test_2449"]["bkt_value"])
        assert_true(resp[0], resp[1])
        self.log.info(
            "Step 2: Tag is set for a bucket %s", bucket_name)
        self.log.info("Step 3: Setting tag for an object %s", obj_name)
        resp = TAG_OBJ.set_object_tag(
            bucket_name,
            obj_name,
            TEST_CONF["test_2449"]["obj_key"],
            TEST_CONF["test_2449"]["obj_value"],
            tag_count=TEST_CONF["test_2449"]["obj_tags"])
        assert_true(resp[0], resp[1])
        self.log.info("Step 3: Set tag for an object %s", obj_name)
        self.log.info("Step 4: Verifying tag is set for a bucket")
        resp = TAG_OBJ.get_bucket_tags(bucket_name)
        assert_true(resp[0], resp[1])
        tag_key = f"{TEST_CONF['test_2449']['bkt_key']}{TEST_CONF['test_2449']['bkt_tag'] - 1}"
        tag_value = f"{TEST_CONF['test_2449']['bkt_value']}{TEST_CONF['test_2449']['bkt_tag'] - 1}"
        assert_equal(resp[1][0]["Key"], tag_key, tag_key)
        assert_equal(resp[1][0]["Value"], tag_value, tag_value)
        self.log.info(
            "Step 4: Verified that tag is set for a bucket successfully")
        self.log.info("Step 5: Verifying tag is set for an object")
        resp = TAG_OBJ.get_object_tags(bucket_name, obj_name)
        assert_true(resp[0], resp[1])
        for num in range(TEST_CONF["test_2449"]["obj_tags"]):
            tag_key = f"{TEST_CONF['test_2449']['obj_key']}{num}"
            tag_val = f"{TEST_CONF['test_2449']['obj_value']}{num}"
            assert_equal(resp[1][num]["Key"], tag_key, tag_key)
            assert_equal(resp[1][num]["Value"], tag_val, tag_val)
        self.log.info("Step 5: Verified tag is set for an object")
        self.log.info("Step 6: Deleting a bucket")
        resp = S3_OBJ.delete_bucket(bucket_name, force=True)
        assert_true(resp[0], resp[1])
        self.log.info("Step 7: Retrieving tag of a bucket")
        try:
            resp = TAG_OBJ.get_bucket_tags(bucket_name)
            assert_false(resp[0], resp[1])
        except CTException as error:
            assert_in(
                TEST_CONF["test_2449"]["err_message"], str(
                    error.message), error.message)
        self.log.info(
            "Step 7: Retrieving tag of a bucket failed with %s",
            TEST_CONF["test_2449"]["err_message"])
        self.log.info("Step 8: Retrieving tag of an object")
        try:
            resp = TAG_OBJ.get_object_tags(bucket_name, obj_name)
            assert_false(resp[0], resp[1])
        except CTException as error:
            assert_in(
                TEST_CONF["test_2449"]["err_message"], str(
                    error.message), error.message)
        self.log.info(
            "Step 8: Retrieving tag of an object failed with %s",
            TEST_CONF["test_2449"]["err_message"])
        self.log.info(
            "ENDED: Delete Bucket having tags associated with Bucket and its Objects")

    # Raised bug EOS-2528, Uncomment when fixed
    @pytest.mark.s3_ops
    @pytest.mark.tags("TEST-5522")
    @CTFailOn(error_handler)
    def test_2450(self):
        """Verify user can create max no of buckets with max no of tags per bucket."""
        self.log.info("STARTED: Verification of max. no. of Buckets user"
                      " can create with max no. of tags per Bucket")
        for i in range(TEST_CONF["test_2450"]["bucket_count"]):
            bucket_name = "{}{}{}".format(TEST_CONF["test_2450"]["bucket_name"],
                                          str(i), str(int(time.time())))
            resp = S3_OBJ.create_bucket(bucket_name)
            assert_is_not_none(resp[0], resp[1])
            assert_equal(bucket_name, resp[1], resp[1])
        buckets = S3_OBJ.bucket_list()[1]
        key = TEST_CONF["test_2450"]["key"]
        value = TEST_CONF["test_2450"]["value"]
        tag_count = TEST_CONF["test_2450"]["tag_count"]
        for bucket in buckets:
            resp = TAG_OBJ.set_bucket_tag(bucket, key, value, tag_count)
            assert_is_not_none(resp[0], resp[1])
            resp = TAG_OBJ.get_bucket_tags(bucket)
            assert_is_not_none(resp[0], resp[1])
        self.log.debug(buckets)
        self.log.debug("Total buckets : %d", len(buckets))
        self.log.info("ENDED: Verification of max. no. of Buckets user can "
                      "create with max no. of tags per Bucket")

    @pytest.mark.s3_ops
    @pytest.mark.tags("TEST-5513")
    @CTFailOn(error_handler)
    def test_2451(self):
        """Verify PUT bucket tagging to non-existing bucket."""
        self.log.info(
            "STARTED: Verify PUT bucket tagging to non-existing bucket")
        self.log.info(
            "Step 1: Setting a tag for non existing bucket: %s",
            TEST_CONF["test_2451"]["bucket_name"])
        try:
            resp = TAG_OBJ.set_bucket_tag(
                TEST_CONF["test_2451"]["bucket_name"],
                TEST_CONF["test_2451"]["key"],
                TEST_CONF["test_2451"]["value"])
            assert_false(resp[0], resp[1])
        except CTException as error:
            assert_in(
                TEST_CONF["test_2451"]["err_message"], str(
                    error.message), error.message)
        self.log.info(
            "Step 1: Setting a tag for non existing bucket failed with: %s",
            TEST_CONF["test_2451"]["err_message"])
        self.log.info(
            "ENDED: Verify PUT bucket tagging to non-existing bucket")

    @pytest.mark.s3_ops
    @pytest.mark.tags("TEST-5516")
    @CTFailOn(error_handler)
    def test_2452(self):
        """verify GET bucket tagging to non-existing bucket."""
        self.log.info(
            "STARTED: Verify GET bucket tagging to non-existing bucket")
        self.log.info("Step 1: Setting a tag for non existing bucket")
        try:
            resp = TAG_OBJ.set_bucket_tag(
                TEST_CONF["test_2452"]["bucket_name"],
                TEST_CONF["test_2452"]["key"],
                TEST_CONF["test_2452"]["value"])
            assert_false(resp[0], resp[1])
        except CTException as error:
            assert_in(
                TEST_CONF["test_2452"]["err_message"], str(
                    error.message), error.message)
        self.log.info(
            "Step 1: Setting a tag for non existing bucket failed with %s",
            TEST_CONF["test_2452"]["err_message"])
        self.log.info("Step 2: Retrieving tag of non existing bucket")
        try:
            resp = TAG_OBJ.get_bucket_tags(
                TEST_CONF["test_2452"]["bucket_name"])
            assert_false(resp[0], resp[1])
        except CTException as error:
            assert_in(
                TEST_CONF["test_2452"]["err_message"], str(
                    error.message), error.message)
        self.log.info(
            "Step 2: Retrieved tag of non existing bucket failed with %s",
            TEST_CONF["test_2452"]["err_message"])
        self.log.info(
            "ENDED: Verify GET bucket tagging to non-existing bucket")

    @pytest.mark.s3_ops
    @pytest.mark.tags("TEST-5518")
    @CTFailOn(error_handler)
    def test_2453(self):
        """verify DELETE bucket tagging to non-existing bucket."""
        self.log.info(
            "STARTED: Verify DELETE bucket tagging to non-existing bucket")
        self.log.info("Step 1: Setting tag for non existing bucket")
        try:
            resp = TAG_OBJ.set_bucket_tag(
                TEST_CONF["test_2453"]["bucket_name"],
                TEST_CONF["test_2453"]["key"],
                TEST_CONF["test_2453"]["value"])
            assert_false(resp[0], resp[1])
        except CTException as error:
            assert_in(
                TEST_CONF["test_2453"]["err_message"], str(
                    error.message), error.message)
        self.log.info("Step 1: Setting tag for non existing bucket failed")
        self.log.info("Step 2: Deleting tag of a non existing bucket")
        try:
            resp = TAG_OBJ.delete_bucket_tagging(
                TEST_CONF["test_2453"]["bucket_name"])
            assert_false(resp[0], resp[1])
        except CTException as error:
            assert_in(
                TEST_CONF["test_2453"]["err_message"], str(
                    error.message), error.message)
        self.log.info(
            "Step 2: Deleting tag of a non existing bucket failed with %s",
            TEST_CONF["test_2453"]["err_message"])
        self.log.info(
            "ENDED: Verify DELETE bucket tagging to non-existing bucket")