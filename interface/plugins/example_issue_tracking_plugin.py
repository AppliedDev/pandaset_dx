from __future__ import annotations

import typing

from simian.public.plugins import issue_tracker_manager
from simian.public.proto import common_pb2
from simian.public.proto import plugin_pb2


class ExampleIssueTrackingPlugin(issue_tracker_manager.AbstractIssueTrackerManager):
    """
    This is a skeleton implementation of the issue tracking plugin.

    Before deploying to cloud, ensure to remove any logging related to auth tokens.
    """

    def __init__(self, _extra_data: dict[str, typing.Any]) -> None:
        pass

    def get_available_issues(
        self, _request: plugin_pb2.GetAvailableIssuesRequest
    ) -> plugin_pb2.GetAvailableIssuesResponse:
        """
        Gets the relevant open and active issues from your issue manager using the given read-only token and project.
        """
        print("get_available_issues called")
        response = plugin_pb2.GetAvailableIssuesResponse()
        available_issues = [("mock_issue_1", 42323), ("mock_issue_2", 23423)]

        for issue_name, issue_id in available_issues:
            issue_proto = response.issues.add()
            issue_proto.id = str(issue_id)
            issue_proto.display_name = issue_name
            issue_proto.hyperlink = "https://www.atlassian.com/software/jira"

        print("Returning response:", response)
        return response

    def create_new_issue(
        self, request: plugin_pb2.CreateNewIssueRequest
    ) -> plugin_pb2.CreateNewIssueResponse:
        """
        Creates a new issue including information related to the event.
        Return metadata about that new issue back to ADP.
        """
        print("create_new_issue called")
        response = plugin_pb2.CreateNewIssueResponse()
        response.common.status = common_pb2.CommonResponse.SUCCESS
        response.issue.id = "32232"
        response.issue.display_name = request.issue_summary
        response.issue.hyperlink = "https://www.atlassian.com/software/jira"
        print("Returning response:", response)
        return response

    def update_issue_with_event(
        self, _request: plugin_pb2.UpdateIssueWithEventRequest
    ) -> plugin_pb2.UpdateIssueWithEventResponse:
        """Updates issue with the new event information.

        If the event was not previously tracked by the issue it is added. This method is
        called when linking an event to an existing issue or when re-syncing a linked
        issue from an event.
        """
        print("update_issue_with_event called")
        response = plugin_pb2.UpdateIssueWithEventResponse()
        response.common.status = common_pb2.CommonResponse.SUCCESS
        return response

    def bulk_update_issue_with_events(
        self, _request: plugin_pb2.BulkUpdateIssueWithEventsRequest
    ) -> plugin_pb2.BulkUpdateIssueWithEventsResponse:
        print("Bulk update issue with events called")
        response = plugin_pb2.BulkUpdateIssueWithEventsResponse()
        response.common.status = common_pb2.CommonResponse.SUCCESS
        return response

    def remove_event_from_issue(
        self, _request: plugin_pb2.RemoveEventFromIssueRequest
    ) -> plugin_pb2.RemoveEventFromIssueResponse:
        """Removes information related to the event from the issue."""
        print("remove_event_from_issue called")
        response = plugin_pb2.BulkUpdateIssueWithEventsResponse()
        response.common.status = common_pb2.CommonResponse.SUCCESS
        return response

    def bulk_remove_events_from_issue(
        self, _request: plugin_pb2.BulkRemoveEventsFromIssueRequest
    ) -> plugin_pb2.BulkRemoveEventsFromIssueResponse:
        print("Bulk remove events from issue called")
        response = plugin_pb2.BulkRemoveEventsFromIssueResponse()
        response.common.status = common_pb2.CommonResponse.SUCCESS
        return response
