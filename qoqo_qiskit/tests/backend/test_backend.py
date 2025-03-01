# Copyright © 2023 HQS Quantum Simulations GmbH.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License
# is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
# or implied. See the License for the specific language governing permissions and limitations under
# the License.
"""Test file for backend.py."""

import pytest
import sys

from qoqo import Circuit
from qoqo import operations as ops
from qoqo.measurements import (  # type:ignore
    ClassicalRegister,
    PauliZProduct,
    PauliZProductInput,
)

from qiskit_aer import AerSimulator

from qoqo_qiskit.backend import QoqoQiskitBackend  # type:ignore

from typing import List, Any


def test_constructor() -> None:
    """Test QoqoQiskitBackend constructor."""
    simulator = AerSimulator()
    try:
        _ = QoqoQiskitBackend()
        _ = QoqoQiskitBackend(simulator)
        _ = QoqoQiskitBackend(simulator, memory=True)
    except Exception:
        AssertionError()

    with pytest.raises(TypeError) as exc:
        _ = QoqoQiskitBackend("wrong_name")
    assert "The input is not a valid Qiskit Backend instance." in str(exc.value)


@pytest.mark.parametrize(
    "operations",
    [
        [ops.PauliX(1), ops.PauliX(0), ops.PauliZ(2), ops.PauliX(3), ops.PauliY(4)],
        [
            ops.Hadamard(0),
            ops.CNOT(0, 1),
            ops.CNOT(1, 2),
            ops.CNOT(2, 3),
            ops.CNOT(3, 4),
        ],
        [ops.RotateX(0, 0.23), ops.RotateY(1, 0.12), ops.RotateZ(2, 0.34)],
    ],
)
def test_run_circuit_errors(operations: List[Any]) -> None:
    """Test QoqoQiskitBackend.run_circuit method errors."""
    backend = QoqoQiskitBackend()

    circuit = Circuit()
    involved_qubits = set()
    for op in operations:
        involved_qubits.update(op.involved_qubits())
        circuit += op

    with pytest.raises(ValueError) as exc:
        _ = backend.run_circuit(circuit)
    assert (
        "The Circuit does not contain Measurement, PragmaGetStateVector or "
        "PragmaGetDensityMatrix operations. Simulation not possible." in str(exc.value)
    )

    circuit_1 = Circuit()
    circuit_1 += circuit
    circuit_1 += ops.DefinitionComplex("ri", len(involved_qubits), True)
    circuit_1 += ops.PragmaGetStateVector("ri", None)
    circuit_1 += ops.PragmaGetDensityMatrix("ri", None)

    with pytest.raises(ValueError) as exc:
        _ = backend.run_circuit(circuit_1)
    assert (
        "The Circuit contains both a PragmaGetStateVector and a PragmaGetDensityMatrix "
        "instruction. Simulation not possible." in str(exc.value)
    )

    circuit_2 = Circuit()
    circuit_2 += circuit
    circuit_2 += ops.DefinitionBit("ri", len(involved_qubits), True)
    for i in range(len(involved_qubits)):
        circuit_2 += ops.MeasureQubit(i, "ri", i)
    circuit_2 += ops.PragmaRepeatedMeasurement("ri", 10)

    with pytest.raises(ValueError) as exc:
        _ = backend.run_circuit(circuit_2)
    assert "Only input Circuits containing one type of measurement." in str(exc.value)

    circuit_3 = Circuit()
    circuit_3 += circuit
    circuit_3 += ops.DefinitionBit("ri", len(involved_qubits), True)
    circuit_3 += ops.PragmaRepeatedMeasurement("ri", 10)

    try:
        _ = backend.run_circuit(circuit_3)
    except Exception:
        assert AssertionError("Correct Circuit failed on '.run_circuit()' call.")


