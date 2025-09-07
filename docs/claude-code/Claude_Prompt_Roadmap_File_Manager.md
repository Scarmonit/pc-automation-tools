# Claude Prompt Roadmap – Personal File Manager Project

This roadmap breaks your project into Claude-ready prompts for a smooth, structured build process using PHP.

---

## ✅ 1. Project Setup (Already Complete)
- Folder structure is finalized
- Basic login system using `parker_authenticated` cookie is working

---

## 🔨 2. File Dashboard

### Prompt 1 – Build `dashboard.php` (File Browser Layout)
```
Now that the folder structure is set up, help me build the `dashboard.php` page.

This page should:

1. Require the user to be logged in using my existing cookie: `parker_authenticated`
2. List the contents of the `/uploads/` directory in a clean layout
3. Let me click into folders to view their contents
4. Show file name, type, size, and last modified date
5. Match the styling of `me.html`

Only build the HTML + PHP file/folder display part for now — we’ll add upload, favorites, and other features later.
```

---

### Prompt 2 – Add File Upload Form
```
Now help me add a file upload form to `dashboard.php`.

The form should:

1. Let me choose a target folder inside `/uploads/`
2. Allow uploading of any file type
3. Use a POST method to send the file to `upload.php`
4. Show a basic success or error message after upload
5. Keep the page styling consistent with `me.html`
6. Only work if the user is authenticated via the `parker_authenticated` cookie

Let’s start with the form and POST logic. We can do the backend `upload.php` handler next.
```

---

### Prompt 3 – Create `upload.php` Backend Handler
```
Now create `upload.php` to handle file uploads.

It should:

1. Check that the user is authenticated using the `parker_authenticated` cookie
2. Accept a POST request from the file upload form
3. Save the uploaded file into the selected folder under `/uploads/`
4. Create the folder if it doesn’t exist yet
5. Validate basic file upload success/failure
6. Return a success or error message that can be displayed in `dashboard.php`

Let’s keep it simple for now — we’ll add file type restrictions, file renaming, or logging later.
```

---

## ⭐ 3. File Favoriting

### Prompt 4 – Add Favoriting Support
```
Add a feature to `dashboard.php` that lets me favorite/unfavorite files.

- Each file should have a star icon (☆/★)
- Clicking the icon adds/removes the file path from `favorites.json`
- Only authenticated users can modify it
- Highlight favorited files in the UI
- We’ll do sorting/filtering of favorites later
```

---

## 📒 4. Error Logging

### Prompt 5 – Add Error Logging Tab
```
Help me add an Error Log tab to the dashboard.

- Log all PHP errors to `logs/errors.log`
- Log should include timestamp, message, file, and line number
- Create `errors.php` to display the log in a styled table
- Protect the page using the `parker_authenticated` cookie
- Prevent the log file from growing infinitely or becoming public
```

---

## 🧰 5. Optional Add-ons

- Add file type filters and search bar
- Add grid/list toggle
- Add tagging/label system saved to `tags.json`
- Add rename/delete buttons
- Add drag-and-drop upload
