# EcoVision — Docker Cheat Sheet

These commands are for **PowerShell on Windows** using the Docker engine
inside WSL2 and the `Ubuntu-22.04` distro. Run them from inside your
EcoVision folder. Do not use PowerShell backticks after entering an
Ubuntu/WSL shell; Bash uses `\` for multiline commands.

If you are already inside Ubuntu/WSL, remove the `wsl -d Ubuntu-22.04 --`
prefix from every command below.

## Build the image

    wsl -d Ubuntu-22.04 -- docker build -t ecovision .

Rebuild this any time you change app.py, model.pt, or any file copied
into the image — Docker doesn't watch your files live; the image is a
frozen snapshot taken at build time.

## Run it (first time, or after removing the old container)

    wsl -d Ubuntu-22.04 -- docker run -d --name ecovision-app -p 8502:8501 ecovision

`-d` runs in the background. `--name` gives the container a stable name.
`-p 8502:8501` maps host port 8502 to Streamlit's container port 8501.
Open `http://localhost:8502` after starting it.

If port 8502 is busy, use another host port, for example:

    wsl -d Ubuntu-22.04 -- docker run -d --name ecovision-app -p 8503:8501 ecovision

Then open `http://localhost:8503`. The port on the right must remain
`8501`; only the host port on the left changes.

## Check what's running

    wsl -d Ubuntu-22.04 -- docker ps

Shows only running containers. Add `-a` to also see stopped ones:

    wsl -d Ubuntu-22.04 -- docker ps -a

## Stop it

    wsl -d Ubuntu-22.04 -- docker stop ecovision-app

This shuts down the running process but keeps the container itself
(and its name) on disk, so you can start it again quickly.

## Start it again (container already exists, just stopped)

    wsl -d Ubuntu-22.04 -- docker start ecovision-app

Faster than `docker run` — no image lookup, no new container created,
just resumes the existing one on the same port you originally gave it.

## Remove the container (so you can `docker run` fresh with the same name)

    wsl -d Ubuntu-22.04 -- docker rm -f ecovision-app

You'll need this if you ever get a "name already in use" error from
`docker run` — it means a container called `ecovision-app` already
exists (running or stopped). The `-f` removes it even if it is running.

## View logs (what the app is printing, useful when something breaks)

    wsl -d Ubuntu-22.04 -- docker logs ecovision-app

Add `-f` to keep watching new lines live, like `tail -f`:

    wsl -d Ubuntu-22.04 -- docker logs -f ecovision-app

## Check the health endpoint manually

    wsl -d Ubuntu-22.04 -- bash -lc "curl --fail --silent http://localhost:8502/_stcore/health && echo"

Prints `ok` if Streamlit is alive and responding inside the container.

## Full rebuild-and-restart cycle (the one you'll use most while developing)

    wsl -d Ubuntu-22.04 -- docker rm -f ecovision-app
    wsl -d Ubuntu-22.04 -- docker build -t ecovision .
    wsl -d Ubuntu-22.04 -- docker run -d --name ecovision-app -p 8502:8501 ecovision

If the remove command says the container does not exist, continue with
the build command. If the run command reports that port 8502 is busy,
replace `8502:8501` with `8503:8501` and use port 8503 in the health
check and browser URL.

## Check or free a host port

Check whether Windows is listening on port 8502:

    Get-NetTCPConnection -LocalPort 8502 -State Listen -ErrorAction SilentlyContinue

Check whether Docker is publishing it:

    wsl -d Ubuntu-22.04 -- docker ps --format "table {{.Names}}\t{{.Ports}}"

Stop the container that owns the port, if it is the EcoVision container:

    wsl -d Ubuntu-22.04 -- docker rm -f ecovision-app

## Clean up old, unused images (optional, frees disk space)

    wsl -d Ubuntu-22.04 -- docker image prune

Only removes *dangling* images (old builds no longer tagged to
anything current) — safe to run any time, won't touch your running
container or current image.
