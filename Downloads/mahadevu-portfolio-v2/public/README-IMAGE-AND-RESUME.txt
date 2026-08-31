PORTFOLIO PERSONALIZATION
==========================

1. PROFILE PHOTO
---------------
Add your real professional photo here:
public/profile.jpg

Recommended:
- JPG or WebP
- 1000 x 1200 px or larger
- Clear head-and-shoulders portrait
- Simple background
- File name: profile.jpg

The website automatically uses /profile.jpg when it exists.
If it does not exist, the built-in placeholder is shown.

2. RESUME
---------
Replace this file:
public/resume.pdf

with your actual resume PDF.

Recommended:
- 1–2 pages
- PDF format
- Professional filename
- Keep the file size reasonably small

The RESUME button downloads /resume.pdf.

3. PROJECT IMAGES
-----------------
You can add your real screenshots in:
public/images/

Then change the image field for a project inside:
src/main.jsx

Example:
image: "/images/my-project.png"

4. SOCIAL LINKS
---------------
Open src/main.jsx and update:
- Instagram
- YouTube
- Any additional social links

5. PROJECT LINKS
----------------
All requested GitHub links are already added.
Change any link later inside the projects array if needed.

6. RUN
------
npm install
npm run dev

7. BUILD
--------
npm run build

8. GITHUB PAGES
---------------
Repository Settings → Pages → Source: GitHub Actions.
Push your main branch.
