"""GPSR语法解析器"""
import re
from pathlib import Path
import xml.etree.ElementTree as ET

class GPSRGrammarParser:
    """GPSR语法规则解析器"""
    
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.grammar_rules = {}
        self.load_grammars()
    
    def load_grammars(self):
        """加载语法规则"""
        grammar_files = [
            self.project_root / "grammars" / "GPSRGrammar.txt",
            self.project_root / "grammars" / "CommonRules.txt"
        ]
        
        for file_path in grammar_files:
            if file_path.exists():
                self.parse_grammar_file(file_path)
                print(f"✓ 加载语法文件: {file_path.name}")
    
    def parse_grammar_file(self, file_path):
        """解析语法文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        current_rule = None
        for line in lines:
            line = line.strip()
            if not line or line.startswith(';'):
                continue  # 跳过注释和空行
            
            # 匹配规则定义: $rule_name = value
            rule_match = re.match(r'^\$(\w+)\s*=\s*(.+)$', line)
            if rule_match:
                rule_name, rule_value = rule_match.groups()
                if rule_name not in self.grammar_rules:
                    self.grammar_rules[rule_name] = []
                self.grammar_rules[rule_name].append(rule_value)
                current_rule = rule_name
    
    def match_grammar(self, text, entities):
        """匹配语法规则"""
        words = text.split()
        matched_rules = []
        
        # GPSR动词词典
        gpsr_verbs = {
            'find': '$vbfind', 'locate': '$vbfind', 'look for': '$vbfind',
            'bring': '$vbbring', 'take': '$vbtake', 'get': '$vbtake',
            'guide': '$vbguide', 'escort': '$vbguide',
            'follow': '$vbfollow',
            'tell': '$vbspeak', 'say': '$vbspeak'
        }
        
        # 匹配动词
        for i, word in enumerate(words):
            if word in gpsr_verbs:
                matched_rules.append({
                    'word': word,
                    'rule': gpsr_verbs[word],
                    'position': i
                })
        
        return matched_rules
    
    def get_rule_definition(self, rule_name):
        """获取规则定义"""
        return self.grammar_rules.get(rule_name, [])
