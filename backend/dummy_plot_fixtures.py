"""AI-extraction fixtures for the 4 dummy plots (frontend/public/dummy-land.svg),
paired 1:1 with government_records.GOVERNMENT_RECORDS by plot_id.

Deliberately NOT a perfect copy of the government record for every field —
a couple of plots have a small AI extraction error (wrong digit, swapped
status) with correspondingly lower confidence, so the Gov Employee Portal's
side-by-side comparison has something real to catch. This is the whole
point of the reviewer's job: confirm the AI got it right, or catch it when
it didn't.
"""

DUMMY_PLOT_FIXTURES = {
    1: {
        # Matches government record closely; only survey_no confidence dips.
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
    2: {
        # Clean match, high confidence across the board — AI got this one right.
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
    3: {
        # Deliberate AI mistakes vs government record: khasra_no digit wrong
        # (901/B -> 901/D) and area misread (4.00 -> 4.60) — both low confidence,
        # for the reviewer to actually catch.
        "fields": [
            {"name": "khata_no", "label": "Khata No.", "value": "347", "confidence": 0.65},
            {"name": "khasra_no", "label": "Khasra No.", "value": "901/D", "confidence": 0.52},
            {"name": "survey_no", "label": "Survey No.", "value": "22-D", "confidence": 0.70},
            {"name": "owner_name", "label": "Owner Name", "value": "M. Raghunath Rao", "confidence": 0.82},
            {"name": "area", "label": "Area (acres)", "value": "4.60", "confidence": 0.41},
            {"name": "mutation", "label": "Mutation", "value": "Disputed", "confidence": 0.60},
        ],
        "review_required": True,
    },
    4: {
        # Deliberate AI mistake: mutation status misread (Approved -> Pending),
        # everything else clean — a subtler single-field error.
        "fields": [
            {"name": "khata_no", "label": "Khata No.", "value": "560/F", "confidence": 0.93},
            {"name": "khasra_no", "label": "Khasra No.", "value": "77", "confidence": 0.96},
            {"name": "survey_no", "label": "Survey No.", "value": "9-C", "confidence": 0.91},
            {"name": "owner_name", "label": "Owner Name", "value": "K. Anitha Reddy", "confidence": 0.95},
            {"name": "area", "label": "Area (acres)", "value": "3.12", "confidence": 0.90},
            {"name": "mutation", "label": "Mutation", "value": "Pending", "confidence": 0.68},
        ],
        "review_required": True,
    },
}


def get_dummy_fixture(plot_id: int) -> dict:
    return DUMMY_PLOT_FIXTURES.get(plot_id)
