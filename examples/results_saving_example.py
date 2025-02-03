import pandas as pd
import numpy as np
from transientbvd import Transducer, open_tau

# Step 1: Create a transducer directly in the code
transducer = Transducer(
    name="ExampleTransducer",
    rs=24.764,  # Series resistance in ohms
    ls=38.959e-3,  # Inductance in henries
    cs=400.33e-12,  # Series capacitance in farads
    c0=3970.1e-12,  # Parallel capacitance in farads
    manufacturer="Example Manufacturer"
)

print("Transducer used for analysis:")
print(transducer)

# Step 2: Perform decay analysis over a resistance range
resistance_range = np.linspace(10, 1000, 50)  # 50 points between 10 and 1000 ohms
decay_times = [open_tau(transducer.rs, transducer.ls,
                         transducer.cs, transducer.c0, rp=rp)
               for rp in resistance_range]

# Create a DataFrame to store the results
decay_df = pd.DataFrame({
    "Resistance (Ohms)": resistance_range,
    "Decay Time (s)": decay_times
})

# Print the first few rows of the analysis
print("\nDecay Analysis Results:")
print(decay_df.head())

# Step 3: Save the results to a CSV file
output_file = "decay_analysis_results.csv"
decay_df.to_csv(output_file, index=False)
print(f"\nDecay analysis results saved to {output_file}.")