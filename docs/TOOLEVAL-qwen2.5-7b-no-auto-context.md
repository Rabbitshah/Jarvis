# Tool-use check: qwen2.5:7b (automatic note search OFF)

Answer correct: 27/42 (64%). Strict (answer correct AND the right tools used, e.g. no notes search for a general question): 27/42 (64%). 3 trials per question, same agent and prompt as voice mode. Notes questions pass when the right note was consulted.

| Question | Answer correct | Strict | Avg seconds |
| --- | --- | --- | --- |
| time | 3/3 | 3/3 | 0.5 |
| date | 3/3 | 3/3 | 0.3 |
| fun fact | 3/3 | 3/3 | 0.3 |
| capital | 3/3 | 3/3 | 0.1 |
| math | 3/3 | 3/3 | 0.1 |
| explain | 3/3 | 3/3 | 0.6 |
| calendar | 3/3 | 3/3 | 0.3 |
| weather | 3/3 | 3/3 | 0.3 |
| remember | 3/3 | 3/3 | 1.0 |
| notes: How did my car-driving neural network co | 0/3 | 0/3 | 0.4 |
| notes: Which universities still need a statemen | 0/3 | 0/3 | 0.4 |
| notes: Why is my study app not live yet? | 0/3 | 0/3 | 0.3 |
| notes: What am I not allowed to say about my em | 0/3 | 0/3 | 0.5 |
| notes: Which wake word library did the first ve | 0/3 | 0/3 | 0.4 |

## Failures

- **notes: How did my car-driving neural network co** (right note not consulted (got none)): `'Search_notes is needed for this question.'`
- **notes: How did my car-driving neural network co** (right note not consulted (got none)): `"I couldn't find any notes on that topic. Let me search."`
- **notes: How did my car-driving neural network co** (right note not consulted (got none)): `"I couldn't find any notes comparing your car-driving neural network with deep reinforcement learning. Let me search your notes."`
- **notes: Which universities still need a statemen** (right note not consulted (got none)): `'I need to search your notes for information on universities and statements of purpose. Let me check.'`
- **notes: Which universities still need a statemen** (right note not consulted (got none)): `'I need to search your notes for information about universities that require a statement of purpose. Let me check.'`
- **notes: Which universities still need a statemen** (right note not consulted (got none)): `"I don't have your notes to check. Let's search your notes for mentions of universities and statements of purpose."`
- **notes: Why is my study app not live yet?** (right note not consulted (got none)): `'The study app is still being tested and refined. It should be live soon.'`
- **notes: Why is my study app not live yet?** (right note not consulted (got none)): `"Check your notes for any recent updates or plans related to the app's development."`
- **notes: Why is my study app not live yet?** (right note not consulted (got none)): `'Check your notes for any updates or plans related to the study app.'`
- **notes: What am I not allowed to say about my em** (right note not consulted (got none)): `'You should not disclose confidential information or trade secrets. Avoid defamatory statements and ensure what you write is not slanderous.'`
- **notes: What am I not allowed to say about my em** (right note not consulted (got none)): `'You should not disclose confidential or sensitive information about your employer. Avoid making defamatory statements that could harm their reputation without e'`
- **notes: What am I not allowed to say about my em** (right note not consulted (got none)): `'You should not disclose confidential or proprietary information about your employer. Avoid making defamatory statements that could harm their reputation without'`
- **notes: Which wake word library did the first ve** (right note not consulted (got none)): `"I don't have notes about the first version of the assistant's wake word library. Let me search for relevant excerpts."`
- **notes: Which wake word library did the first ve** (right note not consulted (got none)): `'search_notes {"query": "wake word library first version"}'`
- **notes: Which wake word library did the first ve** (right note not consulted (got none)): `"I don't have notes about the first version of the assistant's wake word library. Let me search for related notes."`
