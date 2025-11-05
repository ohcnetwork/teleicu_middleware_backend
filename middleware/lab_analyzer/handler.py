import asyncio
import logging
from datetime import datetime
import os
import aiohttp

import hl7
from hl7.containers import Message
from hl7.mllp.streams import HL7StreamReader, HL7StreamWriter

from middleware.utils import _get_headers

logger = logging.getLogger(__name__)


def generate_hl7_message(payload):
    """
    Generate an HL7 OML^O21 (Lab Order) message from the given payload.

    Args:
        payload (dict): A dictionary containing:
            - patient: dict with external_id, name, date_of_birth, gender
            - facility: dict with external_id, name
            - service_request: dict with external_id, test_code (code, system, display), date_time

    Returns:
        str: A formatted HL7 message string.
    """
    # Helper function to format datetime
    def format_hl7_datetime(dt_str):
        if not dt_str:
            return ""
        try:
            dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
            return dt.strftime("%Y%m%d%H%M%S")
        except Exception:
            return ""

    # Extract data from payload
    patient = payload.get("patient", {})
    facility = payload.get("facility", {})
    service_request = payload.get("service_request", {})

    # Prepare data
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    service_request_id = service_request.get("external_id", "")
    facility_id = facility.get("external_id", "")
    facility_name = facility.get("name", "")

    # Patient data
    patient_id = patient.get("external_id", "")
    patient_name = patient.get("name", "")
    name_parts = patient_name.split(" ", 1) if patient_name else ["", ""]
    family_name = name_parts[-1] if len(name_parts) > 1 else name_parts[0] if name_parts else ""
    given_name = name_parts[0] if len(name_parts) > 1 else ""

    gender_map = {"male": "M", "female": "F", "transgender": "O", "other": "O", "unknown": "U"}
    gender = gender_map.get(patient.get("gender", "").lower(), "U")
    dob = format_hl7_datetime(patient.get("date_of_birth", ""))

    # Test code data
    test_code = service_request.get("test_code", {})
    test_code_str = f"{test_code.get('code', '')}^{test_code.get('display', '')}^{test_code.get('system', '')}"
    requested_datetime = format_hl7_datetime(service_request.get("date_time", ""))

    # Build segments as strings
    msh = f"MSH|^~\\&|{facility_id}|{facility_name}|LAB_ANALYZER|LAB|{timestamp}||OML^O21^OML_O21|{service_request_id}|P|2.5.1||||NE|AL"
    pid = f"PID|1||{patient_id}||{family_name}^{given_name}||{dob}|{gender}"
    orc = f"ORC|NW|{service_request_id}|{service_request_id}|||||{requested_datetime}"
    obr = f"OBR|1|{service_request_id}||{test_code_str}||{requested_datetime}|"

    # Join segments with carriage return
    message_str = "\r".join([msh, pid, orc, obr])

    # Parse and return as string
    message = hl7.parse(message_str)
    return str(message)


