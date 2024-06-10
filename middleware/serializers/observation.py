import json
from rest_framework import serializers
from enum import Enum


# String Enums for Observation fields
class ObservationIDChoices(str, Enum):
    HEART_RATE = "heart-rate"
    ST = "ST"
    SPO2 = "SpO2"
    PULSE_RATE = "pulse-rate"
    RESPIRATORY_RATE = "respiratory-rate"
    BODY_TEMPERATURE1 = "body-temperature1"
    BODY_TEMPERATURE2 = "body-temperature2"
    BLOOD_PRESSURE = "blood-pressure"
    WAVEFORM = "waveform"
    DEVICE_CONNECTION = "device-connection"
    WAVEFORM_II = "waveform_II"
    WAVEFORM_PLETH = "waveform_Pleth"
    WAVEFORM_RESPIRATION = "waveform_Respiration"

    @classmethod
    def as_choices(cls):
        """Return choices for use in a Serializer field."""
        return [(x.value, x.value) for x in cls]


class StatusChoices(str, Enum):
    FINAL = "final"
    LEADS_OFF = "Message-Leads Off"
    MEASUREMENT_INVALID = "Message-Measurement Invalid"
    TACHY_CARDIA = "Message-Tachy Cardia"
    PROBE_UNPLUGGED = "Message-Probe Unplugged"
    CONNECTED = "Connected"
    DISCONNECTED = "Disconnected"

    @classmethod
    def as_choices(cls):
        """Return choices for use in a Serializer field."""
        return [(x.value, x.value) for x in cls]


class InterpretationChoices(str, Enum):
    NORMAL = "normal"
    LOW = "low"
    HIGH = "high"
    NA = "NA"

    @classmethod
    def as_choices(cls):
        """Return choices for use in a Serializer field."""
        return [(x.value, x.value) for x in cls]


class WaveNameChoices(str, Enum):
    II = "II"
    PLETH = "Pleth"
    RESPIRATION = "Respiration"

    @classmethod
    def as_choices(cls):
        """Return choices for use in a Serializer field."""
        return [(x.value, x.value) for x in cls]


class BloodPressureSerializer(serializers.Serializer):
    value = serializers.FloatField(required=False, allow_null=True)
    unit = serializers.CharField(max_length=50, required=False, allow_null=True)
    interpretation = serializers.CharField(
        max_length=10, required=False, allow_null=True
    )
    low_limit = serializers.FloatField(required=False, allow_null=True)
    high_limit = serializers.FloatField(required=False, allow_null=True)


