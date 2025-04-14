/**
 * QuantumRand - Frontend Script
 * This script handles the interaction with the backend API for quantum and classical
 * random number generation and visualization.
 */

// Global chart instance
let comparisonChart = null;

// Event listener when DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Set up event listeners
    document.getElementById('generation-type').addEventListener('change', toggleGenerationOptions);
    document.getElementById('generate-btn').addEventListener('click', generateAndCompare);
    
    // Initialize the interface
    toggleGenerationOptions();
});

/**
 * Toggle the display of input fields based on the selected generation type
 */
function toggleGenerationOptions() {
    const generationType = document.getElementById('generation-type').value;
    const bitsOptions = document.getElementById('bits-options');
    const integerMin = document.getElementById('integer-min');
    const integerMax = document.getElementById('integer-max');
    
    if (generationType === 'bits') {
        bitsOptions.style.display = 'block';
        integerMin.style.display = 'none';
        integerMax.style.display = 'none';
    } else {
        bitsOptions.style.display = 'none';
        integerMin.style.display = 'block';
        integerMax.style.display = 'block';
    }
}

/**
 * Generate random numbers and compare the quantum and classical approaches
 */
async function generateAndCompare() {
    // Show loading indicator
    document.getElementById('loading').style.display = 'block';
    document.getElementById('results').style.display = 'none';
    
    // Get form values
    const generationType = document.getElementById('generation-type').value;
    const numSamples = document.getElementById('num-samples').value;
    
    try {
        // Build the API endpoint URL based on generation type
        let url = `/api/compare?type=${generationType}&num_samples=${numSamples}`;
        
        if (generationType === 'bits') {
            const numBits = document.getElementById('num-bits').value;
            url += `&num_bits=${numBits}`;
        } else {
            const minVal = document.getElementById('min-val').value;
            const maxVal = document.getElementById('max-val').value;
            
            // Validate input values
            if (parseInt(minVal) >= parseInt(maxVal)) {
                throw new Error('Minimum value must be less than maximum value');
            }
            
            url += `&min_val=${minVal}&max_val=${maxVal}`;
        }
        
        // Fetch comparison data from the API
        const response = await fetch(url);
        
        // Check for HTTP errors
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP error! Status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Process and display the results
        displayResults(data, generationType);
        
    } catch (error) {
        console.error('Error generating random data:', error);
        
        // Hide loading indicator
        document.getElementById('loading').style.display = 'none';
        
        // Show error message in a more user-friendly way
        const resultsDiv = document.getElementById('results');
        resultsDiv.style.display = 'block';
        resultsDiv.innerHTML = `
            <div class="alert alert-danger">
                <h4 class="alert-heading">Error</h4>
                <p>${error.message || 'An unknown error occurred while generating random data.'}</p>
                <hr>
                <p class="mb-0">Please try again with different parameters or refresh the page.</p>
            </div>
        `;
    } finally {
        // Hide loading indicator if it's still visible
        if (document.getElementById('loading').style.display === 'block') {
            document.getElementById('loading').style.display = 'none';
        }
    }
}

/**
 * Display the comparison results on the page
 * @param {Object} data - The data returned from the API
 * @param {string} generationType - The type of generation ('bits' or 'integers')
 */
function displayResults(data, generationType) {
    // Show results container
    document.getElementById('results').style.display = 'block';
    
    if (generationType === 'bits') {
        displayBitResults(data);
    } else {
        displayIntegerResults(data);
    }
}

/**
 * Display bit generation results
 * @param {Object} data - The bit generation data
 */
