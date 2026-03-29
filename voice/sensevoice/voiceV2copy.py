from funasr import AutoModel
import os
import pyaudio
import numpy as np
from collections import deque
import time
from openai import OpenAI
import rclpy
import pyttsx3

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
        self.CHUNK = 1600  # 每次读取的帧数（1600 @16k = 0.1s）
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100  # 44.1kHz
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                frames_per_buffer=self.CHUNK)

        print("开始实时语音识别...按 Ctrl+C 停止")

    def recognize(self, llm):
        try:
            start_time = time.time()
            total_res = []

            while True:
                # 读音频帧
                data = self.stream.read(self.CHUNK, exception_on_overflow=False)
                # bytes -> int16 -> float32 (-1.0 ~ 1.0)
                samples = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
                self.__buffers.append(samples)
                self.__total_samples += samples.shape[0]

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

                # 每10秒发送累积结果给大模型
                if time.time() - start_time >= 10:
                    final_text = ''.join(total_res)
                    final_text = final_text.join("hello")
                    if final_text.strip():
                        print("发送给大模型:", final_text)
                        response = llm.get_response(final_text)
                        llm.speakout(response)
                    # 重置累积文本和时间
                    total_res = []
                    start_time = time.time()

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

class LLMresponse:
    def __init__(self):
        self.client = OpenAI(base_url="http://127.0.0.1:8080", api_key="EMPTY")
        self.engine = pyttsx3.init()
        # 初始化对话历史，可以包含系统提示
        self.conversation_history = [
            {"role": "user", "content": "你是我的智能助手，协助我完成任务。全程使用英语"}
        ]
        # 可选：获取大模型对系统提示的首次响应
        init_response = self.client.chat.completions.create(
            model="Qwen3.5-9B",
            messages=self.conversation_history,
            temperature=0.7,
            top_p=0.8,
            max_tokens=4096,
        ).choices[0].message.content
        self.conversation_history.append({"role": "assistant", "content": init_response})
        print("LLM初始化完成，系统提示:", init_response)
        self.speakout(init_response)
        # 等待系统提示的语音播报完成
        time.sleep(20)

    def get_response(self, prompt):
        # 将用户消息加入历史
        self.conversation_history.append({"role": "user", "content": prompt})
        # 请求大模型（带上完整历史）
        response = self.client.chat.completions.create(
            model="Qwen3.5-9B",
            messages=self.conversation_history,
            temperature=0.7,
            top_p=0.8,
            max_tokens=16000,
        )
        assistant_msg = response.choices[0].message.content
        # 将助手回复加入历史
        self.conversation_history.append({"role": "assistant", "content": assistant_msg})
        return assistant_msg


    def speakout(self, text):
        print("LLM response:", text)
        # 这里可以添加文本转语音的代码，例如调用 TTS 模型或系统 TTS 功能
        # 例如，使用 pyttsx3 库：
        self.engine.say(text)    
        self.engine.runAndWait()

            

def main():
    llm = LLMresponse()
    recognizer = voice()
    recognizer.recognize(llm)

if __name__ == "__main__":
    main()