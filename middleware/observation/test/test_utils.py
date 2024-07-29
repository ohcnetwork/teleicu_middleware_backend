from unittest import TestCase as UnitTest
from django.test import override_settings
import boto3
from unittest.mock import MagicMock, patch

from sentry_sdk.crons.consts import MonitorStatus

from middleware.observation.test.util_factory import ObservationFactory
from middleware.observation.types import DataDumpRequest, MonitorOptions, Observation
from middleware.observation.utils import make_data_dump_to_json


class TestUtils(UnitTest):

    @patch("middleware.observation.utils.boto3.client")
    @patch("middleware.observation.utils.capture_checkin")
    @patch("middleware.observation.utils.settings")
    def test_make_data_dump_to_json(
        self, mock_settings, mock_capture_checkin, mock_boto3_client
    ):
        mock_settings.S3_BUCKET_NAME = "test-bucket"
        mock_settings.S3_ACCESS_KEY_ID = "test-key"
        mock_settings.S3_SECRET_ACCESS_KEY = "test-secret"
        mock_settings.S3_ENDPOINT_URL = None
        mock_s3 = MagicMock()
        mock_boto3_client.return_value = mock_s3

        mock_capture_checkin.return_value = "test-check-in-id"
        observation_1 = ObservationFactory()
        observation_2 = ObservationFactory()
        request = DataDumpRequest(
            data=[observation_1, observation_2],
            key="test-key",
            monitor_options=MonitorOptions(slug="test-slug", options={}),
        )

        # Execute
        make_data_dump_to_json(request)

        # Assert
        mock_boto3_client.assert_called_once()
        mock_s3.put_object.assert_called_once()
        self.assertEqual(mock_capture_checkin.call_count, 2)
        mock_capture_checkin.assert_any_call(
            monitor_slug="test-slug",
            status=MonitorStatus.IN_PROGRESS,
            monitor_config={},
        )
        mock_capture_checkin.assert_any_call(
            check_in_id="test-check-in-id",
            monitor_slug="test-slug",
            status=MonitorStatus.OK,
        )