function displayBitResults(data) {
    // Display samples
    document.getElementById('quantum-samples').textContent = 
        Object.keys(data.quantum_counts).slice(0, 5).join(', ') + '...';
    
    document.getElementById('classical-samples').textContent = 
        Object.keys(data.classical_counts).slice(0, 5).join(', ') + '...';
    
    // Display stats
    const quantumTotal = Object.values(data.quantum_counts).reduce((a, b) => a + b, 0);
    const classicalTotal = Object.values(data.classical_counts).reduce((a, b) => a + b, 0);
    
    const quantumStatsHTML = Object.entries(data.quantum_counts)
        .map(([pattern, count]) => `<div>${pattern}: ${count} (${(count/quantumTotal*100).toFixed(2)}%)</div>`)
        .join('');
    
    const classicalStatsHTML = Object.entries(data.classical_counts)
        .map(([pattern, count]) => `<div>${pattern}: ${count} (${(count/classicalTotal*100).toFixed(2)}%)</div>`)
        .join('');
    
    document.getElementById('quantum-stats').innerHTML = quantumStatsHTML;
    document.getElementById('classical-stats').innerHTML = classicalStatsHTML;
    
    // Display comparison stats
    document.getElementById('comparison-stats').innerHTML = `
        <div><strong>Chi-square Test Statistic (\(\chi^2\)):</strong> ${data.statistics.chi2_statistic.toFixed(4)}</div>
        <div><strong>p-value:</strong> ${data.statistics.p_value.toFixed(6)}</div>
        <div><strong>Degrees of Freedom:</strong> ${Object.keys(data.quantum_counts).length - 1}</div>
    `;
    
    // Create a conclusion based on the p-value
    let conclusion = '';
    if (data.statistics.p_value < 0.01) {
        conclusion = 'The p-value is less than 0.01, providing strong evidence against the null hypothesis. There is a statistically significant difference between the quantum and classical distributions. This suggests either that (1) the quantum generator is producing truly random output that differs from the pseudo-random output of the classical generator, or (2) there may be biases in the quantum circuit implementation.';
    } else if (data.statistics.p_value < 0.05) {
        conclusion = 'The p-value is less than 0.05, suggesting evidence against the null hypothesis. There is a statistically significant difference between the quantum and classical distributions at the conventional significance level of α=0.05.';
    } else if (data.statistics.p_value < 0.10) {
        conclusion = 'The p-value is between 0.05 and 0.10, indicating marginal evidence against the null hypothesis. The difference between distributions is not significant at the conventional α=0.05 level but might be considered statistically significant with a less stringent criterion.';
    } else {
        conclusion = 'The p-value is greater than 0.10, failing to reject the null hypothesis. We do not have sufficient evidence to conclude that the quantum and classical random number generation distributions differ statistically. This suggests that despite their fundamentally different origins, the observed outputs are statistically indistinguishable in this experiment.';
    }
    document.getElementById('comparison-conclusion').textContent = conclusion;
    
    // Create the comparison chart
    createBitComparisonChart(data.quantum_counts, data.classical_counts);
}

/**
 * Display integer generation results
 * @param {Object} data - The integer generation data
 */
