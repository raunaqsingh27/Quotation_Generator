import streamlit as st
import re
import pandas as pd
from fpdf import FPDF
import tempfile
import os
from num2words import num2words

class PDF(FPDF):
    def header(self):
        pass  # We'll use a custom header method for the quotation

    def quotation_header(self, logo_path, customer_info, quotation_info):
        # --- Main Heading: Quotation ---
        self.set_font("Arial", "BU", 18)  # Underline
        self.cell(0, 16, "Quotation", ln=True, align="C")
        self.ln(2)

        y_start = self.get_y() + 2
        x_left = self.l_margin
        x_right = x_left + 70  # Enough space for logo + phoneme info

        # --- Left: Phoneme logo and info ---
        self.set_xy(x_left, y_start)
        self.image(logo_path, x=x_left, y=y_start, w=40)
        self.set_xy(x_left, y_start + 20)
        self.set_font("Arial", "B", 10)
        self.multi_cell(60, 6, "PHONEME SOLUTIONS PRIVATE LIMITED", 0)
        self.set_font("Arial", "", 9)
        self.multi_cell(60, 5, "B-614 6TH FLOOR TOWER B PLOT NO 7\nNoida Pincode 201305\nNoida, 9 201305\nGSTN: 09AAHCP9748G2ZS", 0)
        y_left_end = self.get_y()

        # --- Right: Customer info ---
        self.set_xy(x_right, y_start + 20)
        self.set_font("Arial", "B", 10)
        self.multi_cell(80, 6, customer_info['name'], 0)
        self.set_x(x_right)  # Reset X after multi_cell
        self.set_font("Arial", "", 9)
        self.multi_cell(80, 5, customer_info['address'], 0)
        self.set_x(x_right)  # Reset X after multi_cell
        if customer_info.get('email'):
            self.cell(80, 5, f"Email: {customer_info['email']}", ln=1)
            self.set_x(x_right)
        if customer_info.get('gstn'):
            self.cell(80, 5, f"GSTN: {customer_info['gstn']}", ln=1)
            self.set_x(x_right)
        y_right_end = self.get_y()

        # --- Below both: Quotation No. and Date ---
        self.set_y(max(y_left_end, y_right_end) + 5)
        self.set_font("Arial", "B", 10)
        self.cell(40, 6, "Quotation No:", 0, 0)
        self.set_font("Arial", "", 10)
        self.cell(40, 6, quotation_info['number'], 0, 0)
        self.set_font("Arial", "B", 10)
        self.cell(40, 6, "Quotation Date:", 0, 0)
        self.set_font("Arial", "", 10)
        self.cell(40, 6, quotation_info['date'], 0, 1)
        self.ln(5)

    def add_terms_and_conditions(self):
        self.set_y(-40)
        self.set_font("Arial", "B", 10)
        self.cell(0, 8, "Terms & Conditions", ln=True, align="C")
        self.set_font("Arial", "", 10)
        combined = "Validity: This quotation is valid for 15 days from the date of issue. This is computer generated Quotation Signature is not required"
        self.cell(0, 7, combined, ln=True, align="C")

    def table(self, title, dataframe):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, title, ln=True)
        self.set_font("Arial", "B", 10)

        # Dynamically calculate column widths
        table_width = self.w - 2 * self.l_margin
        col_widths = []
        min_col_width = 20
        max_col_width = 60
        total_width = 0
        for col in dataframe.columns:
            max_content_width = max(
                [self.get_string_width(str(col))] + [self.get_string_width(str(val)) for val in dataframe[col]]
            ) + 6  # padding
            col_width = min(max(max_content_width, min_col_width), max_col_width)
            col_widths.append(col_width)
            total_width += col_width
        # Scale widths if total exceeds table width
        if total_width > table_width:
            scale = table_width / total_width
            col_widths = [w * scale for w in col_widths]

        # Header
        for i, col in enumerate(dataframe.columns):
            self.cell(col_widths[i], 8, str(col), border=1, align="C")
        self.ln()

        self.set_font("Arial", "", 9)
        # Rows
        for _, row in dataframe.iterrows():
            y_before = self.get_y()
            x_before = self.get_x()
            row_height = 8
            # Calculate max height for this row
            cell_heights = []
            for i, val in enumerate(row):
                val_str = str(val)
                n_lines = max(1, int(self.get_string_width(val_str) / (col_widths[i] - 2)) + 1)
                cell_heights.append(5 * n_lines)
            row_height = max(cell_heights)
            for i, val in enumerate(row):
                val_str = str(val)
                x = self.get_x()
                y = self.get_y()
                self.multi_cell(col_widths[i], 5, val_str, border=1, align="L")
                self.set_xy(x + col_widths[i], y)
            self.ln(row_height)
        self.ln(5)

    def simple_table(self, dataframe):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "Final Summary", ln=True)
        self.set_font("Arial", "", 10)

        for _, row in dataframe.iterrows():
            self.cell(100, 8, str(row['Description']), border=1)
            self.cell(60, 8, str(row['Amount (INR)']), border=1)
            self.ln()
        self.ln(5)

    def main_quotation_table(self, data, grand_total, tax, amount_words):
        self.set_font("Arial", "B", 10)
        headers = ["S. No.", "Items/Services", "Qty", "Unit Price", "Taxable Value", "Tax", "Subtotal"]
        # Calculate available table width
        table_width = self.w - 2 * self.l_margin
        # Relative proportions for each column (adjust as needed)
        col_props = [1, 3.5, 1, 1.5, 2, 2.7, 2]
        total_props = sum(col_props)
        col_widths = [table_width * (prop / total_props) for prop in col_props]
        for i, h in enumerate(headers):
            self.cell(col_widths[i], 8, h, border=1, align="C")
        self.ln()
        self.set_font("Arial", "", 8)  # Use a smaller font for table rows
        for i, row in enumerate(data, 1):
            row_data = [
                str(i),
                row["items_services"],
                str(row["qty"]),
                f"{row['unit_price']:.2f}",
                f"{row['taxable_value']:.2f}",
                "IGST 18%",
                f"{row['taxable_value'] + row['tax']:.2f}"
            ]
            # Calculate the height needed for the Items/Services cell
            lines = self.multi_cell(col_widths[1], 5, row_data[1], border=0, align="L", split_only=True)
            row_height = max(8, 5 * len(lines))
            y_start = self.get_y()
            x_start = self.get_x()
            # S. No.
            self.set_xy(x_start, y_start)
            self.cell(col_widths[0], row_height, row_data[0], border=1)
            # Items/Services (multi_cell)
            self.set_xy(x_start + col_widths[0], y_start)
            self.multi_cell(col_widths[1], 5, row_data[1], border=1, align="L")
            # Move to the right for the rest of the cells
            self.set_xy(x_start + col_widths[0] + col_widths[1], y_start)
            for j in range(2, 7):
                cell_text = row_data[j]
                if j in [3, 4, 5] and len(cell_text) > 15:
                    cell_text = cell_text[:12] + '...'
                self.cell(col_widths[j], row_height, cell_text, border=1, align="R" if j in [3, 5, 6] else "C")
            self.ln(row_height)
        # Grand Total row
        self.set_font("Arial", "B", 10)
        # Label cell spanning first 4 columns
        self.cell(sum(col_widths[:4]), 8, "Grand Total:", border=1)
        # Taxable Value column (empty)
        self.cell(col_widths[4], 8, "", border=1)
        # Tax column (tax amount)
        self.cell(col_widths[5], 8, f"INR {tax:,.2f}", border=1, align="R")
        # Subtotal column (grand total)
        self.cell(col_widths[6], 8, f"INR {grand_total:,.2f}", border=1, align="C")
        self.ln()
        # Amount in Words row
        label_width = col_widths[0] + col_widths[1]
        value_width = sum(col_widths[2:])
        self.set_font("Arial", "", 10)
        lines = self.multi_cell(value_width, 8, amount_words, border=0, align="L", split_only=True)
        value_height = 8 * len(lines)
        y_start = self.get_y()
        x_start = self.get_x()
        self.set_xy(x_start, y_start)
        self.set_font("Arial", "B", 10)
        self.cell(label_width, value_height, "Amount in Words:", border=1)
        self.set_xy(x_start + label_width, y_start)
        self.set_font("Arial", "", 10)
        self.multi_cell(value_width, 8, amount_words, border=1)
        self.ln(2)
        self.ln(8)

