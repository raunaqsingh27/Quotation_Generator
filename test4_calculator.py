import streamlit as st

def calculate_total_cost():
    st.title("💻 Hosting Cost Calculator")
    st.markdown("Customize your VM requirements and get a dynamic quote.")

    # Pricing from Excel (INR/month unless specified)
    PRICING = {
        "vm_configs": {
            "1vCPU_1GB_40GB": {"vCPU": 1, "RAM": 1, "Storage": 40, "Price": 4449},
            "2vCPU_2GB_60GB": {"vCPU": 2, "RAM": 2, "Storage": 60, "Price": 7349},
            "4vCPU_4GB_120GB": {"vCPU": 4, "RAM": 4, "Storage": 120, "Price": 13349},
            "6vCPU_6GB_180GB": {"vCPU": 6, "RAM": 6, "Storage": 180, "Price": 19949},
            "8vCPU_8GB_240GB": {"vCPU": 8, "RAM": 8, "Storage": 240, "Price": 25549},
            "16vCPU_16GB_480GB": {"vCPU": 16, "RAM": 16, "Storage": 480, "Price": 49649},
        },
        "add_ons": {
            "vcpu_unit_price": 2500,  # You can customize this rate
            "ram_per_gb": 849,
            "storage_per_50gb": 499,
        },
        "management": {
            "antivirus": 2083,
            "os_management_linux": 4670,
            "os_management_windows": 1950,
            "backup_management": 1340,
            "database_management": 13440,
        },
        "bandwidth": {
            "10mbps": 250000,
            "100mbps": 750000,
            "250mbps": 1800000,
        }
    }

    st.header("1️⃣ VM Requirements (Auto-Base Selection by vCPU)")

    # User Inputs
    num_vms = st.number_input("How many VMs do you need?", min_value=1, step=1, value=1)
    user_vcpus = st.number_input("Total vCPUs needed per VM", min_value=1)
    user_ram = st.number_input("Total RAM needed per VM (GB)", min_value=1)
    user_storage = st.number_input("Total Storage per VM (GB)", min_value=1)

    # Step 1: Choose base VM based on vCPU only (≤ requested vCPU)
    def get_base_vm_by_vcpu(vm_configs, vcpu_required):
        valid_bases = [spec for spec in vm_configs.values() if spec["vCPU"] <= vcpu_required]
        if valid_bases:
            return max(valid_bases, key=lambda x: x["vCPU"])  # highest valid base
        else:
            return min(vm_configs.values(), key=lambda x: x["vCPU"])  # fallback to lowest

    base_vm = get_base_vm_by_vcpu(PRICING["vm_configs"], user_vcpus)

    # Step 2: Compute extra resources
    extra_vcpu = user_vcpus - base_vm["vCPU"]
    extra_ram = user_ram - base_vm["RAM"]
    extra_storage = user_storage - base_vm["Storage"]

    # Step 3: Pricing
    vcpu_cost = max(0, extra_vcpu) * PRICING["add_ons"]["vcpu_unit_price"]
    ram_cost = max(0, extra_ram) * PRICING["add_ons"]["ram_per_gb"]
    storage_cost = max(0, ((extra_storage + 49) // 50)) * PRICING["add_ons"]["storage_per_50gb"]
    per_vm_cost = base_vm["Price"] + vcpu_cost + ram_cost + storage_cost
    total_vm_cost = per_vm_cost * num_vms

    st.success(f"Base VM: {base_vm['vCPU']}vCPU | {base_vm['RAM']}GB RAM | {base_vm['Storage']}GB Storage — ₹{base_vm['Price']:,}/month")
    st.write(f"Extra vCPUs: {extra_vcpu} → ₹{vcpu_cost:,}")
    st.write(f"Extra RAM: {extra_ram} GB → ₹{ram_cost:,}")
    st.write(f"Extra Storage: {extra_storage} GB → ₹{storage_cost:,}")
    st.write(f"**Total VM Cost (Monthly): ₹{total_vm_cost:,.2f}**")

    st.header("2️⃣ Management Services")
    antivirus_qty = st.number_input("VMs needing Antivirus", min_value=0, max_value=num_vms)
    os_type = st.radio("OS Type", ["linux", "windows"])
    if os_type == "linux":
        os_qty = st.number_input("VMs needing Linux OS Management", min_value=0, max_value=num_vms)
        os_cost = os_qty * PRICING["management"]["os_management_linux"]
    else:
        vcpu_qty = st.number_input("Total vCPUs needing Windows OS Management", min_value=0)
        os_cost = vcpu_qty * PRICING["management"]["os_management_windows"]

    backup_qty = st.number_input("VMs needing Backup Management", min_value=0, max_value=num_vms)
    db_qty = st.number_input("Database Instances needing Management", min_value=0)

    management_cost = (
        antivirus_qty * PRICING["management"]["antivirus"] +
        os_cost +
        backup_qty * PRICING["management"]["backup_management"] +
        db_qty * PRICING["management"]["database_management"]
    )

    st.header("3️⃣ Bandwidth Requirement (Annual)")
    bandwidth_option = st.selectbox("Select Bandwidth", list(PRICING["bandwidth"].keys()))
    bandwidth_cost = PRICING["bandwidth"][bandwidth_option]

    st.header("4️⃣ Apply Discount (Optional)")
    apply_discount = st.checkbox("Apply Discount?")
    discount_percent = st.slider("Discount %", 0, 100, 0) if apply_discount else 0
    discount = (total_vm_cost + management_cost) * (discount_percent / 100)

    subtotal = total_vm_cost + management_cost
    total_monthly = subtotal - discount
    total_annual = total_monthly * 12 + bandwidth_cost

    st.header("💰 Cost Breakdown")
    st.write(f"**VM Cost (Monthly): ₹{total_vm_cost:,.2f}**")
    st.write(f"**Management Cost (Monthly): ₹{management_cost:,.2f}**")
    st.write(f"**Subtotal (Monthly): ₹{subtotal:,.2f}**")
    if discount > 0:
        st.write(f"**Discount ({discount_percent}%): -₹{discount:,.2f}**")
    st.write(f"**Total Monthly Cost: ₹{total_monthly:,.2f}**")
    st.write(f"**Bandwidth (Annual): ₹{bandwidth_cost:,.2f}**")
    st.write(f"### ✅ Total Annual Cost: ₹{total_annual:,.2f}")

if __name__ == "__main__":
    calculate_total_cost()
