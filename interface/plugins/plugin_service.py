# Copyright (C) 2021 Applied Intuition, Inc. All rights reserved.
# This source code file is distributed under and subject to the LICENSE in license.txt
from __future__ import annotations

import json
import typing

from example_export_dataset import ExportDatasetPlugin
from example_issue_tracking_plugin import ExampleIssueTrackingPlugin

from simian.public.plugins import plugin_service


def register_plugins(
    service: plugin_service.PluginService, extra_data: dict[typing.Any, typing.Any]
) -> None:
    service.register_export_dataset(ExportDatasetPlugin, extra_data)
    service.register_issue_tracker_manager(ExampleIssueTrackingPlugin, extra_data)


def main() -> None:
    service = plugin_service.PluginService()
    args = plugin_service.create_argparser().parse_args()
    extra_data = json.loads(args.extra_data) if args.extra_data else None
    register_plugins(service, extra_data)
    plugin_service.start_plugin_service(service, args)


if __name__ == "__main__":
    main()
