# Tool-use check: llama3.1:8b

Answer correct: 33/42 (79%). Strict (answer correct AND the right tools used, e.g. no notes search for a general question): 27/42 (64%). 3 trials per question, same agent and prompt as voice mode. Notes questions pass when the right note was consulted.

| Question | Answer correct | Strict | Avg seconds |
| --- | --- | --- | --- |
| time | 2/3 | 2/3 | 1.5 |
| date | 2/3 | 2/3 | 1.0 |
| fun fact | 0/3 | 0/3 | 1.2 |
| capital | 3/3 | 0/3 | 1.0 |
| math | 1/3 | 1/3 | 0.9 |
| explain | 3/3 | 0/3 | 1.8 |
| calendar | 1/3 | 1/3 | 1.0 |
| weather | 3/3 | 3/3 | 1.3 |
| remember | 3/3 | 3/3 | 1.1 |
| notes: How did my car-driving neural network co | 3/3 | 3/3 | 1.6 |
| notes: Which universities still need a statemen | 3/3 | 3/3 | 1.4 |
| notes: Why is my study app not live yet? | 3/3 | 3/3 | 1.8 |
| notes: What am I not allowed to say about my em | 3/3 | 3/3 | 1.2 |
| notes: Which wake word library did the first ve | 3/3 | 3/3 | 1.2 |

## Failures

- **time** (no correct time in answer (now 16:25)): `'That is the current time.'`
- **date** (no correct date in answer (today 27 October)): `"That's the date I have."`
- **fun fact** (answer contains something invented or off-topic): `'You play pickleball on weekends.'`
- **fun fact** (answer contains something invented or off-topic): `'The user plays pickleball on weekends.'`
- **fun fact** (answer contains something invented or off-topic): `'You play pickleball on weekends.'`
- **capital** (tool should not be used: ['search_notes']): `'The capital of France is Paris.'`
- **capital** (tool should not be used: ['search_notes']): `'The capital of France is Paris.'`
- **capital** (tool should not be used: ['search_notes']): `'The capital of France is Paris.'`
- **math** (answer missing the expected content): `'392.'`
- **math** (answer missing the expected content): `'392.'`
- **explain** (tool should not be used: ['search_notes']): `"An API, or Application Programming Interface, is a set of rules that allow different software systems to communicate with each other. It's like a messenger that"`
- **explain** (tool should not be used: ['search_notes']): `'An API, or Application Programming Interface, is a set of rules that allows different software systems to communicate with each other. It acts as a messenger, t'`
- **explain** (tool should not be used: ['search_notes']): `'An API, or Application Programming Interface, is a set of defined rules that enable different software systems to communicate with each other. It acts as a mess'`
- **calendar** (answer missing the expected content): `"I'm not aware of any meetings scheduled for tonight."`
- **calendar** (answer missing the expected content): `"I'm not aware of any meetings scheduled for tonight."`
