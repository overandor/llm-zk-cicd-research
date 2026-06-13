# Zero-Knowledge Proofs

Zero-knowledge proofs let a prover convince a verifier that a statement is
true without revealing any information beyond the statement's validity.

In the ZK-CI framework, this means a CI pipeline can prove that an LLM's
code review found no critical vulnerabilities, or that test coverage exceeds
a threshold, without exposing the source code, the test data, or the model's
raw output.

Key properties: completeness, soundness, and zero-knowledge. Common
constructions include zk-SNARKs (succinct, require trusted setup) and
zk-STARKs (transparent, post-quantum secure but larger proofs).
