# Tool-use check: qwen2.5:7b

Answer correct: 39/42 (93%). Strict (answer correct AND the right tools used, e.g. no notes search for a general question): 39/42 (93%). 3 trials per question, same agent and prompt as voice mode. Notes questions pass when the right note was consulted.

| Question | Answer correct | Strict | Avg seconds |
| --- | --- | --- | --- |
| time | 3/3 | 3/3 | 1.0 |
| date | 3/3 | 3/3 | 0.3 |
| fun fact | 0/3 | 0/3 | 0.3 |
| capital | 3/3 | 3/3 | 0.2 |
| math | 3/3 | 3/3 | 0.1 |
| explain | 3/3 | 3/3 | 0.7 |
| calendar | 3/3 | 3/3 | 0.3 |
| weather | 3/3 | 3/3 | 0.2 |
| remember | 3/3 | 3/3 | 1.0 |
| notes: How did my car-driving neural network co | 3/3 | 3/3 | 0.9 |
| notes: Which universities still need a statemen | 3/3 | 3/3 | 0.8 |
| notes: Why is my study app not live yet? | 3/3 | 3/3 | 0.7 |
| notes: What am I not allowed to say about my em | 3/3 | 3/3 | 0.4 |
| notes: Which wake word library did the first ve | 3/3 | 3/3 | 0.4 |

## Failures

- **fun fact** (answer contains something invented or off-topic): `'Facts Jarvis was asked to remember include: You play pickleball on weekends.'`
- **fun fact** (answer contains something invented or off-topic): `'Facts Jarvis was asked to remember include playing pickleball on weekends.'`
- **fun fact** (answer contains something invented or off-topic): `'Facts Jarvis was asked to remember include: You play pickleball on weekends.'`
