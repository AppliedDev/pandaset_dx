# Copyright (C) 2021 Applied Intuition, Inc. All rights reserved.
# This source code file is distributed under and subject to the LICENSE in license.txt
from __future__ import annotations

import typing

from simian.public.plugins import export_dataset
from simian.public.proto import plugin_pb2


class ExportDatasetPlugin(export_dataset.AbstractExportDatasetPlugin):
    def __init__(self, _extra_data: dict[str, typing.Any]) -> None:
        pass

    def export_dataset_events(
        self, request: plugin_pb2.ExportDatasetRequest
    ) -> plugin_pb2.ExportDatasetResponse:
        print(request)
        response = plugin_pb2.ExportDatasetResponse(url="")
        return response

    def get_export_options(
        self, _request: plugin_pb2.GetSupportedExportDatasetOptionsRequest
    ) -> plugin_pb2.GetSupportedExportDatasetOptionsResponse:
        response = plugin_pb2.GetSupportedExportDatasetOptionsResponse()
        custom_option = response.options.add()
        custom_option.option_name = "Customizable option"
        custom_option.multi_select.multiselect_options.extend(["Option 1", "Option 2", "Option 3"])

        return response
