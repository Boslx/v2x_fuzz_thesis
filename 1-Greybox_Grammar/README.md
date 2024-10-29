# Documentation

Please note that for some scripts you have to edit the variables within the source code.  

## benchmarkGrammarFuzzPerformance.py

This script benchmarks the performance of the grammar-based input generator for the Ieee1609Dot2Data type by measuring the time it takes to generate the seeds.

## calculateCoverage.py

This script calculates and plots the grammar coverage of a given ASN.1 grammars with coverage awareness and just random feature mutation

## calculateEntropy.py

This script calculates the combined entropy of binary files in a folder.

The script takes one argument:

    folder_path: The path to the folder containing the binary files.

## evaluationAndPlots.py

This script contains all calculations for the evaluation part of the thesis.

The script reads data from AFL `plot_data` files and performs statistical analysis on it. The script also generates the plots of the thesis. 

## exportFeatureModel.py

This script maps a given ASN.1 grammars to a feature models.

## genSeed_max_coverage.py

This script generates seeds for the greybox grammar fuzzer using the max_cov strategy.

## genSeed_t-wise.py

This script uses a t-wise strategy to generate seeds for the greybox grammar fuzzer. To use it, you must first export all possible product combinations from FeatureIDE. To obtain the input for FeatureIDE, use script "exportFeatureModel.py".

**Here's how to export product combinations in FeatureIDE:**

1. **Import the Feature Model XML file into FeatureIDE.**
2. **Right-click on the project.**
3. **Navigate to FeatureIDE -> Product Generator.**
4. **Set the Output Type to "Products".**
5. **Export the products.**

Once you have exported the products, you can use this script to generate seeds for the fuzzer. 