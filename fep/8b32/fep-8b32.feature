Feature: FEP-8b32: Object Integrity Proofs

    @fep-8b32
    Scenario: Signing document
        Given document
            """
            {
                "@context": [
                    "https://www.w3.org/ns/activitystreams",
                    "https://w3id.org/security/data-integrity/v2"
                ],
                "id": "https://server.example/activities/1",
                "type": "Create",
                "actor": "https://server.example/users/alice",
                "object": {
                    "id": "https://server.example/objects/1",
                    "type": "Note",
                    "attributedTo": "https://server.example/users/alice",
                    "content": "Hello world",
                    "location": {
                        "type": "Place",
                        "longitude": -71.184902,
                        "latitude": 25.273962
                    }
                }
            }
            """
        And Ed25519 secret key "z3u2en7t5LR2WtQH5PfFqMqwVHBeXouLzo6haApm8XHqvjxq"
        And current time "2023-02-24T23:36:38Z"
        When Signing the document for key "https://server.example/users/alice#ed25519-key"
        Then The signed document is
            """
            {
                "@context": [
                    "https://www.w3.org/ns/activitystreams",
                    "https://w3id.org/security/data-integrity/v2"
                ],
                "id": "https://server.example/activities/1",
                "type": "Create",
                "actor": "https://server.example/users/alice",
                "object": {
                    "id": "https://server.example/objects/1",
                    "type": "Note",
                    "attributedTo": "https://server.example/users/alice",
                    "content": "Hello world",
                    "location": {
                        "type": "Place",
                        "longitude": -71.184902,
                        "latitude": 25.273962
                    }
                },
                "proof": {
                    "@context": [
                        "https://www.w3.org/ns/activitystreams",
                        "https://w3id.org/security/data-integrity/v2"
                    ],
                    "type": "DataIntegrityProof",
                    "cryptosuite": "eddsa-jcs-2022",
                    "verificationMethod": "https://server.example/users/alice#ed25519-key",
                    "proofPurpose": "assertionMethod",
                    "proofValue": "z42ffGu6AUKPCFcFPiabmUvnGLPJzC7e4DGWC52NUasSSH37UMa9c58tdgVszUcZfytxa4fQ5TYHaJENCxUDe9SdL",
                    "created": "2023-02-24T23:36:38Z"
                }
            }
            """

    @fep-8b32
    Scenario: Verifying a signature
        Given The signed document is
            """
            {
                "@context": [
                    "https://www.w3.org/ns/activitystreams",
                    "https://w3id.org/security/data-integrity/v2"
                ],
                "id": "https://server.example/activities/1",
                "type": "Create",
                "actor": "https://server.example/users/alice",
                "object": {
                    "id": "https://server.example/objects/1",
                    "type": "Note",
                    "attributedTo": "https://server.example/users/alice",
                    "content": "Hello world",
                    "location": {
                        "type": "Place",
                        "longitude": -71.184902,
                        "latitude": 25.273962
                    }
                },
                "proof": {
                    "@context": [
                        "https://www.w3.org/ns/activitystreams",
                        "https://w3id.org/security/data-integrity/v2"
                    ],
                    "type": "DataIntegrityProof",
                    "cryptosuite": "eddsa-jcs-2022",
                    "verificationMethod": "https://server.example/users/alice#ed25519-key",
                    "proofPurpose": "assertionMethod",
                    "proofValue": "z42ffGu6AUKPCFcFPiabmUvnGLPJzC7e4DGWC52NUasSSH37UMa9c58tdgVszUcZfytxa4fQ5TYHaJENCxUDe9SdL",
                    "created": "2023-02-24T23:36:38Z"
                }
            }
            """
        And The actor
            """
            {
                "@context": [
                    "https://www.w3.org/ns/activitystreams",
                    "https://w3id.org/security/data-integrity/v2",
                    "https://w3id.org/security/multikey/v1"
                ],
                "type": "Person",
                "id": "https://server.example/users/alice",
                "inbox": "https://server.example/users/alice/inbox",
                "outbox": "https://server.example/users/alice/outbox",
                "assertionMethod": [
                    {
                        "id": "https://server.example/users/alice#ed25519-key",
                        "type": "Multikey",
                        "controller": "https://server.example/users/alice",
                        "publicKeyMultibase": "z6MkrJVnaZkeFzdQyMZu1cgjg7k1pZZ6pvBQ7XJPt4swbTQ2"
                    }
                ]
            }
            """
        When verifying the document
        Then the document is valid
