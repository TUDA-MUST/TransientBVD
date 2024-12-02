from transientbvd import predefined_transducer, tau_decay, two_tau_decay

def main():
    # Step 1: Select a predefined transducer
    selected_name = "SMBLTD45F40H_1"
    transducer = predefined_transducer(selected_name)
    print(f"Selected Transducer: {transducer}\n")

    # Step 2: Calculate τ (tau) and 2τ (two tau) without parallel resistance (rp=None)
    tau_no_rp = tau_decay(
        rs=transducer.rs,
        ls=transducer.ls,
        cs=transducer.cs,
        c0=transducer.c0,
        rp=None
    )
    two_tau_no_rp = two_tau_decay(
        rs=transducer.rs,
        ls=transducer.ls,
        cs=transducer.cs,
        c0=transducer.c0,
        rp=None
    )

    print("Decay Times without Parallel Resistance (rp=None):")
    print(f"  τ (Tau): {tau_no_rp:.6f} s ({tau_no_rp * 1e3:.2f} ms)")
    print(f"  2τ (Two Tau): {two_tau_no_rp:.6f} s ({two_tau_no_rp * 1e3:.2f} ms)\n")

    # Step 3: Calculate τ (tau) and 2τ (two tau) with a specified parallel resistance (rp=950 Ω)
    rp = 950  # Parallel resistance in ohms
    tau_with_rp = tau_decay(
        rs=transducer.rs,
        ls=transducer.ls,
        cs=transducer.cs,
        c0=transducer.c0,
        rp=rp
    )
    two_tau_with_rp = two_tau_decay(
        rs=transducer.rs,
        ls=transducer.ls,
        cs=transducer.cs,
        c0=transducer.c0,
        rp=rp
    )

    print("Decay Times with Parallel Resistance (rp=950 Ω):")
    print(f"  τ (Tau): {tau_with_rp:.6f} s ({tau_with_rp * 1e3:.2f} ms)")
    print(f"  2τ (Two Tau): {two_tau_with_rp:.6f} s ({two_tau_with_rp * 1e3:.2f} ms)")

if __name__ == "__main__":
    main()
