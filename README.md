# Shaun Porwal's Site Repository

This repository contains the source files for my personal website shaunporwal.com.
### Development Setup
##### Prerequisites
- Python 3.11 or higher
- Poetry (for dependency management)

##### Local Development

1. Clone the repository: git clone https://github.com/shaunporwal/shaunporwal.github.io.git
2. Install dependencies with Poetry: poetry install
3. Activate the Poetry virtual environment: poetry shell

### Site Management
##### Local Preview
To preview the site locally:
poetry run quarto preview

##### Deployment
The site is automatically deployed to GitHub Pages when changes are pushed to the main branch. The GitHub Actions workflow will:

1. Render the Quarto project
2. Deploy to the gh-pages branch
3. Make the changes live on the website

No manual deployment steps are needed! 🎉

##### Project Structure

- `posts/`: Blog posts and project write-ups
- `about/`: About page content
- `_quarto.yml`: Quarto configuration
- `.github/workflows/`: Deployment automation
