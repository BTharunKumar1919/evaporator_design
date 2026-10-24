"""Small, explicit engineering unit conversions used by the calculation layer."""


def mm_to_m(value: float) -> float:
    return float(value) / 1000.0


def m_to_mm(value: float) -> float:
    return float(value) * 1000.0


def kJ_to_J(value: float) -> float:
    return float(value) * 1000.0


def J_to_kJ(value: float) -> float:
    return float(value) / 1000.0


def kPa_to_Pa(value: float) -> float:
    return float(value) * 1000.0


def Pa_to_kPa(value: float) -> float:
    return float(value) / 1000.0
