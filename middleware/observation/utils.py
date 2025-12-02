import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union

import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from django.conf import settings
from django.core.cache import cache
from django.utils.timezone import make_aware, now
from sentry_sdk.crons import capture_checkin
from sentry_sdk.crons.consts import MonitorStatus

from middleware.observation.types import (
    DataDumpRequest,
    DeviceID,
    Observation,
    ObservationID,
    StaticObservation,
    Status,
    ObservationWriteSpec,
    ObservationValueType,
    ObservationValue,
    Coding,
    BloodPressure,
    ReferenceRange,
)

logger = logging.getLogger(__name__)

messages = {
    "Leads Off": {
        "description": "ECG leads disconnected",
        "validity": "The HR value is null, if invalid",
        "observationType": "ECG",
    },
    "Asystole": {
        "description": "Arrhythmia - Asystole",
        "validity": "The HR value is null, if invalid",
        "observationType": "ECG",
    },
    "Missed Beat": {
        "description": "Arrhythmia – Missed beat",
        "validity": "The HR value is null, if invalid",
        "observationType": "ECG",
    },
    "Tachy Cardia": {
        "description": "Arrhythmia - Tachycardia",
        "validity": "The HR value is null, if invalid",
        "observationType": "ECG",
    },
    "Brady Cardia": {
        "description": "Arrhythmia – Brady cardia",
        "validity": "The HR value is null, if invalid",
        "observationType": "ECG",
    },
    "VFIB": {
        "description": "Arrhythmia - Ventricular Fibrillation",
        "validity": "The HR value is null, if invalid",
        "observationType": "ECG",
    },
    "VTAC": {
        "description": "Arrhythmia - Ventricular Tachycardia",
        "validity": "The HR value is null, if invalid",
        "observationType": "ECG",
    },
    "R ON T": {
        "description": "Arrhythmia – R on T",
        "validity": "The HR value is null, if invalid",
        "observationType": "ECG",
    },
    "COUPLET": {
        "description": "Arrhythmia – PVC couplet",
        "validity": "The HR value is null, if invalid",
        "observationType": "ECG",
    },
    "BIGEMINY": {
        "description": "Arrhythmia - Bigeminy",
        "validity": "The HR value is null, if invalid",
        "observationType": "ECG",
    },
    "TRIGEMINY": {
        "description": "Arrhythmia - Trigeminy",
        "validity": "The HR value is null, if invalid",
        "observationType": "ECG",
    },
    "PNC": {
        "description": "Arrhythmia - Premature Nodal contraction",
        "validity": "The HR value is null, if invalid",
        "observationType": "ECG",
    },
    "PNP": {
        "description": "Arrhythmia - Pace not pacing",
        "validity": "The HR value is null, if invalid",
        "observationType": "ECG",
    },
    "ARRHYTHMIA": {
        "description": "Arrhythmia present, couldn’t detect the specific arrhythmia",
        "validity": "The HR value is null, if invalid",
        "observationType": "ECG",
    },
    "Run of PVCs": {
        "description": "Arrhythmia – Run of PVCs",
        "validity": "The HR value is null, if invalid",
        "observationType": "ECG",
    },
    "Ventricular Premature Beat": {
        "description": "Arrhythmia – Ventricular Premature Beat",
        "validity": "The HR value is null, if invalid",
        "observationType": "ECG",
    },
    "PVC High": {
        "description": "Arrhythmia – PVC High",
        "validity": "The HR value is null, if invalid",
        "observationType": "ECG",
    },
    "Non Standard Ventricular Tachycardia": {
        "description": "Arrhythmia – Nonstandard Ventricular Tachycardia",
        "validity": "The HR value is null, if invalid",
        "observationType": "ECG",
    },
    "Extreme Tachycardia": {
        "description": "Arrhythmia – Extreme Tachycardia",
        "validity": "The HR value is null, if invalid",
        "observationType": "ECG",
    },
    "Extreme Bradycardia": {
        "description": "Arrhythmia – Extreme Bradycardia",
        "validity": "The HR value is null, if invalid",
        "observationType": "ECG",
    },
    "Pause": {
        "description": "Arrhythmia – Heart Pause",
        "validity": "The HR value is null, if invalid",
        "observationType": "ECG",
    },
    "Irregular Rhythm": {
        "description": "Arrhythmia – Irregular rhythm",
        "validity": "The HR value is null, if invalid",
        "observationType": "ECG",
    },
    "Ventricular Bradycardia": {
        "description": "Arrhythmia – Ventricular tachycardia",
        "validity": "The HR value is null, if invalid",
        "observationType": "ECG",
    },
    "Ventricular Rhythm": {
        "description": "Arrhythmia – Ventricular rhythm.",
        "validity": "The HR value is null, if invalid",
        "observationType": "ECG",
    },
    "Wrong cuff": {
        "description": "Wrong cuff for the patient (for example paediatric NIBP being measured using ADULT cuff)",
        "validity": "",
        "observationType": "NIBP",
    },
    "Connect Cuff": {
        "description": "No cuff / loose cuff",
        "validity": "",
        "observationType": "NIBP",
    },
    "Measurement error": {
        "description": "Measurement taken is erroneous",
        "validity": "",
        "observationType": "NIBP",
    },
    "No finger in probe": {
        "description": "SpO2 sensor has fallen off the patient finger",
        "validity": "The SpO2, PR value is invalid if this message is present. Value will be set to null.",
        "observationType": "SPO2",
    },
    "Probe unplugged": {
        "description": "The SPO2 sensor probe is disconnected from the patient monitor.",
        "validity": "The SpO2, PR value is invalid if this message is present. Value will be set to null.",
        "observationType": "SPO2",
    },
    "Leads off": {
        "description": "Respiration leads have fallen off / disconnected from the patient",
        "validity": "The value is null if invalid",
        "observationType": "Respiration",
    },
    "Measurement invalid": {
        "description": "The measured value is invalid",
        "validity": "When this message is present, the measured value is invalid.",
        "observationType": "Temperature",
        "invalid": True,
    },
}


