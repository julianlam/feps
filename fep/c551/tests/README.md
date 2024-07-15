# fep-c551-tests

A test suite that tests for conformance to [FEP-c551: Use ECMAScript Modules to Create Conformance Tests for Fediverse Enhancement Proposals][FEP-c551].

## Tests

### fep-c551 module must export test object

* slug: `fep-c551-module-must-export-test-object`
* [Test Module](./fep-c551-module-must-export-test-object.js)

## Usage

### Running local test files via Data URL

```shell
activitypub-testing run test \
--url="$(data-url ./fep-c551-module-must-export-test-object.js)" \
--input.module="$(cat <<EOF
export default {
  name: 'sample test',
  run: () => {
    return { outcome: 'inapplicable' }
  }
}
EOF
)"
```

The `data-url` command is provided by the following shell function:

```shell
data-url() {
  if [ -z "$1" ]; then
    echo "usage: data-url file" >&2
    exit 1
  fi
  mimetype=$(file -bN --mime-type "$1")
  content=$(base64 < "$1")
  echo "data:$mimetype;base64,$content"
}
```

[FEP-c551]: https://codeberg.org/fediverse/fep/src/branch/main/fep/c551/fep-c551.md
