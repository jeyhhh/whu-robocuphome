"""GPSR实体匹配器"""
import re
from pathlib import Path
import xml.etree.ElementTree as ET

class EntityMatcher:
    """GPSR实体识别和匹配器"""
    
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.objects = self.load_entities("data/Objects.xml", "object")
        self.locations = self.load_entities("data/Locations.xml", "location")
        self.names = self.load_entities("data/Names.xml", "name")
    
    def load_entities(self, file_path, entity_type):
        """从XML文件加载实体"""
        entities = []
        full_path = self.project_root / file_path
        
        if not full_path.exists():
            print(f"⚠ 文件不存在: {full_path}")
            return entities
        
        try:
            tree = ET.parse(full_path)
            root = tree.getroot()
            
            if entity_type == "object":
                # 解析Objects.xml
                for category in root.findall('category'):
                    for obj in category.findall('object'):
                        name = obj.get('name')
                        if name:
                            entities.append(name.lower())
            
            elif entity_type == "location":
                # 解析Locations.xml
                for room in root.findall('room'):
                    room_name = room.get('name')
                    if room_name:
                        entities.append(room_name.lower())
                    for location in room.findall('location'):
                        loc_name = location.get('name')
                        if loc_name:
                            entities.append(loc_name.lower())
            
            elif entity_type == "name":
                # 解析Names.xml
                for name_elem in root.findall('name'):
                    name = name_elem.text
                    if name:
                        entities.append(name.lower())
        
        except Exception as e:
            print(f"❌ 解析{entity_type}文件失败: {e}")
        
        return entities
    
    def extract_entities(self, text):
        """从文本中提取实体"""
        entities = {
            'objects': [],
            'locations': [],
            'persons': [],
            'rooms': [],
            'beacons': []
        }
        
        words = text.split()
        
        # 匹配物体
        for obj in self.objects:
            if obj in text:
                entities['objects'].append(obj)
        
        # 匹配位置
        for loc in self.locations:
            if loc in text:
                entities['locations'].append(loc)
        
        # 匹配人名
        for name in self.names:
            if name in text:
                entities['persons'].append(name)
        
        return entities
    
    def fuzzy_match(self, word, entity_list, threshold=0.8):
        """模糊匹配实体"""
        # 简单的编辑距离匹配实现
        from difflib import SequenceMatcher
        
        best_match = None
        best_score = 0
        
        for entity in entity_list:
            score = SequenceMatcher(None, word, entity).ratio()
            if score > best_score and score >= threshold:
                best_score = score
                best_match = entity
        
        return best_match if best_match else word
