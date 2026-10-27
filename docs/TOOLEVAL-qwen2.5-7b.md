# Tool-use check: qwen2.5:7b

Answer correct: 42/42 (100%). Strict (answer correct AND the right tools used, e.g. no notes search for a general question): 40/42 (95%). 3 trials per question, same agent and prompt as voice mode. Notes questions pass when the right note was consulted.

| Question | Answer correct | Strict | Avg seconds |
| --- | --- | --- | --- |
| time | 3/3 | 3/3 | 0.8 |
| date | 3/3 | 3/3 | 0.3 |
| fun fact | 3/3 | 3/3 | 0.4 |
| capital | 3/3 | 3/3 | 0.2 |
| math | 3/3 | 3/3 | 0.1 |
| explain | 3/3 | 3/3 | 0.7 |
| calendar | 3/3 | 3/3 | 0.4 |
| weather | 3/3 | 3/3 | 0.2 |
| remember | 3/3 | 1/3 | 0.6 |
| notes: How did my car-driving neural network co | 3/3 | 3/3 | 0.8 |
| notes: Which universities still need a statemen | 3/3 | 3/3 | 0.8 |
| notes: Why is my study app not live yet? | 3/3 | 3/3 | 0.8 |
| notes: What am I not allowed to say about my em | 3/3 | 3/3 | 0.4 |
| notes: Which wake word library did the first ve | 3/3 | 3/3 | 0.4 |

## Failures

- **remember** (tool not called: ['remember']): `'Remembering your favorite color is green. Please confirm by replying "save".'`
- **remember** (tool not called: ['remember']): `'Remembering your favorite color as green. Please confirm.'`
