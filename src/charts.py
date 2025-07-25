import gspread
from .sheets import open_sheet

CHART_ID_CELL = "H2"

def create_or_update_chart():
    evo_ws = open_sheet("Évolution")
    ana_ws = open_sheet("Analyse")

    try:
        chart_id = int(ana_ws.acell(CHART_ID_CELL).value or 0)
    except Exception:
        chart_id = 0

    last_row = len(evo_ws.col_values(1))
    if last_row <= 1:
        return

    spreadsheet = evo_ws.spreadsheet
    chart_spec = {
        "requests": [{
            "addChart": {
                "chart": {
                    "spec": {
                        "title": "Évolution KDA & Winrate",
                        "basicChart": {
                            "chartType": "LINE",
                            "legendPosition": "BOTTOM_LEGEND",
                            "domains": [{
                                "domain": {
                                    "sourceRange": {
                                        "sources": [{
                                            "sheetId": evo_ws.id,
                                            "startRowIndex": 1,
                                            "endRowIndex": last_row,
                                            "startColumnIndex": 0,
                                            "endColumnIndex": 1
                                        }]
                                    }
                                }
                            }],
                            "series": [
                                {
                                    "series": {
                                        "sourceRange": {
                                            "sources": [{
                                                "sheetId": evo_ws.id,
                                                "startRowIndex": 1,
                                                "endRowIndex": last_row,
                                                "startColumnIndex": 2,
                                                "endColumnIndex": 3
                                            }]
                                        }
                                    },
                                    "targetAxis": "LEFT_AXIS"
                                },
                                {
                                    "series": {
                                        "sourceRange": {
                                            "sources": [{
                                                "sheetId": evo_ws.id,
                                                "startRowIndex": 1,
                                                "endRowIndex": last_row,
                                                "startColumnIndex": 3,
                                                "endColumnIndex": 4
                                            }]
                                        }
                                    },
                                    "targetAxis": "RIGHT_AXIS"
                                }
                            ]
                        }
                    },
                    "position": {
                        "overlayPosition": {
                            "anchorCell": {
                                "sheetId": ana_ws.id,
                                "rowIndex": 0,
                                "columnIndex": 6
                            },
                            "widthPixels": 700,
                            "heightPixels": 400
                        }
                    }
                }
            }
        }]
    }

    if chart_id:
        chart_spec["requests"][0] = {
            "updateChartSpec": {
                "chartId": chart_id,
                "spec": chart_spec["requests"][0]["addChart"]["chart"]["spec"]
            }
        }

    resp = spreadsheet.batch_update(chart_spec)
    if not chart_id:
        new_id = resp["replies"][0]["addChart"]["chart"]["chartId"]
        ana_ws.update(CHART_ID_CELL, new_id)
