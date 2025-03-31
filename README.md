### requirements

- python3 version 10 ish
- docker version 28 ish (for local deployments)


### docker guide

verify works: `systemctl status docker`

build: `docker compose up --build` (sudo optional)

### deployment info

app is deployed automatically from main branch on https://the-real-guy-chilcott.vercel.app and swagger docs can be found on https://the-real-guy-chilcott.vercel.app/docs

### setup 
to make sure all relevant packages are installed and up to date we have made a requirements file. to use it, run 'pip install -r src/requirements.txt'
