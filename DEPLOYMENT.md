# Day 6 — Deploying EcoVision Publicly

## Step 0 — .gitignore
Before pushing anywhere, make sure the dataset and cache files never
get committed — they're large, and re-downloadable via torchvision
anyway, so they add nothing but repo bloat.

    data/
    EuroSAT.zip
    __pycache__/
    *.pyc
    .ipynb_checkpoints/

## Step 1 — Push to GitHub (portfolio copy)
This is the repo a scholarship reviewer will actually browse and read
the README of.

    cd "C:\Users\Maryam Irfan\Desktop\EcoVision"
    git init
    git add .
    git commit -m "EcoVision: EuroSAT classifier with transfer learning, Streamlit app, Docker deployment"
    git branch -M main
    git remote add origin https://github.com/<your-username>/EcoVision.git
    git push -u origin main

(Create the empty repo on github.com first — "New repository", no
README/gitignore auto-generated, since you already have your own.)

## Step 2 — Create a Hugging Face Space
This is the part that has to happen in a browser, not a terminal —
account and Space creation aren't scriptable.

1. Go to huggingface.co, sign up or log in (free).
2. Click your profile icon, then "New Space."
3. Name it (e.g. ecovision), choose "Docker" as the Space SDK — this
   is the setting that makes it build and run your Dockerfile exactly
   as written, rather than reinterpreting it as a generic Python app.
4. Set visibility to Public, so it's actually reachable by anyone with
   the link.
5. Click "Create Space." You'll land on an empty repo page with git
   clone instructions — that repo is what actually gets deployed.

## Step 3 — Push your code to the Space
The Space is its own separate git repository from GitHub — you're
pushing the same files to a second remote, not linking the two
automatically.

    git remote add space https://huggingface.co/spaces/<your-username>/ecovision
    git push space main

The very first push will need you to log in — either paste your
Hugging Face account password when prompted, or (recommended) create
an access token at huggingface.co/settings/tokens and use that as the
password instead.

## Step 4 — Add the Spaces config header to your README
Hugging Face reads YAML frontmatter at the very top of README.md to
know how to build and run your Space — this is not optional
decoration, without it the Space won't know sdk: docker or which port
to expose. Open README_spaces_header.md (created alongside this file)
and paste its top block (the part between the two --- lines) onto the
very first lines of your actual README.md, above your existing
content. Then:

    git add README.md
    git commit -m "Add Hugging Face Spaces config"
    git push space main

## Step 5 — Watch it build
Back in the browser, your Space page will show a "Building" status
with live logs — this is Hugging Face running your exact Dockerfile
on their infrastructure. It typically takes a few minutes, mostly
spent on the torch/torchvision CPU wheel download. Once it switches
to "Running," your app is live at:

    https://huggingface.co/spaces/<your-username>/ecovision

That link works for anyone, anywhere — this is the one to put in your
README and your actual scholarship application, since it's no longer
tied to your laptop being on.

## Updating it later
Any time you change code locally, push to BOTH remotes so GitHub and
the live Space stay in sync:

    git add .
    git commit -m "describe the change"
    git push origin main
    git push space main

Pushing to `space` triggers an automatic rebuild on Hugging Face's
servers — you don't run docker build yourself for this; their
infrastructure does it from your Dockerfile every time you push.
