#语音识别
import pyaudio
import numpy as np
from faster_whisper import WhisperModel

# 加载模型（选择小模型以获得低延迟）
model = WhisperModel("base", device="gpu", compute_type="int8")

# 音频参数
CHUNK = 1600  # 每次读取的帧数
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000  # Whisper 推荐 16kHz

p = pyaudio.PyAudio()
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print("开始实时语音识别...按 Ctrl+C 停止")

audio_buffer = []
while True:
    # 读取音频数据
    data = stream.read(CHUNK, exception_on_overflow=False)
    audio_buffer.append(data)
    
    # 每2秒处理一次（可根据需要调整）
    if len(audio_buffer) * CHUNK >= RATE * 2:
        # 转换为 numpy 数组
        audio_np = np.frombuffer(b''.join(audio_buffer), dtype=np.int16)
        audio_float = audio_np.astype(np.float32) / 32768.0
        
        # 语音识别
        segments, info = model.transcribe(audio_float, beam_size=5)
        
        for segment in segments:
            print(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}")
        
        # 保留最后0.5秒的数据以实现连续识别
        keep_frames = int(RATE * 0.5 / CHUNK)
        audio_buffer = audio_buffer[-keep_frames:]