def is_valid(observation: Observation):
    if (
        not observation
        or not observation.status
        or (
            observation.observation_id != ObservationID.BLOOD_PRESSURE
            and not isinstance(observation.value, (int, float))
        )
    ):
        return False
    if observation.status == Status.FINAL:
        return True
    message = observation.status.replace("Message-", "")
    message_obj = messages.get(message, None)
    if message_obj and message_obj.get("invalid"):
        return False
    return True


UNIT_CODES = {
    "deg F": {
        "system": "http://unitsofmeasure.org",
        "code": "[degF]",
        "display": "degree Fahrenheit",
    },
    "deg C": {
        "system": "http://unitsofmeasure.org",
        "code": "Cel",
        "display": "degree Celsius",
    },
    "Cel": {
        "system": "http://unitsofmeasure.org",
        "code": "Cel",
        "display": "degree Celsius",
    },
    "mmHg": {
        "system": "http://unitsofmeasure.org",
        "code": "mm[Hg]",
        "display": "millimeter of mercury",
    },
    "bpm": {
        "system": "http://unitsofmeasure.org",
        "code": "{beats}/min",
        "display": "heart beats per minute",
    },
    "brpm": {
        "system": "http://unitsofmeasure.org",
        "code": "{Breaths}/min",
        "display": "Breaths / minute",
    },
    "%": {"system": "http://unitsofmeasure.org", "code": "%", "display": "percent"},
}

OBSERVATION_ID_CODE_MAPPING = {
    ObservationID.HEART_RATE: Coding(
        code="8867-4", system="http://loinc.org", display="Heart rate"
    ),
    ObservationID.PULSE_RATE: Coding(
        code="8867-4", system="http://loinc.org", display="Heart rate"
    ),
    ObservationID.SPO2: Coding(
        code="2708-6",
        system="http://loinc.org",
        display="Oxygen saturation in Arterial blood",
    ),
    ObservationID.RESPIRATORY_RATE: Coding(
        code="9279-1", system="http://loinc.org", display="Respiratory rate"
    ),
    ObservationID.BODY_TEMPERATURE1: Coding(
        code="8310-5", system="http://loinc.org", display="Body temperature"
    ),
    ObservationID.BODY_TEMPERATURE2: Coding(
        code="8310-5", system="http://loinc.org", display="Body temperature"
    ),
}

OBSERVATION_TYPES_FOR_AUTOMATED_OBSERVATIONS = [
    ObservationID.HEART_RATE,
    ObservationID.PULSE_RATE,
    ObservationID.SPO2,
    ObservationID.RESPIRATORY_RATE,
    ObservationID.BODY_TEMPERATURE1,
    ObservationID.BODY_TEMPERATURE2,
    ObservationID.BLOOD_PRESSURE,
]


def normalize_interpretation(interpretation: str | None) -> str | None:
    if interpretation is None or interpretation.strip() == "":
        return None
    if interpretation.lower() == "na" or interpretation.lower() == "n/a":
        return None
    return interpretation


