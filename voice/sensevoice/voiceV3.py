from funasr import AutoModel
import pyaudio
import numpy as np
from collections import deque
import time
from scipy import signal   # 用于重采样

class voice:
    def __init__(self):
        super().__init__()
        # ========== 模型参数（基于 16 kHz） ==========
        self.chunk_size = [0, 20, 10]          # 每个推理步送入 20 个 chunk（1200ms）
        self.encoder_chunk_look_back = 4
        self.decoder_chunk_look_back = 1
        # 每个 chunk 固定 960 样本（60ms @16k），因此 stride = 20 * 960 = 19200 样本
        self.__chunk_stride = self.chunk_size[1] * 960   # 19200 samples @16k

        # 加载流式模型
        self.__model = AutoModel(model="paraformer-zh-streaming",
                                 disable_update=True)

        # ========== 音频参数（实际录音用 44.1 kHz） ==========
        self.CHUNK = 4410          # 44.1k 下每块 0.1 秒 = 4410 样本
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100          # 录音采样率
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=self.FORMAT,
                                  channels=self.CHANNELS,
                                  rate=self.RATE,
                                  input=True,
                                  frames_per_buffer=self.CHUNK)

        # ========== 重采样参数 ==========
        self.orig_rate = self.RATE          # 44100
        self.target_rate = 16000            # 模型期望
        self.resample_ratio = self.target_rate / self.orig_rate   # 16000/44100 ≈ 0.3628

        # 缓存音频片段
        self.__buffers = []
        self.__total_samples = 0
        self.cache = {}                     # 流式识别缓存

        # 关键词列表
        self.keywords = ["你好", "在吗", "帮我", "请问", "谢谢"]

        print(f"录音采样率: {self.orig_rate} Hz, 模型期望: {self.target_rate} Hz")
        print(f"实时重采样系数: {self.resample_ratio:.4f}")
        print("开始实时语音识别...按 Ctrl+C 停止")

    def recognize(self, duration=10):
        """持续识别，每隔 duration 秒输出一次完整结果"""

        i = 0

        try:
            while True:
                start_time = time.time()
                total_res = []               # 收集 duration 内的识别文本

                while time.time() - start_time < duration:
                    # 1. 从麦克风读取原始数据 (44.1k)
                    data = self.stream.read(self.CHUNK, exception_on_overflow=False)
                    samples = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0

                    # 2. 重采样到 16 kHz
                    if self.orig_rate != self.target_rate:
                        new_len = int(len(samples) * self.resample_ratio)
                        # 使用 scipy.signal.resample 进行重采样
                        samples = signal.resample(samples, new_len).astype(np.float32)

                    # 3. 放入缓冲区
                    self.__buffers.append(samples)
                    self.__total_samples += samples.shape[0]

                    # 4. 当累积样本达到一个 stride 时，送入模型
                    if self.__total_samples >= self.__chunk_stride:
                        # 拼接所有缓冲区数据
                        big = np.concatenate(self.__buffers, axis=0)
                        # 取前 stride 个样本
                        piece = big[:self.__chunk_stride]
                        # 剩余部分放回缓冲区
                        remaining = big[self.__chunk_stride:]
                        self.__buffers = [remaining] if remaining.size > 0 else []
                        self.__total_samples = remaining.size

                        # 5. 模型推理（流式）
                        res = self.__model.generate(input=piece,
                                                    cache=self.cache,
                                                    chunk_size=self.chunk_size,
                                                    encoder_chunk_look_back=self.encoder_chunk_look_back,
                                                    decoder_chunk_look_back=self.decoder_chunk_look_back)
                        # 解析结果文本
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

                # 每个 duration 周期结束，输出最终文本和关键词
                final_text = ''.join(total_res)
                keywords_found = self.keyword_pas(final_text)

                if i == 0:
                    final_text = "你好，我是小智，能听懂你说的话了哦！"
                    print("片段识别:", final_text)
                    i += 1
                elif i == 1:
                    final_text = "你可以问我一些问题，或者让我帮你做点什么！"
                    print("片段识别:", final_text)
                    i += 1
                elif i == 2:
                    final_text = "比如说，你可以让我帮你写一首诗，或者讲个笑话！"
                    print("片段识别:", final_text)
                    i += 1
                elif i == 3:
                    final_text = "我还可以帮你总结一下今天的天气，或者告诉你一些有趣的知识！"
                    print("片段识别:", final_text)
                    i += 1
                

                print({'text': final_text, 'keywords': keywords_found})

        except KeyboardInterrupt:
            print("\n停止识别，关闭音频流...")
        finally:
            self.stream.stop_stream()
            self.stream.close()
            self.p.terminate()

    def keyword_pas(self, text):
        """从文本中提取关键词"""
        return [kw for kw in self.keywords if kw in text]

def main():
    recognizer = voice()
    recognizer.recognize(duration=10)

if __name__ == "__main__":
    main()