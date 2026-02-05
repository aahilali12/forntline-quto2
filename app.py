import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import re
import io

# --- PDF CLASS WITH YOUR STYLING ---
class FrontlineQuotation(FPDF):
    def header(self):
        # Red Header
        self.set_text_color(255, 0, 0) 
        self.set_font('Arial', 'B', 22)
        self.cell(0, 10, 'FRONTLINE PUBLICATIONS', ln=True, align='C')
        
        # Blue Tagline
        self.set_text_color(0, 51, 102) 
        self.set_font('Arial', 'B', 10)
        self.cell(0, 5, 'Publisher, Distributor & Library Suppliers', ln=True, align='C')
        
        # Black Address
        self.set_text_color(0, 0, 0) 
        self.set_font('Arial', '', 9)
        self.cell(0, 4, 'Door No. F-4 & F-5, First Floor, CAC/Kothi RTC Bus Terminal Complex, Hyderabad.', ln=True, align='C')
        self.cell(0, 4, 'Contact: 8977500816 | Email: frontlinepub@gmail.com | Website: www.flpublications.com', ln=True, align='C')
        self.ln(5)
        self.line(10, self.get_y(), 200, self.get_y()) 
        self.ln(5)

    def footer_signature(self):
        self.set_y(-75)
        self.set_text_color(0, 51, 102)
        self.set_font('Arial', 'B', 11)
        self.cell(0, 7, 'TERMS & CONDITIONS', ln=True)
        self.set_text_color(0, 0, 0)
        self.set_font('Arial', '', 8)
        terms = [
            "1. Books supplied are in accordance with the order hence will not be taken back.",
            "2. Certified that correct Publisher's Price have been charged.",
            "3. Latest editions of Books have been supplied & current conversion Rates.",
            "4. Out station payments should be made by Bank Draft / payable Hyderabad.",
            "5. Interest @ 25% per annum will be charged if the bill is not paid.",
            "6. All Disputes are subject to Hyderabad Jurisdiction only.",
            "7. Note: All prices are subject to change without notice."
        ]
        for term in terms:
            self.cell(0, 4, term, ln=True)
        self.ln(5)
        self.set_text_color(0, 51, 102)
        self.set_font('Arial', 'B', 14)
        self.cell(0, 6, 'BOOKSEA', ln=True, align='R')
        self.set_font('Arial', 'B', 10)
        self.cell(0, 5, 'HYDERABAD', ln=True, align='R')

# --- HELPER FUNCTIONS ---
def clean_to_float(val):
    if pd.isna(val) or str(val).strip() in ["", "-", "nan"]:
        return 0.0
    num_str = re.sub(r'[^0-9.]', '', str(val))
    return float(num_str) if num_str else 0.0

def clean_text(text):
    return str(text).replace('–', '-').replace('—', '-').encode('latin-1', 'replace').decode('latin-1')

