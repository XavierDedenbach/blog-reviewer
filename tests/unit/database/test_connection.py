"""
Unit tests for database connection module.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import os

from core.database.connection import DatabaseConnection, get_database, db_connection


class TestDatabaseConnection:
    """Test DatabaseConnection class."""
    
    @pytest.fixture
    def db_conn(self):
        """Create a DatabaseConnection instance."""
        return DatabaseConnection()
    
    @pytest.mark.asyncio
    async def test_connect_success(self, db_conn):
        """Test successful database connection."""
        with patch('core.database.connection.AsyncIOMotorClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            mock_client.blog_reviewer = AsyncMock()
            
            await db_conn.connect()
            
            assert db_conn.client == mock_client
            assert db_conn.db == mock_client.blog_reviewer
            mock_client.admin.command.assert_called_once_with('ping')
    
    @pytest.mark.asyncio
    async def test_connect_with_custom_uri(self, db_conn):
        """Test database connection with custom URI."""
        custom_uri = "mongodb://custom:uri"
        with patch('core.database.connection.AsyncIOMotorClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            mock_client.blog_reviewer = AsyncMock()
            
            with patch.dict(os.environ, {'MONGODB_URI': custom_uri}):
                await db_conn.connect()
            
            mock_client_class.assert_called_once_with(custom_uri)
    
    @pytest.mark.asyncio
    async def test_connect_with_default_uri(self, db_conn):
        """Test database connection with default URI."""
        with patch('core.database.connection.AsyncIOMotorClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            mock_client.blog_reviewer = AsyncMock()
            
            with patch.dict(os.environ, {}, clear=True):
                await db_conn.connect()
            
            expected_uri = "mongodb://admin:password123@localhost:27017/blog_reviewer"
            mock_client_class.assert_called_once_with(expected_uri)
    
    @pytest.mark.asyncio
    async def test_disconnect_with_client(self, db_conn):
        """Test disconnecting when client exists."""
        mock_client = MagicMock()
        db_conn.client = mock_client
        
        await db_conn.disconnect()
        
        mock_client.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_disconnect_without_client(self, db_conn):
        """Test disconnecting when no client exists."""
        db_conn.client = None
        
        # Should not raise an exception
        await db_conn.disconnect()
    
    def test_get_database_with_db(self, db_conn):
        """Test getting database when db exists."""
        mock_db = AsyncMock()
        db_conn.db = mock_db
        
        result = db_conn.get_database()
        
        assert result == mock_db
    
    def test_get_database_without_db(self, db_conn):
        """Test getting database when db doesn't exist."""
        db_conn.db = None
        
        result = db_conn.get_database()
        
        assert result is None


class TestGetDatabaseFunction:
    """Test get_database function."""
    
    @pytest.mark.asyncio
    async def test_get_database_with_existing_db(self):
        """Test get_database when db already exists."""
        mock_db = AsyncMock()
        db_connection.db = mock_db
        
        result = await get_database()
        
        assert result == mock_db
    
    @pytest.mark.asyncio
    async def test_get_database_without_db(self):
        """Test get_database when db doesn't exist."""
        # Reset the global connection
        db_connection.client = None
        db_connection.db = None
        
        # Test that get_database connects and returns the database
        result = await get_database()
        
        assert result is not None
        assert db_connection.client is not None
        assert db_connection.db is not None
        assert result == db_connection.db


class TestDatabaseConnectionIntegration:
    """Test database connection integration scenarios."""
    
    @pytest.mark.asyncio
    async def test_connection_lifecycle(self):
        """Test complete connection lifecycle."""
        with patch('core.database.connection.AsyncIOMotorClient') as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            mock_client.blog_reviewer = MagicMock()
            mock_client.admin.command = AsyncMock()
            
            # Test connection
            db_conn = DatabaseConnection()
            await db_conn.connect()
            
            assert db_conn.client is not None
            assert db_conn.db is not None
            
            # Test get_database
            db = db_conn.get_database()
            assert db == mock_client.blog_reviewer
            
            # Test disconnect
            await db_conn.disconnect()
            mock_client.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_multiple_connections(self):
        """Test multiple database connections."""
        # Create multiple connections
        conn1 = DatabaseConnection()
        conn2 = DatabaseConnection()
        
        await conn1.connect()
        await conn2.connect()
        
        # Both should connect to the same MongoDB instance
        assert conn1.client is not None
        assert conn2.client is not None
        assert conn1.db is not None
        assert conn2.db is not None
        
        # Test that they can both access the database
        db1 = conn1.get_database()
        db2 = conn2.get_database()
        assert db1 is not None
        assert db2 is not None
        
        await conn1.disconnect()
        await conn2.disconnect()
    
    @pytest.mark.asyncio
    async def test_connection_error_handling(self):
        """Test connection error handling."""
        with patch('core.database.connection.AsyncIOMotorClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.admin.command.side_effect = Exception("Connection failed")
            mock_client_class.return_value = mock_client
            
            db_conn = DatabaseConnection()
            
            with pytest.raises(Exception, match="Connection failed"):
                await db_conn.connect()
    
    @pytest.mark.asyncio
    async def test_environment_variable_priority(self):
        """Test that environment variable takes priority over default."""
        custom_uri = "mongodb://custom:uri"
        
        with patch('core.database.connection.AsyncIOMotorClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            mock_client.blog_reviewer = AsyncMock()
            
            with patch.dict(os.environ, {'MONGODB_URI': custom_uri}):
                db_conn = DatabaseConnection()
                await db_conn.connect()
            
            mock_client_class.assert_called_once_with(custom_uri)
    
    @pytest.mark.asyncio
    async def test_get_database_function_integration(self):
        """Test get_database function integration."""
        # Reset the global connection
        db_connection.client = None
        db_connection.db = None
        
        with patch('core.database.connection.AsyncIOMotorClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            mock_client.blog_reviewer = AsyncMock()
            
            result = await get_database()
            
            assert result == mock_client.blog_reviewer
            assert db_connection.client == mock_client
            assert db_connection.db == mock_client.blog_reviewer
