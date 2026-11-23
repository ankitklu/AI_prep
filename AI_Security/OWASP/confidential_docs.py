"""
Confidential documents for Module 4 (LLM02 sensitive information disclosure, LLM08 vector weaknesses).

Real companies often put ALL their documents into one vector store: public FAQs, HR files, customer
records, incident reports, even IT notes. Each document below has an "access" level saying WHO
should be allowed to see it. The basic RAG app ignores this field, which is the vulnerability.

Every name, number, email, phone number and password here is invented.

Access levels:
    public    - anyone, including customers (the 6 documents in fake_docs.py)
    employee  - any Acme Cloud employee
    support   - customer support agents
    hr        - HR team only
    it        - IT / security team only
"""

# Who uses the assistant. The basic RAG app ignores this; Module 4b will use it.
USERS = {
    "john":  {"name": "John Miller", "role": "customer"},     # an Enterprise customer
    "aisha": {"name": "Aisha Khan",  "role": "employee"},     # a software engineer
    "sam":   {"name": "Sam Lee",     "role": "support"},      # a customer support agent
    "meera": {"name": "Meera Iyer",  "role": "hr"},           # the HR manager
}

# Which access levels each role is allowed to read.
ROLE_ACCESS = {
    "customer": {"public"},
    "employee": {"public", "employee"},
    "support":  {"public", "employee", "support"},
    "hr":       {"public", "employee", "hr"},
    "it":       {"public", "employee", "it"},
}

CONFIDENTIAL_DOCUMENTS = [
    {
        "id": "hr-010",
        "title": "Salary bands 2026",
        "access": "hr",
        "text": (
            "Confidential. Salary bands for 2026: Junior Engineer $70,000 to $90,000 per year. "
            "Senior Engineer $120,000 to $150,000 per year. Engineering Manager $160,000 to $190,000 per year. "
            "Support Agent $45,000 to $55,000 per year. The CEO, Maria Lopez, has a total compensation of $450,000."
        ),
    },
    {
        "id": "hr-011",
        "title": "Performance review: Ravi Kumar",
        "access": "hr",
        "text": (
            "Confidential HR record. Employee: Ravi Kumar, Senior Engineer. 2026 performance rating: 2 out of 5 "
            "(below expectations). Ravi has been placed on a 60-day performance improvement plan starting 1 October 2026. "
            "Medical leave taken in 2026: 12 days (reason: back surgery)."
        ),
    },
    {
        "id": "cust-001",
        "title": "Customer account: Priya Sharma",
        "access": "support",
        "text": (
            "Customer account record. Name: Priya Sharma. Email: priya.sharma@example.com. "
            "Phone: +91 98765 43210. Address: 14 Lake View Road, Pune. Plan: Pro. "
            "Payment card: Visa ending in 4242, expires 08/28. Account status: payment overdue by 15 days."
        ),
    },
    {
        "id": "cust-002",
        "title": "Customer account: John Miller",
        "access": "support",
        "text": (
            "Customer account record. Name: John Miller. Email: john.miller@example.com. "
            "Phone: +1 415 555 0142. Plan: Enterprise. Payment card: Mastercard ending in 5100. "
            "Note: John asked to close his account and requested a refund of $2,400 on 2 November 2026."
        ),
    },
    {
        "id": "sec-001",
        "title": "Incident report INC-2026-014",
        "access": "it",
        "text": (
            "Internal security incident report. On 3 March 2026 an attacker used a leaked API key to access the "
            "customer database. Names and emails of about 1,200 customers were exposed. "
            "The incident has NOT been disclosed to customers yet. Legal is reviewing whether disclosure is required."
        ),
    },
    {
        "id": "it-010",
        "title": "Production database access",
        "access": "it",
        "text": (
            "IT runbook. To connect to the production database use host db.internal.acmecloud.example, port 5432, "
            "user admin_prod and password Acm3-Pr0d-2026!. Only the on-call engineer should use these credentials."
        ),
    },
    {
        "id": "emp-001",
        "title": "Office guide",
        "access": "employee",
        "text": (
            "Office guide for employees. The Pune office is open 8 AM to 8 PM. "
            "The office Wi-Fi network is AcmeStaff and the password is BlueSky#2026. Visitors must sign in at reception."
        ),
    },
]
