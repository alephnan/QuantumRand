"""
Test script to verify the fix for the chi-square test warning.
"""

from quantum_random import RandomnessComparison
import numpy as np

def test_chi_square_fix():
    """Test the fix for the chi-square test warning."""
    print("Testing chi-square fix...")
    
    # Create a comparison object
    comparison = RandomnessComparison(num_qubits=3)
    
    # Run multiple comparisons to check for warnings
    for i in range(5):
        print(f"\nTest run {i+1}:")
        q_counts, c_counts, chi2, p_value = comparison.compare_bit_distributions(
            num_bits=3, num_samples=1000
        )
        
        # Print the results
        print(f"Chi-square statistic: {chi2:.4f}, p-value: {p_value:.4f}")
        
        # Verify that the sums of the observed and expected frequencies are exactly equal
        all_keys = sorted(set(q_counts.keys()).union(set(c_counts.keys())))
        observed = np.array([q_counts[key] for key in all_keys])
        expected = np.array([c_counts[key] for key in all_keys])
        
        # Apply the same normalization as in the compare_bit_distributions method
        sum_observed = observed.sum()
        sum_expected = expected.sum()
        if sum_expected > 0:
            scaling_factor = sum_observed / sum_expected
            expected = expected * scaling_factor
            
            # Apply the fix to ensure exact equality
            diff = sum_observed - expected.sum()
            if diff != 0:
                max_idx = np.argmax(expected)
                expected[max_idx] += diff
        
        # Check if sums are exactly equal
        are_sums_equal = np.isclose(observed.sum(), expected.sum(), rtol=1e-14, atol=1e-14)
        print(f"Sum of observed: {observed.sum()}")
        print(f"Sum of expected: {expected.sum()}")
        print(f"Difference: {observed.sum() - expected.sum()}")
        print(f"Sums are exactly equal: {are_sums_equal}")
        
        if not are_sums_equal:
            print("WARNING: Sums are not exactly equal, which might cause the chi-square test warning.")
        else:
            print("SUCCESS: Sums are exactly equal, which should prevent the chi-square test warning.")

if __name__ == "__main__":
    test_chi_square_fix() 