@pytest.mark.parametrize(
    "operations",
    [
        [ops.PauliX(1), ops.PauliX(0), ops.PauliZ(2), ops.PauliX(3), ops.PauliY(4)],
        [
            ops.Hadamard(0),
            ops.CNOT(0, 1),
            ops.CNOT(1, 2),
            ops.CNOT(2, 3),
            ops.CNOT(3, 4),
        ],
        [ops.RotateX(0, 0.23), ops.RotateY(1, 0.12), ops.RotateZ(2, 0.34)],
    ],
)
def test_run_circuit_results(operations: List[Any]) -> None:
    """Test QoqoQiskitBackend.run_circuit method results."""
    backend = QoqoQiskitBackend()

    circuit = Circuit()
    involved_qubits = set()
    for op in operations:
        involved_qubits.update(op.involved_qubits())
        circuit += op

    circuit_1 = Circuit()
    circuit_1 += circuit
    circuit_1 += ops.DefinitionBit("ri", len(involved_qubits), True)
    circuit_1 += ops.PragmaRepeatedMeasurement("ri", 10)

    result = backend.run_circuit(circuit_1)

    assert result[0]
    assert result[0]["ri"]
    assert not result[1]
    assert not result[2]

    circuit_2 = Circuit()
    circuit_2 += circuit
    circuit_2 += ops.DefinitionComplex("ri", len(involved_qubits), True)
    circuit_2 += ops.PragmaGetStateVector("ri", None)

    result = backend.run_circuit(circuit_2)

    assert not result[0]
    assert not result[1]
    assert result[2]
    assert result[2]["ri"]
    assert len(result[2]["ri"][0]) == 2 ** len(involved_qubits)

    circuit_3 = Circuit()
    circuit_3 += circuit
    circuit_3 += ops.DefinitionComplex("ri", len(involved_qubits), True)
    circuit_3 += ops.PragmaGetDensityMatrix("ri", None)

    result = backend.run_circuit(circuit_3)

    assert not result[0]
    assert not result[1]
    assert result[2]
    assert result[2]["ri"]
    assert len(result[2]["ri"][0]) == (2 ** len(involved_qubits)) ** 2


@pytest.mark.parametrize(
    "operations",
    [
        [ops.PauliX(1), ops.PauliX(0), ops.PauliZ(2), ops.PauliX(3), ops.PauliY(4)],
        [
            ops.Hadamard(0),
            ops.CNOT(0, 1),
            ops.CNOT(1, 2),
            ops.CNOT(2, 3),
            ops.CNOT(3, 4),
        ],
        [ops.RotateX(0, 0.23), ops.RotateY(1, 0.12), ops.RotateZ(2, 0.34)],
    ],
)
def test_measurement_register_classicalregister(operations: List[Any]) -> None:
    """Test QoqoQiskitBackend.run_measurement_registers method classical registers."""
    backend = QoqoQiskitBackend()

    circuit = Circuit()
    involved_qubits = set()
    for op in operations:
        involved_qubits.update(op.involved_qubits())
        circuit += op

    circuit += ops.DefinitionBit("ri", len(involved_qubits), True)
    circuit += ops.PragmaRepeatedMeasurement("ri", 10)

    measurement = ClassicalRegister(constant_circuit=None, circuits=[circuit])

    try:
        output = backend.run_measurement_registers(measurement=measurement)
    except Exception:
        AssertionError()

    assert output[0]["ri"]
    assert len(output[0]["ri"][0]) == len(involved_qubits)
    assert not output[1]
    assert not output[2]


@pytest.mark.parametrize(
    "operations",
    [
        [ops.PauliX(1), ops.PauliX(0), ops.PauliZ(2), ops.PauliX(3), ops.PauliY(4)],
        [
            ops.Hadamard(0),
            ops.CNOT(0, 1),
            ops.CNOT(1, 2),
            ops.CNOT(2, 3),
            ops.CNOT(3, 4),
        ],
        [ops.RotateX(0, 0.23), ops.RotateY(1, 0.12), ops.RotateZ(2, 0.34)],
    ],
)
def test_measurement(operations: List[Any]) -> None:
    """Test QoqoQiskitBackend.run_measurement method."""
    backend = QoqoQiskitBackend()

    circuit = Circuit()
    involved_qubits = set()
    for op in operations:
        involved_qubits.update(op.involved_qubits())
        circuit += op

    circuit += ops.DefinitionBit("ri", len(involved_qubits), True)
    circuit += ops.PragmaRepeatedMeasurement("ri", 10)

    pzpinput = PauliZProductInput(number_qubits=len(involved_qubits), use_flipped_measurement=True)

    measurement = PauliZProduct(constant_circuit=None, circuits=[circuit], input=pzpinput)

    try:
        _ = backend.run_measurement(measurement=measurement)
    except Exception:
        AssertionError()


