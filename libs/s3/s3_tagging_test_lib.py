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
#
#

"""
Python library contains methods which allows you to perform bucket tagging operations using boto3.
"""

import os
import base64
import logging

from commons import errorcodes as err
from commons.exceptions import CTException
from commons.utils.config_utils import read_yaml
from commons.helpers.s3_helper import S3Helper
from commons.utils.system_utils import create_file
from libs.s3.s3_core_lib import Tagging

try:
    s3hobj = S3Helper()
except ImportError as err:
    s3hobj = S3Helper.get_instance()

S3_CONF = read_yaml("config/s3/s3_config.yaml")[1]
LOGGER = logging.getLogger(__name__)


class S3TaggingTestLib(Tagging):
    """
    This Class initialising s3 connection and including methods for bucket and
    object tagging operations.
    """

    def __init__(self,
                 access_key: str = s3hobj.get_local_keys()[0],
                 secret_key: str = s3hobj.get_local_keys()[1],
                 endpoint_url: str = S3_CONF["s3_url"],
                 s3_cert_path: str = S3_CONF["s3_cert_path"],
                 region: str = S3_CONF["region"],
                 aws_session_token: str = None,
                 debug: bool = S3_CONF["debug"]) -> None:
        """
        This method initializes members of S3TaggingTestLib and its parent class.
        :param access_key: access key.
        :param secret_key: secret key.
        :param endpoint_url: endpoint url.
        :param s3_cert_path: s3 certificate path.
        :param region: region.
        :param aws_session_token: aws_session_token.
        :param debug: debug mode.
        """
        super().__init__(
            access_key,
            secret_key,
            endpoint_url,
            s3_cert_path,
            region,
            aws_session_token,
            debug)

    def set_bucket_tag(
            self,
            bucket_name: str,
            key: str,
            value: str,
            tag_count: int = 1) -> tuple:
        """
        Set one or multiple tags to a bucket.
        :param bucket_name: Name of the bucket.
        :param key: Key for bucket tagging.
        :param value: Value for bucket tagging.
        :param tag_count: Tag count.
        :return: (Boolean, response)
        """
        LOGGER.info("Set bucket tagging")
        try:
            tag_set = list()
            for num in range(tag_count):
                tag = dict()
                tag.update([("Key", "{}{}".format(key, str(num))),
                            ("Value", "{}{}".format(value, str(num)))])
                tag_set.append(tag)
            LOGGER.debug(tag_set)
            response = super().set_bucket_tags(
                bucket_name, tag_set={'TagSet': tag_set})
            LOGGER.info(response)
        except BaseException as error:
            LOGGER.error("Error in %s: %s",
                         S3TaggingTestLib.set_bucket_tag.__name__,
                         error)
            raise CTException(err.S3_CLIENT_ERROR, error.args[0])

        return True, response

    def get_bucket_tags(self, bucket_name: str) -> tuple:
        """
        List all bucket tags if any.
        :param bucket_name: Name of the bucket.
        :return: (Boolean, list of tags)
        """
        try:
            LOGGER.info("Getting bucket tagging")
            bucket_tagging = self.get_bucket_tagging(bucket_name)
            LOGGER.debug(bucket_tagging)
            tag_set = bucket_tagging["TagSet"]
            for tag in tag_set:
                LOGGER.info(tag)
        except BaseException as error:
            LOGGER.error("Error in %s: %s",
                         S3TaggingTestLib.get_bucket_tags.__name__,
                         error)
            raise CTException(err.S3_CLIENT_ERROR, error.args[0])

        return True, tag_set

    def delete_bucket_tagging(self, bucket_name: str) -> tuple:
        """
        Delete all bucket tags.
        :param bucket_name: Name of the bucket.
        :return: (Boolean, response).
        """
        try:
            LOGGER.info("Deleting bucket tagging")
            response = super().delete_bucket_tagging(bucket_name)
            LOGGER.info(response)
        except BaseException as error:
            LOGGER.error("Error in %s: %s",
                         S3TaggingTestLib.delete_bucket_tagging.__name__,
                         error)
            raise CTException(err.S3_CLIENT_ERROR, error.args[0])

        return True, response

    def set_object_tag(
            self,
            bucket_name: str,
            obj_name: str,
            key: str,
            value: str,
            tag_count: int = 1) -> tuple:
        """
        Sets the supplied tag-set to an object that already exists in a bucket.
        :param bucket_name: Name of the bucket.
        :param obj_name: Name of the object.
        :param key: Key for object tagging.
        :param value: Value for object tagging.
        :param tag_count: Tag count.
        :return: (Boolean, response)
        """
        try:
            LOGGER.info("Set object tagging")
            tag_set = list()
            for num in range(tag_count):
                tag = dict()
                tag.update([("Key", "{}{}".format(key, str(num))),
                            ("Value", "{}{}".format(value, str(num)))])
                tag_set.append(tag)
            LOGGER.debug(tag_set)
            tags = {"TagSet": tag_set}
            response = self.put_object_tagging(bucket_name, obj_name, tags)
            LOGGER.info(response)
        except Exception as error:
            LOGGER.error("Error in %s: %s",
                         S3TaggingTestLib.set_object_tag.__name__,
                         error)
            raise CTException(err.S3_CLIENT_ERROR, error.args[0])

        return True, response

    def get_object_tags(self, bucket_name: str, obj_name: str) -> tuple:
        """
        Returns the tag-set of an object.
        :param bucket_name: Name of the bucket.
        :param obj_name: Name of the object.
        :return: (Boolean, list of object tags)
        """
        try:
            LOGGER.info("Getting object tags")
            obj_tagging = self.get_object_tagging(
                bucket_name, obj_name)
            LOGGER.debug(obj_tagging)
            tag_set = obj_tagging["TagSet"]
            LOGGER.info(tag_set)
        except Exception as error:
            LOGGER.error("Error in %s: %s",
                         S3TaggingTestLib.get_object_tags.__name__,
                         error)
            raise CTException(err.S3_CLIENT_ERROR, error.args[0])

        return True, tag_set

    def delete_object_tagging(self, bucket_name: str, obj_name: str) -> tuple:
        """
        Removes the tag-set from an existing object.
        :param bucket_name: Name of the bucket.
        :param obj_name: Name of the object.
        :return: (Boolean, response)
        """
        try:
            LOGGER.info("Deleting object tagging")
            response = super().delete_object_tagging(
                bucket_name, obj_name)
            LOGGER.info(response)
        except Exception as error:
            LOGGER.error("Error in %s: %s",
                         S3TaggingTestLib.delete_object_tagging.__name__,
                         error)
            raise CTException(err.S3_CLIENT_ERROR, error.args[0])

        return True, response

    def create_multipart_upload_with_tagging(
            self,
            bucket_name: str,
            obj_name: str,
            tag: str) -> tuple:
        """
        request to initiate a multipart upload.
        :param bucket_name: Name of the bucket.
        :param obj_name: Name of the object.
        :param tag: Tag value(eg: "aaa=bbb").
        :return: (Boolean, response)
        """
        try:
            LOGGER.info("Creating multipart upload with tagging....")
            response = self.s3_client.create_multipart_upload(
                Bucket=bucket_name, Key=obj_name, Tagging=tag)
            mpu_id = response["UploadId"]
            LOGGER.info("Upload id : %s", str(mpu_id))
        except Exception as error:
            LOGGER.error(
                "Error in %s: %s",
                S3TaggingTestLib.create_multipart_upload_with_tagging.__name__,
                error)
            raise CTException(err.S3_CLIENT_ERROR, error.args[0])

        return True, response

    def put_object_with_tagging(self,
                                bucket_name: str,
                                object_name: str,
                                file_path: str,
                                tag: str = None,
                                key: str = None,
                                value: str = None) -> tuple:
        """
        Putting Object to the Bucket (mainly small file) with tagging and metadata.
        :param bucket_name: Name of the bucket.
        :param object_name: Name of the object.
        :param file_path: Path of the file.
        :param tag: Tag value(eg: "aaa=bbb").
        :param key: Key for metadata.
        :param value: Value for metadata.
        :return: (Boolean, response)
        """
        try:
            LOGGER.info("put %s into %s with %s",
                        object_name,
                        bucket_name,
                        tag)
            if not os.path.exists(file_path):
                create_file(file_path, 1)
            LOGGER.info("Putting object with tagging")
            with open(file_path, "rb") as data:
                if key:
                    meta = {key: value}
                    response = super().put_object_with_tagging(
                        bucket_name, object_name, data, tag, meta)
                else:
                    response = super().put_object_with_tagging(bucket_name, object_name, data, tag)
            LOGGER.info(response)
        except Exception as error:
            LOGGER.error("Error in %s: %s",
                         S3TaggingTestLib.put_object_with_tagging.__name__,
                         error)
            raise CTException(err.S3_CLIENT_ERROR, error.args[0])

        return True, response

    def set_bucket_tag_duplicate_keys(
            self,
            bucket_name: str,
            key: str,
            value: str) -> tuple:
        """
        Set tags to a bucket with duplicate keys.
        :param bucket_name: Name of bucket.
        :param key: Key for bucket tagging.
        :param value: Value for bucket tagging.
        :return: True or False and response.
        """
        try:
            LOGGER.info("Set bucket tag with duplicate key")
            tag_set = list()
            for num in range(2):
                tag = dict()
                tag.update([("Key", "{}".format(key)),
                            ("Value", "{}{}".format(value, str(num)))])
                tag_set.append(tag)
            LOGGER.info("Put bucket tagging with TagSet: %s", str(tag_set))
            response = super().set_bucket_tags(
                bucket_name, tag_set={"TagSet": tag_set})
            LOGGER.info(response)
        except BaseException as error:
            LOGGER.error(
                "Error in %s: %s",
                S3TaggingTestLib.set_bucket_tag_duplicate_keys.__name__,
                error)
            raise CTException(err.S3_CLIENT_ERROR, error.args[0])

        return True, response

    def set_bucket_tag_invalid_char(
            self,
            bucket_name: str,
            key: str,
            value: str) -> tuple:
        """
        Set tag to a bucket with invalid special characters(convert tag to encode base64).
        :param bucket_name: Name of bucket.
        :param key: Key for bucket tagging.
        :param value: Value for bucket tagging.
        :return: True or False and response.
        """
        try:
            LOGGER.info("Set bucket tag with invalid special chars in key.")
            tag_set = list()
            encoded = base64.b64encode(b'?')
            encoded_str = encoded.decode('utf-8')
            tag = dict()
            tag.update([("Key", "{}{}".format(key, encoded_str)),
                        ("Value", "{}{}".format(value, encoded_str))])
            tag_set.append(tag)
            LOGGER.info(
                "Put bucket tagging with invalid TagSet: %s", str(tag_set))
            response = super().set_bucket_tags(
                bucket_name, tag_set={'TagSet': tag_set})
        except BaseException as error:
            LOGGER.error("Error in %s: %s",
                         S3TaggingTestLib.set_bucket_tag_invalid_char.__name__,
                         error)
            raise CTException(err.S3_CLIENT_ERROR, error.args[0])

        return True, response

    def set_duplicate_object_tags(self,
                                  bucket_name: str,
                                  obj_name: str,
                                  key: str,
                                  value: str,
                                  duplicate_key: bool = True) -> tuple:
        """
        Sets the duplicate tag-set to an object that already exists in a bucket.
        :param bucket_name: Name of bucket.
        :param obj_name: Name of object.
        :param key: Key for object tagging.
        :param value: Value for object tagging.
        :param duplicate_key: Set True for duplicate keys, False for duplicate values, default True.
        :return: True or False and response.
        """
        LOGGER.info("Set duplicate tag set to an object.")
        try:
            tag_set = list()
            for num in range(2):
                tag = dict()
                if duplicate_key:
                    tag.update([("Key", "{}".format(key)),
                                ("Value", "{}{}".format(value, str(num)))])
                    tag_set.append(tag)
                else:
                    tag.update([("Key", "{}{}".format(key, str(num))),
                                ("Value", "{}".format(value))])
                    tag_set.append(tag)
            LOGGER.info("Put object tagging with TagSet: %s", str(tag_set))
            response = super().put_object_tagging(
                bucket_name, obj_name, tags={'TagSet': tag_set})
            LOGGER.info(response)
        except BaseException as error:
            LOGGER.error("Error in %s: %s",
                         S3TaggingTestLib.set_duplicate_object_tags.__name__,
                         error)
            raise CTException(err.S3_CLIENT_ERROR, error.args[0])

        return True, response

    def set_object_tag_invalid_char(
            self,
            bucket_name: str,
            obj_name: str,
            key: str,
            value: str) -> tuple:
        """
        Set tag to a object with invalid special characters(convert tag to encode base64).
        :param bucket_name: Name of bucket.
        :param obj_name: Name of object.
        :param key: Key for object tagging.
        :param value: Value for object tagging.
        :return: True or False and response.
        :rtype: (Boolean, dict/str).
        """
        try:
            LOGGER.info("Set object tag with invalid special char in key.")
            tag_set = list()
            encoded = base64.b64encode(b'?')
            encoded_str = encoded.decode('utf-8')
            tag = dict()
            tag.update([("Key", "{}{}".format(key, encoded_str)),
                        ("Value", "{}{}".format(value, encoded_str))])
            tag_set.append(tag)
            LOGGER.info("Put object tagging with TagSet: %s", str(tag_set))
            response = super().put_object_tagging(
                bucket_name, obj_name, tags={'TagSet': tag_set, })
            LOGGER.info(response)
        except BaseException as error:
            LOGGER.error("Error in %s: %s",
                         S3TaggingTestLib.set_object_tag_invalid_char.__name__,
                         error)
            raise CTException(err.S3_CLIENT_ERROR, error.args[0])

        return True, response

    def get_object_with_tagging(self, bucket_name: str, key: str) -> tuple:
        """
        Get object using tag key.
        :param bucket_name: Name of bucket.
        :param key: tag key of the object.
        :return: True or False and response.
        """
        try:
            LOGGER.info("Getting object with tag key: %s", key)
            response = self.s3_client.get_object(Bucket=bucket_name, Key=key)
            LOGGER.info(response)
        except BaseException as error:
            LOGGER.error("Error in %s: %s",
                         S3TaggingTestLib.get_object_with_tagging.__name__,
                         error)
            raise CTException(err.S3_CLIENT_ERROR, error.args[0])

        return True, response