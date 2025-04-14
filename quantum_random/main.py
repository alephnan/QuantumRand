#!/usr/bin/env python3
"""
Quantum Random Number Generator - Main Application

This module provides a command-line interface for using the quantum random number
generator and comparing it with classical random number generation.
"""

import argparse
import sys
import json
import matplotlib.pyplot as plt

from .qrng import QuantumRandomNumberGenerator
from .comparison import RandomnessComparison


def generate_bits(args):
    """Generate random bits using the quantum random number generator."""
    qrng = QuantumRandomNumberGenerator(num_qubits=args.num_qubits)
    counts, bit_strings = qrng.generate_random_bits(num_shots=args.num_samples)
    
    if args.verbose:
        print(f"Generated {len(bit_strings)} random bit sequences:")
        for i, bits in enumerate(bit_strings[:10], 1):
            print(f"{i}. {bits}")
        if len(bit_strings) > 10:
            print(f"... and {len(bit_strings) - 10} more")
    
    print("\nDistribution of bit patterns:")
    for pattern, count in sorted(counts.items()):
        percentage = (count / args.num_samples) * 100
        print(f"{pattern}: {count} occurrences ({percentage:.2f}%)")
    
    # Save to file if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump({
                'num_qubits': args.num_qubits,
                'num_samples': args.num_samples,
                'counts': counts,
                'bit_strings': bit_strings
            }, f, indent=2)
        print(f"\nResults saved to {args.output}")


def generate_integers(args):
    """Generate random integers using the quantum random number generator."""
    qrng = QuantumRandomNumberGenerator(num_qubits=args.num_qubits)
    integers = qrng.generate_random_integers(
        min_val=args.min, max_val=args.max, num_samples=args.num_samples
    )
    
    if args.verbose:
        print(f"Generated {len(integers)} random integers:")
        for i, num in enumerate(integers[:20], 1):
            print(f"{i}. {num}")
        if len(integers) > 20:
            print(f"... and {len(integers) - 20} more")
    
    print("\nSummary statistics:")
    print(f"Min: {min(integers)}")
    print(f"Max: {max(integers)}")
    print(f"Mean: {sum(integers) / len(integers):.2f}")
    
    # Save to file if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump({
                'num_qubits': args.num_qubits,
                'min_val': args.min,
                'max_val': args.max,
                'num_samples': args.num_samples,
                'integers': integers
            }, f, indent=2)
        print(f"\nResults saved to {args.output}")


def compare_distributions(args):
    """Compare quantum and classical random number distributions."""
    comparison = RandomnessComparison(num_qubits=args.num_qubits)
    
    if args.type == 'bits':
        # Compare bit distributions
        quantum_counts, classical_counts, chi2_stat, p_value = comparison.compare_bit_distributions(
            num_bits=args.num_qubits, num_samples=args.num_samples
        )
        
        print("\nBit Pattern Distribution Comparison:")
        print(f"Chi-square statistic: {chi2_stat:.4f}")
        print(f"p-value: {p_value:.4f}")
        
        if p_value < 0.05:
            print("\nThe distributions are significantly different (p < 0.05).")
        else:
            print("\nNo significant difference found between the distributions (p >= 0.05).")
        
        # Plot comparison if requested
        if args.plot:
            fig = comparison.plot_comparison(
                quantum_counts, classical_counts, 
                title=f"Comparison of Quantum vs Classical {args.num_qubits}-bit Patterns",
                x_label="Bit Pattern", y_label="Frequency"
            )
            plt.tight_layout()
            
            if args.output:
                fig.savefig(args.output)
                print(f"Plot saved to {args.output}")
            else:
                plt.show()
        
    elif args.type == 'integers':
        # Compare integer distributions
        quantum_integers, classical_integers, ks_stat, p_value = comparison.compare_integer_distributions(
            min_val=args.min, max_val=args.max, num_samples=args.num_samples
        )
        
        print("\nInteger Distribution Comparison:")
        print(f"Kolmogorov-Smirnov statistic: {ks_stat:.4f}")
        print(f"p-value: {p_value:.4f}")
        
        if p_value < 0.05:
            print("\nThe distributions are significantly different (p < 0.05).")
        else:
            print("\nNo significant difference found between the distributions (p >= 0.05).")
        
        # Plot comparison if requested
        if args.plot:
            fig = comparison.plot_comparison(
                quantum_integers, classical_integers, 
                title=f"Comparison of Quantum vs Classical Random Integers ({args.min}-{args.max})",
                x_label="Value", y_label="Frequency"
            )
            plt.tight_layout()
            
            if args.output:
                fig.savefig(args.output)
                print(f"Plot saved to {args.output}")
            else:
                plt.show()


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description="Quantum Random Number Generator")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Generate bits command
    bits_parser = subparsers.add_parser("bits", help="Generate random bits")
    bits_parser.add_argument("--num-qubits", type=int, default=3, help="Number of qubits to use (default: 3)")
    bits_parser.add_argument("--num-samples", type=int, default=1024, help="Number of samples to generate (default: 1024)")
    bits_parser.add_argument("--output", type=str, help="File to save results to (JSON format)")
    bits_parser.add_argument("--verbose", "-v", action="store_true", help="Print verbose output")
    
    # Generate integers command
    int_parser = subparsers.add_parser("integers", help="Generate random integers")
    int_parser.add_argument("--num-qubits", type=int, default=5, help="Number of qubits to use (default: 5)")
    int_parser.add_argument("--min", type=int, default=0, help="Minimum value (inclusive, default: 0)")
    int_parser.add_argument("--max", type=int, default=100, help="Maximum value (inclusive, default: 100)")
    int_parser.add_argument("--num-samples", type=int, default=1000, help="Number of samples to generate (default: 1000)")
    int_parser.add_argument("--output", type=str, help="File to save results to (JSON format)")
    int_parser.add_argument("--verbose", "-v", action="store_true", help="Print verbose output")
    
    # Compare distributions command
    compare_parser = subparsers.add_parser("compare", help="Compare quantum and classical random distributions")
    compare_parser.add_argument("--type", choices=["bits", "integers"], default="bits", 
                             help="Type of comparison to perform (default: bits)")
    compare_parser.add_argument("--num-qubits", type=int, default=3, help="Number of qubits to use (default: 3)")
    compare_parser.add_argument("--min", type=int, default=0, help="Minimum integer value (default: 0)")
    compare_parser.add_argument("--max", type=int, default=100, help="Maximum integer value (default: 100)")
    compare_parser.add_argument("--num-samples", type=int, default=1000, help="Number of samples to generate (default: 1000)")
    compare_parser.add_argument("--plot", action="store_true", help="Generate a plot of the comparison")
    compare_parser.add_argument("--output", type=str, help="File to save plot to (if --plot is specified)")
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        sys.exit(1)
    
    # Execute the selected command
    if args.command == "bits":
        generate_bits(args)
    elif args.command == "integers":
        generate_integers(args)
    elif args.command == "compare":
        compare_distributions(args)
    

if __name__ == "__main__":
    main() 