function displayIntegerResults(data) {
    // Display samples
    document.getElementById('quantum-samples').textContent = 
        Object.keys(data.quantum_frequency).slice(0, 5).join(', ') + '...';
    
    document.getElementById('classical-samples').textContent = 
        Object.keys(data.classical_frequency).slice(0, 5).join(', ') + '...';
    
    // Calculate statistics for both distributions
    const qKeys = Object.keys(data.quantum_frequency).map(k => parseInt(k));
    const qValues = Object.values(data.quantum_frequency);
    const cKeys = Object.keys(data.classical_frequency).map(k => parseInt(k));
    const cValues = Object.values(data.classical_frequency);
    
    const qMean = qKeys.reduce((sum, key, i) => sum + key * qValues[i], 0) / qValues.reduce((a, b) => a + b, 0);
    const cMean = cKeys.reduce((sum, key, i) => sum + key * cValues[i], 0) / cValues.reduce((a, b) => a + b, 0);
    
    // Display stats - show most frequent values
    const topQuantumValues = Object.entries(data.quantum_frequency)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10)
        .map(([value, count]) => `<div>Value ${value}: ${count} occurrences</div>`)
        .join('');
    
    const topClassicalValues = Object.entries(data.classical_frequency)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10)
        .map(([value, count]) => `<div>Value ${value}: ${count} occurrences</div>`)
        .join('');
    
    document.getElementById('quantum-stats').innerHTML = `
        <div><strong>Mean:</strong> ${qMean.toFixed(2)}</div>
        <div><strong>Range:</strong> ${Math.min(...qKeys)} to ${Math.max(...qKeys)}</div>
        <div><strong>Most Frequent Values:</strong></div>
        ${topQuantumValues}
    `;
    
    document.getElementById('classical-stats').innerHTML = `
        <div><strong>Mean:</strong> ${cMean.toFixed(2)}</div>
        <div><strong>Range:</strong> ${Math.min(...cKeys)} to ${Math.max(...cKeys)}</div>
        <div><strong>Most Frequent Values:</strong></div>
        ${topClassicalValues}
    `;
    
    // Display comparison stats
    document.getElementById('comparison-stats').innerHTML = `
        <div><strong>Kolmogorov-Smirnov Test Statistic (D):</strong> ${data.statistics.ks_statistic.toFixed(4)}</div>
        <div><strong>p-value:</strong> ${data.statistics.p_value.toFixed(6)}</div>
        <div><strong>Mean Difference:</strong> ${Math.abs(qMean - cMean).toFixed(4)}</div>
        <div><strong>Sample Size:</strong> ${qValues.reduce((a, b) => a + b, 0)}</div>
    `;
    
    // Create a conclusion based on the p-value with more statistical rigor
    let conclusion = '';
    if (data.statistics.p_value < 0.01) {
        conclusion = 'The Kolmogorov-Smirnov test yields a p-value less than 0.01, providing strong evidence against the null hypothesis that the two samples come from the same distribution. The empirical cumulative distribution functions of the quantum and classical random numbers differ significantly.';
    } else if (data.statistics.p_value < 0.05) {
        conclusion = 'The Kolmogorov-Smirnov test yields a p-value less than 0.05, indicating that we can reject the null hypothesis at the conventional significance level. There is a statistically significant difference between the cumulative distribution functions of the quantum and classical random numbers.';
    } else if (data.statistics.p_value < 0.10) {
        conclusion = 'The Kolmogorov-Smirnov test yields a p-value between 0.05 and 0.10, suggesting marginal evidence against the null hypothesis. The difference between distributions falls short of statistical significance at α=0.05 but may be considered significant under less stringent criteria.';
    } else {
        conclusion = 'The Kolmogorov-Smirnov test yields a p-value greater than 0.10, failing to reject the null hypothesis. The empirical distribution of quantum random numbers is not statistically distinguishable from that of classical pseudo-random numbers in this experiment. This suggests that for finite sampling, the practical differences between quantum and classical randomness may be negligible despite their distinct theoretical foundations.';
    }
    document.getElementById('comparison-conclusion').textContent = conclusion;
    
    // Create the comparison chart
    createIntegerComparisonChart(data.quantum_frequency, data.classical_frequency);
}

/**
 * Create a chart comparing bit distributions
 * @param {Object} quantumCounts - The quantum bit counts
 * @param {Object} classicalCounts - The classical bit counts
 */
function createBitComparisonChart(quantumCounts, classicalCounts) {
    // Get all unique keys
    const allKeys = [...new Set([...Object.keys(quantumCounts), ...Object.keys(classicalCounts)])].sort();
    
    // Prepare data for the chart
    const quantumData = allKeys.map(key => quantumCounts[key] || 0);
    const classicalData = allKeys.map(key => classicalCounts[key] || 0);
    
    // Get the canvas element
    const ctx = document.getElementById('comparison-chart').getContext('2d');
    
    // Destroy previous chart if it exists
    if (comparisonChart) {
        comparisonChart.destroy();
    }
    
    // Create a new chart
    comparisonChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: allKeys,
            datasets: [
                {
                    label: 'Quantum',
                    data: quantumData,
                    backgroundColor: 'rgba(54, 162, 235, 0.7)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                },
                {
                    label: 'Classical',
                    data: classicalData,
                    backgroundColor: 'rgba(255, 99, 132, 0.7)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Quantum vs Classical Bit Distribution'
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                },
                legend: {
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Frequency'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Bit Pattern'
                    }
                }
            }
        }
    });
}

