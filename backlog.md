# Backlog

This document will list backlog tips we intend to create in the future.

- Set up your system to be re-playable: once you have traces logged, you should also be able to "replay" certain queries, selectively enabling a cached response to be returned instead of running the code, this way you can reproduce issues in a granular way.
- Temperature escalation: when hitting a failure, retry the request with higher temperature
- better agent escalation: when hitting a failure, retry the request with a better model
- Lack of production evals...
- scalable end user feedback
- Review your chunks manually (duplicates, low info)
- Find chunks that are not relevant for *any* query
- resilient parsing (schema aligned / yaml)
-