def get_reference_ranges(data: BloodPressure | Observation):
    results: list[ReferenceRange] = []
    unit = UNIT_CODES.get(data.unit)["code"] if data.unit else None
    if data.low_limit:
        results.append(
            ReferenceRange(min=data.low_limit, unit=unit, interpretation="low")
        )
    if data.high_limit:
        results.append(
            ReferenceRange(max=data.high_limit, unit=unit, interpretation="high")
        )
    return results


def get_blood_pressure_observation(
    data: BloodPressure, coding: Coding, time: datetime
) -> ObservationWriteSpec:
    return ObservationWriteSpec(
        main_code=coding,
        effective_datetime=time,
        value_type=ObservationValueType.integer,
        value=ObservationValue(
            value=data.value and str(int(data.value)),
            unit=data.unit and UNIT_CODES.get(data.unit),
        ),
        interpretation=normalize_interpretation(data.interpretation),
        reference_ranges=get_reference_ranges(data),
    )


def get_entries_for_automated_observations(
    data: StaticObservation,
) -> list[ObservationWriteSpec]:
    threshold_time = now() - timedelta(minutes=settings.AUTOMATED_OBSERVATIONS_INTERVAL)
    if data.last_updated < threshold_time:
        return []
    results: List[ObservationWriteSpec] = []
    for type in OBSERVATION_TYPES_FOR_AUTOMATED_OBSERVATIONS:
        observations = data.observations.get(type, [])
        if not observations:
            continue
        observation = observations[-1]
        observation_time = make_aware(observation.date_time)
        if observation_time < threshold_time:
            continue
        if not is_valid(observation):
            logger.info(f"Observation {observation.observation_id} is invalid")
            continue
        if type == ObservationID.BLOOD_PRESSURE:
            systolic, diastolic, mean = (
                observation.systolic,
                observation.diastolic,
                observation.map,
            )
            if systolic and systolic.value:
                results.append(
                    get_blood_pressure_observation(
                        systolic,
                        coding=Coding(
                            code="8480-6",
                            system="http://loinc.org",
                            display="Systolic blood pressure",
                        ),
                        time=observation_time,
                    )
                )
            if diastolic and diastolic.value:
                results.append(
                    get_blood_pressure_observation(
                        diastolic,
                        coding=Coding(
                            code="8462-4",
                            system="http://loinc.org",
                            display="Diastolic blood pressure",
                        ),
                        time=observation_time,
                    )
                )
            if mean and mean.value:
                results.append(
                    get_blood_pressure_observation(
                        mean,
                        coding=Coding(
                            code="8478-0",
                            system="http://loinc.org",
                            display="Mean blood pressure",
                        ),
                        time=observation_time,
                    )
                )
        if observation.value is None:
            continue
        value: str | None = None
        unit = observation.unit and UNIT_CODES.get(observation.unit)
        value_type: ObservationValueType | None = None
        if type in [
            ObservationID.HEART_RATE,
            ObservationID.SPO2,
            ObservationID.PULSE_RATE,
            ObservationID.RESPIRATORY_RATE,
            ObservationID.BODY_TEMPERATURE1,
        ]:
            value_type = ObservationValueType.integer
            value = str(int(observation.value))
        if type in [ObservationID.BODY_TEMPERATURE1, ObservationID.BODY_TEMPERATURE2]:
            value_type = ObservationValueType.decimal
            value = str(observation.value)
        results.append(
            ObservationWriteSpec(
                main_code=OBSERVATION_ID_CODE_MAPPING[type],
                effective_datetime=observation_time,
                value_type=value_type,
                value=ObservationValue(value=value, unit=unit),
                interpretation=normalize_interpretation(observation.interpretation),
                reference_ranges=get_reference_ranges(observation),
            )
        )
    return results


def get_value_from_data(
    type: ObservationID,
    data: Dict[
        ObservationID,
        Union[Observation, List[Observation]],
    ],
):
    if not data or type not in data:
        return None

    observation: Observation = (
        data[type][-1] if isinstance(data[type], list) else data[type]
    )

    if not observation.date_time:
        return None

    converted_date_time = make_aware(observation.date_time)

    is_stale = converted_date_time < (
        now() - timedelta(minutes=settings.AUTOMATED_OBSERVATIONS_INTERVAL)
    )

    if is_stale or not is_valid(observation):
        logger.info("Observations are stale or invalid Returning None")
        return None

    if type in [
        ObservationID.BODY_TEMPERATURE1,
        ObservationID.BODY_TEMPERATURE2,
    ]:
        if observation.low_limit < observation.value < observation.high_limit:
            return {
                "temperature": observation.value,
                "temperature_measured_at": converted_date_time.isoformat(),
            }
        return None
    elif type == "blood-pressure":
        if observation.systolic is None or observation.diastolic is None:
            return None
        return {
            "systolic": observation.systolic.value,
            "diastolic": observation.diastolic.value,
        }
    else:
        return observation.value


