from datetime import datetime
from typing import Dict, List, Union
from middleware.serializers.observation import (
    DailyRoundObservationSerializer,
    ObservationIDChoices,
    ObservationSerializer,
)
from django.conf import settings
from middleware.types.observations import LogData, StaticObservation
from middleware.views import static_observations


messages = [
    {
        "message": "Leads Off",
        "description": "ECG leads disconnected",
        "validity": "The HR value is null, if invalid",
        "observationType": "ECG",
    },
    {
        "message": "Asystole",
        "description": "Arrhythmia - Asystole",
        "validity": "The HR value is null, if invalid",
        "observationType": "ECG",
    },
    {
        "message": "Missed Beat",
        "description": "Arrhythmia – Missed beat",
        "validity": "The HR value is null, if invalid",
        "observationType": "ECG",
    },
    {
        "message": "Tachy Cardia",
        "description": "Arrhythmia - Tachycardia",
        "validity": "The HR value is null, if invalid",
        "observationType": "ECG",
    },
    {
        "message": "Brady Cardia",
        "description": "Arrhythmia – Brady cardia",
        "validity": "The HR value is null, if invalid",
        "observationType": "ECG",
    },
    {
        "message": "VFIB",
        "description": "Arrhythmia - Ventricular Fibrillation",
        "validity": "The HR value is null, if invalid",
        "observationType": "ECG",
    },
    {
        "message": "VTAC",
        "description": "Arrhythmia - Ventricular Tachycardia",
        "validity": "The HR value is null, if invalid",
        "observationType": "ECG",
    },
    {
        "message": "R ON T",
        "description": "Arrhythmia – R on T",
        "validity": "The HR value is null, if invalid",
        "observationType": "ECG",
    },
    {
        "message": "COUPLET",
        "description": "Arrhythmia – PVC couplet",
        "validity": "The HR value is null, if invalid",
        "observationType": "ECG",
    },
    {
        "message": "BIGEMINY",
        "description": "Arrhythmia - Bigeminy",
        "validity": "The HR value is null, if invalid",
        "observationType": "ECG",
    },
    {
        "message": "TRIGEMINY",
        "description": "Arrhythmia - Trigeminy",
        "validity": "The HR value is null, if invalid",
        "observationType": "ECG",
    },
    {
        "message": "PNC",
        "description": "Arrhythmia - Premature Nodal contraction",
        "validity": "The HR value is null, if invalid",
        "observationType": "ECG",
    },
    {
        "message": "PNP",
        "description": "Arrhythmia - Pace not pacing",
        "validity": "The HR value is null, if invalid",
        "observationType": "ECG",
    },
    {
        "message": "ARRHYTHMIA",
        "description": "Arrhythmia present, couldn’t detect the specific arrhythmia",
        "validity": "The HR value is null, if invalid",
        "observationType": "ECG",
    },
    {
        "message": "Run of PVCs",
        "description": "Arrhythmia – Run of PVCs",
        "validity": "The HR value is null, if invalid",
        "observationType": "ECG",
    },
    {
        "message": "Ventricular Premature Beat",
        "description": "Arrhythmia – Ventricular Premature Beat",
        "validity": "The HR value is null, if invalid",
        "observationType": "ECG",
    },
    {
        "message": "PVC High",
        "description": "Arrhythmia – PVC High",
        "validity": "The HR value is null, if invalid",
        "observationType": "ECG",
    },
    {
        "message": "Non Standard Ventricular Tachycardia",
        "description": "Arrhythmia – Nonstandard Ventricular Tachycardia",
        "validity": "The HR value is null, if invalid",
        "observationType": "ECG",
    },
    {
        "message": "Extreme Tachycardia",
        "description": "Arrhythmia – Extreme Tachycardia",
        "validity": "The HR value is null, if invalid",
        "observationType": "ECG",
    },
    {
        "message": "Extreme Bradycardia",
        "description": "Arrhythmia – Extreme Bradycardia",
        "validity": "The HR value is null, if invalid",
        "observationType": "ECG",
    },
    {
        "message": "Pause",
        "description": "Arrhythmia – Heart Pause",
        "validity": "The HR value is null, if invalid",
        "observationType": "ECG",
    },
    {
        "message": "Irregular Rhythm",
        "description": "Arrhythmia – Irregular rhythm",
        "validity": "The HR value is null, if invalid",
        "observationType": "ECG",
    },
    {
        "message": "Ventricular Bradycardia",
        "description": "Arrhythmia – Ventricular tachycardia",
        "validity": "The HR value is null, if invalid",
        "observationType": "ECG",
    },
    {
        "message": "Ventricular Rhythm",
        "description": "Arrhythmia – Ventricular rhythm.",
        "validity": "The HR value is null, if invalid",
        "observationType": "ECG",
    },
    {
        "message": "Wrong cuff",
        "description": "Wrong cuff for the patient (for example paediatric NIBP being measured using ADULT cuff)",
        "validity": "",
        "observationType": "NIBP",
    },
    {
        "message": "Connect Cuff",
        "description": "No cuff / loose cuff",
        "validity": "",
        "observationType": "NIBP",
    },
    {
        "message": "Measurement error",
        "description": "Measurement taken is erroneous",
        "validity": "",
        "observationType": "NIBP",
    },
    {
        "message": "No finger in probe",
        "description": "SpO2 sensor has fallen off the patient finger",
        "validity": "The SpO2, PR value is invalid if this message is present. Value will be set to null.",
        "observationType": "SPO2",
    },
    {
        "message": "Probe unplugged",
        "description": "The SPO2 sensor probe is disconnected from the patient monitor.",
        "validity": "The SpO2, PR value is invalid if this message is present. Value will be set to null.",
        "observationType": "SPO2",
    },
    {
        "message": "Leads off",
        "description": "Respiration leads have fallen off / disconnected from the patient",
        "validity": "The value is null if invalid",
        "observationType": "Respiration",
    },
    {
        "message": "Measurement invalid",
        "description": "The measured value is invalid",
        "validity": "When this message is present, the measured value is invalid.",
        "observationType": "Temperature",
        "invalid": True,
    },
]


