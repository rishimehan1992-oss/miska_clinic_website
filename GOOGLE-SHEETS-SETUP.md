# Google Sheets Form Integration – Setup

Your forms (Hair Profile + Contact) are wired to send data to your Google Apps Script Web App. For it to work from your website, you need to **enable CORS** in your Apps Script.

## Update your Apps Script

Open your Google Sheet → **Extensions** → **Apps Script**, and replace your code with:

```javascript
function doGet() {
  return ContentService.createTextOutput(JSON.stringify({ status: 'ok', message: 'Web App is running. Use POST to submit form data.' }))
    .setMimeType(ContentService.MimeType.JSON);
}

function doOptions() {
  return ContentService.createTextOutput('')
    .setMimeType(ContentService.MimeType.TEXT);
}

function doPost(e) {
  try {
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const data = JSON.parse(e.postData.contents);
    const formType = data.formType || 'contact';
    var sheet = ss.getSheetByName(formType === 'hair_profile' ? 'Hair Profile' : 'Contact');
    if (!sheet) sheet = ss.getActiveSheet();
    const row = Object.keys(data).map(function(k) { return data[k]; });
    sheet.appendRow(row);

    return ContentService.createTextOutput(JSON.stringify({ success: true }))
      .setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({ success: false, error: err.toString() }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}
```

> **Note:** Google Apps Script’s `TextOutput` does not support `setHeaders`. CORS for Web Apps is handled by Google when deployed with **Execute as: Me** and **Who has access: Anyone**.

## What this does

1. **`doOptions`** – Handles CORS preflight so the browser can send POST requests from your domain.
2. **`doPost`** – Parses JSON and appends each submission as a new row to the appropriate sheet.
3. **CORS headers** – Let your website (miska.in or localhost) call the script.

## Deploy

1. **Deploy** → **Manage deployments**
2. **Edit** the existing deployment → **Version** → **New version**
3. Save and ensure the URL stays the same.

## Sheet setup

- Create two tabs in your Google Sheet: **"Contact"** and **"Hair Profile"**.
- Add header rows in row 1. Suggested headers:

  **Contact tab:** `formType | source | name | phone | serviceRequired | preferredTime | message`
  
  **Hair Profile tab:** `formType | source | age | gender | duration | mainConcern | familyHistory | hairlineStage | shedding | scalpIssues | breakage | hairTexture | hairThickness | stress | sleep | diet | smoking | medicalConditions | previousTreatment | heatStyling | chemicals | washFreq | goal | name | phone | email | contactPref`

## Forms connected

| Form         | Page           | formType    |
|-------------|----------------|-------------|
| Hair Profile| hair-profile.html | hair_profile |
| Contact     | contact.html   | contact     |

---

## Troubleshooting: Data not posting to Sheets

### 1. Deploy settings
- **Deploy** → **Manage deployments** → Edit (pencil)
- **Execute as:** Me
- **Who has access:** Anyone
- Create a **new version** after any script change, then deploy

### 2. Don’t use `file://` – use a local server
Opening HTML directly from disk (`file:///...`) can block fetch requests. Run a local server instead:

```bash
# From your project folder:
npx serve .
# or
python3 -m http.server 8000
```

Then open `http://localhost:3000` (or `http://localhost:8000`) and submit the forms.

### 3. Check browser console
- Press **F12** (or right‑click → Inspect) → **Console**
- Submit a form
- Look for red errors (CORS, network failed, etc.)

### 4. Verify the Web App URL
The URL in `script.js` and `hair-profile.html` must match your deployment URL exactly. It should look like:

`https://script.google.com/macros/s/.../exec`
