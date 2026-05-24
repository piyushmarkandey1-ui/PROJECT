#!/usr/bin/env python3
"""
Load testing script for the multi-tenant customer care bot.
Simulates multiple concurrent users across different companies.
"""

import asyncio
import logging
import time
import uuid
from typing import List, Dict

import httpx

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000/api"

# Test companies configuration
TEST_COMPANIES = [
    {"slug": "acme-corp", "name": "Acme Corp"},
    {"slug": "tech-solutions", "name": "Tech Solutions"},
    {"slug": "global-retail", "name": "Global Retail"},
]

# Sample test questions
TEST_QUESTIONS = [
    "How do I view my invoice?",
    "What payment methods do you accept?",
    "How do I track my order?",
    "What is your return policy?",
    "How do I reset my password?",
    "What are your support hours?",
    "Do you offer free trials?",
    "How do I upgrade my plan?",
]


class LoadTester:
    def __init__(self, num_users: int = 10, duration_seconds: int = 30):
        self.num_users = num_users
        self.duration_seconds = duration_seconds
        self.results: List[Dict] = []
        self.start_time = 0.0

    async def simulate_user(self, company_slug: str):
        """Simulate a single user's interactions."""
        session_id = str(uuid.uuid4())
        user_results = []
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Send multiple messages
                for i, question in enumerate(TEST_QUESTIONS[:5]):  # Send 5 questions per user
                    msg_start = time.time()
                    
                    try:
                        response = await client.post(
                            f"{BASE_URL}/chat",
                            json={
                                "session_id": session_id,
                                "message": question,
                                "company_slug": company_slug,
                            },
                        )
                        
                        latency = time.time() - msg_start
                        success = response.status_code == 200
                        
                        user_results.append({
                            "success": success,
                            "latency": latency,
                            "status_code": response.status_code,
                        })
                        
                        logger.debug(
                            f"User {session_id[:8]}: Q{i+1} - {response.status_code} in {latency:.2f}s"
                        )
                        
                    except Exception as e:
                        user_results.append({
                            "success": False,
                            "latency": 0,
                            "error": str(e),
                        })
                    
                    # Random delay between messages (0.5-2 seconds)
                    await asyncio.sleep(0.5 + (1.5 * (i % 2)))
                    
        except Exception as e:
            logger.error(f"User {session_id[:8]} failed: {e}")
        
        self.results.extend(user_results)
        return user_results

    async def run_load_test(self):
        """Run the full load test."""
        logger.info("=" * 70)
        logger.info(f"Starting Load Test: {self.num_users} concurrent users for {self.duration_seconds}s")
        logger.info("=" * 70)
        
        self.start_time = time.time()
        tasks = []
        
        # Create users distributed across companies
        for i in range(self.num_users):
            company = TEST_COMPANIES[i % len(TEST_COMPANIES)]
            task = asyncio.create_task(self.simulate_user(company["slug"]))
            tasks.append(task)
        
        logger.info(f"Started {len(tasks)} concurrent users")
        
        # Run for specified duration or until all tasks complete
        try:
            await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=self.duration_seconds,
            )
        except asyncio.TimeoutError:
            logger.info("Load test duration reached")
        
        self.print_results()

    def print_results(self):
        """Print load test results."""
        total_time = time.time() - self.start_time
        
        if not self.results:
            logger.warning("No results collected")
            return
        
        successful = [r for r in self.results if r.get("success", False)]
        failed = [r for r in self.results if not r.get("success", False)]
        
        latencies = [r["latency"] for r in successful]
        
        logger.info("\n" + "=" * 70)
        logger.info("LOAD TEST RESULTS")
        logger.info("=" * 70)
        logger.info(f"Total duration: {total_time:.2f}s")
        logger.info(f"Total requests: {len(self.results)}")
        logger.info(f"Successful: {len(successful)}")
        logger.info(f"Failed: {len(failed)}")
        logger.info(f"Success rate: {(len(successful)/len(self.results)*100):.1f}%")
        
        if latencies:
            logger.info(f"\nLatency (seconds):")
            logger.info(f"  Min: {min(latencies):.3f}")
            logger.info(f"  Max: {max(latencies):.3f}")
            logger.info(f"  Avg: {sum(latencies)/len(latencies):.3f}")
            logger.info(f"  Median: {sorted(latencies)[len(latencies)//2]:.3f}")
        
        logger.info(f"\nThroughput: {len(self.results)/total_time:.2f} req/s")
        logger.info("=" * 70)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Load testing for customer care bot")
    parser.add_argument("--users", type=int, default=10, help="Number of concurrent users (default: 10)")
    parser.add_argument("--duration", type=int, default=60, help="Test duration in seconds (default: 60)")
    
    args = parser.parse_args()
    
    tester = LoadTester(num_users=args.users, duration_seconds=args.duration)
    asyncio.run(tester.run_load_test())


if __name__ == "__main__":
    main()
