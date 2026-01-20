from funasr import AutoModel
import os
import os
import pyaudio
import numpy as np
from collections import deque
import time

class voice:
    def __init__(self):
        super().__init__()
        # 模型参数
        self.chunk_size = [0, 20, 10]  # [0, 10, 5] 600ms, [0, 8, 4] 480ms
        self.encoder_chunk_look_back = 4  # number of chunks to lookback for encoder self-attention
        self.decoder_chunk_look_back = 1  # number of encoder chunks to lookback for decoder cross-attention
        #self.model_path = "C:/Users/Jupku/.cache/modelscope/hub/models/iic/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-online"
        # self.__model = AutoModel(model=self.model_path,
        #                        disable_update = True)

        self.__model = AutoModel(model="paraformer-zh-streaming",
                          disable_update = True)
        
        # 每个推理块的样本数 (与原代码 chunk_size 对应，960 samples ~= 0.06s @16k)
        self.__chunk_stride = self.chunk_size[1] * 960

        # 用于累积从麦克风读取到的样本
        self.__buffers = []  # 列表存放 numpy arrays
        self.__total_samples = 0
        self.cache = {}

        #关键词合集
        self.keywords = ["你好","在吗","帮我","请问","谢谢"]

        # 音频参数
        self.CHUNK = 1600  # 每次读取的帧数（1600 @16k = 0.1s）
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000  # 16kHz
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                frames_per_buffer=self.CHUNK)

        print("开始实时语音识别...按 Ctrl+C 停止")

    def recognize(self, duration=10):
        try:
            #开始计时
            while True:
                start_time = time.time()
                total_res = []

                while time.time() - start_time < duration:  # 运行10秒后停止
                    # 读音频帧
                    data = self.stream.read(self.CHUNK, exception_on_overflow=False)
                    # bytes -> int16 -> float32 (-1.0 ~ 1.0)
                    samples = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
                    self.__buffers.append(samples)
                    self.__total_samples += samples.shape[0]

                    keywords_found = []

                    # 当累积样本达到一个块长度时，拼接并送入模型
                    if self.__total_samples >= self.__chunk_stride:
                        big = np.concatenate(self.__buffers, axis=0)
                        piece = big[:self.__chunk_stride]
                        remaining = big[self.__chunk_stride:]

                        # 把剩余样本保留到 buffers
                        self.__buffers = [remaining] if remaining.size > 0 else []
                        self.__total_samples = remaining.size
                        # 调用模型进行流式识别（保持 cache）
                        res = self.__model.generate(input=piece, cache=self.cache, chunk_size=self.chunk_size,
                                            encoder_chunk_look_back=self.encoder_chunk_look_back,
                                            decoder_chunk_look_back=self.decoder_chunk_look_back)
                        # 兼容不同返回类型：dict / list / str
                        txt = ''
                        if isinstance(res, dict):
                            txt = res.get('text', '')
                        elif isinstance(res, list):
                            parts = []
                            for it in res:
                                if isinstance(it, dict):
                                    parts.append(it.get('text', ''))
                                else:
                                    parts.append(str(it))
                            txt = ''.join(parts)
                        else:
                            txt = str(res)

                        if txt:
                            total_res.append(txt)
                            print("片段识别:", txt)
                
                final_text = ''.join(total_res)
                print({'text': final_text})
                
                keywords_found.append(str(self.keyword_pas(final_text)))
                keywords_found = self.keyword_pas(final_text)
                print({'text': final_text, 'keywords': keywords_found})

        except KeyboardInterrupt:
            print("停止识别，关闭音频流...")
        finally:
            try:
                self.stream.stop_stream()
                self.stream.close()
                self.p.terminate()
            except Exception:
                pass

    def keyword_pas(self, text):
        keywords_found = []
        for keyword in self.keywords:
            if keyword in text:
                keywords_found.append(keyword)
        return keywords_found
        

def main():
    recognizer = voice()
    recognizer.recognize(duration=10)

if __name__ == "__main__":
    main()