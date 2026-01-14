#!/usr/bin/env python3
"""
GPU加速的高精度实时语音识别
"""

import argparse
import torch
import pyaudio
import numpy as np
from faster_whisper import WhisperModel
import noisereduce as nr
import time
import warnings
warnings.filterwarnings("ignore")

class HighAccuracyRealtimeASR:
    def __init__(self, args):
        # 设备配置
        self.device = "cuda" if torch.cuda.is_available() and args.use_gpu else "cpu"
        self.compute_type = "float16" if self.device == "cuda" else "int8"
        
        print(f"\n{'='*60}")
        print("高精度实时语音识别系统")
        print(f"{'='*60}")
        print(f"设备: {self.device.upper()}")
        print(f"模型: {args.model_size}")
        print(f"语言: {args.language}")
        print(f"计算类型: {self.compute_type}")
        
        # 加载模型（显示进度）
        print("正在加载模型，请稍候...")
        self.model = WhisperModel(
            model_size_or_path=args.model_size,
            device=self.device,
            compute_type=self.compute_type,
            download_root="./models",  # 模型下载目录
            local_files_only=False
        )
        
        # 音频配置
        self.sample_rate = 16000
        self.chunk_duration = 0.03  # 30ms
        self.chunk_size = int(self.sample_rate * self.chunk_duration)
        
        # 识别参数
        self.language = args.language
        self.beam_size = args.beam_size
        self.vad_threshold = args.vad_threshold
        
        # 状态
        self.is_running = False
        self.audio_buffer = []
        
        print("模型加载完成！")
        print(f"{'='*60}\n")
    
    def preprocess_audio(self, audio_data):
        """音频预处理"""
        # 转换为float32
        audio_np = np.frombuffer(audio_data, dtype=np.int16)
        audio_float = audio_np.astype(np.float32) / 32768.0
        
        # 降噪处理
        if len(audio_float) > 1000:  # 确保有足够的数据
            try:
                audio_float = nr.reduce_noise(
                    y=audio_float,
                    sr=self.sample_rate,
                    stationary=True,
                    prop_decrease=0.7
                )
            except:
                pass
        
        return audio_float
    
    def transcribe_audio(self, audio_float):
        """转录音频"""
        try:
            # 使用优化的参数
            segments, info = self.model.transcribe(
                audio_float,
                language=self.language,
                beam_size=self.beam_size,
                best_of=5,
                temperature=0,
                vad_filter=True,
                vad_parameters={
                    "min_silence_duration_ms": 400,
                    "threshold": self.vad_threshold,
                    "speech_pad_ms": 300,
                },
                word_timestamps=False,  # 关闭以加速
                suppress_tokens=[-1],  # 抑制特定token
                without_timestamps=True,  # 不生成时间戳以加速
                max_initial_timestamp=1.0,
                condition_on_previous_text=False,
                compression_ratio_threshold=2.2,
                logprob_threshold=-0.8,
                no_speech_threshold=0.5,
            )
            
            # 收集结果
            texts = []
            for segment in segments:
                if segment.text.strip():
                    texts.append(segment.text.strip())
            
            return " ".join(texts)
            
        except Exception as e:
            print(f"转录错误: {e}")
            return ""
    
    def start(self):
        """开始实时识别"""
        self.is_running = True
        
        # 初始化音频输入
        p = pyaudio.PyAudio()
        
        # 列出可用设备
        print("可用音频输入设备:")
        for i in range(p.get_device_count()):
            dev_info = p.get_device_info_by_index(i)
            if dev_info['maxInputChannels'] > 0:
                print(f"  {i}: {dev_info['name']}")
        
        # 打开音频流
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size,
            input_device_index=None  # 默认设备
        )
        
        print("\n开始录音... (按 Ctrl+C 停止)")
        print("等待语音输入...\n")
        
        # 语音活动检测状态
        speech_buffer = []
        in_speech = False
        speech_start_time = None
        
        try:
            while self.is_running:
                # 读取音频数据
                data = stream.read(self.chunk_size, exception_on_overflow=False)
                
                # 简单能量检测（VAD）
                audio_chunk = np.frombuffer(data, dtype=np.int16)
                energy = np.sqrt(np.mean(audio_chunk**2))
                
                if energy > 100:  # 能量阈值
                    if not in_speech:
                        in_speech = True
                        speech_start_time = time.time()
                        speech_buffer = []
                        print("🔊 检测到语音...")
                    
                    speech_buffer.append(data)
                    
                    # 如果持续说话超过1秒，开始识别
                    if in_speech and len(speech_buffer) * self.chunk_duration >= 1.0:
                        # 拼接音频
                        audio_data = b''.join(speech_buffer)
                        
                        # 预处理
                        audio_processed = self.preprocess_audio(audio_data)
                        
                        # 转录
                        if len(audio_processed) > self.sample_rate * 0.5:  # 至少0.5秒
                            start_time = time.time()
                            text = self.transcribe_audio(audio_processed)
                            inference_time = time.time() - start_time
                            
                            if text:
                                print(f"\n[{time.strftime('%H:%M:%S')}] {text}")
                                print(f"识别耗时: {inference_time:.2f}s")
                                print("-" * 50)
                            
                            # 保留最后0.3秒的音频用于连续识别
                            keep_chunks = int(0.3 / self.chunk_duration)
                            speech_buffer = speech_buffer[-keep_chunks:] if len(speech_buffer) > keep_chunks else []
                
                else:
                    if in_speech:
                        # 静音超过0.5秒，结束当前语音段
                        if time.time() - speech_start_time > 0.5:
                            in_speech = False
                            if speech_buffer:
                                # 处理剩余音频
                                audio_data = b''.join(speech_buffer)
                                audio_processed = self.preprocess_audio(audio_data)
                                
                                if len(audio_processed) > self.sample_rate * 0.3:
                                    text = self.transcribe_audio(audio_processed)
                                    if text:
                                        print(f"\n[{time.strftime('%H:%M:%S')}] {text}")
                                        print("-" * 50)
                                
                                speech_buffer = []
                            print("等待语音输入...")
        
        except KeyboardInterrupt:
            print("\n停止录音...")
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()
            self.is_running = False
            print("系统已停止")

def main():
    parser = argparse.ArgumentParser(description="GPU加速高精度实时语音识别")
    parser.add_argument("--model-size", default="small",
                       choices=["tiny", "base", "small", "medium", "large", "large-v2", "large-v3"],
                       help="模型大小（越大越准确）")
    parser.add_argument("--language", default="zh",
                       help="识别语言，如 zh, en, ja, ko")
    parser.add_argument("--beam-size", type=int, default=5,
                       help="束搜索大小（越大越准确但越慢）")
    parser.add_argument("--vad-threshold", type=float, default=0.5,
                       help="VAD阈值（0-1，越小越敏感）")
    parser.add_argument("--use-gpu", action="store_true", default=True,
                       help="使用GPU加速")
    
    args = parser.parse_args()
    
    # 显示系统信息
    print("系统信息:")
    print(f"  PyTorch版本: {torch.__version__}")
    print(f"  CUDA可用: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"  GPU: {torch.cuda.get_device_name(0)}")
        print(f"  CUDA版本: {torch.version.cuda}")
    
    # 创建并启动ASR
    asr = HighAccuracyRealtimeASR(args)
    asr.start()

if __name__ == "__main__":
    main()