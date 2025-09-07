# Claude Enhancement Integration Prompts – Personal File Manager Project

Use these prompts to integrate Claude's enhancement ideas into your existing site, one step at a time.

---

## 🔍 1. File Preview on Hover (Images and PDFs)

```
Help me integrate this idea into my project:

📝 Idea: Add file previews on hover for images and PDFs

My current system:
- Uses `dashboard.php` to list all uploaded files
- Login protected with `parker_authenticated`
- Favoriting and upload logic already working

Requirements:
1. Only apply preview logic to image files (.jpg, .png, .gif) and PDFs
2. Show a small floating preview near the mouse when hovering a file
3. Use JavaScript + CSS only — no backend changes yet
4. Keep styling consistent with my current dashboard (`me.html` style)

Let’s start with the JS/CSS for image previews. We’ll do PDFs next.
```

---

## ⌨️ 2. Keyboard Shortcuts

```
Now help me add keyboard shortcuts to my dashboard:

📝 Idea: Use keys to switch views

Requirements:
1. Press `G` for Grid View
2. Press `L` for List View
3. Use JavaScript event listeners
4. Don’t trigger shortcuts while typing in inputs/search

My grid/list toggle is already working.
```

---

## 🧭 3. Breadcrumb Navigation Enhancements

```
Help me enhance breadcrumb navigation in `dashboard.php`.

📝 Idea: Improve folder path display and make each segment clickable

Requirements:
1. Display current folder path as clickable breadcrumbs (e.g. Home / Uploads / Invoices)
2. Clicking a segment should load that folder without reloading the full page
3. Keep it JavaScript-based and styled cleanly

Let’s start by building the HTML structure and navigation logic.
```

---

## 📑 4. File Type Icons

```
I want to add custom icons next to each file based on its type.

📝 Idea: Improve visual recognition with file-type icons

Requirements:
1. Show icons like 📄 for docs, 🖼 for images, 🎵 for audio, etc.
2. Use Unicode or small inline SVGs
3. Add them dynamically based on file extension
4. Keep styling compact and clean

Let’s start with a basic set of 5 icons for common file types.
```

---

## ⚡ 5. Quick Actions (Rename/Delete)

```
Help me add rename and delete quick-action buttons to each file entry.

📝 Idea: Inline management of files

Requirements:
1. Add small icons or buttons next to each file: ✏️ (rename) and 🗑️ (delete)
2. When clicked, prompt the user for confirmation or a new name
3. Use `rename.php` and `delete.php` to process the requests
4. Ensure they’re only available to logged-in users (`parker_authenticated`)

Start with the HTML/JS for rename. We’ll add delete after that.
```

