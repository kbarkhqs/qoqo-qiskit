// Copyright © 2023 HQS Quantum Simulations GmbH. All Rights Reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except
// in compliance with the License. You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software distributed under the
// License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
// express or implied. See the License for the specific language governing permissions and
// limitations under the License.

//! IBM Devices
//!
//! Provides the devices that are used to execute quantum programs on IBM's devices.

use ndarray::{array, Array2};
use std::collections::HashMap;

use roqoqo::devices::{GenericDevice, QoqoDevice};
use roqoqo::RoqoqoError;

mod ibm_belem;
pub use crate::devices::ibm_belem::IBMBelemDevice;

mod ibm_jakarta;
pub use crate::devices::ibm_jakarta::IBMJakartaDevice;

mod ibm_lagos;
pub use crate::devices::ibm_lagos::IBMLagosDevice;

mod ibm_lima;
pub use crate::devices::ibm_lima::IBMLimaDevice;

mod ibm_manila;
pub use crate::devices::ibm_manila::IBMManilaDevice;

mod ibm_nairobi;
pub use crate::devices::ibm_nairobi::IBMNairobiDevice;

mod ibm_perth;
pub use crate::devices::ibm_perth::IBMPerthDevice;

mod ibm_quito;
pub use crate::devices::ibm_quito::IBMQuitoDevice;

/// Collection of IBM quantum devices.
///
pub enum IBMDevice {
    // IBMLagosDevice(IBMLagosDevice),
    // IBMNairobiDevice(IBMNairobiDevice),
    // IBMPerthDevice(IBMPerthDevice),
    IBMBelemDevice(IBMBelemDevice),
    // IBMJakartaDevice(IBMJakartaDevice),
    // IBMLimaDevice(IBMLimaDevice),
    // IBMManilaDevice(IBMManilaDevice),
    // IBMQuitoDevice(IBMQuitoDevice),
}

type TwoQubitGates = HashMap<(usize, usize), f64>;

pub trait IBMDeviceTrait: QoqoDevice + Clone {
    /// Returns the IBM's identifier.
    ///
    /// # Returns
    ///
    /// A str of the name IBM uses as identifier.
    fn name(&self) -> &'static str;

    /// Returns the IBM's identifier.
    ///
    /// # Returns
    ///
    /// A str of the name IBM uses as identifier.
    fn single_qubit_gates(&mut self) -> &mut HashMap<String, HashMap<usize, f64>>;

    /// Returns the IBM's identifier.
    ///
    /// # Returns
    ///
    /// A str of the name IBM uses as identifier.
    fn two_qubit_gates(&mut self) -> &mut HashMap<String, TwoQubitGates>;

    /// Returns the IBM's identifier.
    ///
    /// # Returns
    ///
    /// A str of the name IBM uses as identifier.
    fn decoherence_rates(&mut self) -> &mut HashMap<usize, Array2<f64>>;

    /// Setting the gate time of a single qubit gate.
    ///
    /// # Arguments
    ///
    /// * `gate` - hqslang name of the single-qubit-gate.
    /// * `qubit` - The qubit for which the gate time is set.
    /// * `gate_time` - gate time for the given gate.
    fn set_single_qubit_gate_time(
        &mut self,
        gate: &str,
        qubit: usize,
        gate_time: f64,
    ) -> Result<(), RoqoqoError> {
        if qubit >= self.number_qubits() {
            return Err(RoqoqoError::GenericError {
                msg: format!(
                    "Qubit {} larger than number qubits {}",
                    qubit,
                    self.number_qubits()
                ),
            });
        }
        match self.single_qubit_gates().get_mut(gate) {
            Some(gate_times) => {
                let gatetime = gate_times.entry(qubit).or_insert(gate_time);
                *gatetime = gate_time;
            }
            None => {
                let mut new_map = HashMap::new();
                new_map.insert(qubit, gate_time);
                self.single_qubit_gates().insert(gate.to_string(), new_map);
            }
        }
        Ok(())
    }

