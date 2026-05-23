"""Generate 20 realistic sample documents: 6 Invoice, 5 Resume, 5 Utility Bill, 2 Other, 2 Unclassifiable"""
import os

os.makedirs("sample_docs", exist_ok=True)

docs = {

# ─────────────── INVOICES (6) ───────────────
"invoice_001.txt": """
NEXUS DIGITAL SOLUTIONS LTD
88 Innovation Park, London EC2A 4NW
VAT No: GB123456789

INVOICE

Invoice #: INV-2025-0041
Invoice Date: 15/01/2025
Due Date: 14/02/2025

Bill To:
Orion Retail Group
22 Commerce Street, Manchester M1 2AB

Description                          Qty    Unit Price    Total
Web Development (Phase 1)              1      £3,200.00   £3,200.00
UI/UX Design Services                  1      £1,500.00   £1,500.00
Monthly Hosting & Maintenance          3        £150.00     £450.00

Subtotal:  £5,150.00
VAT (20%): £1,030.00
Total Amount Due: £6,180.00

Bank Details: Barclays | Sort: 20-44-51 | Acc: 73829104
Payment Terms: Net 30. Late fees apply after due date.
""",

"invoice_002.txt": """
ALPHA CONSULTING GROUP INC.
Suite 400, 1200 Bay Street, Toronto, ON M5R 2A5

TAX INVOICE

Invoice Number: AC-INV-8821
Date: February 3, 2025
Payment Due: March 5, 2025

Vendor: Alpha Consulting Group Inc.

Billed To:
Lakeside Finance Corp.
900 King West, Toronto ON M5V 3G4

Services Rendered:
  Financial Risk Assessment (Q4 2024)     $4,500.00
  Regulatory Compliance Review            $2,800.00
  Board Report Preparation                $1,200.00

Subtotal:          $8,500.00
HST (13%):         $1,105.00
Grand Total:       $9,605.00

Please remit payment to: accounts@alphaconsulting.ca
PO Number: PO-2024-LC-009
""",

"invoice_003.txt": """
BRIGHTSTAR EVENTS & CATERING
Plot 5, Industrial Estate, Karachi 75600
NTN: 1234567-8

INVOICE

Invoice No: BSE-0099
Invoice Date: 2025-01-28

Bill To:
Horizon Corporation Ltd.
14th Floor, Dolmen Mall, Karachi

Items:
  Corporate Dinner (150 pax) @ Rs.1,800/head    Rs.270,000
  Stage Setup & AV Equipment                    Rs.45,000
  Floral Decoration                             Rs.22,500
  Waitstaff (10 staff × 8 hrs)                  Rs.18,000

Subtotal:    Rs.355,500
GST (17%):   Rs.60,435
Total Due:   Rs.415,935

Payment Instructions: Meezan Bank | IBAN: PK91MEZN0001010123456789
""",

"invoice_004.txt": """
CLOUDWARE TECHNOLOGIES
789 Silicon Avenue, San Francisco CA 94105
EIN: 47-1234567

INVOICE

Invoice #: CWT-2025-JAN-114
Date: January 10, 2025
Due Date: January 25, 2025

Bill To:
DataVault Inc.
3900 Freedom Circle, Santa Clara CA 95054

Line Items:
  SaaS Platform License (Annual)              $12,000.00
  Premium Support Package                      $3,600.00
  Onboarding & Training (8 hrs)                $1,600.00
  Custom API Integration                       $2,800.00

Subtotal:                                    $20,000.00
Discount (10%):                              -$2,000.00
Sales Tax (9.25%):                            $1,665.00
Total Amount Due:                            $19,665.00

ACH / Wire: Chase Bank | Routing: 021000021 | Acct: 9876543210
""",

"invoice_005.txt": """
GREEN LEAF PRINTING PRESS
Industrial Zone B, Block 12, Lahore

INVOICE

Inv No.: GLP-441
Date: 03-Feb-2025
Due Date: 18-Feb-2025

Customer: Punjab Education Foundation

Printed Material:
  Textbooks Grade 5 (2,000 copies)   Rs.180,000
  Workbooks (1,500 copies)           Rs.67,500
  Posters & Charts (500 sets)        Rs.15,000

Total Amount:  Rs.262,500
Advance Paid: -Rs.100,000
Balance Due:   Rs.162,500

Payment via bank transfer only. Cheques not accepted.
""",

"invoice_006.txt": """
MEDITECH SUPPLIES CO.
44 Health Avenue, Dubai Healthcare City
TRN: 100234567890123

TAX INVOICE

Invoice Number: MTS-INV-3301
Invoice Date: 20 January 2025
Payment Due: 19 February 2025

Bill To:
Al Zahra Private Hospital
PO Box 3499, Dubai, UAE

Item Description                    Qty     Unit Price (AED)    Total (AED)
Surgical Gloves (Box of 100)        200           45.00          9,000.00
Disposable Syringes 5ml (Box)        50           38.00          1,900.00
IV Cannula 20G (Box)                 30           85.00          2,550.00
Sterile Gauze Pads (Pack)           100           22.00          2,200.00

Subtotal:    AED 15,650.00
VAT (5%):       AED 782.50
Total Due:   AED 16,432.50

Purchase Order Ref: AZH-PO-2025-018
""",

# ─────────────── RESUMES (5) ───────────────
"resume_001.txt": """
SARA AHMED
sara.ahmed@gmail.com | +92-333-5678901 | Karachi, Pakistan
linkedin.com/in/saraahmed | github.com/sara-dev

PROFESSIONAL SUMMARY
Full-stack developer with 4 years of experience building scalable web applications using React, Node.js, and PostgreSQL. Passionate about clean code and agile workflows.

WORK EXPERIENCE

Senior Frontend Developer — TechNova Solutions, Karachi (2022 – Present)
  • Led development of company's flagship SaaS dashboard (50k+ users)
  • Reduced page load time by 60% through lazy loading and code splitting
  • Mentored 3 junior developers

Frontend Developer — DigiSoft Ltd., Karachi (2021 – 2022)
  • Built reusable React component library used across 5 projects
  • Integrated REST APIs and implemented JWT authentication

EDUCATION
B.S. Computer Science — NED University of Engineering & Technology, 2021

SKILLS
React, TypeScript, Node.js, PostgreSQL, MongoDB, Docker, Git, Agile/Scrum
""",

"resume_002.txt": """
MICHAEL OKONKWO
m.okonkwo@outlook.com
Phone: +44 7911 234567
London, United Kingdom

CURRICULUM VITAE

OBJECTIVE
Experienced data scientist with 7 years of experience in machine learning, statistical modeling, and big data analytics seeking a senior role in a forward-thinking organisation.

PROFESSIONAL EXPERIENCE

Lead Data Scientist — FinSight Analytics, London (2021 – Present)
  Developed credit scoring models reducing default rates by 18%
  Built real-time fraud detection pipeline processing 2M transactions/day

Senior Data Analyst — RetailIQ, Birmingham (2018 – 2021)
  Delivered customer segmentation analysis boosting campaign ROI by 34%

Data Analyst — StartupBase Ltd (2017 – 2018)
  Created Tableau dashboards for C-suite weekly reporting

EDUCATION
MSc Data Science — University of Edinburgh, 2017
BSc Statistics — University of Lagos, 2015

CERTIFICATIONS
AWS Certified Machine Learning Specialist
Google Professional Data Engineer
Microsoft Azure Data Scientist Associate

SKILLS
Python, R, SQL, TensorFlow, Spark, Tableau, Azure ML, Scikit-learn
""",

"resume_003.txt": """
FATIMA AL-RASHIDI
fatima.alrashidi@email.com | +971-50-987-6543
Dubai, UAE | linkedin.com/in/fatima-rashidi

RESUME

PROFILE
Marketing professional with 6 years of experience in digital marketing, brand strategy, and content creation across FMCG and retail sectors.

EXPERIENCE

Digital Marketing Manager — Emirates Retail Group, Dubai (2022 – Present)
  • Grew social media following from 80k to 420k in 18 months
  • Managed $2M annual digital advertising budget
  • Launched 3 major product campaigns with 40%+ engagement rates

Marketing Executive — Al Futtaim Group, Dubai (2019 – 2022)
  • Coordinated with agencies for ATL and BTL campaigns
  • Developed email marketing sequences (38% open rate)

EDUCATION
Bachelor of Arts in Marketing — American University of Sharjah, 2019

SKILLS
Google Ads, Meta Ads, SEO, HubSpot, Canva, Google Analytics, Content Strategy

LANGUAGES
English (Fluent), Arabic (Native), French (Intermediate)
""",

"resume_004.txt": """
JAMES PETERSON
james.p@protonmail.com
(312) 555-0182
Chicago, Illinois

RESUME

SUMMARY
Civil engineer with 11 years of experience in structural design, construction management, and infrastructure projects across commercial and residential sectors.

WORK EXPERIENCE

Senior Structural Engineer — Morrison & Burke Engineering (2018 – Present)
  Designed structural systems for 12 high-rise buildings (15–45 floors)
  Led team of 8 engineers on $90M downtown redevelopment project
  Ensured compliance with IBC, ACI 318, and AISC standards

Project Engineer — Lakefront Constructors (2014 – 2018)
  Managed construction of 3 bridge rehabilitation projects ($15M–$40M)
  Coordinated with city inspectors and subcontractors

Graduate Engineer — TerraStruct LLC (2013 – 2014)
  Assisted in foundation design and geotechnical analysis

EDUCATION
M.S. Civil Engineering (Structural) — Illinois Institute of Technology, 2013
B.S. Civil Engineering — University of Illinois at Chicago, 2011

CERTIFICATIONS
Professional Engineer (PE) License — Illinois
LEED Green Associate
""",

"resume_005.txt": """
AISHA MALIK
aisha.malik92@yahoo.com
Mobile: 0300-1234567
Islamabad, Pakistan

CURRICULUM VITAE

CAREER OBJECTIVE
Dedicated HR professional with 3 years of experience in recruitment, employee relations, and performance management seeking growth in a dynamic organization.

PROFESSIONAL EXPERIENCE

HR Executive — Packages Limited, Islamabad (2022 – Present)
  Managed end-to-end recruitment for 200+ positions annually
  Implemented new onboarding process reducing time-to-productivity by 25%
  Handled employee grievances and disciplinary procedures

HR Assistant — BankAl Habib, Islamabad (2021 – 2022)
  Assisted payroll processing for 300+ employees
  Maintained HRIS database and employee records

EDUCATION
MBA (Human Resource Management) — COMSATS University Islamabad, 2021
BBA — Fatima Jinnah Women University, 2019

SKILLS
MS Office, SAP HR, Recruitment, Performance Management, Labour Law, HRIS

REFERENCES
Available upon request
""",

# ─────────────── UTILITY BILLS (5) ───────────────
"utility_bill_001.txt": """
KARACHI ELECTRIC SUPPLY COMPANY (KESC)
Customer Care: 118 | kesc.com.pk

ELECTRICITY BILL

Account Number: KE-0045-778821-03
Consumer Name: Muhammad Tariq
Service Address: House 12, Block 7, PECHS, Karachi

Billing Period: 01 January 2025 – 31 January 2025
Bill Date: 03 February 2025
Due Date: 18 February 2025

Meter Readings:
  Previous:   14,320 kWh
  Current:    14,707 kWh
  Usage:         387 kWh

Charges:
  Energy Charges (387 kWh × Rs.22.50)     Rs.8,707.50
  Fixed Charges                             Rs.300.00
  Fuel Price Adjustment                   Rs.1,161.00
  Electricity Duty (1.5%)                   Rs.152.51
  GST (18%)                               Rs.1,855.09

Amount Due:  Rs.12,176.10

Last Date: 18-Feb-2025. Disconnection after due date.
""",

"utility_bill_002.txt": """
SUSTAINABLE GAS NETWORK
PO Box 7700, Birmingham B1 1AA
Customer Services: 0800 111 999

GAS BILL

Account Number: SGN-884421-B
Service Address: 45 Maple Close, Coventry CV3 2PQ
Customer: Helen Richards

Statement Date: 1 February 2025
Payment Due By: 20 February 2025
Billing Period: December 2024 – January 2025

Meter Reading (Start):    4,821 m³
Meter Reading (End):      5,109 m³
Gas Consumed:               288 m³
kWh Equivalent:           3,168 kWh

Tariff: Standard Variable
Unit Rate: 7.42p per kWh
Standing Charge: 29.50p/day (62 days)

Gas Charges: £235.07
Standing Charges: £18.29
VAT (5%): £12.67

Total Amount Due: £266.03

Pay online at: sgn.co.uk/pay | Direct Debit reference: SGN-DD-884421
""",

"utility_bill_003.txt": """
ISLAMABAD ELECTRIC SUPPLY COMPANY
IESCO Customer Portal: iesco.com.pk

ELECTRICITY BILL / بجلی کا بل

Reference No: IESCO-F4-221-009987
Account Number: F4-0099-221-87
Consumer: Dr. Nasreen Akhtar
Meter No: 4521-A

Address: House 7, Street 22, F-7/1, Islamabad

Billing Month: January 2025
Issue Date: 2025-02-01
Due Date: 2025-02-16

Previous Units: 22,410
Current Units:  22,823
Units Consumed: 413 kWh

Rate Slab:
  1–100 units @ Rs.16.00        Rs.1,600.00
  101–200 units @ Rs.21.00      Rs.2,100.00
  201–300 units @ Rs.24.00      Rs.2,400.00
  301–413 units @ Rs.27.00      Rs.3,024.00
FC:                               Rs.500.00
NJ Surcharge:                     Rs.412.00
GST (18%):                      Rs.1,718.28

Amount Due: Rs.11,354.28

Helpline: 051-111-000-118
""",

"utility_bill_004.txt": """
METRO WATER & SEWERAGE AUTHORITY
www.mwasa.gov

WATER UTILITY BILL

Account Number: MWSA-00334-78B
Billing Period: January 1 – January 31, 2025
Statement Date: February 1, 2025
Due Date: February 15, 2025

Customer: Robert & Lisa Chen
Service Address: 712 Riverside Drive, Apt 3B, Austin TX 78701

Consumption:
  Previous Reading: 38,220 gallons
  Current Reading:  39,640 gallons
  Usage This Period: 1,420 gallons

Water Service:       $18.45
Sewer Service:       $16.20
Stormwater Fee:       $4.80
Infrastructure Levy:  $3.55

Amount Due: $43.00

AutoPay enrolled. Payment will be deducted on Feb 15, 2025.
Questions? Call 512-555-0100 or visit mwsa.gov
""",

"utility_bill_005.txt": """
NATIONAL GRID ELECTRIC
Albany, NY 12201
1-800-867-5309 | nationalgrid.com

ELECTRIC SERVICE BILL

Account Number: NG-77-0098-44321
Service Address: 34 Pine Street, Albany NY 12207
Customer Name: Patricia Gomez

Billing Period: Jan 3, 2025 – Feb 2, 2025 (30 days)
Statement Date: Feb 3, 2025
Due Date: Feb 24, 2025

Usage Summary:
  kWh Used This Period: 612 kWh
  kWh Used Same Period Last Year: 589 kWh

Delivery Charges:
  Customer Charge:           $18.00
  Energy Delivery (612 kWh): $56.30

Supply Charges:
  Energy Supply (612 kWh × $0.089): $54.47

Taxes & Fees:
  State & Local Taxes:        $9.22
  Revenue-Based Pilots:        $1.44

Amount Due: $139.43

Budget Billing Plan: Enrolled. Estimated monthly: $141.00
""",

# ─────────────── OTHER (2) ───────────────
"other_001.txt": """
MEMORANDUM

TO:    All Staff
FROM:  Office of the Managing Director
DATE:  January 20, 2025
RE:    Annual Performance Review Process — 2024

This memo is to inform all employees that the annual performance review cycle for the year 2024 will commence on February 3, 2025.

All line managers are required to:
1. Schedule one-on-one sessions with each direct report by February 7, 2025
2. Submit completed review forms to HR by February 14, 2025
3. Ensure ratings are calibrated in accordance with the company grading guidelines

Employees are encouraged to complete their self-assessment forms, available on the HR portal, before their scheduled sessions.

Any questions regarding the process should be directed to hr@company.com or extension 4400.

We thank you in advance for your cooperation.

Regards,
Office of the MD
""",

"other_002.txt": """
MEETING MINUTES
Project: Phoenix Digital Transformation
Date: January 28, 2025 | Time: 10:00 AM – 11:30 AM
Location: Conference Room B, Head Office
Facilitator: Amna Siddiqui, Project Manager

ATTENDEES
Amna Siddiqui (PM), Bilal Raza (Tech Lead), Sana Mir (QA), Tariq Hassan (Business Analyst), Rida Fatima (UX Designer)

AGENDA & DISCUSSION

1. Sprint 4 Review
   Bilal reported that 14 of 17 user stories were completed. Remaining 3 stories deferred to Sprint 5 due to dependency on third-party API.

2. UAT Planning
   Sana presented UAT test plan covering 120 test cases across 8 modules. UAT to begin February 10, 2025.

3. Go-Live Date
   Discussed risk of March 1 go-live. Team agreed to reassess after UAT completion.

4. Budget Update
   Tariq flagged a 12% cost overrun in infrastructure procurement. CFO to be briefed separately.

ACTION ITEMS
- Bilal: Complete deferred stories by Feb 5
- Sana: Share UAT scripts with stakeholders by Feb 7
- Amna: Schedule CFO briefing before Feb 3

NEXT MEETING: February 4, 2025 at 10:00 AM
""",

# ─────────────── UNCLASSIFIABLE (2) ───────────────
"unclassifiable_001.txt": """
7F 29 AA 01 00 00 00 4C 6F 72 65 6D 20 69 70 73
75 6D 20 64 6F 6C 6F 72 20 73 69 74 20 61 6D 65
00 FF FE 03 00 00 1A 2B 3C 4D 5E 6F 70 81 92 A3
B4 C5 D6 E7 F8 09 1A 2B 3C 4D 00 00 00 00 00 00
BLOCK_END 0xDEADBEEF CHECKSUM_FAIL
""",

"unclassifiable_002.txt": """
x
""",

}

written = 0
for filename, content in docs.items():
    with open(f"sample_docs/{filename}", "w", encoding="utf-8") as f:
        f.write(content.strip())
    written += 1

print(f"✅ Generated {written} documents in sample_docs/")
print("\nBreakdown:")
print("  Invoice:         6 files")
print("  Resume:          5 files")
print("  Utility Bill:    5 files")
print("  Other:           2 files")
print("  Unclassifiable:  2 files")
print("  TOTAL:          20 files")