def hl7_result_message_to_json(hl7_message: Message) -> dict:
    """
    Convert an HL7 ORU^R01 (Observation Result) message to JSON format.
    
    Args:
        hl7_message: Parsed HL7 message object
        
    Returns:
        dict: JSON representation with interpretation and component details
    """
    result = {
        "interpretation": "normal",
        "status": "final",
        "encounter": None,
        "subject_type": "patient",
        "value_type": "quantity",
        "value": {"value": ""},
        "component": []
    }
    
    # Helper function to parse coded value (format: code^display^system)
    def parse_coded_value(field_value):
        if not field_value:
            return {"code": "", "system": "", "display": ""}
        
        parts = str(field_value).split("^")
        return {
            "code": parts[0] if len(parts) > 0 else "",
            "system": parts[2] if len(parts) > 2 else "",
            "display": parts[1] if len(parts) > 1 else ""
        }

    
    # Helper function to determine interpretation based on abnormal flag
    def get_interpretation(abnormal_flag):
        # HL7 abnormal flags: N=Normal, L=Low, H=High, A=Abnormal
        flag_map = {
            "N": "normal",
            "L": "low",
            "H": "high",
            "A": "abnormal",
            "": "normal"
        }
        return flag_map.get(str(abnormal_flag).strip(), "normal")
    
    # Helper to convert HL7 timestamp to ISO 8601
    def parse_hl7_datetime(dt_value):
        dt_str = str(dt_value).strip()
        if not dt_str:
            return ""

        formats = [
            ("%Y%m%d%H%M%S", 14),
            ("%Y%m%d%H%M", 12),
            ("%Y%m%d", 8),
            ("%Y%m", 6),
        ]

        for fmt, length in formats:
            if len(dt_str) >= length:
                try:
                    parsed = datetime.strptime(dt_str[:length], fmt)
                    return parsed.isoformat()
                except ValueError:
                    continue
        return dt_str

    # Extract service request identifier from the ORC segment
    service_request_id = ""
    effective_datetime = ""

    # Parse OBX segments (Observation/Result segments)
    obx_segments = []
    for segment in hl7_message:
        if len(segment) > 0 and str(segment[0]) == "OBX":
            obx_segments.append(segment)
        elif len(segment) > 0 and str(segment[0]) == "ORC" and not service_request_id:
            service_request_id = str(segment[2]) if len(segment) > 2 else ""
        elif len(segment) > 0 and str(segment[0]) == "OBR" and not effective_datetime:
            effective_datetime = parse_hl7_datetime(segment[7] if len(segment) > 7 else "")
    
    # Determine overall interpretation (if any result is abnormal, overall is abnormal)
    overall_abnormal = False
    
    # Process each OBX segment
    for obx in obx_segments:
        # OBX segment structure:
        # OBX|Set ID|Value Type|Observation ID|Sub-ID|Value|Units|Reference Range|Abnormal Flags|...
        if len(obx) < 6:
            continue
            
        # OBX-3: Observation Identifier (code^display^system)
        observation_id = parse_coded_value(obx[3] if len(obx) > 3 else "")
        
        # OBX-5: Observation Value
        value = str(obx[5]) if len(obx) > 5 else ""
        
        # OBX-6: Units
        unit_code = str(obx[6]) if len(obx) > 6 else ""
        
        # OBX-8: Abnormal Flags
        abnormal_flag = str(obx[8]) if len(obx) > 8 else "N"
        interpretation = get_interpretation(abnormal_flag)
        
        if interpretation != "normal":
            overall_abnormal = True
        
        # Build component
        component = {
            "code": observation_id,
            "value": {
                "value": value,
                "unit": {
                    "code": unit_code,
                    "system": "http://unitsofmeasure.org",
                    "display": unit_code
                }
            },
            "interpretation": interpretation
        }
        
        result["component"].append(component)

        if not effective_datetime and len(obx) > 14:
            effective_datetime = parse_hl7_datetime(obx[14])
    
    # Set overall interpretation
    if overall_abnormal:
        result["interpretation"] = "abnormal"

    result["effective_datetime"] = effective_datetime
    
    return {
        "service_request": service_request_id,
        "result": result
    }


async def process_hl7_messages(
    hl7_reader: HL7StreamReader, hl7_writer: HL7StreamWriter
):
    """This will be called every time a socket connects
    with us.
    """

    peername = hl7_writer.get_extra_info("peername")
    logger.info(f"Connection established {peername}")
    try:
        while not hl7_writer.is_closing():
            hl7_message = await hl7_reader.readmessage()
            logger.info(f"[HL7] Received message\n {hl7_message}".replace("\r", "\n"))
            # acknowledge the message
            hl7_writer.writemessage(hl7_message.create_ack())
            await hl7_writer.drain()

            try:
                json_data = hl7_result_message_to_json(hl7_message)
                logger.info(f"[HL7] Converted result to JSON: {json_data}")
            except Exception as e:
                logger.error(f"[HL7] Error converting message to JSON: {e}")

            try:
                care_api_url = os.getenv("CARE_API")
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{care_api_url}/api/lab_analyzer_device/automation/create_observation/",
                        headers=_get_headers(),
                        json=json_data,
                    ) as resp:
                        if resp.status == 200:
                            logger.info("[HL7] Successfully sent observation to CARE")
                        else:
                            logger.error(f"[HL7] Failed to send observation to CARE. Status: {resp.status}")
            except Exception as e:
                logger.error(f"[HL7] Error processing message: {e}")


    except asyncio.IncompleteReadError:
        if not hl7_writer.is_closing():
            hl7_writer.close()
            await hl7_writer.wait_closed()

    logger.info(f"Connection closed {peername}")