class ObservationSerializer(serializers.Serializer):
    observation_id = serializers.ChoiceField(choices=ObservationIDChoices.as_choices())
    device_id = serializers.CharField(max_length=100)
    date_time = serializers.DateTimeField()
    patient_id = serializers.CharField(max_length=100)
    patient_name = serializers.CharField(
        max_length=100, required=False, allow_null=True
    )
    status = serializers.ChoiceField(
        choices=StatusChoices.as_choices(), required=False, allow_null=True
    )
    value = serializers.FloatField(required=False, allow_null=True)
    unit = serializers.CharField(max_length=50, required=False, allow_null=True)
    interpretation = serializers.ChoiceField(
        choices=InterpretationChoices.as_choices(), required=False, allow_null=True
    )
    low_limit = serializers.FloatField(required=False, allow_null=True)
    high_limit = serializers.FloatField(required=False, allow_null=True)
    systolic = BloodPressureSerializer(required=False, allow_null=True)
    diastolic = BloodPressureSerializer(required=False, allow_null=True)
    map = BloodPressureSerializer(required=False, allow_null=True)
    wave_name = serializers.ChoiceField(
        choices=WaveNameChoices.as_choices(), required=False, allow_null=True
    )
    resolution = serializers.CharField(max_length=50, required=False, allow_null=True)
    sampling_rate = serializers.CharField(
        max_length=50, required=False, allow_null=True
    )
    data_baseline = serializers.FloatField(required=False, allow_null=True)
    data_low_limit = serializers.FloatField(required=False, allow_null=True)
    data_high_limit = serializers.FloatField(required=False, allow_null=True)
    data = serializers.CharField(required=False, allow_null=True)

    def to_internal_value(self, data):
        data["date_time"] = data.pop("date-time")
        data["patient_id"] = data.pop("patient-id")
        data["patient_name"] = data.pop("patient-name")
        if data.get("wave-name"):
            data["wave_name"] = data.pop("wave-name")
        if data.get("sampling rate"):
            data["sampling_rate"] = data.pop("sampling rate")

        if data.get("data-baseline"):
            data["data_baseline"] = data.pop("data-baseline")

        if data.get("data-low-limit"):
            data["data_low_limit"] = data.pop("data-low-limit")

        if data.get("data-high-limit"):
            data["data_high_limit"] = data.pop("data-high-limit")
        if data.get("low-limit"):
            data["low_limit"] = data.pop("low-limit")

        if data.get("high-limit"):
            data["high_limit"] = data.pop("high-limit")

        return super().to_internal_value(data)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["date-time"] = ret.pop("date_time")
        ret["patient-id"] = ret.pop("patient_id")
        ret["patient-name"] = ret.pop("patient_name")

        if "wave_name" in ret:
            ret["wave-name"] = ret.pop("wave_name")
        if "sampling_rate" in ret:
            ret["sampling rate"] = ret.pop("sampling_rate")

        ret["low-limit"] = ret.pop("low_limit")
        ret["high-limit"] = ret.pop("high_limit")

        if "data_baseline" in ret:

            ret["data-baseline"] = ret.pop("data_baseline")

        if "data_low_limit" in ret:
            print()
            ret["data-low-limit"] = ret.pop("data_low_limit")

        if "data_high_limit" in ret:
            print(ret.get("data_high_limit"))
            ret["data-high-limit"] = ret.pop("data_high_limit")
        return ret

    def create_object(self, validated_data):
        # Here, 'Observation' is presumed to be your custom class
        return Observation(**validated_data)


class BloodPressureDailyRoundSerializer(serializers.Serializer):
    systolic = serializers.IntegerField(required=False, allow_null=True)
    diastolic = serializers.IntegerField(required=False, allow_null=True)
    mean = serializers.IntegerField(required=False, allow_null=True)


class DailyRoundObservationSerializer(serializers.Serializer):
    spo2 = serializers.FloatField(required=False, allow_null=True)
    ventilator_spo2 = serializers.FloatField(required=False, allow_null=True)
    resp = serializers.FloatField(required=False, allow_null=True)
    pulse = serializers.FloatField(required=False, allow_null=True)
    temperature = serializers.FloatField(required=False, allow_null=True)
    temperature_measured_at = serializers.DateTimeField(required=False, allow_null=True)
    bp = BloodPressureDailyRoundSerializer(required=False, allow_null=True)
    taken_at = serializers.DateTimeField(required=False, allow_null=True)
    rounds_type = serializers.ChoiceField(choices=["AUTOMATED"], required=False)
    is_parsed_by_ocr = serializers.BooleanField(required=False)


class Observation:
    def __init__(
        self,
        observation_id,
        device_id,
        date_time,
        patient_id,
        patient_name=None,
        status=None,
        value=None,
        unit=None,
        interpretation=None,
        low_limit=None,
        high_limit=None,
        systolic=None,
        diastolic=None,
        map=None,
        wave_name=None,
        resolution=None,
        sampling_rate=None,
        data_baseline=None,
        data_low_limit=None,
        data_high_limit=None,
        data=None,
    ):
        self.observation_id = observation_id
        self.device_id = device_id
        self.date_time = date_time
        self.patient_id = patient_id
        self.patient_name = patient_name
        self.status = status
        self.value = value
        self.unit = unit
        self.interpretation = interpretation
        self.low_limit = low_limit
        self.high_limit = high_limit
        self.systolic = systolic
        self.diastolic = diastolic
        self.map = map
        self.wave_name = wave_name
        self.resolution = resolution
        self.sampling_rate = sampling_rate
        self.data_baseline = data_baseline
        self.data_low_limit = data_low_limit
        self.data_high_limit = data_high_limit
        self.data = data
