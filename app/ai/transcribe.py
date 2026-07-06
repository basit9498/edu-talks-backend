from transformers import pipeline


class AIVoiceToText:
    def __init__(self, model: str = "openai/whisper-base"):
        self.asr_pipe = pipeline(
            "automatic-speech-recognition",
            model=model,
            chunk_length_s=30,
            return_timestamps=True,
        )

    def transcribe(self, file_path):
        transcription_result = self.asr_pipe(file_path)
        text = transcription_result["text"]
        return text


aiVoiceToText = AIVoiceToText()
