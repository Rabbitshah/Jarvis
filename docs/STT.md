# Speech-to-text comparison

4 clips from your microphone. Time = warm run, average per clip. Real-time factor 0.10 means 1 s of speech takes 0.1 s. WER = share of words wrong (lower is better).

| Engine | Load (s) | Time per clip (s) | Real-time factor | WER |
| --- | --- | --- | --- | --- |
| faster-whisper:base | 24.3 | 0.27 | 0.06 | 0.070 |
| faster-whisper:small | 70.5 | 0.87 | 0.19 | 0.000 |
| mlx-whisper:whisper-base-mlx | 30.8 | 0.06 | 0.01 | 0.229 |
| mlx-whisper:whisper-small-mlx | 50.4 | 0.07 | 0.01 | 0.000 |

## What each engine heard

| Engine | Clip | Text | WER |
| --- | --- | --- | --- |
| faster-whisper:base | clip1.wav | Hey Jarvis, what time is it? | 0.00 |
| faster-whisper:base | clip2.wav | Remind me to call to Rahul tomorrow morning. | 0.14 |
| faster-whisper:base | clip3.wav | What is the weather in Valladara today and do I have any meetings after lunch? | 0.07 |
| faster-whisper:base | test.wav | Hello Jarvis, what time is it? |  |
| faster-whisper:small | clip1.wav | Hey Jarvis, what time is it? | 0.00 |
| faster-whisper:small | clip2.wav | Remind me to call Rahul tomorrow morning. | 0.00 |
| faster-whisper:small | clip3.wav | What is the weather in Vadodara today and do I have any meetings after lunch? | 0.00 |
| faster-whisper:small | test.wav | Hello Jarvis, what time is it? |  |
| mlx-whisper:whisper-base-mlx | clip1.wav | What time is it? | 0.33 |
| mlx-whisper:whisper-base-mlx | clip2.wav | Rewind me to call to Rahul tomorrow morning. | 0.29 |
| mlx-whisper:whisper-base-mlx | clip3.wav | What is the weather in Valladara today and do I have any meetings after lunch? | 0.07 |
| mlx-whisper:whisper-base-mlx | test.wav | Hello Jarvis, what time is it? |  |
| mlx-whisper:whisper-small-mlx | clip1.wav | Hey Jarvis, what time is it? | 0.00 |
| mlx-whisper:whisper-small-mlx | clip2.wav | Remind me to call Rahul tomorrow morning. | 0.00 |
| mlx-whisper:whisper-small-mlx | clip3.wav | What is the weather in Vadodara today and do I have any meetings after lunch? | 0.00 |
| mlx-whisper:whisper-small-mlx | test.wav | Hello Jarvis, what time is it? |  |