    /// Setting the gate time of a two qubit gate.
    ///
    /// # Arguments
    ///
    /// * `gate` - hqslang name of the two-qubit-gate.
    /// * `control` - The control qubit for which the gate time is set.
    /// * `target` - The target qubit for which the gate time is set.
    /// * `gate_time` - gate time for the given gate.
    fn set_two_qubit_gate_time(
        &mut self,
        gate: &str,
        control: usize,
        target: usize,
        gate_time: f64,
    ) -> Result<(), RoqoqoError> {
        if control >= self.number_qubits() {
            return Err(RoqoqoError::GenericError {
                msg: format!(
                    "Qubit {} larger than number qubits {}",
                    control,
                    self.number_qubits()
                ),
            });
        }
        if target >= self.number_qubits() {
            return Err(RoqoqoError::GenericError {
                msg: format!(
                    "Qubit {} larger than number qubits {}",
                    target,
                    self.number_qubits()
                ),
            });
        }
        if !self
            .two_qubit_edges()
            .iter()
            .any(|&(a, b)| (a, b) == (control, target) || (a, b) == (target, control))
        {
            return Err(RoqoqoError::GenericError {
                msg: format!(
                    "Qubits {} and {} are not connected in the device",
                    control, target
                ),
            });
        }

        match self.two_qubit_gates().get_mut(gate) {
            Some(gate_times) => {
                let gatetime = gate_times.entry((control, target)).or_insert(gate_time);
                *gatetime = gate_time;
            }
            None => {
                let mut new_map = HashMap::new();
                new_map.insert((control, target), gate_time);
                self.two_qubit_gates().insert(gate.to_string(), new_map);
            }
        }
        Ok(())
    }

    /// Adds qubit damping to noise rates.
    ///
    /// # Arguments
    ///
    /// * `qubit` - The qubit for which the dampins is added.
    /// * `daming` - The damping rates.
    fn add_damping(&mut self, qubit: usize, damping: f64) -> Result<(), RoqoqoError> {
        if qubit > self.number_qubits() {
            return Err(RoqoqoError::GenericError {
                msg: format!(
                    "Qubit {} out of range for device of size {}",
                    qubit,
                    self.number_qubits()
                ),
            });
        }
        let aa = self
            .decoherence_rates()
            .entry(qubit)
            .or_insert_with(|| Array2::zeros((3, 3)));
        *aa = aa.clone() + array![[damping, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]];
        Ok(())
    }

    /// Adds qubit dephasing to noise rates.
    ///
    /// # Arguments
    ///
    /// * `qubit` - The qubit for which the dephasing is added.
    /// * `dephasing` - The dephasing rates.
    fn add_dephasing(&mut self, qubit: usize, dephasing: f64) -> Result<(), RoqoqoError> {
        if qubit > self.number_qubits() {
            return Err(RoqoqoError::GenericError {
                msg: format!(
                    "Qubit {} out of range for device of size {}",
                    qubit,
                    self.number_qubits()
                ),
            });
        }
        let aa = self
            .decoherence_rates()
            .entry(qubit)
            .or_insert_with(|| Array2::zeros((3, 3)));
        *aa = aa.clone() + array![[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, dephasing]];
        Ok(())
    }

    /// Converts the device to a qoqo GenericDevice.
    ///
    /// # Returns
    ///
    /// * `GenericDevice` - The converted device.
    /// * `RoqoqoError` - The error propagated from adding gate times and decoherence rates.
    fn to_generic_device(&self) -> Result<GenericDevice, RoqoqoError> {
        let mut new_generic_device = GenericDevice::new(self.number_qubits());

        // Gate times
        for gate in self.single_qubit_gate_names() {
            for qubit in 0..self.number_qubits() {
                if let Some(x) = self.single_qubit_gate_time(gate.as_str(), &qubit) {
                    new_generic_device.set_single_qubit_gate_time(gate.as_str(), qubit, x)?;
                }
            }
        }
        for gate in self.two_qubit_gate_names() {
            for (control, target) in self.two_qubit_edges() {
                if let Some(x) = self.two_qubit_gate_time(gate.as_str(), &control, &target) {
                    new_generic_device.set_two_qubit_gate_time(
                        gate.as_str(),
                        control,
                        target,
                        x,
                    )?;
                }
            }
            for (control, target) in self.two_qubit_edges() {
                if let Some(x) = self.two_qubit_gate_time(gate.as_str(), &target, &control) {
                    new_generic_device.set_two_qubit_gate_time(
                        gate.as_str(),
                        target,
                        control,
                        x,
                    )?;
                }
            }
        }
        // for gate in self.multi_qubit_gate_names() {} // - skipped here as none of the devies have multi-qubit gates

        // Decoherence rates
        for qubit in 0..self.number_qubits() {
            if let Some(x) = self.qubit_decoherence_rates(&qubit) {
                new_generic_device.set_qubit_decoherence_rates(qubit, x)?;
            }
        }

        Ok(new_generic_device)
    }
}
