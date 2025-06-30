import streamlit as st

def calculate_total_cost():
    st.set_page_config(page_title="VM Hosting Quotation Generator", layout="wide")
    st.title("💻 Hosting Quotation Generator")
    st.markdown("Customize your VM configuration and services to get an accurate cost estimate.")

    # Pricing Data
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
            "vcpu_unit_price": 2500,
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

    st.header("1️⃣ VM Requirements (Auto-Select Base on vCPU)")
    num_vms = st.number_input("How many VMs do you need?", min_value=1, step=1, value=1)
    user_vcpus = st.number_input("Total vCPUs per VM", min_value=1)
    user_ram = st.number_input("Total RAM per VM (GB)", min_value=1)
    user_storage = st.number_input("Total Storage per VM (GB)", min_value=1)

    # Choose the base VM based on vCPU
    def get_base_vm_by_vcpu(vm_configs, vcpu_required):
        valid_bases = [spec for spec in vm_configs.values() if spec["vCPU"] <= vcpu_required]
        if valid_bases:
            return max(valid_bases, key=lambda x: x["vCPU"])
        return min(vm_configs.values(), key=lambda x: x["vCPU"])

    base_vm = get_base_vm_by_vcpu(PRICING["vm_configs"], user_vcpus)
    extra_vcpu = max(0, user_vcpus - base_vm["vCPU"])
    extra_ram = max(0, user_ram - base_vm["RAM"])
    extra_storage = max(0, user_storage - base_vm["Storage"])

    vcpu_cost = extra_vcpu * PRICING["add_ons"]["vcpu_unit_price"]
    ram_cost = extra_ram * PRICING["add_ons"]["ram_per_gb"]
    storage_cost = ((extra_storage + 49) // 50) * PRICING["add_ons"]["storage_per_50gb"]

    per_vm_cost = base_vm["Price"] + vcpu_cost + ram_cost + storage_cost
    total_vm_cost_monthly = per_vm_cost * num_vms
    total_vm_cost_annual = total_vm_cost_monthly * 12

    st.success(f"Selected Base VM: {base_vm['vCPU']}vCPU | {base_vm['RAM']}GB RAM | {base_vm['Storage']}GB Storage → ₹{base_vm['Price']}/month")
    st.write(f"Extra vCPUs: {extra_vcpu} → ₹{vcpu_cost}")
    st.write(f"Extra RAM: {extra_ram}GB → ₹{ram_cost}")
    st.write(f"Extra Storage: {extra_storage}GB → ₹{storage_cost}")
    st.write(f"**Total VM Cost (Monthly for all VMs): ₹{total_vm_cost_monthly:,.2f}**")

    # Management Services
    st.header("2️⃣ Management Services")
    antivirus_qty = st.number_input("VMs needing Antivirus", min_value=0, max_value=num_vms)
    os_type = st.radio("OS Type", ["linux", "windows"])

    if os_type == "linux":
        os_qty = st.number_input("VMs needing Linux OS Management", min_value=0, max_value=num_vms)
        os_cost_monthly = os_qty * PRICING["management"]["os_management_linux"]
    else:
        vcpu_qty = st.number_input("Total vCPUs needing Windows OS Management", min_value=0)
        os_cost_monthly = vcpu_qty * PRICING["management"]["os_management_windows"]

    backup_qty = st.number_input("VMs needing Backup Management", min_value=0, max_value=num_vms)
    db_qty = st.number_input("Databases needing Management", min_value=0)

    antivirus_cost = antivirus_qty * PRICING["management"]["antivirus"]
    backup_cost = backup_qty * PRICING["management"]["backup_management"]
    db_cost = db_qty * PRICING["management"]["database_management"]

    management_cost_monthly = antivirus_cost + os_cost_monthly + backup_cost + db_cost
    management_cost_annual = management_cost_monthly * 12

    # Bandwidth
    st.header("3️⃣ Bandwidth Requirement (Annual)")
    bandwidth_choice = st.selectbox("Select Bandwidth Option", list(PRICING["bandwidth"].keys()))
    bandwidth_cost = PRICING["bandwidth"][bandwidth_choice]

    # Discount
    st.header("4️⃣ Apply Discount (Optional)")
    apply_discount = st.checkbox("Apply Discount?")
    discount_percent = st.slider("Discount Percentage", 0, 100, 0) if apply_discount else 0
    discount_monthly = (total_vm_cost_monthly + management_cost_monthly) * (discount_percent / 100)
    discount_annual = discount_monthly * 12

    # Final Calculations
    subtotal_monthly = total_vm_cost_monthly + management_cost_monthly
    subtotal_annual = total_vm_cost_annual + management_cost_annual
    total_annual_with_bandwidth = subtotal_annual + bandwidth_cost - discount_annual

    # Cost Breakdown Table Format
    st.header("📊 Final Cost Breakdown")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Total (A) - Infrastructure")
        st.write(f"**VMs Total Annual (Base + Add-ons):** ₹{total_vm_cost_annual:,.0f}")
    with col2:
        st.subheader("Total (B) - Management")
        st.write(f"Antivirus: ₹{antivirus_cost * 12:,.0f}")
        st.write(f"OS Mgmt ({os_type}): ₹{os_cost_monthly * 12:,.0f}")
        st.write(f"Backup Mgmt: ₹{backup_cost * 12:,.0f}")
        st.write(f"DB Mgmt: ₹{db_cost * 12:,.0f}")
        st.write(f"**Total (B): ₹{management_cost_annual:,.0f}**")

    st.markdown("---")

    st.subheader("🧾 Annual Summary")
    st.write(f"**Total Annual Recurring Cost (A + B): ₹{subtotal_annual:,.0f}**")
    st.write(f"**Bandwidth (Annual): ₹{bandwidth_cost:,.0f}**")
    if apply_discount and discount_percent > 0:
        st.write(f"**Discount ({discount_percent}%): -₹{discount_annual:,.0f}**")

    st.markdown(f"### ✅ **Final Total Annual Cost: ₹{total_annual_with_bandwidth:,.0f}**")

if __name__ == "__main__":
    calculate_total_cost()
