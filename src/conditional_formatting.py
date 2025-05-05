


def colour_application_status(SHEET_ID):
    """
    Apply conditional formatting to the 'Application Status' column in the Google Sheet.
    The function highlights cells based on their content:
    - "rejected" in red
    - "viewed" in yellow
    """
    # Replace with your actual sheet ID

        # Define the conditional formatting rules
    rule = {
        "requests": [
            {
                "addConditionalFormatRule": {
                    "rule": {
                        "ranges": [{
                            "sheetId": SHEET_ID,
                            "startRowIndex": 2,
                            "startColumnIndex": 4,  # Column E = index 4
                            "endColumnIndex": 5
                        }],
                        "booleanRule": {
                            "condition": {
                                "type": "TEXT_CONTAINS",
                                "values": [{"userEnteredValue": "rejected"}]
                            },
                            "format": {
                                "backgroundColor": {"red": 1.0, "green": 0.8, "blue": 0.8}
                            }
                        }
                    },
                    "index": 0
                }
            },
            {
                "addConditionalFormatRule": {
                    "rule": {
                        "ranges": [{
                            "sheetId": SHEET_ID,
                            "startRowIndex": 2,
                            "startColumnIndex": 4,
                            "endColumnIndex": 5
                        }],
                        "booleanRule": {
                            "condition": {
                                "type": "TEXT_CONTAINS",
                                "values": [{"userEnteredValue": "viewed"}]
                            },
                            "format": {
                                "backgroundColor": {"red": 1.0, "green": 1.0, "blue": 0.6}
                            }
                        }
                    },
                    "index": 0
                }
            }
        ]
    }
    return rule