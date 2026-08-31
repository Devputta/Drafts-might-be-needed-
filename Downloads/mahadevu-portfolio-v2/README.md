# Mahadevu M P — Portfolio v2

A complete, cumulative React + Vite portfolio designed around the requested analyst / software-engineer visual style.

## Included

- Professional dark/light theme
- Responsive mobile navigation
- Home / About / Skills / Projects / Experience / Publication / Education / Contact
- GitHub + LinkedIn + Email contact cards
- Bengaluru, Karnataka location card
- Contact form that opens the user's email client
- Resume download
- Profile photo placeholder + clear image instructions
- Project image placeholders + instructions for replacing them
- Project search
- Project category filters
- Click any project for a detailed project brief
- GitHub link inside every project popup
- Python + SQL coverage
- Data Analytics
- Data Engineering
- Manual Testing / QA
- Machine Learning
- Full Stack
- AI app / website creation
- Publication link
- GitHub Pages deployment workflow

## Requested links already included

### Publication
https://tarce.co/index.php/tarce/article/view/4261

### Manual Testing
https://github.com/Devputta/Manual-Testing-Project---1-By-DevPutta

### Data Analysis
https://github.com/Devputta/AC-Company-Product-Analysis-

### Data Engineering
https://github.com/Devputta/DE_PROJECT---AWS---SNOWFLAKE---DBT

### Python + SQL
https://github.com/Devputta/ALL-IN-ONE

### Machine Learning
https://github.com/Devputta/Final-Year-Project

### Full Stack
https://github.com/Devputta/Hospital-Management-System

### AI Creation
https://github.com/Devputta/lumen-cinematic-vault-By-AI

## Add your photo

Put your real image here:

`public/profile.jpg`

The website falls back to `public/profile-placeholder.svg` if the photo is missing.

Recommended:
- Professional headshot
- JPG/WebP
- 1000×1200 or larger
- Clear lighting
- Simple background

## Add your resume

Replace:

`public/resume.pdf`

with your real resume PDF.

The Resume button is already connected to `/resume.pdf`.

## Add real project screenshots

Put images in:

`public/images/`

Then update the corresponding `image` value in `src/main.jsx`.

Example:

```js
image: "/images/airbnb-dashboard.png"
```

## Run locally

```bash
npm install
npm run dev
```

## Build

```bash
npm run build
```

## GitHub Pages

1. Create/use your GitHub repository.
2. Push this project to the `main` branch.
3. Open **Settings → Pages**.
4. Set **Source** to **GitHub Actions**.
5. Push again if necessary.
6. GitHub Actions will build `dist` and deploy it.

## Important

Do not put API keys, passwords or private credentials in this frontend repository.
