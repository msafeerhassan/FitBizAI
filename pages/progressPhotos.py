from flask import Blueprint
from db import loadFullRecordData
from layout import renderPage

progressPhotosBp = Blueprint("progressPhotos", __name__)

def sortByDate(entry):
    return entry.get("date", "")

@progressPhotosBp.route("/progress-photos", methods = [
    "GET"
])
def progressPhotos():
    recordData = loadFullRecordData()

    if not recordData:
        return renderPage("Progress Photos", "<p>No Data recorded yet - Nothing to show here :(</p>")
    fortnightlyLogs = recordData.get("fortnightly", [])

    if not fortnightlyLogs:
        return renderPage("Progress Photos", "<p>No Fortnightly Logs Found :(</p>")
    
    sortedData = sorted(fortnightlyLogs, key=sortByDate)

    body = "<h2>Progress Photos Timeline</h2>"

    for cp in sortedData:
        cpDate = cp.get("date", "Unknown Date")
        cpWeight = cp.get("weight", "Unknown Weight")
        imageUrls = cp.get("image_paths", [])

        body += f'<div class="card"><h3>{cpDate} - {cpWeight} kg</h3>'

        if imageUrls:
            body += '<div style="display: flex; gap: 10px; flex-wrap: wrap;">'

            for url in imageUrls:
                body += f'<img src="{url}" style="width: 180px; height: 180px; object-fit: cover; border-radius: 8px;">'
            
            body += "</div>"
        else:
            body += '<p class="caption">Images Missing :(</p>'
        
        body += "</div>"
    return renderPage("Progress Photos", body)