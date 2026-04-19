from dataclasses import dataclass

from cyclonedds.idl import IdlStruct
from cyclonedds.idl.types import uint64, float64, bounded_str


@dataclass
class TrianglePose(IdlStruct):
    sequence_id: uint64
    name: bounded_str[32]
    x: float64
    y: float64
    theta: float64
    timestamp_ns: uint64


@dataclass
class TriangleMove(IdlStruct):
    sequence_id: uint64
    name: bounded_str[32]
    delta_lin: float64
    delta_theta: float64
    timestamp_ns: uint64
