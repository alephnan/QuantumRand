"""
Flask application for the QuantumRand project.
"""

from flask import Flask, jsonify, render_template, request, send_from_directory
import json
import os
from quantum_random import QuantumRandomNumberGenerator, RandomnessComparison

app = Flask(__name__, static_folder='frontend', static_url_path='')

# Initialize the quantum random number generator and comparison objects
qrng = QuantumRandomNumberGenerator(num_qubits=3)
comparison = RandomnessComparison(num_qubits=3)

@app.route('/')
def index():
    """
    Serve the main index.html page.
    """
    return send_from_directory('frontend', 'index.html')

@app.route('/api/quantum-bits', methods=['GET'])
def get_quantum_bits():
    """
    API endpoint to generate quantum random bits.
    
    Query Parameters:
        num_qubits (int): Number of qubits to use
        num_shots (int): Number of times to run the circuit
        
    Returns:
        JSON: Counts of each bit pattern and the first few raw bit strings
    """
    try:
        num_qubits = int(request.args.get('num_qubits', 3))
        num_shots = int(request.args.get('num_shots', 1024))
        
        # Validate parameters
        if num_qubits < 1 or num_qubits > 12:
            return jsonify({'error': 'Number of qubits must be between 1 and 12'}), 400
            
        if num_shots < 1 or num_shots > 10000:
            return jsonify({'error': 'Number of shots must be between 1 and 10000'}), 400
        
        # Set the number of qubits
        qrng.num_qubits = num_qubits
        
        # Generate quantum random bits
        counts, bit_strings = qrng.generate_random_bits(num_shots=num_shots)
        
        return jsonify({
            'counts': counts,
            'samples': bit_strings[:min(10, len(bit_strings))],  # Return only the first 10 samples
            'num_qubits': num_qubits,
            'num_shots': num_shots
        })
    except ValueError as e:
        return jsonify({'error': f'Invalid parameters: {str(e)}'}), 400
    except Exception as e:
        app.logger.error(f"Error in get_quantum_bits: {str(e)}")
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/api/classical-bits', methods=['GET'])
def get_classical_bits():
    """
    API endpoint to generate classical random bits.
    
    Query Parameters:
        num_bits (int): Number of bits per sample
        num_samples (int): Number of samples to generate
        
    Returns:
        JSON: Counts of each bit pattern and the first few raw bit strings
    """
    try:
        num_bits = int(request.args.get('num_bits', 3))
        num_samples = int(request.args.get('num_samples', 1024))
        
        # Validate parameters
        if num_bits < 1 or num_bits > 12:
            return jsonify({'error': 'Number of bits must be between 1 and 12'}), 400
            
        if num_samples < 1 or num_samples > 10000:
            return jsonify({'error': 'Number of samples must be between 1 and 10000'}), 400
        
        # Generate classical random bits
        counts, bit_strings = comparison.generate_classical_bits(num_bits, num_samples)
        
        return jsonify({
            'counts': counts,
            'samples': bit_strings[:min(10, len(bit_strings))],  # Return only the first 10 samples
            'num_bits': num_bits,
            'num_samples': num_samples
        })
    except ValueError as e:
        return jsonify({'error': f'Invalid parameters: {str(e)}'}), 400
    except Exception as e:
        app.logger.error(f"Error in get_classical_bits: {str(e)}")
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/api/quantum-integers', methods=['GET'])
def get_quantum_integers():
    """
    API endpoint to generate quantum random integers.
    
    Query Parameters:
        min_val (int): Minimum value (inclusive)
        max_val (int): Maximum value (inclusive)
        num_samples (int): Number of samples to generate
        
    Returns:
        JSON: List of random integers and basic statistics
    """
    try:
        min_val = int(request.args.get('min_val', 1))
        max_val = int(request.args.get('max_val', 100))
        num_samples = int(request.args.get('num_samples', 1000))
        
        # Validate parameters
        if min_val >= max_val:
            return jsonify({'error': 'Minimum value must be less than maximum value'}), 400
            
        if max_val - min_val > 1000:
            return jsonify({'error': 'Range too large (max - min > 1000)'}), 400
            
        if num_samples < 1 or num_samples > 10000:
            return jsonify({'error': 'Number of samples must be between 1 and 10000'}), 400
        
        # Generate quantum random integers
        integers = qrng.generate_random_integers(min_val, max_val, num_samples)
        
        # Calculate basic statistics
        mean = sum(integers) / len(integers)
        sorted_integers = sorted(integers)
        median = sorted_integers[len(sorted_integers) // 2]
        
        # Count frequency of each value
        frequency = {}
        for value in integers:
            frequency[value] = frequency.get(value, 0) + 1
        
        return jsonify({
            'integers': integers[:min(100, len(integers))],  # Return at most 100 samples
            'statistics': {
                'mean': mean,
                'median': median,
                'min': min(integers),
                'max': max(integers)
            },
            'frequency': frequency,
            'parameters': {
                'min_val': min_val,
                'max_val': max_val,
                'num_samples': num_samples
            }
        })
    except ValueError as e:
        return jsonify({'error': f'Invalid parameters: {str(e)}'}), 400
    except Exception as e:
        app.logger.error(f"Error in get_quantum_integers: {str(e)}")
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/api/classical-integers', methods=['GET'])
def get_classical_integers():
    """
    API endpoint to generate classical random integers.
    
    Query Parameters:
        min_val (int): Minimum value (inclusive)
        max_val (int): Maximum value (inclusive)
        num_samples (int): Number of samples to generate
        
    Returns:
        JSON: List of random integers and basic statistics
    """
    try:
        min_val = int(request.args.get('min_val', 1))
        max_val = int(request.args.get('max_val', 100))
        num_samples = int(request.args.get('num_samples', 1000))
        
        # Validate parameters
        if min_val >= max_val:
            return jsonify({'error': 'Minimum value must be less than maximum value'}), 400
            
        if max_val - min_val > 1000:
            return jsonify({'error': 'Range too large (max - min > 1000)'}), 400
            
        if num_samples < 1 or num_samples > 10000:
            return jsonify({'error': 'Number of samples must be between 1 and 10000'}), 400
        
        # Generate classical random integers
        integers = comparison.generate_classical_integers(min_val, max_val, num_samples)
        
        # Calculate basic statistics
        mean = sum(integers) / len(integers)
        sorted_integers = sorted(integers)
        median = sorted_integers[len(sorted_integers) // 2]
        
        # Count frequency of each value
        frequency = {}
        for value in integers:
            frequency[value] = frequency.get(value, 0) + 1
        
        return jsonify({
            'integers': integers[:min(100, len(integers))],  # Return at most 100 samples
            'statistics': {
                'mean': mean,
                'median': median,
                'min': min(integers),
                'max': max(integers)
            },
            'frequency': frequency,
            'parameters': {
                'min_val': min_val,
                'max_val': max_val,
                'num_samples': num_samples
            }
        })
    except ValueError as e:
        return jsonify({'error': f'Invalid parameters: {str(e)}'}), 400
    except Exception as e:
        app.logger.error(f"Error in get_classical_integers: {str(e)}")
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/api/compare', methods=['GET'])
def compare_randomness():
    """
    API endpoint to compare quantum and classical random number generation.
    
    Query Parameters:
        type (str): Type of comparison ('bits' or 'integers')
        num_bits/num_qubits (int): Number of bits per sample (for 'bits' type)
        min_val (int): Minimum value (for 'integers' type)
        max_val (int): Maximum value (for 'integers' type)
        num_samples (int): Number of samples to generate
        
    Returns:
        JSON: Comparison results
    """
    try:
        comparison_type = request.args.get('type', 'bits')
        num_samples = int(request.args.get('num_samples', 1000))
        
        if comparison_type == 'bits':
            num_bits = int(request.args.get('num_bits', 3))
            
            # Compare bit distributions
            q_counts, c_counts, chi2, p_value = comparison.compare_bit_distributions(
                num_bits=num_bits, num_samples=num_samples
            )
            
            return jsonify({
                'type': 'bits',
                'quantum_counts': q_counts,
                'classical_counts': c_counts,
                'statistics': {
                    'chi2_statistic': float(chi2),
                    'p_value': float(p_value)
                },
                'parameters': {
                    'num_bits': num_bits,
                    'num_samples': num_samples
                }
            })
        
        elif comparison_type == 'integers':
            min_val = int(request.args.get('min_val', 1))
            max_val = int(request.args.get('max_val', 100))
            
            # Compare integer distributions
            q_ints, c_ints, ks, p_value = comparison.compare_integer_distributions(
                min_val=min_val, max_val=max_val, num_samples=num_samples
            )
            
            # Count frequency of each value for both distributions
            q_frequency = {}
            for value in q_ints:
                q_frequency[value] = q_frequency.get(value, 0) + 1
                
            c_frequency = {}
            for value in c_ints:
                c_frequency[value] = c_frequency.get(value, 0) + 1
            
            return jsonify({
                'type': 'integers',
                'quantum_frequency': q_frequency,
                'classical_frequency': c_frequency,
                'statistics': {
                    'ks_statistic': float(ks),
                    'p_value': float(p_value)
                },
                'parameters': {
                    'min_val': min_val,
                    'max_val': max_val,
                    'num_samples': num_samples
                }
            })
        
        else:
            return jsonify({'error': 'Invalid comparison type'}), 400
            
    except ValueError as e:
        # Handle parameter conversion errors
        return jsonify({'error': f'Invalid parameters: {str(e)}'}), 400
    except Exception as e:
        # Handle other errors
        app.logger.error(f"Error in compare_randomness: {str(e)}")
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 