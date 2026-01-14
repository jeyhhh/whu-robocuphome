from funasr import AutoModel
import os
chunk_size = [0, 10, 5]  # [0, 10, 5] 600ms, [0, 8, 4] 480ms
encoder_chunk_look_back = 4  # number of chunks to lookback for encoder self-attention
decoder_chunk_look_back = 1  # number of encoder chunks to lookback for decoder cross-attention

model_path = "C:/Users/Jupku/.cache/modelscope/hub/models/iic/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-online"

# model = AutoModel(model="paraformer-zh-streaming",
#                   disable_update = True)
model = AutoModel(model=model_path,
                  disable_update = True)
import os
import pyaudio
import numpy as np
from collections import deque
import time
# 音频参数
CHUNK = 1600  # 每次读取的帧数（1600 @16k = 0.1s）
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000  # 16kHz

p = pyaudio.PyAudio()
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print("开始实时语音识别...按 Ctrl+C 停止")

# 每个推理块的样本数 (与原代码 chunk_size 对应，960 samples ~= 0.06s @16k)
chunk_stride = chunk_size[1] * 960  # e.g. 10*960=9600 samples (~0.6s)

# 用于累积从麦克风读取到的样本
buffers = []  # 列表存放 numpy arrays
total_samples = 0
cache = {}

try:
    while True:
        # 读音频帧
        data = stream.read(CHUNK, exception_on_overflow=False)
        # bytes -> int16 -> float32 (-1.0 ~ 1.0)
        samples = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
        buffers.append(samples)
        total_samples += samples.shape[0]

        total_res = []

        # 当累积样本达到一个块长度时，拼接并送入模型
        if total_samples >= chunk_stride:
            big = np.concatenate(buffers, axis=0)
            piece = big[:chunk_stride]
            remaining = big[chunk_stride:]

            # 把剩余样本保留到 buffers
            buffers = [remaining] if remaining.size > 0 else []
            total_samples = remaining.size

            # 调用模型进行流式识别（保持 cache）
            res = model.generate(input=piece, cache=cache, chunk_size=chunk_size,
                                 encoder_chunk_look_back=encoder_chunk_look_back,
                                 decoder_chunk_look_back=decoder_chunk_look_back)
            total_res.append(res)
            print(res)

except KeyboardInterrupt:
    print("停止识别，关闭音频流...")
finally:
    try:
        stream.stop_stream()
        stream.close()
        p.terminate()
    except Exception:
        pass