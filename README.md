### requirements

- python3 version 10 ish ig
- docker version 28 ish


### docker guide

verify works: `systemctl status docker`

build: `docker compose up --build` (sudo optional)

### deployment info

app is deployed automatically from main branch on https://seng2021-nine.vercel.app/

```
note from andrea:

**DO NOT PUSH UNTESTED CODE TO MAIN BRANCH**

we(i) should set up a testing branch and/or pipeline so we dont deploy any untested code
```
