# Shaun Porwal's Site Repository

This repository contains the source files for my personal website shaunporwal.com.

---

## Virtual Environment Management

### Using `renv` (Handles R & Python Dependencies)
Activate `renv` with:  

```bash
source ./renv/python/virtualenvs/renv-python-3.11/bin/activate
```
### Using `venv` (Current Setup)
Since `uv` and `renv` are not working, use `venv` located in the `env/` directory:  
```bash
source ./env/bin/activate
```

#### Installing Python Libraries
Once the virtual environment is activated, install Python libraries as needed:  
```bash
pip install <library_name>
```
---

## Site Management

### Rendering the Site Locally
To render the site locally:  
```bash
quarto render
```
### Publishing to GitHub Pages
To publish changes live on GitHub Pages:  
```bash
quarto publish gh-pages
```
---

## Notes

### 2024-12-07 Updates:
1. Switched to `venv` due to issues with `uv` and `renv`.
2. Removed the dedicated "Projects" tab:
   - Projects can now be blog posts with the `project` tag for easy categorization.

---
