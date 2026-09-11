import hashlib

FIXTURES = [
    {
        "fields": [
            {"name": "khata_no", "label": "Khata No.", "value": "213/A", "confidence": 0.94},
            {"name": "khasra_no", "label": "Khasra No.", "value": "402", "confidence": 0.88},
            {"name": "survey_no", "label": "Survey No.", "value": "17-B", "confidence": 0.61},
            {"name": "owner_name", "label": "Owner Name", "value": "R. Venkataiah", "confidence": 0.97},
            {"name": "area", "label": "Area (acres)", "value": "2.35", "confidence": 0.72},
            {"name": "mutation", "label": "Mutation", "value": "Pending", "confidence": 0.55},
        ],
        "review_required": True,
    },
    {
        "fields": [
            {"name": "khata_no", "label": "Khata No.", "value": "88/C", "confidence": 0.91},
            {"name": "khasra_no", "label": "Khasra No.", "value": "119", "confidence": 0.95},
            {"name": "survey_no", "label": "Survey No.", "value": "5-A", "confidence": 0.89},
            {"name": "owner_name", "label": "Owner Name", "value": "S. Lakshmi Devi", "confidence": 0.98},
            {"name": "area", "label": "Area (acres)", "value": "1.10", "confidence": 0.93},
            {"name": "mutation", "label": "Mutation", "value": "Approved", "confidence": 0.90},
        ],
        "review_required": False,
    },
    {
        "fields": [
            {"name": "khata_no", "label": "Khata No.", "value": "347", "confidence": 0.65},
            {"name": "khasra_no", "label": "Khasra No.", "value": "901/B", "confidence": 0.58},
            {"name": "survey_no", "label": "Survey No.", "value": "22-D", "confidence": 0.70},
            {"name": "owner_name", "label": "Owner Name", "value": "M. Raghunath Rao", "confidence": 0.82},
            {"name": "area", "label": "Area (acres)", "value": "4.00", "confidence": 0.45},
            {"name": "mutation", "label": "Mutation", "value": "Disputed", "confidence": 0.60},
        ],
        "review_required": True,
    },
]


def pick_fixture(filename: str) -> dict:
    digest = hashlib.sha256(filename.encode("utf-8")).hexdigest()
    index = int(digest, 16) % len(FIXTURES)
    return FIXTURES[index]
