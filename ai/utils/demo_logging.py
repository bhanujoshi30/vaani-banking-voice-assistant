"""
Demo-friendly logging utilities for AI backend
Designed for clear visibility during video recordings
"""
import logging
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional
import json


class DemoLogger:
    """Enhanced logger with clean structured output for demos"""
    
    # ANSI color codes for terminal output
    COLORS = {
        'RESET': '\033[0m',
        'BOLD': '\033[1m',
        'DIM': '\033[2m',
        'BLUE': '\033[94m',
        'GREEN': '\033[92m',
        'YELLOW': '\033[93m',
        'RED': '\033[91m',
        'CYAN': '\033[96m',
        'MAGENTA': '\033[95m',
    }
    
    def __init__(self, name: str = "demo"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Remove existing handlers
        self.logger.handlers.clear()
        
        # Create console handler with custom formatter
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def _format_timestamp(self) -> str:
        """Format timestamp for display"""
        return datetime.now().strftime("%H:%M:%S.%f")[:-3]
    
    def chat_request(self, user_id: str, session_id: str, message: str, **kwargs):
        """Log chat request"""
        timestamp = self._format_timestamp()
        self.logger.info(f"{self.COLORS['BLUE']}{self.COLORS['BOLD']}[CHAT REQUEST] {timestamp}{self.COLORS['RESET']}")
        message_preview = message[:70] + "..." if len(message) > 70 else message
        self.logger.info(f"{self.COLORS['BLUE']}  User Message: {message_preview}{self.COLORS['RESET']}")
        self.logger.info(f"{self.COLORS['BLUE']}  User ID: {user_id}{self.COLORS['RESET']}")
        self.logger.info(f"{self.COLORS['BLUE']}  Session: {session_id[:20]}{self.COLORS['RESET']}")
        
        for key, value in kwargs.items():
            if value is not None:
                display_value = str(value)
                if len(display_value) > 60:
                    display_value = display_value[:57] + "..."
                self.logger.info(f"{self.COLORS['BLUE']}  {key}: {display_value}{self.COLORS['RESET']}")
    
    def state_transition(self, from_state: str, to_state: str, reason: Optional[str] = None):
        """Log state transition"""
        timestamp = self._format_timestamp()
        self.logger.info(f"{self.COLORS['MAGENTA']}{self.COLORS['BOLD']}[STATE TRANSITION] {timestamp}{self.COLORS['RESET']}")
        self.logger.info(f"{self.COLORS['MAGENTA']}  {from_state} -> {to_state}{self.COLORS['RESET']}")
        if reason:
            self.logger.info(f"{self.COLORS['MAGENTA']}  Reason: {reason}{self.COLORS['RESET']}")
    
    def rag_retrieval(self, query: str, collection: str, k: int, **kwargs):
        """Log RAG retrieval operation"""
        timestamp = self._format_timestamp()
        self.logger.info(f"{self.COLORS['CYAN']}{self.COLORS['BOLD']}[RAG RETRIEVAL] {timestamp}{self.COLORS['RESET']}")
        
        query_preview = query[:70] + "..." if len(query) > 70 else query
        self.logger.info(f"{self.COLORS['CYAN']}  Query: {query_preview}{self.COLORS['RESET']}")
        self.logger.info(f"{self.COLORS['CYAN']}  Collection: {collection}{self.COLORS['RESET']}")
        self.logger.info(f"{self.COLORS['CYAN']}  Top-K: {k}{self.COLORS['RESET']}")
        
        for key, value in kwargs.items():
            if value is not None:
                display_value = str(value)
                if len(display_value) > 60:
                    display_value = display_value[:57] + "..."
                self.logger.info(f"{self.COLORS['CYAN']}  {key}: {display_value}{self.COLORS['RESET']}")
    
    def rag_results(self, documents: list, scores: Optional[list] = None):
        """Log RAG retrieval results"""
        self.logger.info(f"{self.COLORS['CYAN']}{self.COLORS['BOLD']}[RAG RESULTS] Documents Found: {len(documents)}{self.COLORS['RESET']}")
        
        for i, doc in enumerate(documents[:5], 1):  # Show top 5
            source = doc.metadata.get("source", "Unknown")
            doc_type = doc.metadata.get("document_type", "unknown")
            loan_type = doc.metadata.get("loan_type", "")
            scheme_type = doc.metadata.get("scheme_type", "")
            
            type_label = scheme_type or loan_type or doc_type
            if type_label:
                type_label = type_label.replace("_", " ").title()
            
            score_str = f"{scores[i-1]:.3f}" if scores and i <= len(scores) else None
            
            self.logger.info(f"{self.COLORS['CYAN']}  [{i}] {type_label}{self.COLORS['RESET']}")
            self.logger.info(f"{self.COLORS['CYAN']}      Source: {source}{self.COLORS['RESET']}")
            if score_str:
                self.logger.info(f"{self.COLORS['CYAN']}      Score: {score_str}{self.COLORS['RESET']}")
            
            # Show content preview
            content_preview = doc.page_content[:60].replace("\n", " ")
            if len(doc.page_content) > 60:
                content_preview += "..."
            self.logger.info(f"{self.COLORS['CYAN']}      Preview: {content_preview}{self.COLORS['RESET']}")
        
        if len(documents) > 5:
            self.logger.info(f"{self.COLORS['CYAN']}  ... and {len(documents) - 5} more documents{self.COLORS['RESET']}")
    
    def agent_decision(self, agent_name: str, intent: str, confidence: Optional[float] = None, **kwargs):
        """Log agent routing decision"""
        timestamp = self._format_timestamp()
        self.logger.info(f"{self.COLORS['YELLOW']}{self.COLORS['BOLD']}[AGENT ROUTING] {timestamp}{self.COLORS['RESET']}")
        
        self.logger.info(f"{self.COLORS['YELLOW']}  Selected Agent: {agent_name}{self.COLORS['RESET']}")
        self.logger.info(f"{self.COLORS['YELLOW']}  Detected Intent: {intent}{self.COLORS['RESET']}")
        
        if confidence is not None:
            conf_color = 'GREEN' if confidence > 0.7 else 'YELLOW' if confidence > 0.5 else 'RED'
            self.logger.info(f"{self.COLORS['YELLOW']}  Confidence: {self.COLORS[conf_color]}{confidence:.2%}{self.COLORS['RESET']}")
        
        for key, value in kwargs.items():
            if value is not None:
                display_value = str(value)
                if len(display_value) > 60:
                    display_value = display_value[:57] + "..."
                self.logger.info(f"{self.COLORS['YELLOW']}  {key}: {display_value}{self.COLORS['RESET']}")
    
    def data_processing(self, operation: str, input_data: Any, output_data: Any = None, **kwargs):
        """Log data processing step"""
        timestamp = self._format_timestamp()
        self.logger.info(f"{self.COLORS['MAGENTA']}{self.COLORS['BOLD']}[DATA PROCESSING] {timestamp}{self.COLORS['RESET']}")
        self.logger.info(f"{self.COLORS['MAGENTA']}  Operation: {operation}{self.COLORS['RESET']}")
        
        input_str = str(input_data)
        if len(input_str) > 70:
            input_str = input_str[:67] + "..."
        self.logger.info(f"{self.COLORS['MAGENTA']}  Input: {input_str}{self.COLORS['RESET']}")
        
        if output_data is not None:
            output_str = str(output_data)
            if len(output_str) > 70:
                output_str = output_str[:67] + "..."
            self.logger.info(f"{self.COLORS['MAGENTA']}  Output: {output_str}{self.COLORS['RESET']}")
        
        for key, value in kwargs.items():
            if value is not None:
                display_value = str(value)
                if len(display_value) > 60:
                    display_value = display_value[:57] + "..."
                self.logger.info(f"{self.COLORS['MAGENTA']}  {key}: {display_value}{self.COLORS['RESET']}")
    
    def llm_call(self, model: str, prompt_length: int, response_length: int, 
                  tokens: int = 0, duration_ms: float = 0):
        """Log LLM API call"""
        timestamp = self._format_timestamp()
        self.logger.info(f"{self.COLORS['GREEN']}{self.COLORS['BOLD']}[LLM CALL] {timestamp}{self.COLORS['RESET']}")
        
        self.logger.info(f"{self.COLORS['GREEN']}  Model: {model}{self.COLORS['RESET']}")
        self.logger.info(f"{self.COLORS['GREEN']}  Prompt Length: {prompt_length} chars{self.COLORS['RESET']}")
        self.logger.info(f"{self.COLORS['GREEN']}  Response Length: {response_length} chars{self.COLORS['RESET']}")
        
        if tokens > 0:
            self.logger.info(f"{self.COLORS['GREEN']}  Tokens Used: {tokens}{self.COLORS['RESET']}")
        
        if duration_ms > 0:
            self.logger.info(f"{self.COLORS['GREEN']}  Duration: {duration_ms:.2f}ms{self.COLORS['RESET']}")
    
    def tool_execution(self, tool_name: str, success: bool, duration_ms: float = 0, 
                      result: Any = None, error: Optional[str] = None):
        """Log tool execution"""
        timestamp = self._format_timestamp()
        status_color = 'GREEN' if success else 'RED'
        status_text = "SUCCESS" if success else "FAILED"
        
        self.logger.info(f"{self.COLORS[status_color]}{self.COLORS['BOLD']}[TOOL EXECUTION] {timestamp}{self.COLORS['RESET']}")
        self.logger.info(f"{self.COLORS[status_color]}  Tool: {tool_name}{self.COLORS['RESET']}")
        self.logger.info(f"{self.COLORS[status_color]}  Status: {status_text}{self.COLORS['RESET']}")
        
        if duration_ms > 0:
            self.logger.info(f"{self.COLORS[status_color]}  Duration: {duration_ms:.2f}ms{self.COLORS['RESET']}")
        
        if result is not None:
            result_str = str(result)
            if len(result_str) > 70:
                result_str = result_str[:67] + "..."
            self.logger.info(f"{self.COLORS[status_color]}  Result: {result_str}{self.COLORS['RESET']}")
        
        if error:
            error_str = str(error)
            if len(error_str) > 70:
                error_str = error_str[:67] + "..."
            self.logger.info(f"{self.COLORS['RED']}  Error: {error_str}{self.COLORS['RESET']}")
    
    def ai_response(self, response: str, agent: str, language: str):
        """Log AI response"""
        timestamp = self._format_timestamp()
        self.logger.info(f"{self.COLORS['GREEN']}{self.COLORS['BOLD']}[AI RESPONSE] {timestamp}{self.COLORS['RESET']}")
        
        self.logger.info(f"{self.COLORS['GREEN']}  Agent: {agent}{self.COLORS['RESET']}")
        self.logger.info(f"{self.COLORS['GREEN']}  Language: {language}{self.COLORS['RESET']}")
        
        response_preview = response[:70] + "..." if len(response) > 70 else response
        self.logger.info(f"{self.COLORS['GREEN']}  Response: {response_preview}{self.COLORS['RESET']}")
    
    def info(self, message: str, **kwargs):
        """Standard info log"""
        self.logger.info(f"[INFO] {message} {json.dumps(kwargs) if kwargs else ''}")
    
    def error(self, message: str, **kwargs):
        """Error log"""
        timestamp = self._format_timestamp()
        self.logger.error(f"{self.COLORS['RED']}{self.COLORS['BOLD']}[ERROR] {timestamp} | {message}{self.COLORS['RESET']}")
        if kwargs:
            for key, value in kwargs.items():
                self.logger.error(f"{self.COLORS['RED']}  {key}: {value}{self.COLORS['RESET']}")


# Global demo logger instance
demo_logger = DemoLogger("demo")