/**
 * Create a chart comparing integer distributions
 * @param {Object} quantumFreq - The quantum integer frequency
 * @param {Object} classicalFreq - The classical integer frequency
 */
function createIntegerComparisonChart(quantumFreq, classicalFreq) {
    // Get all unique keys as integers
    const allKeys = [...new Set([
        ...Object.keys(quantumFreq).map(k => parseInt(k)), 
        ...Object.keys(classicalFreq).map(k => parseInt(k))
    ])].sort((a, b) => a - b);
    
    // Determine if we should use histogram bins
    if (allKeys.length > 30) {
        createHistogramChart(quantumFreq, classicalFreq, allKeys);
    } else {
        // Simple bar chart for direct comparison
        
        // Prepare data for the chart
        const quantumData = allKeys.map(key => quantumFreq[key] || 0);
        const classicalData = allKeys.map(key => classicalFreq[key] || 0);
        
        // Get the canvas element
        const ctx = document.getElementById('comparison-chart').getContext('2d');
        
        // Destroy previous chart if it exists
        if (comparisonChart) {
            comparisonChart.destroy();
        }
        
        // Create a new chart
        comparisonChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: allKeys,
                datasets: [
                    {
                        label: 'Quantum',
                        data: quantumData,
                        backgroundColor: 'rgba(54, 162, 235, 0.7)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 1
                    },
                    {
                        label: 'Classical',
                        data: classicalData,
                        backgroundColor: 'rgba(255, 99, 132, 0.7)',
                        borderColor: 'rgba(255, 99, 132, 1)',
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Quantum vs Classical Integer Distribution'
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    },
                    legend: {
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Frequency'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Value'
                        }
                    }
                }
            }
        });
    }
}

/**
 * Create a histogram chart for larger distribution ranges
 * @param {Object} quantumFreq - The quantum integer frequency
 * @param {Object} classicalFreq - The classical integer frequency
 * @param {Array} allKeys - All unique keys as integers
 */
function createHistogramChart(quantumFreq, classicalFreq, allKeys) {
    // Create histogram bins
    const min = Math.min(...allKeys);
    const max = Math.max(...allKeys);
    const binCount = 20; // Number of bins
    const binSize = Math.ceil((max - min) / binCount);
    
    // Create bin labels
    const binLabels = [];
    const quantumBins = Array(binCount).fill(0);
    const classicalBins = Array(binCount).fill(0);
    
    for (let i = 0; i < binCount; i++) {
        const binStart = min + i * binSize;
        const binEnd = binStart + binSize - 1;
        binLabels.push(`${binStart}-${binEnd}`);
        
        // Fill the bins with data
        for (let j = binStart; j <= binEnd; j++) {
            if (quantumFreq[j]) {
                quantumBins[i] += quantumFreq[j];
            }
            if (classicalFreq[j]) {
                classicalBins[i] += classicalFreq[j];
            }
        }
    }
    
    // Get the canvas element
    const ctx = document.getElementById('comparison-chart').getContext('2d');
    
    // Destroy previous chart if it exists
    if (comparisonChart) {
        comparisonChart.destroy();
    }
    
    // Create a new chart
    comparisonChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: binLabels,
            datasets: [
                {
                    label: 'Quantum',
                    data: quantumBins,
                    backgroundColor: 'rgba(54, 162, 235, 0.7)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                },
                {
                    label: 'Classical',
                    data: classicalBins,
                    backgroundColor: 'rgba(255, 99, 132, 0.7)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Quantum vs Classical Integer Distribution (Histogram)'
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                },
                legend: {
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Frequency'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Value Range'
                    }
                }
            }
        }
    });
} 