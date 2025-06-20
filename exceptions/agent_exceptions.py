"""
Agent-specific Exception Classes
智能代理專用異常類
"""

from typing import Dict, Any, Optional, List
from .base_exceptions import TalentEcosystemException


class AgentAnalysisError(TalentEcosystemException):
    """代理分析錯誤基類"""
    
    def __init__(
        self,
        message: str = "代理分析過程中發生錯誤",
        agent_name: Optional[str] = None,
        analysis_type: Optional[str] = None,
        input_data: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if agent_name:
            details['agent_name'] = agent_name
        if analysis_type:
            details['analysis_type'] = analysis_type
        if input_data:
            details['input_data_keys'] = list(input_data.keys())
        
        super().__init__(message, details=details, **kwargs)
        self.agent_name = agent_name
        self.analysis_type = analysis_type
        self.input_data = input_data


class AgentCommunicationError(TalentEcosystemException):
    """代理間通信錯誤"""
    
    def __init__(
        self,
        message: str = "代理間通信失敗",
        source_agent: Optional[str] = None,
        target_agent: Optional[str] = None,
        communication_type: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if source_agent:
            details['source_agent'] = source_agent
        if target_agent:
            details['target_agent'] = target_agent
        if communication_type:
            details['communication_type'] = communication_type
        
        super().__init__(message, details=details, **kwargs)
        self.source_agent = source_agent
        self.target_agent = target_agent
        self.communication_type = communication_type


class AgentTimeoutError(TalentEcosystemException):
    """代理執行超時錯誤"""
    
    def __init__(
        self,
        message: str = "代理執行超時",
        agent_name: Optional[str] = None,
        operation: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if agent_name:
            details['agent_name'] = agent_name
        if operation:
            details['operation'] = operation
        if timeout_seconds:
            details['timeout_seconds'] = timeout_seconds
        
        super().__init__(message, details=details, **kwargs)
        self.agent_name = agent_name
        self.operation = operation
        self.timeout_seconds = timeout_seconds


class AgentValidationError(TalentEcosystemException):
    """代理輸入驗證錯誤"""
    
    def __init__(
        self,
        message: str = "代理輸入數據驗證失敗",
        agent_name: Optional[str] = None,
        invalid_fields: Optional[List[str]] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if agent_name:
            details['agent_name'] = agent_name
        if invalid_fields:
            details['invalid_fields'] = invalid_fields
        
        super().__init__(message, details=details, **kwargs)
        self.agent_name = agent_name
        self.invalid_fields = invalid_fields or []


class BrainAgentError(AgentAnalysisError):
    """Brain Agent專用錯誤"""
    
    def __init__(
        self,
        message: str = "認知智能體分析錯誤",
        cognitive_process: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if cognitive_process:
            details['cognitive_process'] = cognitive_process
        
        super().__init__(
            message=message,
            agent_name="BrainAgent",
            details=details,
            **kwargs
        )
        self.cognitive_process = cognitive_process


class TalentAgentError(AgentAnalysisError):
    """Talent Agent專用錯誤"""
    
    def __init__(
        self,
        message: str = "人才智能體分析錯誤",
        talent_process: Optional[str] = None,
        employee_id: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if talent_process:
            details['talent_process'] = talent_process
        if employee_id:
            details['employee_id'] = employee_id
        
        super().__init__(
            message=message,
            agent_name="TalentAgent",
            details=details,
            **kwargs
        )
        self.talent_process = talent_process
        self.employee_id = employee_id


class CultureAgentError(AgentAnalysisError):
    """Culture Agent專用錯誤"""
    
    def __init__(
        self,
        message: str = "文化智能體分析錯誤",
        culture_dimension: Optional[str] = None,
        team_id: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if culture_dimension:
            details['culture_dimension'] = culture_dimension
        if team_id:
            details['team_id'] = team_id
        
        super().__init__(
            message=message,
            agent_name="CultureAgent",
            details=details,
            **kwargs
        )
        self.culture_dimension = culture_dimension
        self.team_id = team_id


class FutureAgentError(AgentAnalysisError):
    """Future Agent專用錯誤"""
    
    def __init__(
        self,
        message: str = "未來智能體預測錯誤",
        prediction_type: Optional[str] = None,
        time_horizon: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if prediction_type:
            details['prediction_type'] = prediction_type
        if time_horizon:
            details['time_horizon'] = time_horizon
        
        super().__init__(
            message=message,
            agent_name="FutureAgent",
            details=details,
            **kwargs
        )
        self.prediction_type = prediction_type
        self.time_horizon = time_horizon


class ProcessAgentError(AgentAnalysisError):
    """Process Agent專用錯誤"""
    
    def __init__(
        self,
        message: str = "流程智能體優化錯誤",
        process_type: Optional[str] = None,
        optimization_target: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if process_type:
            details['process_type'] = process_type
        if optimization_target:
            details['optimization_target'] = optimization_target
        
        super().__init__(
            message=message,
            agent_name="ProcessAgent",
            details=details,
            **kwargs
        )
        self.process_type = process_type
        self.optimization_target = optimization_target


class OrchestratorError(TalentEcosystemException):
    """Master Orchestrator專用錯誤"""
    
    def __init__(
        self,
        message: str = "主協調器執行錯誤",
        orchestration_phase: Optional[str] = None,
        failed_agents: Optional[List[str]] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if orchestration_phase:
            details['orchestration_phase'] = orchestration_phase
        if failed_agents:
            details['failed_agents'] = failed_agents
        
        super().__init__(message, details=details, **kwargs)
        self.orchestration_phase = orchestration_phase
        self.failed_agents = failed_agents or []


class AgentInitializationError(TalentEcosystemException):
    """代理初始化錯誤"""
    
    def __init__(
        self,
        message: str = "代理初始化失敗",
        agent_name: Optional[str] = None,
        missing_dependencies: Optional[List[str]] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if agent_name:
            details['agent_name'] = agent_name
        if missing_dependencies:
            details['missing_dependencies'] = missing_dependencies
        
        super().__init__(message, details=details, **kwargs)
        self.agent_name = agent_name
        self.missing_dependencies = missing_dependencies or []


class AgentConfigurationError(TalentEcosystemException):
    """代理配置錯誤"""
    
    def __init__(
        self,
        message: str = "代理配置錯誤",
        agent_name: Optional[str] = None,
        config_issue: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if agent_name:
            details['agent_name'] = agent_name
        if config_issue:
            details['config_issue'] = config_issue
        
        super().__init__(message, details=details, **kwargs)
        self.agent_name = agent_name
        self.config_issue = config_issue


class LLMIntegrationError(TalentEcosystemException):
    """LLM集成錯誤"""
    
    def __init__(
        self,
        message: str = "LLM服務集成錯誤",
        llm_provider: Optional[str] = None,
        error_type: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if llm_provider:
            details['llm_provider'] = llm_provider
        if error_type:
            details['error_type'] = error_type
        
        super().__init__(message, details=details, **kwargs)
        self.llm_provider = llm_provider
        self.error_type = error_type