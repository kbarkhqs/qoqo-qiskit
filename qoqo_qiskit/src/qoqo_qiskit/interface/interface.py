# Copyright © 2023-2025 HQS Quantum Simulations GmbH.
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
"""Qiskit interface for qoqo circuits."""

from qoqo import Circuit
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

from qoqo_qasm import QasmBackend

from typing import Tuple, Optional, Dict, Any


def to_qiskit_circuit(
    circuit: Circuit, qubit_register_name: Optional[str] = None
) -> Tuple[QuantumCircuit, Dict[str, int]]:
    """Applies the qoqo Circuit -> Qiskit QuantumCircuit conversion.

    Args:
        circuit (Circuit): the qoqo Circuit to port.
        qubit_register_name (Optional[str]): the name of the qubit register.

    Returns:
        Tuple[QuantumCircuit, Dict[str, int]]: equivalent QuantumCircuit and dict\
                                            containing info for Qiskit's backend.

    Raises:
        ValueError: the circuit contains a symbolic PragmaLoop operation.
    """
    filtered_circuit, circuit_info, initial_statevector, to_fix = _filter_circuit(circuit)

    # qoqo_qasm call
    qasm_backend = QasmBackend(qubit_register_name=qubit_register_name)
    input_qasm_str = qasm_backend.circuit_to_qasm_str(filtered_circuit)

    # QASM -> Qiskit transformation
    return_circuit: QuantumCircuit
    from_qasm_circuit = QuantumCircuit.from_qasm_str(input_qasm_str)

    # Fixing custom gates qiskit translation
    if to_fix:
        from_qasm_circuit = _custom_gates_fix(from_qasm_circuit)

    # Handling PragmaSetStateVector
    if len(initial_statevector) != 0:
        qregs = []
        for qreg in from_qasm_circuit.qregs:
            qregs.append(QuantumRegister(qreg.size, qreg.name))
        cregs = []
        for creg in from_qasm_circuit.cregs:
            cregs.append(ClassicalRegister(creg.size, creg.name))
        regs = qregs + cregs
        initial_circuit = QuantumCircuit(*regs)
        initial_circuit.initialize(initial_statevector)
        return_circuit = initial_circuit.compose(from_qasm_circuit)
    else:
        return_circuit = from_qasm_circuit

    return (return_circuit, circuit_info)


def _filter_circuit(circuit: Circuit) -> Circuit:
    # Populating dict output. Currently handling:
    #   - PragmaSetStateVector (continues further down)
    #   - PragmaGetStateVector
    #   - PragmaGetDensityMatrix
    #   - PragmaSetNumberOfMeasurement
    #   - PragmaRepeatedMeasurement
    #   - PragmaLoop
    #   - MeasureQubit
    filtered_circuit = Circuit()
    to_fix = False
    circuit_info: Dict[str, Any] = {}
    circuit_info["MeasurementInfo"] = {}
    circuit_info["SimulationInfo"] = {}
    circuit_info["SimulationInfo"]["PragmaGetStateVector"] = False
    circuit_info["SimulationInfo"]["PragmaGetDensityMatrix"] = False
    initial_statevector = []

    for op in circuit:
        if "PragmaSetStateVector" in op.tags():
            initial_statevector = op.statevector()
        elif "PragmaRepeatedMeasurement" in op.tags():
            if "PragmaRepeatedMeasurement" not in circuit_info["MeasurementInfo"]:
                circuit_info["MeasurementInfo"]["PragmaRepeatedMeasurement"] = []
            circuit_info["MeasurementInfo"]["PragmaRepeatedMeasurement"].append(
                (op.readout(), op.number_measurements(), op.qubit_mapping())
            )
            filtered_circuit += op
        elif "MeasureQubit" in op.tags():
            if "MeasureQubit" not in circuit_info["MeasurementInfo"]:
                circuit_info["MeasurementInfo"]["MeasureQubit"] = []
            circuit_info["MeasurementInfo"]["MeasureQubit"].append(
                (op.qubit(), op.readout(), op.readout_index())
            )
            filtered_circuit += op
        elif "PragmaSetNumberOfMeasurements" in op.tags():
            if "PragmaSetNumberOfMeasurements" not in circuit_info["SimulationInfo"]:
                circuit_info["SimulationInfo"]["PragmaSetNumberOfMeasurements"] = []
            circuit_info["SimulationInfo"]["PragmaSetNumberOfMeasurements"].append(
                (op.readout(), op.number_measurements())
            )
        elif "PragmaGetStateVector" in op.tags():
            circuit_info["SimulationInfo"]["PragmaGetStateVector"] = True
        elif "PragmaGetDensityMatrix" in op.tags():
            circuit_info["SimulationInfo"]["PragmaGetDensityMatrix"] = True
        elif "PragmaLoop" in op.tags():
            if op.repetitions().is_float:
                for _ in range(int(op.repetitions().float())):
                    filtered_circuit += op.circuit()
                for in_op in filtered_circuit:
                    if "PragmaSleep" in in_op.tags() or "RotateXY" in in_op.tags():
                        to_fix = True
            else:
                raise ValueError("A symbolic PragmaLoop operation is not supported.")
        elif "PragmaSleep" in op.tags() or "RotateXY" in op.tags():
            to_fix = True
            filtered_circuit += op
        else:
            filtered_circuit += op

    return filtered_circuit, circuit_info, initial_statevector, to_fix


def _custom_gates_fix(from_qasm_circuit: QuantumCircuit) -> QuantumCircuit:
    """Transforms the custom gates imported by qiskit via QASM to correct qiskit Instructions.

    In case of incompatibilities, this step allows to directly keep the already transformed
    QuantumCircuit and modify the Instruction references imported via QASM.

    Args:
        from_qasm_circuit (QuantumCircuit): the qiskit QuantumCircuit to modify.

    Returns:
        QuantumCircuit: the modified qiskit QuantumCircuit.
    """
    out_circuit = from_qasm_circuit.copy_empty_like()
    for inst, qargs, cargs in from_qasm_circuit.data:
        if inst.name == "pragmasleep":
            out_circuit.delay(inst.params[0], qargs[0], unit="s")
        elif inst.name == "rxy":
            out_circuit.r(inst.params[0], inst.params[1], qargs[0])
        else:
            out_circuit.append(inst, qargs, cargs)
    return out_circuit
