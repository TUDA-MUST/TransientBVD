import pandas as pd
from transientbvd import select_transducer

# Define the transducer models and their numbers
transducer_info = {
    1: "Custom",
    2: "8AF200184",
    3: "GB-4540-4SH",
    4: "SMBLTD45F40H_1",
    5: "MA40S4S",
    6: "SMBLTD45F28H_28kHz"
}

# Data storage for export
data = []

# Process each transducer
for number, name in transducer_info.items():
    try:
        # Load the predefined transducer
        transducer = select_transducer(name)

        # Calculate decay times without using Rp
        tau_no_rp = 2 * transducer.ls / transducer.rs
        two_tau_no_rp = 2 * tau_no_rp

        # Store data for export
        data.append({
            "Transducer Number": number,
            "Model": name,
            "Rs (Ω)": transducer.rs,
            "Ls (mH)": transducer.ls * 1e3,  # Convert H to mH
            "Cs (pF)": transducer.cs * 1e12,  # Convert F to pF
            "C0 (pF)": transducer.c0 * 1e12,  # Convert F to pF
            "Two Tau (ms)": two_tau_no_rp * 1e3  # Convert s to ms
        })

    except Exception as e:
        print(f"Error processing {name}: {e}")

# Export data to CSV
export_df = pd.DataFrame(data)
export_df.to_csv("transducer_two_tau.csv", index=False)

print("Regular decay data exported to transducer_two_tau.csv")
