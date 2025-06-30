def calculate_total_cost():
    print("Welcome to the Hosting Cost Calculator!\n")
    
    # Pricing from Excel (INR/month unless specified)
    PRICING = {
        # VM Configurations (vCPU, RAM, Storage)
        "vm_configs": {
            "1vCPU_1GB_40GB": 4449,
            "2vCPU_2GB_60GB": 7349,
            "4vCPU_4GB_120GB": 13349,
            "6vCPU_6GB_180GB": 19949,
            "8vCPU_8GB_240GB": 25549,
            "16vCPU_16GB_480GB": 49649,
        },
        # Add-ons (per unit)
        "add_ons": {
            "ram_per_gb": 849,
            "storage_per_50gb": 499,
        },
        # Management Services
        "management": {
            "antivirus": 2083,  # per VM
            "os_management_linux": 4670,  # per VM
            "os_management_windows": 1950,  # per vCPU
            "backup_management": 1340,  # per VM
            "database_management": 13440,  # per instance
        },
        # Bandwidth (annual cost)
        "bandwidth": {
            "10mbps": 250000,
            "100mbps": 750000,
            "250mbps": 1800000,
        }
    }

    # --- Step 1: VM Requirements ---
    print("Step 1: Virtual Machine (VM) Requirements")
    vm_cost = 0
    vms = []
    
    while True:
        print("\nAvailable VM Configurations:")
        for i, (config, price) in enumerate(PRICING["vm_configs"].items(), 1):
            print(f"{i}. {config} (₹{price}/month)")
        
        choice = input("\nSelect a VM config (1-6) or 'done' to finish: ").strip().lower()
        if choice == 'done':
            break
        
        try:
            choice = int(choice)
            if 1 <= choice <= len(PRICING["vm_configs"]):
                config = list(PRICING["vm_configs"].keys())[choice - 1]
                quantity = int(input(f"How many '{config}' VMs do you need? "))
                
                # Additional RAM/Storage
                extra_ram = int(input("Additional RAM needed (GB, 0 if none): "))
                extra_storage = int(input("Additional Storage needed (50 GB units, 0 if none): "))
                
                # Calculate cost
                base_cost = PRICING["vm_configs"][config] * quantity
                ram_cost = extra_ram * PRICING["add_ons"]["ram_per_gb"] * quantity
                storage_cost = extra_storage * PRICING["add_ons"]["storage_per_50gb"] * quantity
                total_vm_cost = base_cost + ram_cost + storage_cost
                
                vms.append({
                    "config": config,
                    "quantity": quantity,
                    "extra_ram": extra_ram,
                    "extra_storage": extra_storage,
                    "cost": total_vm_cost
                })
                vm_cost += total_vm_cost
                print(f"Added {quantity}x {config} (₹{total_vm_cost}/month)")
            else:
                print("Invalid choice. Try again.")
        except ValueError:
            print("Invalid input. Enter a number or 'done'.")

    # --- Step 2: Management Services ---
    print("\nStep 2: Management Services")
    management_cost = 0
    
    # Antivirus
    antivirus_qty = int(input("Number of VMs needing antivirus: "))
    management_cost += antivirus_qty * PRICING["management"]["antivirus"]
    
    # OS Management (Linux/Windows)
    os_choice = input("OS type (linux/windows): ").strip().lower()
    if os_choice == "linux":
        os_qty = int(input("Number of VMs needing Linux OS management: "))
        management_cost += os_qty * PRICING["management"]["os_management_linux"]
    elif os_choice == "windows":
        vcpu_qty = int(input("Total vCPUs for Windows OS management: "))
        management_cost += vcpu_qty * PRICING["management"]["os_management_windows"]
    
    # Backup & Database Management
    backup_qty = int(input("Number of VMs needing backup management: "))
    management_cost += backup_qty * PRICING["management"]["backup_management"]
    
    db_qty = int(input("Number of database instances needing management: "))
    management_cost += db_qty * PRICING["management"]["database_management"]

    # --- Step 3: Bandwidth 
    print("\nStep 3: Bandwidth Requirements")
    print("1. 10 Mbps (₹250,000/year)")
    print("2. 100 Mbps (₹750,000/year)")
    print("3. 250 Mbps (₹1,800,000/year)")
    
    bw_choice = int(input("Select bandwidth option (1-3): "))
    bandwidth_cost = PRICING["bandwidth"][list(PRICING["bandwidth"].keys())[bw_choice - 1]]

    # --- Step 4: Discount (Optional) ---
    discount = 0
    apply_discount = input("\nApply discount? (yes/no): ").strip().lower()
    if apply_discount == "yes":
        discount_percent = float(input("Discount percentage (e.g., 30 for 30%): "))
        discount = (vm_cost + management_cost) * (discount_percent / 100)

    # --- Step 5: Calculate Total ---
    subtotal = vm_cost + management_cost
    total_monthly = subtotal - discount
    total_annual = (total_monthly * 12) + bandwidth_cost

    # --- Display Results 
    print("\n--- Cost Breakdown ---")
    print(f"VM Costs (Monthly): ₹{vm_cost:,.2f}")
    print(f"Management Services (Monthly): ₹{management_cost:,.2f}")
    print(f"Subtotal (Monthly): ₹{subtotal:,.2f}")
    if discount > 0:
        print(f"Discount (₹{discount:,.2f}): -{discount_percent}%")
    print(f"Total Monthly Recurring Cost: ₹{total_monthly:,.2f}")
    print(f"Bandwidth (Annual): ₹{bandwidth_cost:,.2f}")
    print(f"Total Annual Cost: ₹{total_annual:,.2f}")

if __name__ == "__main__":
    calculate_total_cost()