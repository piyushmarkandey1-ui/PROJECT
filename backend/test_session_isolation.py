#!/usr/bin/env python3
"""
Test script for session isolation and multi-tenant functionality.
Verifies that company data is properly isolated and no cross-company data leaks occur.
"""

import asyncio
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.sessionservice.memory import SessionManager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def test_session_isolation():
    """Test that sessions are properly isolated by company."""
    logger.info("=" * 60)
    logger.info("TEST 1: Session Isolation")
    logger.info("=" * 60)
    
    session_manager = SessionManager()
    
    # Create sessions for two different companies
    company1 = "acme-corp"
    company2 = "tech-solutions"
    
    session1 = session_manager.create_session(company1)
    session2 = session_manager.create_session(company2)
    
    logger.info(f"Created session {session1} for {company1}")
    logger.info(f"Created session {session2} for {company2}")
    
    # Add messages to each session
    session_manager.add_message(company1, session1, "user", "Hello from Acme Corp!")
    session_manager.add_message(company1, session1, "assistant", "Hi Acme Corp user!")
    
    session_manager.add_message(company2, session2, "user", "Hello from Tech Solutions!")
    session_manager.add_message(company2, session2, "assistant", "Hi Tech Solutions user!")
    
    # Verify isolation
    logger.info("\nVerifying session isolation...")
    
    history1 = session_manager.get_history(company1, session1)
    history2 = session_manager.get_history(company2, session2)
    
    logger.info(f"\nSession {session1} ({company1}) history:")
    for msg in history1:
        logger.info(f"  {msg['role']}: {msg['content']}")
    
    logger.info(f"\nSession {session2} ({company2}) history:")
    for msg in history2:
        logger.info(f"  {msg['role']}: {msg['content']}")
    
    # Verify cross-company access is denied
    logger.info("\nTesting cross-company access...")
    cross_access = session_manager.get_history(company1, session2)
    assert len(cross_access) == 0, "Cross-company session access should be denied!"
    logger.info("✓ Cross-company session access is properly denied!")
    
    # Verify session counts
    count1 = session_manager.get_company_session_count(company1)
    count2 = session_manager.get_company_session_count(company2)
    logger.info(f"\nSession counts: {company1}={count1}, {company2}={count2}")
    assert count1 == 1
    assert count2 == 1
    
    logger.info("\n✓ TEST 1 PASSED: Session isolation verified!")
    return True


def test_multiple_sessions():
    """Test multiple sessions per company."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 2: Multiple Sessions per Company")
    logger.info("=" * 60)
    
    session_manager = SessionManager()
    company = "test-company"
    
    # Create 5 sessions
    sessions = []
    for i in range(5):
        sid = session_manager.create_session(company)
        sessions.append(sid)
        session_manager.add_message(company, sid, "user", f"Message {i+1}")
        logger.info(f"Created session {sid}")
    
    # Verify all sessions exist
    count = session_manager.get_company_session_count(company)
    assert count == 5, f"Expected 5 sessions, got {count}"
    logger.info(f"\n✓ All 5 sessions created successfully!")
    
    # Verify each session has correct messages
    for i, sid in enumerate(sessions):
        history = session_manager.get_history(company, sid)
        assert len(history) == 1
        assert history[0]["content"] == f"Message {i+1}"
    
    logger.info("\n✓ TEST 2 PASSED: Multiple sessions per company work correctly!")
    return True


def test_session_cleanup():
    """Test that deleting company sessions works."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 3: Session Cleanup")
    logger.info("=" * 60)
    
    session_manager = SessionManager()
    company = "cleanup-test"
    
    # Create sessions
    for i in range(3):
        session_manager.create_session(company)
    
    count = session_manager.get_company_session_count(company)
    assert count == 3
    logger.info(f"Created {count} sessions")
    
    # Delete all sessions
    deleted = session_manager.delete_company_sessions(company)
    assert deleted == 3
    logger.info(f"Deleted {deleted} sessions")
    
    # Verify sessions are gone
    count = session_manager.get_company_session_count(company)
    assert count == 0
    logger.info(f"✓ All sessions deleted!")
    
    logger.info("\n✓ TEST 3 PASSED: Session cleanup works correctly!")
    return True


def main():
    """Run all tests."""
    logger.info("Starting Session Isolation Tests")
    logger.info("=" * 60)
    
    tests = [
        test_session_isolation,
        test_multiple_sessions,
        test_session_cleanup,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            logger.error(f"\n✗ TEST FAILED: {e}")
            import traceback
            logger.error(traceback.format_exc())
            failed += 1
    
    logger.info("\n" + "=" * 60)
    logger.info(f"TEST RESULTS: {passed} passed, {failed} failed")
    logger.info("=" * 60)
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