# ---- Main Function Begins ----
def calculate_total_cost():
    st.set_page_config(page_title="VM Hosting Quotation Generator", layout="wide")
    st.title(" VM Hosting Quotation Generator")

    # ---- Quotation & Customer Info ----
    st.header(" Quotation & Customer Info")
    cust_col1, cust_col2 = st.columns([1, 1])
    with cust_col1:
        customer_name = st.text_input("Customer Company Name", "", key="customer_name", help="Enter the company name", max_chars=50)
        customer_gstn = st.text_input("Customer GSTN", "", key="customer_gstn", help="GSTN (optional)", max_chars=20)
        customer_email = st.text_input("Customer Email (optional)", "", key="customer_email", help="Email (optional)", max_chars=40)
    with cust_col2:
        customer_address = st.text_area("Customer Address", "", key="customer_address", help="Enter the address", height=90, max_chars=120)
        quotation_no = st.text_input("Quotation No.", "", key="quotation_no", help="Quotation number", max_chars=20)
        quotation_date = st.date_input("Quotation Date", key="quotation_date")

    # ---- Pricing Dictionary ----
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
            "Dedicated 10 MBPS": 250000,
            "Default": 0,
        }
    }

    # ---- Input Section ----
    st.header(" VM Requirements")
    st.markdown("Enter your VM requirement like: `8vCPU 32GB RAM 1000GB Storage`")
    vm_col1, vm_col2 = st.columns([1, 1])
    with vm_col1:
        num_vms = st.number_input("How many VMs?", min_value=1, step=1, value=1, key="num_vms", help="Number of VMs", format="%d")
        user_vcpus = st.number_input("No. of vCPUs", min_value=1, step=1, value=1, key="vcpu", help="Number of vCPUs per VM")
    with vm_col2:
        user_ram = st.number_input("RAM (GB)", min_value=1, step=1, value=1, key="ram", help="RAM per VM in GB")
        user_storage = st.number_input("Storage (GB)", min_value=1, step=1, value=1, key="storage", help="Storage per VM in GB")

    if not all([user_vcpus, user_ram, user_storage]):
        st.warning("⚠️ Please enter all VM requirements.")
        return

    # ---- Cost Calculation ----
    def get_base_vm(vm_configs, user_vcpu):
        valid = [v for v in vm_configs.values() if v["vCPU"] <= user_vcpu]
        return max(valid, key=lambda x: x["vCPU"]) if valid else min(vm_configs.values(), key=lambda x: x["vCPU"])

    base_vm = get_base_vm(PRICING["vm_configs"], user_vcpus)
    extra_vcpu = max(0, user_vcpus - base_vm["vCPU"])
    extra_ram = max(0, user_ram - base_vm["RAM"])
    extra_storage = max(0, user_storage - base_vm["Storage"])

    vcpu_cost = extra_vcpu * PRICING["add_ons"]["vcpu_unit_price"]
    ram_cost = extra_ram * PRICING["add_ons"]["ram_per_gb"]
    storage_cost = ((extra_storage + 49) // 50) * PRICING["add_ons"]["storage_per_50gb"]
    per_vm_cost = base_vm["Price"] + vcpu_cost + ram_cost + storage_cost
    total_vm_monthly = per_vm_cost * num_vms
    total_vm_annual = total_vm_monthly * 12

    st.success(f"Selected Base VM: {base_vm['vCPU']}vCPU | {base_vm['RAM']}GB RAM | {base_vm['Storage']}GB → ₹{base_vm['Price']} / mo")

    # ---- Management Section ----
    st.header(" Management Services")
    mgmt_col1, mgmt_col2 = st.columns([1, 1])
    with mgmt_col1:
        antivirus_qty = st.number_input("Antivirus (VMs)", min_value=0, max_value=num_vms, key="antivirus")
        backup_qty = st.number_input("Backup Management VMs", min_value=0, max_value=num_vms, key="backup")
        db_qty = st.number_input("Databases to Manage", min_value=0, key="db")
    with mgmt_col2:
        os_type = st.radio("OS Type", ["linux", "windows"], key="os_type")
        os_qty = st.number_input("Linux OS Mgmt VMs" if os_type == "linux" else "Windows OS Mgmt vCPUs", min_value=0, key="os_qty")

    antivirus_cost = antivirus_qty * PRICING["management"]["antivirus"]
    os_cost = os_qty * PRICING["management"]["os_management_linux" if os_type == "linux" else "os_management_windows"]
    backup_cost = backup_qty * PRICING["management"]["backup_management"]
    db_cost = db_qty * PRICING["management"]["database_management"]
    mgmt_monthly = antivirus_cost + os_cost + backup_cost + db_cost
    mgmt_annual = mgmt_monthly * 12

    # ---- Bandwidth and Discount Headers (side by side above tables) ----
    band_col, disc_col = st.columns([1, 1])
    with band_col:
        st.header(" Bandwidth (Annual)")
    with disc_col:
        st.header(" Optional Discount")

    # ---- Bandwidth and Discount Controls ----
    band_col, disc_col = st.columns([1, 1])
    with band_col:
        bw_choice = st.selectbox("Bandwidth", list(PRICING["bandwidth"].keys()), key="bandwidth")
        bandwidth_cost = PRICING["bandwidth"][bw_choice]
    with disc_col:
        apply_discount = st.checkbox("Apply Discount?", key="apply_discount")
        discount_percent = st.slider("Discount (%)", 0, 100, 0, key="discount") if apply_discount else 0
    discount_amt = (total_vm_annual + mgmt_annual) * (discount_percent / 100)
    final_total = (total_vm_annual + mgmt_annual + bandwidth_cost - discount_amt)

    # ---- VM Table ----
    df_vm_rows = [
        {
            "Item/Specification": f"{base_vm['vCPU']}vCPU {base_vm['RAM']}GB {base_vm['Storage']}GB",
            "Qty": num_vms,
            "Unit Monthly Price": base_vm["Price"],
            "Total Monthly Price": base_vm["Price"] * num_vms,
            "Total Annual Price": base_vm["Price"] * num_vms * 12,
        }
    ]
    # Add extra rows for additional requirements if any
    if extra_vcpu > 0:
        df_vm_rows.append({
            "Item/Specification": f"Extra vCPU x{extra_vcpu}",
            "Qty": num_vms,
            "Unit Monthly Price": PRICING["add_ons"]["vcpu_unit_price"],
            "Total Monthly Price": vcpu_cost,
            "Total Annual Price": vcpu_cost * 12,
        })
    if extra_ram > 0:
        df_vm_rows.append({
            "Item/Specification": f"Extra RAM x{extra_ram}GB",
            "Qty": num_vms,
            "Unit Monthly Price": PRICING["add_ons"]["ram_per_gb"],
            "Total Monthly Price": ram_cost,
            "Total Annual Price": ram_cost * 12,
        })
    if extra_storage > 0:
        df_vm_rows.append({
            "Item/Specification": f"Extra Storage x{extra_storage}GB",
            "Qty": num_vms,
            "Unit Monthly Price": PRICING["add_ons"]["storage_per_50gb"],
            "Total Monthly Price": storage_cost,
            "Total Annual Price": storage_cost * 12,
        })
    df_vm = pd.DataFrame(df_vm_rows)
    df_vm.index += 1
    st.subheader("🔹 Infrastructure Cost")
    # Ensure numeric columns for formatting
    for col in ["Unit Monthly Price", "Total Monthly Price", "Total Annual Price"]:
        df_vm[col] = pd.to_numeric(df_vm[col], errors='coerce')
    st.dataframe(df_vm.style.format({
        "Unit Monthly Price": "INR {:,.0f}",
        "Total Monthly Price": "INR {:,.0f}",
        "Total Annual Price": "INR {:,.0f}"
    }), use_container_width=True)

    # ---- Management Table ----
    df_mgmt = pd.DataFrame([
        {"Item/Specification": "Antivirus", "Qty": antivirus_qty, "Unit Monthly Price": PRICING["management"]["antivirus"], "Total Monthly Price": antivirus_cost, "Total Annual Price": antivirus_cost * 12},
        {"Item/Specification": f"OS Mgmt ({os_type})", "Qty": os_qty, "Unit Monthly Price": PRICING["management"]["os_management_linux" if os_type == "linux" else "os_management_windows"], "Total Monthly Price": os_cost, "Total Annual Price": os_cost * 12},
        {"Item/Specification": "Backup", "Qty": backup_qty, "Unit Monthly Price": PRICING["management"]["backup_management"], "Total Monthly Price": backup_cost, "Total Annual Price": backup_cost * 12},
        {"Item/Specification": "Database Mgmt", "Qty": db_qty, "Unit Monthly Price": PRICING["management"]["database_management"], "Total Monthly Price": db_cost, "Total Annual Price": db_cost * 12},
    ])
    df_mgmt.index += 1
    st.subheader("🔹 Management Services")
    # Ensure numeric columns for formatting
    for col in ["Unit Monthly Price", "Total Monthly Price", "Total Annual Price"]:
        df_mgmt[col] = pd.to_numeric(df_mgmt[col], errors='coerce')
    st.dataframe(df_mgmt.style.format({
        "Unit Monthly Price": "INR {:,.0f}",
        "Total Monthly Price": "INR {:,.0f}",
        "Total Annual Price": "INR {:,.0f}"
    }), use_container_width=True)

    # ---- Summary ----
    summary = [
        {"Description": "Total Recurring (Infra + Mgmt)", "Amount (INR)": f"INR {(total_vm_annual + mgmt_annual):,.0f}"},
        {"Description": f"Bandwidth ({bw_choice})", "Amount (INR)": f"INR {bandwidth_cost:,.0f}"},
    ]
    if discount_percent > 0:
        summary.append({"Description": f"Discount ({discount_percent}%)", "Amount (INR)": f"-INR {discount_amt:,.0f}"})
    summary.append({"Description": "Final Quotation", "Amount (INR)": f"INR {final_total:,.0f}"})
    df_summary = pd.DataFrame(summary)
    df_summary.index += 1
    st.subheader(" Final Summary")
    st.dataframe(df_summary, use_container_width=True)

    # ---- PDF Download ----
    if st.button("Download Final Quotation as PDF"):
        pdf = PDF()
        pdf.add_page()

        # Prepare info for header
        logo_path = "phoneme_logo.png"
        customer_info = {
            "name": customer_name,
            "address": customer_address,
            "gstn": customer_gstn,
            "email": customer_email,
        }
        quotation_info = {
            "number": quotation_no,
            "date": quotation_date.strftime("%d-%m-%Y") if hasattr(quotation_date, 'strftime') else str(quotation_date),
        }
        # Calculate values for the main table
        main_items_services = f"App server {user_vcpus}vCPU {user_ram}GB RAM {user_storage}GB Storage, Antivirus, OS Managemnt({os_type.title()}), Backup Management"
        main_qty = num_vms
        main_unit_price = per_vm_cost
        main_taxable_value = final_total  # Use final quotation amount as taxable value
        main_tax = round(main_taxable_value * 0.18, 2)
        main_tax_str = f"IGST 18% INR {main_tax:,.2f}"
        main_grand_total = main_taxable_value + main_tax  # Grand total is taxable value + 18% IGST
        # Amount in words (using num2words)
        total_amount = round(main_grand_total, 2)
        # Format to two decimal places and keep on one line
        main_amount_words = num2words(int(total_amount), lang='en_IN').replace(',', '').title()
        decimal_part = int(round((total_amount - int(total_amount)) * 100))
        if decimal_part > 0:
            # Convert each digit to words
            decimal_words = ' '.join([num2words(int(d), lang='en_IN').title() for d in f'{decimal_part:02d}'])
            main_amount_words += f" Point {decimal_words}"
        main_amount_words += " Rupees Only"
        pdf.quotation_header(logo_path, customer_info, quotation_info)
        pdf.main_quotation_table(
            data=[{
                "items_services": main_items_services,
                "item_description": main_items_services,
                "qty": main_qty,
                "unit_price": main_unit_price,
                "taxable_value": main_taxable_value,
                "tax": float(main_tax),  # Ensure this is always a float
            }],
            grand_total=main_grand_total,
            tax=main_tax,
            amount_words=main_amount_words
        )
        # Add Terms & Conditions at the end of the first page, before page break
        pdf.add_terms_and_conditions()

        pdf.add_page()
        pdf.table("Infrastructure Cost", df_vm)
        pdf.table("Management Services", df_mgmt)
        pdf.simple_table(df_summary)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            pdf.output(tmp.name)
            with open(tmp.name, "rb") as f:
                st.download_button("📥 Download PDF", f, "vm_quotation.pdf", "application/pdf")

if __name__ == "__main__":
    calculate_total_cost()
