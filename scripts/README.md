# tools for fep facilitators

Please follow the steps in configuration before following "Merge a FEP".

## Merge a FEP

Merge the Pull Request in [https://codeberg.org/fediverse/fep/pulls](https://codeberg.org/fediverse/fep/pulls)
and note the slug.

```bash
./scripts/create_issue.py $SLUG
```

creates the tracking issue and updates the FEP with the information.
Then run

```bash
./scripts/create_readme.py
```

to update the table in `README.md`. You are now ready to commit the
changes to the FEP (added `trackingIssue` to frontmatter) and README.md,
added the new FEP.

## Configuration

Add a file `config.json` to the directory `scripts` with content

```json
{
  "repo": "fep",
  "owner": "fediverse",
  "token": "CODEBERG_API_TOKEN"
}
```

The API token can be obtained by visiting [https://codeberg.org/user/settings/applications](https://codeberg.org/user/settings/applications) and generating one with scope `write:issue`.

## Setup for running pytest

Ensure dependencies (use a virtualenv)

```bash
pip install pytest
```

Check validity

```bash
pytest
```
