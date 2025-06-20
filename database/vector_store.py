"""
Vector Database Implementation for AI Talent Ecosystem
向量數據庫實現 - 用於語義搜索和相似性匹配
"""

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import logging
from sentence_transformers import SentenceTransformer
import json
from datetime import datetime


class ChromaVectorStore:
    """ChromaDB向量存儲實現"""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.logger = logging.getLogger(__name__)
        
        # 初始化ChromaDB客戶端
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # 初始化嵌入模型
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # 創建集合
        self.collections = {
            'employees': self._get_or_create_collection('employees'),
            'skills': self._get_or_create_collection('skills'), 
            'jobs': self._get_or_create_collection('jobs'),
            'knowledge': self._get_or_create_collection('knowledge'),
            'policies': self._get_or_create_collection('policies')
        }
        
        self.logger.info("ChromaVectorStore initialized successfully")
    
    def _get_or_create_collection(self, name: str):
        """獲取或創建集合"""
        try:
            return self.client.get_collection(name)
        except Exception:
            return self.client.create_collection(
                name=name,
                metadata={"description": f"Collection for {name} data"}
            )
    
    async def add_employee_profile(self, employee_id: str, profile_data: Dict[str, Any]) -> bool:
        """添加員工檔案"""
        try:
            # 構建文本表示
            text_representation = self._build_employee_text(profile_data)
            
            # 生成嵌入向量
            embedding = self.embedding_model.encode(text_representation).tolist()
            
            # 添加到向量數據庫
            self.collections['employees'].add(
                embeddings=[embedding],
                documents=[text_representation],
                metadatas=[{
                    'employee_id': employee_id,
                    'name': profile_data.get('name', ''),
                    'department': profile_data.get('department', ''),
                    'role': profile_data.get('role', ''),
                    'updated_at': datetime.now().isoformat(),
                    'skills': json.dumps(profile_data.get('skills', {})),
                    'experience_years': profile_data.get('experience_years', 0)
                }],
                ids=[employee_id]
            )
            
            self.logger.info(f"Added employee profile: {employee_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding employee profile {employee_id}: {str(e)}")
            return False
    
    async def search_similar_employees(self, query_profile: Dict[str, Any], 
                                     top_k: int = 5) -> List[Dict[str, Any]]:
        """搜索相似員工"""
        try:
            # 構建查詢文本
            query_text = self._build_employee_text(query_profile)
            
            # 生成查詢嵌入
            query_embedding = self.embedding_model.encode(query_text).tolist()
            
            # 執行相似性搜索
            results = self.collections['employees'].query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=['documents', 'metadatas', 'distances']
            )
            
            # 格式化結果
            similar_employees = []
            if results['ids'][0]:
                for i, employee_id in enumerate(results['ids'][0]):
                    similar_employees.append({
                        'employee_id': employee_id,
                        'similarity_score': 1 - results['distances'][0][i],  # 轉換為相似度
                        'metadata': results['metadatas'][0][i],
                        'profile_text': results['documents'][0][i]
                    })
            
            return similar_employees
            
        except Exception as e:
            self.logger.error(f"Error searching similar employees: {str(e)}")
            return []
    
    async def add_skill_profile(self, skill_id: str, skill_data: Dict[str, Any]) -> bool:
        """添加技能檔案"""
        try:
            text_representation = self._build_skill_text(skill_data)
            embedding = self.embedding_model.encode(text_representation).tolist()
            
            self.collections['skills'].add(
                embeddings=[embedding],
                documents=[text_representation],
                metadatas=[{
                    'skill_id': skill_id,
                    'name': skill_data.get('name', ''),
                    'category': skill_data.get('category', ''),
                    'difficulty': skill_data.get('difficulty', 'medium'),
                    'market_demand': skill_data.get('market_demand', 0.5),
                    'updated_at': datetime.now().isoformat()
                }],
                ids=[skill_id]
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding skill profile {skill_id}: {str(e)}")
            return False
    
    async def search_related_skills(self, skill_query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """搜索相關技能"""
        try:
            query_embedding = self.embedding_model.encode(skill_query).tolist()
            
            results = self.collections['skills'].query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=['documents', 'metadatas', 'distances']
            )
            
            related_skills = []
            if results['ids'][0]:
                for i, skill_id in enumerate(results['ids'][0]):
                    related_skills.append({
                        'skill_id': skill_id,
                        'relevance_score': 1 - results['distances'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'description': results['documents'][0][i]
                    })
            
            return related_skills
            
        except Exception as e:
            self.logger.error(f"Error searching related skills: {str(e)}")
            return []
    
    async def search_laws(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """搜索相關法規（為LegalAdvisorAgent提供）"""
        try:
            query_embedding = self.embedding_model.encode(query).tolist()
            
            results = self.collections['policies'].query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=['documents', 'metadatas', 'distances']
            )
            
            relevant_laws = []
            if results['ids'][0]:
                for i, policy_id in enumerate(results['ids'][0]):
                    relevant_laws.append({
                        'policy_id': policy_id,
                        'relevance_score': 1 - results['distances'][0][i],
                        'content': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i]
                    })
            
            return relevant_laws
            
        except Exception as e:
            self.logger.error(f"Error searching laws: {str(e)}")
            return []
    
    def _build_employee_text(self, profile_data: Dict[str, Any]) -> str:
        """構建員工檔案的文本表示"""
        parts = []
        
        # 基本信息
        if 'name' in profile_data:
            parts.append(f"Name: {profile_data['name']}")
        if 'role' in profile_data:
            parts.append(f"Role: {profile_data['role']}")
        if 'department' in profile_data:
            parts.append(f"Department: {profile_data['department']}")
        
        # 技能
        if 'skills' in profile_data:
            skills_text = []
            for skill, level in profile_data['skills'].items():
                skills_text.append(f"{skill} (level: {level})")
            parts.append(f"Skills: {', '.join(skills_text)}")
        
        # 經驗
        if 'experience_years' in profile_data:
            parts.append(f"Experience: {profile_data['experience_years']} years")
        
        # 興趣和目標
        if 'interests' in profile_data:
            parts.append(f"Interests: {', '.join(profile_data['interests'])}")
        if 'career_goals' in profile_data:
            parts.append(f"Career Goals: {', '.join(profile_data['career_goals'])}")
        
        return ". ".join(parts)
    
    def _build_skill_text(self, skill_data: Dict[str, Any]) -> str:
        """構建技能檔案的文本表示"""
        parts = []
        
        if 'name' in skill_data:
            parts.append(f"Skill: {skill_data['name']}")
        if 'category' in skill_data:
            parts.append(f"Category: {skill_data['category']}")
        if 'description' in skill_data:
            parts.append(f"Description: {skill_data['description']}")
        if 'related_skills' in skill_data:
            parts.append(f"Related: {', '.join(skill_data['related_skills'])}")
        if 'learning_resources' in skill_data:
            parts.append(f"Resources: {', '.join(skill_data['learning_resources'])}")
        
        return ". ".join(parts)
    
    async def get_collection_stats(self) -> Dict[str, int]:
        """獲取集合統計信息"""
        stats = {}
        for name, collection in self.collections.items():
            try:
                count = collection.count()
                stats[name] = count
            except Exception as e:
                self.logger.error(f"Error getting stats for {name}: {str(e)}")
                stats[name] = 0
        
        return stats
    
    async def delete_employee_profile(self, employee_id: str) -> bool:
        """刪除員工檔案"""
        try:
            self.collections['employees'].delete(ids=[employee_id])
            self.logger.info(f"Deleted employee profile: {employee_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error deleting employee profile {employee_id}: {str(e)}")
            return False
    
    async def update_employee_profile(self, employee_id: str, profile_data: Dict[str, Any]) -> bool:
        """更新員工檔案"""
        # 先刪除舊檔案，再添加新檔案
        await self.delete_employee_profile(employee_id)
        return await self.add_employee_profile(employee_id, profile_data)