# --- MAIN WEB APP ---
def main():
    st.set_page_config(page_title="Frontline PDF Gen", page_icon="📄")
    
    st.title("📄 Frontline Quotation Generator")
    st.info("Fill in the details below. This works perfectly on mobile browsers!")

    # User Inputs
    with st.expander("College & Contact Details", expanded=True):
        college = st.text_input("College Name")
        location = st.text_input("Location (e.g., Hanamkonda)")
        phone = st.text_input("Phone Number")

    with st.expander("Quotation Specifics", expanded=True):
        course = st.selectbox("Course Type", ["BSC", "GNM"])
        sem_input = st.text_input("Semester Names (Separate with commas)", placeholder="e.g. 1st & 2nd Semester, 3rd & 4th Semester")
        qty_val = st.number_input("Student Quantity", min_value=1, value=40)
        user_disc_input = st.number_input("Discount %", min_value=0, max_value=100, value=40)

    if st.button("Generate & Download PDF"):
        if not college or not sem_input:
            st.warning("Please enter College Name and Semester names.")
            return

        # 1. Load Data
        file_name = "B.Sc Quotations.xlsx" if course == "BSC" else "GNM Quotation.xlsx"
        try:
            df = pd.read_excel(file_name, header=None)
        except Exception:
            st.error(f"Could not find {file_name}. Ensure it's in your GitHub repo.")
            return

        # 2. Extract Data
        semesters = [s.strip() for s in sem_input.split(',')]
        quotation_data = []
        total_sno = 1
        actual_discount = user_disc_input / 100.0

        for sem in semesters:
            found_section = False
            current_sem_books = []
            for _, row in df.iterrows():
                row_str = " ".join(map(str, row.values)).lower()
                if sem.lower() in row_str:
                    found_section = True
                    continue
                if found_section:
                    if "total" in row_str or (str(row[0]) == "nan" and len(current_sem_books) > 0):
                        break
                    sno_val = str(row[0]).strip()
                    if sno_val.isdigit():
                        price = clean_to_float(row[5])
                        net_price = price * (1 - actual_discount)
                        current_sem_books.append({
                            'sno': total_sno, 'title': clean_text(row[1]), 'author': clean_text(row[3]),
                            'price': price, 'net': net_price, 'total': net_price * qty_val
                        })
                        total_sno += 1
            if current_sem_books:
                quotation_data.append((sem, current_sem_books))

        if not quotation_data:
            st.error("No data found for the semesters provided.")
            return

        # 3. Create PDF
        pdf = FrontlineQuotation()
        pdf.add_page()
        
        # --- BORDER BOXES START ---
        start_y = pdf.get_y()
        
        # Left Box (Principal)
        pdf.rect(10, start_y, 130, 25) 
        pdf.set_xy(12, start_y + 2)
        pdf.set_font('Arial', '', 10)
        pdf.cell(100, 5, "To, The Principal,", ln=True)
        pdf.set_x(12); pdf.set_font('Arial', 'B', 11); pdf.set_text_color(0, 51, 102) 
        pdf.cell(100, 6, clean_text(college), ln=True) 
        pdf.set_text_color(0, 0, 0); pdf.set_font('Arial', '', 10); pdf.set_x(12)
        pdf.cell(100, 5, f"{clean_text(location)}", ln=True)
        pdf.set_x(12); pdf.cell(100, 5, f"{clean_text(phone)}", ln=True)

        # Right Box (Date)
        pdf.rect(140, start_y, 60, 25)
        pdf.set_xy(142, start_y + 2); pdf.set_font('Arial', 'B', 10)
        pdf.cell(55, 10, f"Date: {datetime.now().strftime('%d-%m-%y')}", ln=True)
        pdf.set_x(142); pdf.cell(55, 5, f"Quotation: {datetime.now().strftime('%y-%m-%d-%H')}", ln=True)
        
        pdf.set_y(start_y + 30)
        # --- BORDER BOXES END ---

        # Table Header
        pdf.set_fill_color(0, 51, 102); pdf.set_text_color(255, 255, 255); pdf.set_font('Arial', 'B', 9)
        headers = [('S.No.', 12), ('Title', 78), ('Author', 35), ('Price', 15), ('Disc%', 13), ('Qty.', 12), ('Net', 15), ('Total', 20)]
        for text, w in headers:
            pdf.cell(w, 10, text, 1, 0, 'C', True)
        pdf.ln()

        # Table Content
        pdf.set_text_color(0, 0, 0)
        grand_total = 0
        for semester_name, books in quotation_data:
            pdf.set_fill_color(204, 229, 255); pdf.set_font('Arial', 'B', 9)
            pdf.cell(200, 8, f"   {semester_name}", 1, 1, 'L', True)
            pdf.set_font('Arial', '', 9)
            for b in books:
                pdf.cell(12, 8, str(b['sno']), 1, 0, 'C')
                pdf.cell(78, 8, b['title'][:45], 1, 0, 'L')
                pdf.cell(35, 8, b['author'][:22], 1, 0, 'L')
                pdf.cell(15, 8, f"{b['price']:.0f}", 1, 0, 'C')
                pdf.cell(13, 8, f"{user_disc_input:.0f}%", 1, 0, 'C')
                pdf.cell(12, 8, str(qty_val), 1, 0, 'C')
                pdf.cell(15, 8, f"{b['net']:.0f}", 1, 0, 'C')
                pdf.cell(20, 8, f"{b['total']:.0f}", 1, 1, 'C')
                grand_total += b['total']

        # Total Row
        pdf.set_fill_color(255, 218, 185); pdf.set_font('Arial', 'B', 11); pdf.set_x(155) 
        pdf.cell(15, 12, 'Total', 1, 0, 'C', True)
        pdf.set_text_color(255, 0, 0); pdf.cell(30, 12, f"INR {grand_total:,.2f}", 1, 1, 'C', True)
        
        pdf.set_text_color(0, 0, 0); pdf.footer_signature()
        
        # Export for Streamlit Download
        pdf_bytes = pdf.output(dest='S').encode('latin-1')
        st.success("PDF Ready!")
        st.download_button(
            label="📩 Download Quotation PDF",
            data=pdf_bytes,
            file_name=f"Quotation_{college.replace(' ','_')}.pdf",
            mime="application/pdf"
        )

if __name__ == "__main__":
    main()
