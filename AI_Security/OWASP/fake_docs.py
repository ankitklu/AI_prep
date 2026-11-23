"""
Fake knowledge base for the course.

"Acme Cloud" is a made-up company. Every fact below is invented so that
students can see clearly where an answer came from. Later security modules
will add new documents here (for example a poisoned document for LLM04, or
a document with hidden instructions for LLM01 indirect prompt injection).
"""

DOCUMENTS = [
    {
        "id": "hr-001",
        "title": "Leave policy",
        "text": (
            "Acme Cloud employees get 20 days of paid leave per year. "
            "Unused leave of up to 5 days can be carried over to the next year. "
            "Leave requests must be submitted in the HR portal at least 7 days in advance."
        ),
    },
    {
        "id": "hr-002",
        "title": "Remote work policy",
        "text": (
            "Employees may work remotely up to 3 days per week. "
            "Tuesdays and Thursdays are office days for all teams. "
            "Remote work from another country needs written approval from a manager."
        ),
    },
    {
        "id": "it-001",
        "title": "Password policy",
        "text": (
            "Passwords must be at least 14 characters long and must be changed every 180 days. "
            "Multi-factor authentication (MFA) is required for every company account. "
            "Never share your password with anyone, including the IT team."
        ),
    },
    {
        "id": "product-001",
        "title": "Pricing plans",
        "text": (
            "Acme Cloud has three plans. Starter costs $10 per month and includes 50 GB of storage. "
            "Pro costs $25 per month and includes 500 GB of storage. "
            "Enterprise has custom pricing and unlimited storage."
        ),
    },
    {
        "id": "product-002",
        "title": "Refund policy",
        "text": (
            "Customers can request a full refund within 30 days of purchase. "
            "After 30 days, refunds are not available, but the plan can be cancelled at any time. "
            "Refunds are processed within 5 business days."
        ),
    },
    {
        "id": "support-001",
        "title": "Customer support",
        "text": (
            "Support is available Monday to Friday, 9 AM to 6 PM IST. "
            "Customers can reach support by email at support@acmecloud.example or through live chat. "
            "Enterprise customers get 24/7 phone support."
        ),
    },
]
