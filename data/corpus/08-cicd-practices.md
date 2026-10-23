# Continuous Integration and Delivery Practices

Continuous integration means every developer merges code into the shared main branch frequently, and every merge triggers an automated build and test run. The practice keeps integration problems small, because a failure is always caused by the most recent small change rather than by weeks of divergent work.

A delivery pipeline usually runs stages in order: unit tests, integration tests against ephemeral environments, a security and dependency scan, and then deployment to a staging environment that mirrors production. A failure at any stage stops the pipeline and notifies the author of the change.

A canary deployment releases a new version to a small subset of production traffic first. Typically the canary receives about five percent of requests while error rates and latency are compared against the old version. If the canary metrics stay healthy for a defined observation window, the rollout continues to all traffic; if errors rise, the deployment is rolled back automatically and the majority of users never see the faulty version.

Feature flags complement canary deployments. Code for an unfinished feature is merged but hidden behind a flag, so the release of the software and the activation of the feature become separate decisions. Flags also act as a kill switch when a new feature misbehaves in production.

Pipelines record an artefact for every build. Because the exact artefact that passed the tests is the one promoted to production, there is no recompilation between staging and production and therefore no chance for the tested and deployed code to differ.
