# Fediverse Enhancement Proposals

<!-- DO NOT EDIT! File automatically generated with `./scripts/create_readme.py`. -->

This is the Git repository containing Fediverse Enhancment Proposals (FEPs).

A Fediverse Enhancement Proposal (FEP) is a document that provides information to the Fediverse community. The goal of a FEP is to improve interoperability and well-being of diverse services, applications and communities that form the Fediverse.

The FEP Process is an initiative of the [SocialHub](https://socialhub.activitypub.rocks) developer community, a liaison of the [W3C Social Web Incubator Community Group](https://www.w3.org/community/SocialCG/). For ongoing and past discussion see the [SocialHub FEP category](https://socialhub.activitypub.rocks/c/standards/fep/54).

## Submitting a FEP

Do you have an idea, opinion or information that you want to share with the wider Fediverse community? You may do so with a Fediverse Enhancement Proposal (FEP).

To create and submit a FEP:

1. Fork this repository, and then clone it to your local machine. Check the Codeberg [Cheat sheet](https://docs.codeberg.org/collaborating/pull-requests-and-git-flow/#cheat-sheet) on how to prepare your Pull Request.
2. Think of a title for the FEP you want to submit.
3. Compute the identifier of the FEP by computing the hash of the title. This can be done with following Unix command:

```
$ echo -n "The title of my proposal" | sha256sum | cut -c-4
b3f0
```

4. Create a subdirectory of [`fep/`](./fep/) using the identifier you just computed.
5. Copy the FEP template ([fep-xxxx-template.md](./fep-xxxx-template.md)) to this subdirectory and change the filename appropriately.
6. Use the identifer as the "slug" when filling out the frontmatter.

    - For example, if your computed identifier was `abcd`, then your file would be located at `fep/abcd/fep-abcd.md` and your frontmatter would include `slug: "abcd"`.

7. Write down your idea in the newly created file and commit it to a new branch in your repository (ex. fep-xxxx).
8. When you are ready to submit the FEP, change the value of `dateReceived` field in the frontmatter to the current date.
9. Create a discussion topic for your FEP. You can use [ActivityPub category](https://socialhub.activitypub.rocks/c/activitypub/5) on the SocialHub forum.
10. Add `discussionsTo` field containing the URL of the discussion topic to the front matter of your FEP.
11. Create a Pull Request to complete Step 1 of [FEP-a4ed: The Fediverse Enhancement Proposal Process](./fep/a4ed/fep-a4ed.md). Further process is described in FEP-a4ed.

Alternatively to steps 3. to 6., you can run

```bash
python scripts/new_proposal.py TITLE OF YOUR PROPOSAL
```

that should create a prefilled template for you.

## Facilitators

The list of FEP's is maintained by the facilitators who are listed in the [FACILITATORS.md](FACILITATORS.md) file. Facilitators are neutral custodians of the FEP process, who merge PR's and create tracking issues.

## Contributing

Do you have ideas to improve the FEP Process? Post your suggestions to the issue tracker, or on the [SocialHub](https://socialhub.activitypub.rocks) forum. The SocialHub developer community is a "DoOcracy" which means: “pick up any task you want, and then steer it to completion”. Your contributions are most welcome, so delve in and find out how you can help.

## FEPs

<!-- TODO: This table is not CommonMark (as specified by FEP-a4ed) and requires maintenance. -->

| Title                                                                               | Status  | Tracking issue                                                                              | `dateReceived` | `dateFinalized` (or `dateWithdrawn`) |
| ---                                                                                 | ---     | -----                                                                                       | -------        | ------                               |
