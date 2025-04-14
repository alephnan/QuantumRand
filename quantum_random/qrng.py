"""
Quantum Random Number Generator (QRNG) implemented using Qiskit.
This module creates quantum circuits that generate random bits based on quantum superposition.
"""

from qiskit import QuantumCircuit, execute
import numpy as np
import matplotlib.pyplot as plt

# First try to import Aer, but fall back to BasicAer if not available
try:
    from qiskit import Aer
    HAS_AER = True
except ImportError:
    from qiskit import BasicAer
    HAS_AER = False
    print("Warning: qiskit-aer not found, falling back to BasicAer simulator. Install qiskit-aer for better performance.")

try:
    from qiskit.visualization import plot_histogram
    HAS_VISUALIZATION = True
except ImportError:
    HAS_VISUALIZATION = False
    print("Warning: qiskit visualization module not available. Some plotting features may be limited.")

class QuantumRandomNumberGenerator:
    """
    A class to generate random numbers using quantum circuits.
    """
    
    def __init__(self, num_qubits=1):
        """
        Initialize the QRNG with the specified number of qubits.
        
        Args:
            num_qubits (int): Number of qubits to use in the circuit
        """
        self.num_qubits = num_qubits
        
        # Use Aer simulator if available, otherwise use BasicAer
        if HAS_AER:
            self.simulator = Aer.get_backend('qasm_simulator')
        else:
            self.simulator = BasicAer.get_backend('qasm_simulator')
        
    def _create_circuit(self):
        """
        Create a quantum circuit that generates random bits.
        
        Returns:
            QuantumCircuit: A quantum circuit with Hadamard gates applied to all qubits
        """
        # Create a quantum circuit with qubits and classical bits
        circuit = QuantumCircuit(self.num_qubits, self.num_qubits)
        
        # Apply Hadamard gates to all qubits to create superposition
        for qubit in range(self.num_qubits):
            circuit.h(qubit)
            
        # Measure all qubits
        circuit.measure(range(self.num_qubits), range(self.num_qubits))
        
        return circuit
    
    def generate_random_bits(self, num_shots=1024):
        """
        Generate random bits using the quantum circuit.
        
        Args:
            num_shots (int): Number of times to run the circuit
            
        Returns:
            dict: Counts of each bit pattern
            list: List of individual bit strings generated
        """
        # Create and execute the circuit
        circuit = self._create_circuit()
        job = execute(circuit, self.simulator, shots=num_shots)
        result = job.result()
        counts = result.get_counts(circuit)
        
        # Convert counts to a list of individual results
        bit_strings = []
        for bit_string, count in counts.items():
            bit_strings.extend([bit_string] * count)
            
        # Shuffle to ensure randomness in the order
        np.random.shuffle(bit_strings)
        
        return counts, bit_strings[:num_shots]
    
    def generate_random_integers(self, min_val=0, max_val=1, num_samples=1024):
        """
        Generate random integers within a range using quantum random bits.
        
        Args:
            min_val (int): Minimum value (inclusive)
            max_val (int): Maximum value (inclusive)
            num_samples (int): Number of random integers to generate
            
        Returns:
            list: List of random integers
        """
        # Calculate how many qubits are needed to represent the range
        range_size = max_val - min_val + 1
        bits_needed = max(1, int(np.ceil(np.log2(range_size))))
        
        # Temporarily set the number of qubits
        original_qubits = self.num_qubits
        self.num_qubits = bits_needed
        
        # Generate random bits
        _, bit_strings = self.generate_random_bits(num_samples)
        
        # Convert bit strings to integers
        random_integers = []
        for bit_string in bit_strings:
            # Convert binary string to integer
            int_val = int(bit_string, 2)
            
            # Map to the desired range if within bounds
            if int_val < range_size:
                random_integers.append(int_val + min_val)
            else:
                # If the value exceeds our range, we'll need to generate another
                # For simplicity, we'll just take the modulo for now
                random_integers.append((int_val % range_size) + min_val)
        
        # Reset the number of qubits
        self.num_qubits = original_qubits
        
        return random_integers
    
    def plot_distribution(self, counts, title="Quantum Random Bit Distribution"):
        """
        Plot the distribution of quantum random bits.
        
        Args:
            counts (dict): Counts of each bit pattern
            title (str): Title for the plot
            
        Returns:
            matplotlib.figure.Figure: Figure object containing the plot
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if HAS_VISUALIZATION:
            plot_histogram(counts, title=title, ax=ax)
        else:
            # Create a simple bar chart if plot_histogram is not available
            patterns = list(counts.keys())
            values = list(counts.values())
            ax.bar(patterns, values)
            ax.set_xlabel('Bit Pattern')
            ax.set_ylabel('Frequency')
            ax.set_title(title)
            
        return fig

# Example usage
if __name__ == "__main__":
    # Create a QRNG with 3 qubits
    qrng = QuantumRandomNumberGenerator(num_qubits=3)
    
    # Generate 1000 random bit patterns
    counts, bit_strings = qrng.generate_random_bits(num_shots=1000)
    
    # Print the first 10 bit strings
    print("First 10 random bit strings:", bit_strings[:10])
    
    # Generate 20 random integers between 1 and 100
    random_integers = qrng.generate_random_integers(min_val=1, max_val=100, num_samples=20)
    print("Random integers:", random_integers)
    
    # Plot the distribution
    fig = qrng.plot_distribution(counts)
    plt.show() 