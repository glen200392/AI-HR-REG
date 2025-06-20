"""
Graph Database Implementation for AI Talent Ecosystem
圖數據庫實現 - 用於組織關係和網絡分析
"""

from neo4j import GraphDatabase
from typing import List, Dict, Any, Optional, Tuple
import logging
from datetime import datetime
import json


class Neo4jGraphStore:
    """Neo4j圖數據庫實現"""
    
    def __init__(self, uri: str = "bolt://localhost:7687", 
                 username: str = "neo4j", password: str = "password"):
        self.logger = logging.getLogger(__name__)
        
        try:
            self.driver = GraphDatabase.driver(uri, auth=(username, password))
            self.driver.verify_connectivity()
            self.logger.info("Neo4j connection established successfully")
            
            # 初始化數據庫約束和索引
            self._setup_constraints()
            
        except Exception as e:
            self.logger.error(f"Failed to connect to Neo4j: {str(e)}")
            # 使用內存模擬圖數據庫作為後備方案
            self.driver = None
            self._init_memory_graph()
    
    def _init_memory_graph(self):
        """初始化內存圖數據庫（後備方案）"""
        self.memory_graph = {
            'nodes': {},
            'relationships': []
        }
        self.logger.info("Using in-memory graph store as fallback")
    
    def _setup_constraints(self):
        """設置數據庫約束和索引"""
        if not self.driver:
            return
            
        constraints = [
            "CREATE CONSTRAINT employee_id IF NOT EXISTS FOR (e:Employee) REQUIRE e.id IS UNIQUE",
            "CREATE CONSTRAINT team_id IF NOT EXISTS FOR (t:Team) REQUIRE t.id IS UNIQUE",
            "CREATE CONSTRAINT skill_id IF NOT EXISTS FOR (s:Skill) REQUIRE s.id IS UNIQUE",
            "CREATE CONSTRAINT role_id IF NOT EXISTS FOR (r:Role) REQUIRE r.id IS UNIQUE"
        ]
        
        with self.driver.session() as session:
            for constraint in constraints:
                try:
                    session.run(constraint)
                except Exception as e:
                    # 約束可能已存在，忽略錯誤
                    pass
    
    async def add_employee_node(self, employee_data: Dict[str, Any]) -> bool:
        """添加員工節點"""
        try:
            if self.driver:
                return await self._add_employee_neo4j(employee_data)
            else:
                return self._add_employee_memory(employee_data)
        except Exception as e:
            self.logger.error(f"Error adding employee node: {str(e)}")
            return False
    
    async def _add_employee_neo4j(self, employee_data: Dict[str, Any]) -> bool:
        """使用Neo4j添加員工節點"""
        query = """
        MERGE (e:Employee {id: $employee_id})
        SET e.name = $name,
            e.email = $email,
            e.department = $department,
            e.role = $role,
            e.hire_date = $hire_date,
            e.experience_years = $experience_years,
            e.performance_score = $performance_score,
            e.updated_at = datetime()
        RETURN e
        """
        
        with self.driver.session() as session:
            result = session.run(query, 
                employee_id=employee_data['id'],
                name=employee_data.get('name', ''),
                email=employee_data.get('email', ''),
                department=employee_data.get('department', ''),
                role=employee_data.get('role', ''),
                hire_date=employee_data.get('hire_date', ''),
                experience_years=employee_data.get('experience_years', 0),
                performance_score=employee_data.get('performance_score', 0.0)
            )
            return result.single() is not None
    
    def _add_employee_memory(self, employee_data: Dict[str, Any]) -> bool:
        """使用內存圖添加員工節點"""
        employee_id = employee_data['id']
        self.memory_graph['nodes'][employee_id] = {
            'type': 'Employee',
            'data': employee_data,
            'created_at': datetime.now().isoformat()
        }
        return True
    
    async def add_team_node(self, team_data: Dict[str, Any]) -> bool:
        """添加團隊節點"""
        try:
            if self.driver:
                return await self._add_team_neo4j(team_data)
            else:
                return self._add_team_memory(team_data)
        except Exception as e:
            self.logger.error(f"Error adding team node: {str(e)}")
            return False
    
    async def _add_team_neo4j(self, team_data: Dict[str, Any]) -> bool:
        """使用Neo4j添加團隊節點"""
        query = """
        MERGE (t:Team {id: $team_id})
        SET t.name = $name,
            t.description = $description,
            t.department = $department,
            t.size = $size,
            t.created_date = $created_date,
            t.updated_at = datetime()
        RETURN t
        """
        
        with self.driver.session() as session:
            result = session.run(query,
                team_id=team_data['id'],
                name=team_data.get('name', ''),
                description=team_data.get('description', ''),
                department=team_data.get('department', ''),
                size=team_data.get('size', 0),
                created_date=team_data.get('created_date', '')
            )
            return result.single() is not None
    
    def _add_team_memory(self, team_data: Dict[str, Any]) -> bool:
        """使用內存圖添加團隊節點"""
        team_id = team_data['id']
        self.memory_graph['nodes'][team_id] = {
            'type': 'Team',
            'data': team_data,
            'created_at': datetime.now().isoformat()
        }
        return True
    
    async def create_relationship(self, from_node_id: str, to_node_id: str, 
                                relationship_type: str, properties: Dict[str, Any] = None) -> bool:
        """創建節點關係"""
        try:
            if self.driver:
                return await self._create_relationship_neo4j(from_node_id, to_node_id, relationship_type, properties)
            else:
                return self._create_relationship_memory(from_node_id, to_node_id, relationship_type, properties)
        except Exception as e:
            self.logger.error(f"Error creating relationship: {str(e)}")
            return False
    
    async def _create_relationship_neo4j(self, from_node_id: str, to_node_id: str,
                                       relationship_type: str, properties: Dict[str, Any] = None) -> bool:
        """使用Neo4j創建關係"""
        query = f"""
        MATCH (a), (b)
        WHERE a.id = $from_id AND b.id = $to_id
        MERGE (a)-[r:{relationship_type}]->(b)
        SET r += $properties
        SET r.created_at = datetime()
        RETURN r
        """
        
        with self.driver.session() as session:
            result = session.run(query,
                from_id=from_node_id,
                to_id=to_node_id,
                properties=properties or {}
            )
            return result.single() is not None
    
    def _create_relationship_memory(self, from_node_id: str, to_node_id: str,
                                  relationship_type: str, properties: Dict[str, Any] = None) -> bool:
        """使用內存圖創建關係"""
        relationship = {
            'from': from_node_id,
            'to': to_node_id,
            'type': relationship_type,
            'properties': properties or {},
            'created_at': datetime.now().isoformat()
        }
        self.memory_graph['relationships'].append(relationship)
        return True
    
    async def get_employee_network(self, employee_id: str, depth: int = 2) -> Dict[str, Any]:
        """獲取員工關係網絡"""
        try:
            if self.driver:
                return await self._get_employee_network_neo4j(employee_id, depth)
            else:
                return self._get_employee_network_memory(employee_id, depth)
        except Exception as e:
            self.logger.error(f"Error getting employee network: {str(e)}")
            return {}
    
    async def _get_employee_network_neo4j(self, employee_id: str, depth: int) -> Dict[str, Any]:
        """使用Neo4j獲取員工網絡"""
        query = f"""
        MATCH path = (e:Employee {{id: $employee_id}})-[*1..{depth}]-(connected)
        RETURN e, connected, relationships(path) as rels
        """
        
        network = {'nodes': [], 'relationships': []}
        
        with self.driver.session() as session:
            result = session.run(query, employee_id=employee_id)
            
            for record in result:
                # 添加節點
                employee = record['e']
                connected = record['connected']
                
                network['nodes'].extend([
                    {'id': employee['id'], 'label': employee.get('name', ''), 'type': 'Employee'},
                    {'id': connected['id'], 'label': connected.get('name', ''), 'type': connected.labels[0]}
                ])
                
                # 添加關係
                rels = record['rels']
                for rel in rels:
                    network['relationships'].append({
                        'from': rel.start_node['id'],
                        'to': rel.end_node['id'],
                        'type': rel.type,
                        'properties': dict(rel)
                    })
        
        return network
    
    def _get_employee_network_memory(self, employee_id: str, depth: int) -> Dict[str, Any]:
        """使用內存圖獲取員工網絡"""
        network = {'nodes': [], 'relationships': []}
        visited = set()
        current_level = {employee_id}
        
        for level in range(depth + 1):
            if not current_level:
                break
                
            next_level = set()
            
            for node_id in current_level:
                if node_id in visited:
                    continue
                    
                visited.add(node_id)
                
                # 添加節點
                if node_id in self.memory_graph['nodes']:
                    node_data = self.memory_graph['nodes'][node_id]
                    network['nodes'].append({
                        'id': node_id,
                        'label': node_data['data'].get('name', node_id),
                        'type': node_data['type']
                    })
                
                # 查找相關關係
                for rel in self.memory_graph['relationships']:
                    if rel['from'] == node_id:
                        next_level.add(rel['to'])
                        network['relationships'].append(rel)
                    elif rel['to'] == node_id:
                        next_level.add(rel['from'])
                        if rel not in network['relationships']:
                            network['relationships'].append(rel)
            
            current_level = next_level
        
        return network
    
    async def analyze_team_dynamics(self, team_id: str) -> Dict[str, Any]:
        """分析團隊動態"""
        try:
            if self.driver:
                return await self._analyze_team_dynamics_neo4j(team_id)
            else:
                return self._analyze_team_dynamics_memory(team_id)
        except Exception as e:
            self.logger.error(f"Error analyzing team dynamics: {str(e)}")
            return {}
    
    async def _analyze_team_dynamics_neo4j(self, team_id: str) -> Dict[str, Any]:
        """使用Neo4j分析團隊動態"""
        queries = {
            'team_size': """
                MATCH (t:Team {id: $team_id})-[:HAS_MEMBER]->(e:Employee)
                RETURN count(e) as size
            """,
            'collaboration_strength': """
                MATCH (t:Team {id: $team_id})-[:HAS_MEMBER]->(e1:Employee)
                MATCH (e1)-[c:COLLABORATES_WITH]->(e2:Employee)
                MATCH (t)-[:HAS_MEMBER]->(e2)
                RETURN avg(c.strength) as avg_collaboration
            """,
            'skill_diversity': """
                MATCH (t:Team {id: $team_id})-[:HAS_MEMBER]->(e:Employee)-[:HAS_SKILL]->(s:Skill)
                RETURN count(DISTINCT s) as skill_count
            """
        }
        
        dynamics = {}
        
        with self.driver.session() as session:
            for metric, query in queries.items():
                result = session.run(query, team_id=team_id)
                record = result.single()
                if record:
                    dynamics[metric] = record[list(record.keys())[0]]
        
        return dynamics
    
    def _analyze_team_dynamics_memory(self, team_id: str) -> Dict[str, Any]:
        """使用內存圖分析團隊動態"""
        # 簡化的團隊動態分析
        team_members = []
        
        for rel in self.memory_graph['relationships']:
            if rel['from'] == team_id and rel['type'] == 'HAS_MEMBER':
                team_members.append(rel['to'])
        
        collaboration_count = 0
        for rel in self.memory_graph['relationships']:
            if (rel['from'] in team_members and rel['to'] in team_members and 
                rel['type'] == 'COLLABORATES_WITH'):
                collaboration_count += 1
        
        return {
            'team_size': len(team_members),
            'collaboration_density': collaboration_count / max(len(team_members), 1),
            'member_count': len(team_members)
        }
    
    async def find_skill_gaps(self, target_skills: List[str]) -> List[Dict[str, Any]]:
        """查找技能差距"""
        try:
            if self.driver:
                return await self._find_skill_gaps_neo4j(target_skills)
            else:
                return self._find_skill_gaps_memory(target_skills)
        except Exception as e:
            self.logger.error(f"Error finding skill gaps: {str(e)}")
            return []
    
    async def _find_skill_gaps_neo4j(self, target_skills: List[str]) -> List[Dict[str, Any]]:
        """使用Neo4j查找技能差距"""
        query = """
        UNWIND $skills as skill_name
        OPTIONAL MATCH (s:Skill {name: skill_name})<-[:HAS_SKILL]-(e:Employee)
        RETURN skill_name, count(e) as employee_count, collect(e.name) as employees
        """
        
        gaps = []
        
        with self.driver.session() as session:
            result = session.run(query, skills=target_skills)
            
            for record in result:
                gaps.append({
                    'skill': record['skill_name'],
                    'current_employee_count': record['employee_count'],
                    'employees_with_skill': record['employees'],
                    'gap_severity': 'high' if record['employee_count'] < 2 else 'medium' if record['employee_count'] < 5 else 'low'
                })
        
        return gaps
    
    def _find_skill_gaps_memory(self, target_skills: List[str]) -> List[Dict[str, Any]]:
        """使用內存圖查找技能差距"""
        gaps = []
        
        for skill in target_skills:
            employees_with_skill = []
            
            for rel in self.memory_graph['relationships']:
                if rel['type'] == 'HAS_SKILL' and rel['to'] == skill:
                    employees_with_skill.append(rel['from'])
            
            count = len(employees_with_skill)
            gaps.append({
                'skill': skill,
                'current_employee_count': count,
                'employees_with_skill': employees_with_skill,
                'gap_severity': 'high' if count < 2 else 'medium' if count < 5 else 'low'
            })
        
        return gaps
    
    async def get_graph_statistics(self) -> Dict[str, Any]:
        """獲取圖數據庫統計信息"""
        try:
            if self.driver:
                return await self._get_statistics_neo4j()
            else:
                return self._get_statistics_memory()
        except Exception as e:
            self.logger.error(f"Error getting graph statistics: {str(e)}")
            return {}
    
    async def _get_statistics_neo4j(self) -> Dict[str, Any]:
        """使用Neo4j獲取統計信息"""
        queries = {
            'employee_count': "MATCH (e:Employee) RETURN count(e) as count",
            'team_count': "MATCH (t:Team) RETURN count(t) as count",
            'skill_count': "MATCH (s:Skill) RETURN count(s) as count",
            'relationship_count': "MATCH ()-[r]->() RETURN count(r) as count"
        }
        
        stats = {}
        
        with self.driver.session() as session:
            for metric, query in queries.items():
                result = session.run(query)
                record = result.single()
                stats[metric] = record['count'] if record else 0
        
        return stats
    
    def _get_statistics_memory(self) -> Dict[str, Any]:
        """使用內存圖獲取統計信息"""
        node_types = {}
        for node_data in self.memory_graph['nodes'].values():
            node_type = node_data['type']
            node_types[node_type] = node_types.get(node_type, 0) + 1
        
        return {
            'employee_count': node_types.get('Employee', 0),
            'team_count': node_types.get('Team', 0),
            'skill_count': node_types.get('Skill', 0),
            'relationship_count': len(self.memory_graph['relationships']),
            'total_nodes': len(self.memory_graph['nodes'])
        }
    
    def close(self):
        """關閉數據庫連接"""
        if self.driver:
            self.driver.close()
            self.logger.info("Neo4j connection closed")