def test_run_options() -> None:
    """Test QoqoQiskitBackend.run_circuit method with modified run option."""
    backend = QoqoQiskitBackend()

    circuit = Circuit()
    circuit += ops.Hadamard(0)
    circuit += ops.CNOT(0, 1)

    circuit_0 = Circuit()
    circuit_0 += circuit
    circuit_0 += ops.DefinitionBit("ri", 2, True)
    circuit_0 += ops.PragmaRepeatedMeasurement("ri", 1000)

    result = backend.run_circuit(circuit_0)

    assert len(result[0]["ri"]) == 1000

    circuit_1 = Circuit()
    circuit_1 += circuit
    circuit_1 += ops.DefinitionBit("ro", 2, True)
    circuit_1 += ops.MeasureQubit(0, "ro", 0)
    circuit_1 += ops.MeasureQubit(1, "ro", 1)
    circuit_1 += ops.PragmaSetNumberOfMeasurements(250, "ro")

    result = backend.run_circuit(circuit_1)

    assert len(result[0]["ro"]) == 250


def test_debugged_circuit() -> None:
    """Test QoqoQiskitBackend.run_circuit method with repeated Definition operations."""
    backend = QoqoQiskitBackend()

    circuit = Circuit()
    circuit += ops.DefinitionBit("ri", 1, True)
    circuit += ops.DefinitionBit("ri", 1, True)
    circuit += ops.DefinitionBit("ro", 1, True)
    circuit += ops.MeasureQubit(0, "ri", 0)
    circuit += ops.MeasureQubit(1, "ro", 0)

    circuit_test = Circuit()
    circuit_test += ops.DefinitionBit("ri", 1, True)
    circuit_test += ops.DefinitionBit("ro", 1, True)
    circuit_test += ops.MeasureQubit(0, "ri", 0)
    circuit_test += ops.MeasureQubit(1, "ro", 0)

    result = backend.run_circuit(circuit)
    comparison = backend.run_circuit(circuit_test)

    assert result == comparison


@pytest.mark.parametrize(
    "operations, outcome",
    [
        (
            [
                ops.PauliX(0),
                ops.CNOT(0, 1),
                ops.PauliX(2),
                ops.CNOT(0, 1),
                ops.PauliX(3),
            ],
            [True, False, True, True],
        ),
        (
            [
                ops.PauliX(0),
                ops.CNOT(0, 1),
                ops.CNOT(1, 2),
                ops.CNOT(2, 3),
                ops.PauliX(0),
                ops.PauliX(2),
            ],
            [False, True, False, True],
        ),
        (
            [ops.PauliX(0), ops.PauliX(2), ops.PauliX(2), ops.CNOT(0, 1)],
            [True, True, False],
        ),
    ],
)
def test_deterministic_circuit(operations: List[Any], outcome: List[bool]) -> None:
    """Test QoqoQiskitBackend deterministc circuit."""
    backend = QoqoQiskitBackend()

    circuit = Circuit()
    involved_qubits = set()
    for op in operations:
        involved_qubits.update(op.involved_qubits())
        circuit += op
    circuit += ops.DefinitionBit("ro", len(involved_qubits), True)
    circuit += ops.PragmaRepeatedMeasurement("ro", 10)

    result = backend.run_circuit(circuit)

    for el in result[0]["ro"]:
        assert el == outcome


def test_memory() -> None:
    """Test QoqoQiskitBackend memory parameter."""
    backend_no_mem = QoqoQiskitBackend(memory=False)
    backend_mem = QoqoQiskitBackend(memory=True)

    circuit = Circuit()
    circuit += ops.PauliX(0)
    circuit += ops.PauliX(2)

    circuit += ops.DefinitionBit("ro", 2, True)
    circuit += ops.DefinitionBit("ri", 1, True)
    circuit += ops.MeasureQubit(0, "ro", 0)
    circuit += ops.MeasureQubit(1, "ro", 1)
    circuit += ops.MeasureQubit(2, "ri", 0)

    result_no_mem = backend_no_mem.run_circuit(circuit)
    result_mem = backend_mem.run_circuit(circuit)

    for el1, el2 in zip(result_no_mem, result_mem):
        assert el1 == el2


def test_split() -> None:
    """Test QoqoQiskitBackend._split method."""
    clas_regs = {}
    clas_regs["ro"] = 1
    clas_regs["ri"] = 2
    shot_result_ws = "01 1"
    shot_result_no_ws = "011"

    backend_no_mem = QoqoQiskitBackend(memory=False)
    backend_mem = QoqoQiskitBackend(memory=True)

    assert backend_mem._split(shot_result_ws, clas_regs) == backend_mem._split(
        shot_result_no_ws, clas_regs
    )
    assert backend_no_mem._split(shot_result_ws, clas_regs) == backend_no_mem._split(
        shot_result_no_ws, clas_regs
    )


# For pytest
if __name__ == "__main__":
    pytest.main(sys.argv)
