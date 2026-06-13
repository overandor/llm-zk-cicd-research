# CI/CD Pipelines

Continuous Integration and Continuous Deployment pipelines automatically
build, test, and deploy code on every change. A typical pipeline runs
linting, unit tests, security scans, and a deployment step gated on all
checks passing.

Adding an LLM analysis stage - for example, an automated review of a diff or
a summary of failing tests - turns the pipeline into a source of generated
content. Running that stage with a local model like Ollama keeps the
analysis reproducible and avoids per-run API costs, while a content
commitment (SHA-256 hash) of the input lets later stages verify that the
analysis matches the exact code that was checked.
