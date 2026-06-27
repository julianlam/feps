Feature: FEP-8b32: Object Integrity Proofs

    @fep-8b32
    Scenario: Signing a document
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
        When signing the document for key "https://server.example/users/alice#ed25519-key"
        Then the canonicalized document is
            """
            {"@context":["https://www.w3.org/ns/activitystreams","https://w3id.org/security/data-integrity/v2"],"actor":"https://server.example/users/alice","id":"https://server.example/activities/1","object":{"attributedTo":"https://server.example/users/alice","content":"Hello world","id":"https://server.example/objects/1","location":{"latitude":25.273962,"longitude":-71.184902,"type":"Place"},"type":"Note"},"type":"Create"}
            """
        Then the canonicalized proof configuration is
            """
            {"@context":["https://www.w3.org/ns/activitystreams","https://w3id.org/security/data-integrity/v2"],"created":"2023-02-24T23:36:38Z","cryptosuite":"eddsa-jcs-2022","proofPurpose":"assertionMethod","type":"DataIntegrityProof","verificationMethod":"https://server.example/users/alice#ed25519-key"}
            """
        Then the combined hash is "cf63e2308ce7d1137667192c5c5e751ba7b1c6e3d5e746a7b717d309654ad1980793e8d97e2de4b989b2b2d7a5fae8cf941f102a03c0ecab00f03eaa2330c650"
        Then the signed document is
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
        Given the signed document is
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
        And the actor
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
