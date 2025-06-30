# Copyright 2019 Red Hat
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
from __future__ import absolute_import

import io

from oslo_log import log


LOG = log.getLogger(__name__)

COMPRESSED_FILE_TYPES = {}


def comressed_file_type(cls):
    COMPRESSED_FILE_TYPES[cls.compression_type] = cls
    return cls


def open_image_file(filename, mode, compression_type=None):
    if compression_type is None:
        max_magic_len = max(len(cls.file_magic)
                            for cls in COMPRESSED_FILE_TYPES.values())
        with io.open(filename, 'rb') as f:
            magic = f.read(max_magic_len)
        for cls in COMPRESSED_FILE_TYPES.values():
            if magic.startswith(cls.file_magic):
                compression_type = cls.compression_type
                LOG.debug("Compression type %r of file %r got from file magic",
                          compression_type, filename)
                break

    if compression_type:
        LOG.debug("Open compressed file %r (mode=%r, compression_type=%r)",
                  filename, mode, compression_type)
        open_func = COMPRESSED_FILE_TYPES[compression_type].open_file
    else:
        LOG.debug("Open flat file %r (mode=%r)", filename, mode)
        open_func = io.open

    return open_func(filename, mode)
