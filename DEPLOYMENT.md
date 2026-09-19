# Deploying EcoVision with Streamlit Community Cloud

EcoVision is deployed with **Streamlit Community Cloud**. The app runs
from `app.py`, installs packages from `requirements.txt`, and loads the
model files stored in this repository.

## Step 0 - Check files before pushing
The repository should include these runtime files:

- `app.py`
- `inference.py`
- `model.py`
- `utils.py`
- `model.pt`
- `model_metadata.json`
- `input/model_comparison.csv`
- `requirements.txt`

The dataset and Python cache files must stay out of Git. The project
`.gitignore` should contain:

    data/
    EuroSAT.zip
    __pycache__/
    *.pyc
    .ipynb_checkpoints/

## Step 1 - Create the GitHub repository
Create an empty repository at:

    https://github.com/new

Name it `EcoVision`. Do not generate a README, `.gitignore`, or license;
this project already contains its own files.

## Step 2 - Initialize Git and push to GitHub

Git for this computer is installed in WSL2, so these commands work from
Windows PowerShell. Run them from any PowerShell directory:

    wsl -d Ubuntu-22.04 -- bash -lc "cd '/mnt/c/Users/Maryam Irfan/Desktop/EcoVision' && git init"
    wsl -d Ubuntu-22.04 -- bash -lc "cd '/mnt/c/Users/Maryam Irfan/Desktop/EcoVision' && git add ."
    wsl -d Ubuntu-22.04 -- bash -lc "cd '/mnt/c/Users/Maryam Irfan/Desktop/EcoVision' && git commit -m 'EcoVision: EuroSAT classifier with transfer learning, Streamlit app, Docker deployment'"
    wsl -d Ubuntu-22.04 -- bash -lc "cd '/mnt/c/Users/Maryam Irfan/Desktop/EcoVision' && git branch -M main"
    wsl -d Ubuntu-22.04 -- bash -lc "cd '/mnt/c/Users/Maryam Irfan/Desktop/EcoVision' && git remote add origin 'https://github.com/maryammkirfan/EcoVision.git'"
    wsl -d Ubuntu-22.04 -- bash -lc "cd '/mnt/c/Users/Maryam Irfan/Desktop/EcoVision' && git push -u origin main"

When GitHub asks for credentials, use your GitHub username and a
Personal Access Token as the password. GitHub no longer accepts a
normal account password for Git pushes.

If `origin` already exists, use this instead of `git remote add origin`:

    wsl -d Ubuntu-22.04 -- bash -lc "cd '/mnt/c/Users/Maryam Irfan/Desktop/EcoVision' && git remote set-url origin 'https://github.com/maryammkirfan/EcoVision.git'"
Check the result:

    wsl -d Ubuntu-22.04 -- bash -lc "cd '/mnt/c/Users/Maryam Irfan/Desktop/EcoVision' && git status --short --branch && git remote -v"

## Step 3 - Deploy from GitHub to Streamlit Cloud
1. Open `https://share.streamlit.io/`.
2. Sign in with the GitHub account that owns `maryammkirfan/EcoVision`.
3. Select **New app**.
4. Choose repository: `maryammkirfan/EcoVision`.
5. Choose branch: `main`.
6. Set the main file path to: `app.py`.
7. Choose the free Community Cloud option if prompted.
8. Click **Deploy**.

Streamlit Cloud reads `requirements.txt` automatically, installs the
dependencies, and starts `app.py`. Do not select a Static site option;
the app needs Python, Streamlit, PyTorch, and the saved model.

## Step 4 - Test the deployed app
After the deployment finishes, Streamlit Cloud provides a URL similar to:

    https://ecovision-<your-account>.streamlit.app

Open that URL, upload a JPG or PNG satellite image, and confirm that a
prediction and confidence score are displayed.

If the app fails to start, open the app's **Manage app** menu and view
the deployment logs. The most common causes are a missing `model.pt`, an
incorrect main file path, or a dependency installation failure.

## Updating the deployed app

After changing code or app styling, run:

    wsl -d Ubuntu-22.04 -- bash -lc "cd '/mnt/c/Users/Maryam Irfan/Desktop/EcoVision' && git add . && git commit -m 'Describe the change' && git push origin main"

Streamlit Cloud watches the `main` branch and automatically rebuilds the
app after the push. You do not need to run `docker build` for the hosted
Streamlit Cloud version; Docker is only for local container testing.

## Local Docker testing

To test the Docker version locally, use the separate guide in
`DOCKER_CHEATSHEET.md`. Streamlit Cloud does not use your local Docker
container; it deploys the repository as a Streamlit app.
