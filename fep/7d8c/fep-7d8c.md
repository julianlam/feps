---
slug: "7d8c"
authors: Helge <@helge@mymath.rocks>
status: DRAFT
discussionsTo: https://socialhub.activitypub.rocks/t/fep-repo-rights/4797/3
dateReceived: 2025-01-20
trackingIssue: https://codeberg.org/fediverse/fep/issues/470
---
# FEP-7d8c: Documentation: Automation of FEP

## Summary

This FEP discusses scripts and woodpecker configuration used to automate parts of the FEP process. The FEP process is described in [FEP-a4ed][a4ed].

As [FEP-a4ed][a4ed], this is a living document, and should be updated as the FEP process evolves.

## Vision

Automation has the goal of reducing the burden on facilitators by:

- allowing people without deep knowledge of git to become facilitators. Basically, the job will boil down to read a document and ensure it meets our standards, then click "merge".
- performing as many checks as possible via automation

Once one has simplified this job, one can seek broader adoption of the FEP process..

### Todos

This is a living document. So let's have a todo list

- [ ] Check for broken links
- [ ] Simplify creating FEPs. Does one really need git and a codeberg account?
- [ ] Code documentation to enable more people to write tools, e.g. an automatic generation of which FEP is used where

The first two items have been on my personal todo list for a long time, and might stay there ... so feel free to pick them up.

## Automation

Automation for the FEP repository uses the [codeberg woodpecker](https://ci.codeberg.org). There are two jobs:

- test runs basic checks on the contained FEPs
- readme updates the `README.md` file and creates the tracking issue
- create a static website

Automation code is written in python and is contained in the [script folder](https://codeberg.org/fediverse/fep/src/branch/main/scripts).

### Scripts and tests

FEP uses python scripts to manage some aspects of it. These should be runnable
without installing packages. In order to ensure these scripts stay working,
include them in [.woodpecker/test.yml](https://codeberg.org/fediverse/fep/src/branch/main/.woodpecker/test.yml)

## Configuration variables

To be able to do these configuration tasks, you need to be in the __admin__ group. See the
first discussion [here](https://socialhub.activitypub.rocks/t/fep-repo-rights/4797/2).

The configuration [.woodpecker/readme.yml](https://codeberg.org/fediverse/fep/src/branch/main/.woodpecker/readme.yml) uses two secrets:

- codeberg_api_token, a codeberg API token used to create the tracking issues.
- deploy_key, an SSH private key used to push to the codeberg repository.

Furthermore, the environment variable `CI_REPO_CLONE_SSH_URL` is used see [woodpecker documentation](https://woodpecker-ci.org/docs/usage/environment).

We will now discuss how to obtain these secrets.

### The api token

API tokens can be generated on [codeberg](https://codeberg.org/user/settings) under user settings -> `applications` -> `select permissions` -> `issue`: `Read and Write` and giving it a name. They are hexstrings with 40 characters (if I counted correctly), e.g.

```text
33104dd6847e87ef3d6925effdfc852349233034
```

### Deploy key

As already mentioned the deploy key is an ssh key. One can generate these on linux via

```bash
ssh-keygen -t ed25519 -f deploy_key
```

Do not specify a passphrase. Examples:

```bash
$ cat deploy_key
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACCQ5XqPCdvHPHsukhPS+RMDpMnOCCLW0csGGoFgijQRiwAAAJDpM7fx6TO3
8QAAAAtzc2gtZWQyNTUxOQAAACCQ5XqPCdvHPHsukhPS+RMDpMnOCCLW0csGGoFgijQRiw
AAAEB2ofBDBwUcZs5FHsaFMvyO95Qrvn8+PO3BchraucMRwJDleo8J28c8ey6SE9L5EwOk
yc4IItbRywYagWCKNBGLAAAADWhlbGdlQHJhaW5ib3c=
-----END OPENSSH PRIVATE KEY-----
$ cat deploy_key.pub
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJDleo8J28c8ey6SE9L5EwOkyc4IItbRywYagWCKNBGL helge@rainbow
```

The public key `deploy_key.pub` should be added to the codeberg repo under `settings` -> `deploy keys` -> `add deploy key` and checking the `enable write access` checkbox.

See [here](https://codeberg.org/fediverse/fep/settings/keys).

### Adding the secrets to woodpecker

One can add these secrets on [woodpecker](https://ci.codeberg.org/repos/12388), then selecting the settings wheel -> `secrets` -> `add secret`. The secrets only need to available for the `push` action (corresponding to a merged pull request).

The deploy_key needs to be end with a new line when pasting into the woodpecker ui.

## Development

The tools are located in the `scripts` folder, with the `scripts/fep_tools` folder containing the python package `fep_tools`. Most of this tooling only uses python, e.g.
`scripts/new_proposal.py` and `scripts/create_readme.md`, so they can be run from any
environment.

### Running tests

To run the tests, one needs [pytest](https://docs.pytest.org/). We note that the
tests run from the base folder. The following commands demonstrate how to setup
a virtual environment, install the dependencies, and run the tests.

```bash
python -mvenv .venv
pip install ./scripts
pytest
```

One can leave the venv, by running `deactivate`.


### Building the website

To build the website, first install the dependencies

```bash
python -mvenv .venv
pip install ./scripts
./scripts/create_site_pages.py
```

Then run mkdocs via

```bash
mkdocs serve --config-file scripts/mkdocs.yml
```

References:

- The website is build with [mkdocs](https://www.mkdocs.org/)
- and uses [mkdocs-material](https://squidfunk.github.io/mkdocs-material/) for its many plugins

### Automatic deployment

See [website.yml](https://codeberg.org/fediverse/fep/src/branch/main/.woodpecker/website.yml).

## Changes

- Added discussion link to tracking issue, use table to format (@helge, 2025-03-07)
- Added static website stuff [fep#673](https://codeberg.org/fediverse/fep/pulls/673)

## References

- pukkamustard, [FEP-a4ed: The Fediverse Enhancement Proposal Process][a4ed], 2020

[a4ed]: https://codeberg.org/fediverse/fep/src/branch/main/fep/a4ed/fep-a4ed.md

## Copyright

CC0 1.0 Universal (CC0 1.0) Public Domain Dedication

To the extent possible under law, the authors of this Fediverse Enhancement Proposal have waived all copyright and related or neighboring rights to this work.
