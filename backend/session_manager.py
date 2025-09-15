import redis
import json
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SessionManager:
    def __init__(self):
        self.config = Config()
        self.redis_client = None
        self._initialize_redis()
    
    def _initialize_redis(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.from_url(
                self.config.REDIS_URL,
                password=self.config.REDIS_PASSWORD if self.config.REDIS_PASSWORD else None,
                decode_responses=True
            )
            
            # Test connection
            self.redis_client.ping()
            logger.info("Redis connection established")
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            # Create a mock Redis client for development
            self.redis_client = MockRedisClient()
    
    async def create_session(self, session_id: str) -> bool:
        """Create a new chat session"""
        try:
            session_data = {
                "session_id": session_id,
                "created_at": datetime.now().isoformat(),
                "last_activity": datetime.now().isoformat(),
                "messages": []
            }
            
            # Store session data
            self.redis_client.setex(
                f"session:{session_id}",
                self.config.SESSION_TTL,
                json.dumps(session_data)
            )
            
            # Add to sessions list
            self.redis_client.sadd("sessions", session_id)
            
            logger.info(f"Created session: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating session {session_id}: {str(e)}")
            return False
    
    async def add_message(self, session_id: str, role: str, content: str) -> bool:
        """Add a message to a session"""
        try:
            # Get existing session data
            session_data = await self.get_session_data(session_id)
            if not session_data:
                # Create session if it doesn't exist
                await self.create_session(session_id)
                session_data = await self.get_session_data(session_id)
            
            # Create message
            message = {
                "id": str(uuid.uuid4()),
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat()
            }
            
            # Add message to session
            session_data["messages"].append(message)
            session_data["last_activity"] = datetime.now().isoformat()
            
            # Update session in Redis
            self.redis_client.setex(
                f"session:{session_id}",
                self.config.SESSION_TTL,
                json.dumps(session_data)
            )
            
            # Cache the message for quick access
            self.redis_client.lpush(
                f"messages:{session_id}",
                json.dumps(message)
            )
            self.redis_client.expire(f"messages:{session_id}", self.config.SESSION_TTL)
            
            logger.debug(f"Added message to session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding message to session {session_id}: {str(e)}")
            return False
    
    async def get_session_data(self, session_id: str) -> Optional[Dict]:
        """Get session data from Redis"""
        try:
            session_json = self.redis_client.get(f"session:{session_id}")
            if session_json:
                return json.loads(session_json)
            return None
            
        except Exception as e:
            logger.error(f"Error getting session data for {session_id}: {str(e)}")
            return None
    
    async def get_session_history(self, session_id: str) -> Optional[Dict]:
        """Get complete session history"""
        try:
            session_data = await self.get_session_data(session_id)
            if not session_data:
                return None
            
            # Get cached messages if available
            cached_messages = self.redis_client.lrange(f"messages:{session_id}", 0, -1)
            if cached_messages:
                # Convert cached messages back to dict format
                messages = [json.loads(msg) for msg in reversed(cached_messages)]
                session_data["messages"] = messages
            
            return session_data
            
        except Exception as e:
            logger.error(f"Error getting session history for {session_id}: {str(e)}")
            return None
    
    async def clear_session(self, session_id: str) -> bool:
        """Clear all messages from a session"""
        try:
            # Get session data
            session_data = await self.get_session_data(session_id)
            if not session_data:
                return False
            
            # Clear messages
            session_data["messages"] = []
            session_data["last_activity"] = datetime.now().isoformat()
            
            # Update session in Redis
            self.redis_client.setex(
                f"session:{session_id}",
                self.config.SESSION_TTL,
                json.dumps(session_data)
            )
            
            # Clear cached messages
            self.redis_client.delete(f"messages:{session_id}")
            
            logger.info(f"Cleared session: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing session {session_id}: {str(e)}")
            return False
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete a session completely"""
        try:
            # Remove session data
            self.redis_client.delete(f"session:{session_id}")
            self.redis_client.delete(f"messages:{session_id}")
            
            # Remove from sessions list
            self.redis_client.srem("sessions", session_id)
            
            logger.info(f"Deleted session: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting session {session_id}: {str(e)}")
            return False
    
    async def list_sessions(self) -> List[Dict]:
        """List all active sessions with messages"""
        try:
            session_ids = self.redis_client.smembers("sessions")
            sessions = []
            
            for session_id in session_ids:
                session_data = await self.get_session_data(session_id)
                if session_data:
                    message_count = len(session_data.get("messages", []))
                    # Only include sessions that have messages
                    if message_count > 0:
                        sessions.append({
                            "session_id": session_id,
                            "created_at": session_data["created_at"],
                            "last_activity": session_data["last_activity"],
                            "message_count": message_count
                        })
            
            # Sort by last activity
            sessions.sort(key=lambda x: x["last_activity"], reverse=True)
            return sessions
            
        except Exception as e:
            logger.error(f"Error listing sessions: {str(e)}")
            return []
    
    async def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        try:
            session_ids = self.redis_client.smembers("sessions")
            current_time = datetime.now()
            
            for session_id in session_ids:
                session_data = await self.get_session_data(session_id)
                if not session_data:
                    # Session doesn't exist, remove from list
                    self.redis_client.srem("sessions", session_id)
                    continue
                
                # Check if session is expired
                last_activity = datetime.fromisoformat(session_data["last_activity"])
                if current_time - last_activity > timedelta(seconds=self.config.SESSION_TTL):
                    await self.delete_session(session_id)
                    logger.info(f"Cleaned up expired session: {session_id}")
            
        except Exception as e:
            logger.error(f"Error cleaning up expired sessions: {str(e)}")

class MockRedisClient:
    """Mock Redis client for development when Redis is not available"""
    
    def __init__(self):
        self.data = {}
        self.sets = {}
        self.lists = {}
        logger.warning("Using mock Redis client - data will not persist")
    
    def setex(self, key: str, time: int, value: str):
        self.data[key] = value
    
    def get(self, key: str) -> Optional[str]:
        return self.data.get(key)
    
    def delete(self, *keys):
        for key in keys:
            self.data.pop(key, None)
            self.lists.pop(key, None)
    
    def sadd(self, key: str, *values):
        if key not in self.sets:
            self.sets[key] = set()
        for value in values:
            self.sets[key].add(value)
    
    def srem(self, key: str, *values):
        if key in self.sets:
            for value in values:
                self.sets[key].discard(value)
    
    def smembers(self, key: str):
        return self.sets.get(key, set())
    
    def lpush(self, key: str, *values):
        if key not in self.lists:
            self.lists[key] = []
        for value in values:
            self.lists[key].insert(0, value)
    
    def lrange(self, key: str, start: int, end: int):
        if key not in self.lists:
            return []
        return self.lists[key][start:end+1] if end != -1 else self.lists[key][start:]
    
    def expire(self, key: str, time: int):
        pass  # Mock implementation
    
    def ping(self):
        return True

