from middleware.lab_analyzer.handler import generate_hl7_message
import asyncio
import logging

from django.utils.timezone import now, timedelta
from hl7.mllp import open_hl7_connection
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from common.authentication import CareAuthentication
from middleware.lab_analyzer.types import (
    LabAnalyzerAsset,
    LabAnalyzerOrder,
    LabAnalyzerResultModel,
)
from middleware.models import LabAnalyzerResult

logger = logging.getLogger(__name__)


class LabAnalyzerViewSet(viewsets.ViewSet):
    authentication_classes = [CareAuthentication]
    permission_classes = [IsAuthenticated]
    def _get_lab_analyzer_params(self, request):
        try:
            return LabAnalyzerAsset(
                hostname=str(request.query_params["hostname"]),
                port=int(request.query_params["port"]),
            )
        except KeyError as e:
            raise ValidationError(f"Missing parameter: {e}")

    @action(detail=False, methods=["get"])
    def status(self, request):
        lab_analyzer_request = self._get_lab_analyzer_params(request)
        response_data = {
            "hostname": lab_analyzer_request.hostname,
            "port": lab_analyzer_request.port,
            "status": "connected",
        }
        return Response(response_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def order_test(self, request):
        lab_analyzer_request = LabAnalyzerOrder.model_validate(request.data)
        logger.info(f"Received lab analyzer order: {lab_analyzer_request}")

        try:
            hl7_message = generate_hl7_message(lab_analyzer_request.payload)
            logger.info(f"Generated HL7 message: {hl7_message.replace("\r", "\n")}")
        except Exception as e:
            raise ValidationError(f"Invalid HL7 message format: {e}")

        async def send_hl7_message():
            try:
                hl7_reader, hl7_writer = await asyncio.wait_for(
                    open_hl7_connection(
                        lab_analyzer_request.hostname, lab_analyzer_request.port
                    ),
                    timeout=10,
                )
                hl7_writer.writemessage(hl7_message)
                await hl7_writer.drain()

                hl7_ack = await asyncio.wait_for(hl7_reader.readmessage(), timeout=10)
                logger.info(f"Received HL7 ACK: {hl7_ack}".replace("\r", "\n"))
                hl7_writer.close()
                return {"status": "HL7 message sent successfully"}, status.HTTP_200_OK
            except Exception as e:
                logger.error(f"Error sending HL7 message: {e}")
                return {"error": "Failed to send HL7 message"}, status.HTTP_500_INTERNAL_SERVER_ERROR

        try:
            response_data, response_status = asyncio.run(send_hl7_message())
            return Response(response_data, status=response_status)
        except Exception as e:
            logger.error(f"Error running async operation: {e}")
            return Response(
                {"error": "Failed to send HL7 message"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    # @action(detail=False, methods=["get"])
    # def get_results(self, request):
    #     lab_analyzer_request = self._get_lab_analyzer_params(request)

    #     result_window = now() - timedelta(hours=24)

    #     results = LabAnalyzerResult.objects.filter(
    #         ip_address=lab_analyzer_request.hostname, time__gte=result_window
    #     ).order_by("-time")
    #     results_data = [
    #         LabAnalyzerResultModel.model_construct(result).model_dump(mode="json")
    #         for result in results
    #     ]

    #     return Response({"results": results_data}, status=status.HTTP_200_OK)

    # @action(detail=False, methods=["post"])
    # def clear_results(self, request):
    #     lab_analyzer_request = LabAnalyzerOrder.model_validate(request.data)

    #     deleted_count, _ = LabAnalyzerResult.objects.filter(
    #         ip_address=lab_analyzer_request.hostname
    #     ).delete()

    #     return Response(
    #         {"status": f"Deleted {deleted_count} results"},
    #         status=status.HTTP_200_OK,
    #     )
