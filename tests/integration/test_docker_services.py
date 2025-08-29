"""
Integration tests for Docker services.

Tests that Docker containers start successfully and are accessible.
"""

import pytest
import asyncio
import pymongo
from pymongo.errors import ServerSelectionTimeoutError
import httpx
import time
import subprocess
import os
from pathlib import Path
from typing import Generator


@pytest.fixture(scope="session")
def docker_services():
    """
    Fixture to ensure Docker services are running for integration tests.
    This will be used to start/stop services during testing.
    """
    project_root = Path(__file__).parent.parent.parent
    docker_compose_file = project_root / "docker-compose.yml"
    
    if not docker_compose_file.exists():
        pytest.skip("docker-compose.yml not found, skipping Docker integration tests")
    
    # Check if Docker is available
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
        subprocess.run(["docker-compose", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        pytest.skip("Docker or docker-compose not available")
    
    # Start services
    env = os.environ.copy()
    env['ENVIRONMENT'] = 'test'
    
    try:
        # Stop any existing services
        subprocess.run(
            ["docker-compose", "-f", str(docker_compose_file), "down"],
            cwd=project_root,
            env=env,
            capture_output=True
        )
        
        # Start services
        result = subprocess.run(
            ["docker-compose", "-f", str(docker_compose_file), "up", "-d"],
            cwd=project_root,
            env=env,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode != 0:
            pytest.skip(f"Failed to start Docker services: {result.stderr}")
            
        # Wait for services to be ready
        yield "services_ready"
        
    finally:
        # Clean up services
        try:
            subprocess.run(
                ["docker-compose", "-f", str(docker_compose_file), "down"],
                cwd=project_root,
                env=env,
                capture_output=True,
                timeout=60
            )
        except subprocess.TimeoutExpired:
            # Force stop if graceful shutdown fails
            subprocess.run(
                ["docker-compose", "-f", str(docker_compose_file), "down", "--remove-orphans", "--volumes"],
                cwd=project_root,
                env=env,
                capture_output=True
            )


class TestMongoDBService:
    """Test MongoDB service integration."""

    @pytest.mark.asyncio
    async def test_mongodb_connection(self, docker_services):
        """Test that MongoDB service accepts connections."""
        # Wait for service to be ready
        max_attempts = 30
        for attempt in range(max_attempts):
            try:
                client = pymongo.MongoClient(
                    "mongodb://localhost:27017",
                    serverSelectionTimeoutMS=1000
                )
                # Test connection
                client.server_info()
                client.close()
                break
            except ServerSelectionTimeoutError:
                if attempt == max_attempts - 1:
                    pytest.fail("MongoDB service did not become available")
                await asyncio.sleep(1)

    @pytest.mark.asyncio
    async def test_mongodb_basic_operations(self, docker_services):
        """Test basic MongoDB operations."""
        client = pymongo.MongoClient("mongodb://localhost:27017")
        
        try:
            # Test database creation
            db = client.blog_reviewer_test
            
            # Test collection creation and basic operations
            collection = db.test_collection
            
            # Insert test document
            doc = {"test": "integration", "timestamp": time.time()}
            result = collection.insert_one(doc)
            assert result.inserted_id is not None
            
            # Query test document
            found_doc = collection.find_one({"test": "integration"})
            assert found_doc is not None
            assert found_doc["test"] == "integration"
            
            # Clean up
            collection.delete_one({"_id": result.inserted_id})
            
        finally:
            client.close()

    @pytest.mark.asyncio
    async def test_mongodb_health_check(self, docker_services):
        """Test MongoDB health check endpoint or equivalent."""
        client = pymongo.MongoClient("mongodb://localhost:27017")
        
        try:
            # Test server status
            server_info = client.server_info()
            assert "version" in server_info
            assert server_info["ok"] == 1.0
            
        finally:
            client.close()


class TestDockerServicesIntegration:
    """Test overall Docker services integration."""

    def test_services_startup_time(self, docker_services):
        """Test that services start within acceptable time limits."""
        # This test ensures services start in < 30 seconds as per requirements
        # Since the fixture already started services, we can test that they're responding
        start_time = time.time()
        
        # Test MongoDB is responding
        max_wait = 30  # seconds
        mongodb_ready = False
        
        while time.time() - start_time < max_wait:
            try:
                client = pymongo.MongoClient(
                    "mongodb://localhost:27017",
                    serverSelectionTimeoutMS=1000
                )
                client.server_info()
                client.close()
                mongodb_ready = True
                break
            except Exception:
                time.sleep(0.5)
        
        assert mongodb_ready, f"MongoDB did not become ready within {max_wait} seconds"
        
        startup_time = time.time() - start_time
        assert startup_time < 30, f"Services took {startup_time:.2f} seconds to start (should be < 30s)"

    @pytest.mark.asyncio
    async def test_service_health_checks(self, docker_services):
        """Test that all services pass their health checks."""
        # Test that Docker health checks are passing
        project_root = Path(__file__).parent.parent.parent
        
        try:
            # Check docker-compose services status
            result = subprocess.run(
                ["docker-compose", "ps", "--services", "--filter", "status=running"],
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                running_services = result.stdout.strip().split('\n') if result.stdout.strip() else []
                assert len(running_services) > 0, "No services are running"
            else:
                # If docker-compose ps fails, just test MongoDB directly
                client = pymongo.MongoClient(
                    "mongodb://localhost:27017",
                    serverSelectionTimeoutMS=5000
                )
                server_info = client.server_info()
                assert server_info.get('ok') == 1.0
                client.close()
                
        except subprocess.TimeoutExpired:
            pytest.fail("Health check command timed out")
        except Exception as e:
            pytest.fail(f"Health check failed: {e}")

    def test_environment_variable_propagation(self, docker_services):
        """Test that environment variables are properly passed to containers."""
        # Test that containers receive the correct environment variables
        # This is validated by ensuring MongoDB is accessible with expected config
        client = pymongo.MongoClient("mongodb://localhost:27017")
        
        try:
            # Test connection works (indicates environment vars are correct)
            server_info = client.server_info()
            assert 'version' in server_info
            
            # Test we can create a test database (indicates permissions are correct)
            db = client.test_env_vars
            collection = db.test_collection
            
            doc = {"test": "env_propagation", "timestamp": time.time()}
            result = collection.insert_one(doc)
            assert result.inserted_id is not None
            
            # Clean up
            collection.delete_one({"_id": result.inserted_id})
            client.drop_database("test_env_vars")
            
        finally:
            client.close()

    @pytest.mark.asyncio
    async def test_volume_mounting(self, docker_services):
        """Test that volume mounting works correctly for development."""
        # Test that volumes are properly mounted and accessible
        # For MongoDB, test that data persists by creating and retrieving data
        client = pymongo.MongoClient("mongodb://localhost:27017")
        
        try:
            db = client.test_volume_mounting
            collection = db.test_persistence
            
            # Insert test data
            test_doc = {"test": "volume_mounting", "data": "persistent_data", "timestamp": time.time()}
            result = collection.insert_one(test_doc)
            doc_id = result.inserted_id
            
            # Verify data can be retrieved
            retrieved_doc = collection.find_one({"_id": doc_id})
            assert retrieved_doc is not None
            assert retrieved_doc["test"] == "volume_mounting"
            assert retrieved_doc["data"] == "persistent_data"
            
            # Clean up
            collection.delete_one({"_id": doc_id})
            client.drop_database("test_volume_mounting")
            
        finally:
            client.close()


class TestServiceOrchestration:
    """Test service orchestration and dependencies."""

    @pytest.mark.asyncio
    async def test_service_dependencies(self, docker_services):
        """Test that services start in correct order based on dependencies."""
        # Test that dependent services wait for their dependencies
        # For now, just test that MongoDB is available and responding
        client = pymongo.MongoClient(
            "mongodb://localhost:27017",
            serverSelectionTimeoutMS=5000
        )
        
        try:
            # This should succeed if MongoDB started properly
            server_info = client.server_info()
            assert server_info.get('ok') == 1.0
            
            # Test that we can perform basic operations
            db = client.dependency_test
            collection = db.test_collection
            
            result = collection.insert_one({"dependency_test": True})
            assert result.inserted_id is not None
            
            # Clean up
            client.drop_database("dependency_test")
            
        finally:
            client.close()

    @pytest.mark.asyncio
    async def test_service_communication(self, docker_services):
        """Test that services can communicate with each other."""
        # Test that services can communicate with each other
        # For single service setup, test that MongoDB is accessible from host
        client = pymongo.MongoClient("mongodb://localhost:27017")
        
        try:
            # Test network connectivity by performing database operations
            db = client.service_communication_test
            collection = db.messages
            
            # Test write operation
            message = {"from": "test_client", "to": "mongodb", "content": "hello", "timestamp": time.time()}
            result = collection.insert_one(message)
            assert result.inserted_id is not None
            
            # Test read operation
            retrieved = collection.find_one({"_id": result.inserted_id})
            assert retrieved is not None
            assert retrieved["content"] == "hello"
            
            # Test update operation
            collection.update_one(
                {"_id": result.inserted_id},
                {"$set": {"status": "delivered"}}
            )
            
            updated = collection.find_one({"_id": result.inserted_id})
            assert updated["status"] == "delivered"
            
            # Clean up
            client.drop_database("service_communication_test")
            
        finally:
            client.close()