def extract_datetime(key):
    # Split the string to get the timestamp part
    timestamp_str = key.split("_", 1)[1]
    # Convert the string to a datetime object
    return datetime.fromisoformat(timestamp_str)


def get_observations_from_redis():
    observation_keys = cache.keys(f"{settings.REDIS_OBSERVATIONS_KEY}*")

    sorted_keys = sorted(observation_keys, key=extract_datetime)
    observations = []
    for key in sorted_keys:
        observations.extend(cache.get(key))
    return observations


def get_static_observations(device_id: DeviceID):
    observations = get_observations_from_redis()
    stale_time = now() - timedelta(minutes=settings.AUTOMATED_OBSERVATIONS_INTERVAL)

    # last one hour data matching the device id
    valid_observations: List[Observation] = []
    if not observations:
        logger.info(" No observations for device id : %s stored in redis ", device_id)
        return None
    for observation in observations:
        parsed_observation = Observation.model_validate(observation)

        if (
            parsed_observation.taken_at > stale_time
        ) and parsed_observation.device_id == device_id:
            valid_observations.append(parsed_observation)

    if not valid_observations:
        logger.info(
            " No observations Valid observations for device id : %s stored in redis ",
            device_id,
        )
        return None
    return generate_static_observations(observation_list=valid_observations)


def generate_static_observations(observation_list: List[Observation]):
    observations_dict = {}
    for observation in observation_list:
        observation_type = observation.observation_id
        if observation_type in observations_dict:
            observations_dict[observation_type].append(observation)
        else:
            observations_dict[observation_type] = [observation]

    return StaticObservation(
        observations=observations_dict, last_updated=observation_list[-1].taken_at
    )


def get_data_for_s3_dump():
    observations = get_observations_from_redis()
    stale_time = now() - timedelta(minutes=settings.AUTOMATED_OBSERVATIONS_INTERVAL)

    if not observations:
        return None
    observation_data_to_dump: List[Observation] = []

    # for makimg dumps we just use all the stale data
    for observation in observations:
        parsed_observation = Observation.model_validate(observation)
        if parsed_observation.taken_at < stale_time:
            observation_data_to_dump.append(parsed_observation)

    return observation_data_to_dump


def make_data_dump_to_s3(request: DataDumpRequest):
    check_in_id: Optional[str] = None

    if request.monitor_options:
        check_in_id = capture_checkin(
            monitor_slug=request.monitor_options.slug,
            status=MonitorStatus.IN_PROGRESS,
            monitor_config=request.monitor_options.options,
        )

    try:
        s3 = boto3.client(
            "s3",
            aws_access_key_id=settings.S3_ACCESS_KEY_ID,
            aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY,
            endpoint_url=settings.S3_ENDPOINT_URL if settings.S3_ENDPOINT_URL else None,
        )
        if not settings.S3_BUCKET_NAME:
            raise Exception("S3 Bucket Name not found")
        data = [
            observation.model_dump(mode="json", by_alias=True)
            for observation in request.data
        ]
        if not data:
            logger.info("No data to upload to S3")
            return
        s3.put_object(
            Bucket=settings.S3_BUCKET_NAME,
            Key=request.key,
            Body=data,
            ContentType="application/json",
        )
        logger.info("Successfully uploaded data to S3")

        if request.monitor_options and check_in_id:
            capture_checkin(
                check_in_id=check_in_id,
                monitor_slug=request.monitor_options.slug,
                status=MonitorStatus.OK,
            )
    except (NoCredentialsError, PartialCredentialsError) as e:
        logger.error("Failed to upload data to S3 due to credential issues")
        if request.monitor_options and check_in_id:
            capture_checkin(
                check_in_id=check_in_id,
                monitor_slug=request.monitor_options.slug,
                status=MonitorStatus.ERROR,
            )
        logger.error(e)

    except Exception as e:
        logger.error("Failed to upload data to S3")
        if request.monitor_options and check_in_id:
            capture_checkin(
                check_in_id=check_in_id,
                monitor_slug=request.monitor_options.slug,
                status=MonitorStatus.ERROR,
            )
        logger.error(e)