def is_valid(observation: ObservationSerializer):
    if (
        not observation
        or not observation.get("status")
        or (
            observation.get("observation_id") != ObservationIDChoices.BLOOD_PRESSURE
            and not isinstance(observation.get("value"), (int, float))
        )
    ):
        return False

    if observation["status"] == "final":
        return True

    message = observation["status"].replace("Message-", "")
    message_obj = next((m for m in messages if m["message"] == message), None)

    if message_obj and message_obj.get("invalid"):
        return False

    return True


def get_vitals_from_observations(ip_address: str):
    global static_observations
    print("static is", static_observations)

    def get_value_from_data(
        type: ObservationIDChoices,
        data: Dict[
            ObservationIDChoices,
            Union[ObservationSerializer, List[ObservationSerializer]],
        ],
    ):
        if not data or type not in data:
            return None

        observation = data[type][0] if isinstance(data[type], list) else data[type]

        if "date-time" not in observation:
            return None

        observation_time = datetime.fromisoformat(
            observation["date-time"].replace(" ", "T") + "+05:30"
        )

        is_stale = (datetime.now() - observation_time) > settings.UPDATE_INTERVAL

        if is_stale or not is_valid(observation):
            return None

        if type in [
            ObservationIDChoices.BODY_TEMPERATURE1,
            ObservationIDChoices.BODY_TEMPERATURE2,
        ]:
            if (
                observation.get("low-limit", None)
                < observation.get("value", None)
                < observation.get("high-limit", None)
            ):
                return {
                    "temperature": observation["value"],
                    "temperature_measured_at": observation_time.isoformat(),
                }
            return None
        elif type == "blood-pressure":
            return {
                "systolic": observation.get("systolic", {}).get("value"),
                "diastolic": observation.get("diastolic", {}).get("value"),
            }
        else:
            return observation.get("value", None)

    print("Getting vitals from observations for the asset: %s", ip_address)

    observation: StaticObservation = None
    print("static_observations", static_observations)
    print("Static is ", static_observations)
    for static_observation in static_observations:
        if static_observation.device_id == ip_address:
            observation = static_observation
            break
    print("observation are", observation)
    if (
        not observation
        or (
            datetime.now() - datetime.fromisoformat(observation.last_updated)
        ).total_seconds()
        * 1000
        > settings.UPDATE_INTERVAL
    ):
        return None
    data = observation.observations

    temperature_data = get_value_from_data(
        "body-temperature1", data
    ) or get_value_from_data("body-temperature2", data)
    if temperature_data is None:
        temperature_data = {"temperature": None, "temperature_measured_at": None}
    response = {
        "taken_at": observation.last_updated,
        "spo2": get_value_from_data("SpO2", data),
        "ventilator_spo2": get_value_from_data("SpO2", data),
        "resp": get_value_from_data("respiratory-rate", data),
        "pulse": get_value_from_data("heart-rate", data)
        or get_value_from_data("pulse-rate", data),
        **temperature_data,
        "bp": get_value_from_data("blood-pressure", data) or {},
        "rounds_type": "AUTOMATED",
        "is_parsed_by_ocr": False,
    }
    serialized_response = DailyRoundObservationSerializer(response, data)
    if serialized_response.is_valid():
        return serialized_response.validated_data
    else:
        return serialized_response.errors
