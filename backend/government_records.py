"""Fixed 'official government record' fixtures for the 4 dummy plots shown
in frontend/public/dummy-land.svg. These represent ground-truth data
already on file with the government — separate from whatever the AI
extracts from an uploaded scan — so a reviewer can compare AI output
against the official record and catch AI mistakes.
"""

GOVERNMENT_RECORDS = {
    1: {
        "plot_id": 1,
        "plot_label": "Plot A (North-West)",
        "khata_no": "213/A",
        "khasra_no": "402",
        "survey_no": "17-B",
        "owner_name": "R. Venkataiah",
        "area": "2.35",
        "mutation": "Pending",
        "on_file_since": "2018-03-14",
    },
    2: {
        "plot_id": 2,
        "plot_label": "Plot B (North-East)",
        "khata_no": "88/C",
        "khasra_no": "119",
        "survey_no": "5-A",
        "owner_name": "S. Lakshmi Devi",
        "area": "1.10",
        "mutation": "Approved",
        "on_file_since": "2015-11-02",
    },
    3: {
        "plot_id": 3,
        "plot_label": "Plot C (South-West)",
        "khata_no": "347",
        "khasra_no": "901/B",
        "survey_no": "22-D",
        "owner_name": "M. Raghunath Rao",
        "area": "4.00",
        "mutation": "Disputed",
        "on_file_since": "2020-07-21",
    },
    4: {
        "plot_id": 4,
        "plot_label": "Plot D (South-East)",
        "khata_no": "560/F",
        "khasra_no": "77",
        "survey_no": "9-C",
        "owner_name": "K. Anitha Reddy",
        "area": "3.12",
        "mutation": "Approved",
        "on_file_since": "2012-01-30",
    },
}


def get_government_record(plot_id: int) -> dict:
    return GOVERNMENT_RECORDS.get(plot_id)


def list_government_records() -> list:
    return list(GOVERNMENT_RECORDS.values())
