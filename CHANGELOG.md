# Changelog

This changelog tracks changes of the qoqo_qiskit project starting at version 0.1.0 (initial release).

## 0.14.0

### Updated in 0.14.0

* Updated qiskit requirement from `"qiskit>=2.2,<2.3"` to `"qiskit>2.4.2,<=2.5.2"`.
* Updated qiskit-ibm-runtime requirement from `"qiskit_ibm_runtime>=0.41,<0.42"` to `"qiskit_ibm_runtime>=0.41,<=0.50"`.
* Updated tests to use qiskit 2.5.0 decompositions.

## 0.13.0

### Added in 0.13.0

* Added the `get_qoqo_noise_models_from_aer_noise_model` and `qoqo_device_from_qiskit_backend` functions.

## 0.12.0

### Added in 0.12.0

* Added `run_pauli_operator` and `measure_pauli_operator`.

## 0.11.0

### Updated in 0.11.0

* Updated minimum supported Python version from 3.9 to 3.10.
* Updated minimum supported qoqo_qasm version to 0.14.
* Updated minimum supported qiskit version to 2.2.
* Updated minimum supported qiskit_aer version to 0.17.
* Updated minimum supported qiskit_ibm_runtime version to 0.41.

### Added in 0.11.0

* Added `utils` module with `struqture_hamiltonian_to_qiskit_op`, making it possible to cast a struqture's PauliHamiltonian into a qiskit's SparsePauliOp.

### Changed in 0.11.0

* Archived `qoqo_qiskit_devices` and `roqoqo_qiskit_devices` packages.

## 0.10.1

### Fixed in 0.10.1

* Fixed an issue concerning the JobStatus check for QPUs jobs

## 0.10.0

### Updated in 0.10.0

* Updated to Pyo3 0.23, qoqo 1.19, ndarray 0.16, numpy 0.23

### Changed in 0.10.0

* Migrated `backend.run()` method to using qiskit's `Sampler`
* Temporarily removed support for statevector simulation (no support for `PragmaGetStateVector` and `PragmaGetDensityMatrix`)

## 0.9.0

### Fixed in 0.9.0

* Fixed bug involving the `_custom_gates_fix` method not being called correctly if `RotateXY` was inside a `PragmaLoop`

### Changed in 0.9.0

* Changed MSRV to 1.76
* Upped minimum required Python version to 3.9

## 0.8.1

### Fixed in 0.8.1

* Fixed `.run_program()` allowing it to run with a single list of parameters
* Fixed support for `InputBit` operation by keeping track of it and correct the circuit result in post-process

## 0.8.0

### Updated in 0.8.0

* Updated to qiskit 1.2

## 0.7.0

### Updated in 0.7.0

* Updated to pyo3 0.21

## 0.6.0

### Added in 0.6.0

* Added `transpiler_helper` submodule

## 0.5.0

### Added in 0.5.0

* Added `run_circuit_list()` and `run_circuit_list_queued()` allowing to have a single job reference a list of running circuits

### Changed in 0.5.0

* Simplified the registers representation via dataclasses

### Updated in 0.5.0

* Updated to qoqo 1.11

## 0.4.2

### Fixed in 0.4.2

* Fixed `RotateXY` qiskit equivalence

## 0.4.1

### Fixed in 0.4.1

* Fixed overwriting registers bug

## 0.4.0

### Added in 0.4.0

* Added `run_program()`, `run_program_queued()` allowing for multiple runs in one call thanks to a list of lists of parameter values

## 0.3.0

### Added in 0.3.0

* Added async support via `QueuedCircuitRun` and `QueuedProgramRun`

## 0.2.5

### Added in 0.2.5

* Added `get_noise_models` function

### Changed in 0.2.5

* Changed function name from `set_qiskit_noise_information` to `set_qiskit_device_information`
* Removed noise information from `set_qiskit_device_information`

## 0.2.4

### Added in 0.2.4

* Added support for `PragmaSleep`

## 0.2.3

### Added in 0.2.3

* Added support for Python 3.12
* Added deprecation warnings for retired devices (Lagos, Nairobi, Perth)

### Changed in 0.2.3

* Pinned qiskit dependency to <0.46

### Updated in 0.2.3

* Updated to qoqo 1.9

## 0.2.2

### Updated in 0.2.2

* Updated qoqo_qiskit_devices `get_decoherence_on_gate_model` method docstring

## 0.2.1

### Updated in 0.2.1

* Updated to qoqo 1.8
* Updated to Pyo3 0.20

## 0.2.0

### Added in 0.2.0

* Added `get_decoherence_on_gate_model` function.
* Added deprecation warnings for retired devices (Belem, Jakarta, Lima, Manila, Quito)
* Added `Identity` gate error info retrieval

### Updated in 0.2.0

* Updated to qoqo 1.7

## 0.1.10

### Fixed in 0.1.10

* Fixed linux deploy issues

### Updated in 0.1.10

* Updated to qoqo 1.6

## 0.1.9

### Fixed in 0.1.9

* Corrected `0.1.8` release issues
* Fixed README
* Fixed docs

## 0.1.8

### Added in 0.1.8

* Added `qoqo_qiskit_device_from_ibmq_identifier` function
* Added warning in case the dephasing obtained from IBM's machines turns out to be negative

## 0.1.7

### Fixed in 0.1.7

* Fixed missing transformation of T2 to Tphi

## 0.1.6

### Added in 0.1.6

* Added `to_generic_device` method

## 0.1.5

### Updated in 0.1.5

* Updated to qoqo 1.5
* Updated to pyo3 0.19

## 0.1.4

### Added in 0.1.4

* Added qoqo_qiskit_devices and roqoqo_qiskit_devices to the repository

## 0.1.3

### Fixed in 0.1.3

* Correcting Github release issues

## 0.1.2

### Added in 0.1.2

* Added support for `PragmaLoop`

## 0.1.1

### Fixed in 0.1.1

* Corrects initial release

## 0.1.0

### Added in 0.1.0

* Initial release
