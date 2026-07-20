from flask import Blueprint, request, redirect
from datetime import datetime, date
from db import saveData, uploadProgressPhoto
from layout import renderPage

fortnightlyBp = Blueprint("fortnightly", __name__)

@fortnightlyBp.route("/fortnightly", methods = [
    "GET",
    "POST"
])

def fortnightlyLog():
    error = None

    if request.method == "POST":
        images = request.files.getlist("images")

        validImages = []

        for f in images:
            if f and f.filename:
                validImages.append(f)
        
        images = validImages

        weightRaw = request.form.get("weight", "0")

        try:
            weight = float(weightRaw)
        except ValueError:
            weight = 0.0
        
        if len(images) < 3:
            error = "Please upload atleast 3 images!"
        elif weight <= 20.0:
            error = "Please enter a valid weight value."
        else:
            savedImagesUrls = []
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            for i, file in enumerate(images):
                fileExt = file.filename.rsplit(".", 1)[-1].lower()
                fileName = f"face_{timestamp}_{i}.{fileExt}"
                imageUrl = uploadProgressPhoto(fileName, file.read(), file.content_type or "image/jpeg")
                savedImagesUrls.append(imageUrl)
            
            data = {
                "date": date.today().isoformat(),
                "weight": weight,
                "image_paths": savedImagesUrls
            }

            saveData("fortnightly", data)
            return redirect("/")
    
    if error:
        errorHtml = f'p style="color: #dc2626;">{error}</p>'
    else:
        errorHtml = ""
    
    body = f"""
<h2>Fortnightly Log</h2>
{errorHtml}

<form method="POST" enctype="multipart/form-data" class="card">
    <label>Upload your Facial Images (at least 3)</label>
    <input type="file" name="images" accept=".jpg,.jpeg,.png" multiple required>
    <label>Enter your current weight (kg's)</label>
    <input type="number" name="weight" step="0.1" min="20.1" required>
    <button type="submit">Submit Fortnightly Report</button>
</form>
"""
    
    return renderPage("Fortnightly Log", body)