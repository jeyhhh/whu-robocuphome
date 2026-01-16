"""GPSR语音识别与命令生成主程序"""
import os
import re
from pathlib import Path
from grammar_parser import GPSRGrammarParser
from entity_matcher import EntityMatcher

class GPSRVoiceProcessor:
    """GPSR语音处理主类"""
    
    def __init__(self, project_root="."):
        self.project_root = Path(project_root)
        self.grammar_parser = GPSRGrammarParser(self.project_root)
        self.entity_matcher = EntityMatcher(self.project_root)
        
    def process_speech(self, speech_text):
        """处理语音识别结果"""
        # 1. 预处理文本
        cleaned_text = self.preprocess_text(speech_text)
        print(f"预处理后: {cleaned_text}")
        
        # 2. 实体识别
        entities = self.entity_matcher.extract_entities(cleaned_text)
        print(f"识别实体: {entities}")
        
        # 3. 语法匹配
        matched_rules = self.grammar_parser.match_grammar(cleaned_text, entities)
        print(f"匹配规则: {matched_rules}")
        
        # 4. 生成GPSR命令
        gpsr_command = self.generate_gpsr_command(matched_rules, entities)
        
        return {
            "original_text": speech_text,
            "cleaned_text": cleaned_text,
            "entities": entities,
            "matched_rules": matched_rules,
            "gpsr_command": gpsr_command
        }
    
    def preprocess_text(self, text):
        """预处理语音文本"""
        # 转换为小写
        text = text.lower()
        # 去除标点符号
        text = re.sub(r'[^\w\s]', '', text)
        # 去除多余空格
        text = ' '.join(text.split())
        return text
    
    def generate_gpsr_command(self, matched_rules, entities):
        """生成GPSR命令"""
        # 这里实现命令生成逻辑
        if matched_rules and entities:
            return "生成的GPSR命令示例"
        return "无法生成有效命令"

def main():
    """主函数"""
    processor = GPSRVoiceProcessor()
    
    # 测试示例
    test_sentences = [
        "请去厨房拿一个杯子",
        "找到客厅里的人",
        "引导张三到卧室",
        "告诉我桌子上有多少个苹果"
    ]
    
    for sentence in test_sentences:
        print(f"\n测试句子: {sentence}")
        result = processor.process_speech(sentence)
        print(f"处理结果: {result['gpsr_command']}")

if __name__ == "__main__":
    main()
