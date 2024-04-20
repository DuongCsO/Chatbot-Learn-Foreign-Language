# `pip3 install assemblyai` (macOS)
# `pip install assemblyai` (Windows)

import assemblyai as aai

aai.settings.api_key = "cf9519c108174b4d90e28b88b4125876"
transcriber = aai.Transcriber()

transcript = transcriber.transcribe("./output.mp3")
# transcript = transcriber.transcribe("./my-local-audio-file.wav")

if transcript.status == aai.TranscriptStatus.error:
    print(transcript.error)
else:
    print(transcript.text)
