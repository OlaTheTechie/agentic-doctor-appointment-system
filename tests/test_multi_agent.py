#!/usr/bin/env python3
"""
Test the new Multi-Agent System
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.agents.multi_agent_system import MultiAgentOrchestrator
from langchain_core.messages import HumanMessage
import json

def test_multi_agent_system():
    """Test the multi-agent system with various queries"""
    
    print("🤖 Testing Multi-Agent Doctor Appointment System")
    print("=" * 60)
    
    # initialize the orchestrator
    try:
        orchestrator = MultiAgentOrchestrator()
        print("multi-agent system initialized successfully")
    except Exception as e:
        print(f"failed to initialize multi-agent system: {e}")
        return False
    
    # Test queries
    test_cases = [
        {
            "query": "is jane smith available today",
            "expected_agent": "availability",
            "description": "Availability check query"
        },
        {
            "query": "book an appointment with dr. johnson",
            "expected_agent": "booking", 
            "description": "Appointment booking query"
        },
        {
            "query": "cancel my appointment",
            "expected_agent": "booking",
            "description": "Appointment cancellation query"
        },
        {
            "query": "what doctors do you have",
            "expected_agent": "general",
            "description": "General information query"
        },
        {
            "query": "hello",
            "expected_agent": "general",
            "description": "Greeting query"
        }
    ]
    
    success_count = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}: {test_case['description']}")
        print(f"Query: '{test_case['query']}'")
        
        try:
            # Create test messages
            messages = [HumanMessage(content=test_case['query'])]
            
            # Process the request
            result = orchestrator.process_request(12345678, messages)
            
            # Check results
            active_agent = result.get('active_agent', 'unknown')
            agent_response = result.get('agent_response', 'No response')
            is_complete = result.get('is_complete', False)
            
            print(f"agent used: {active_agent}")
            print(f"completed: {is_complete}")
            print(f"response: {agent_response[:100]}...")
            
            # Check if correct agent was used
            if test_case['expected_agent'] in active_agent:
                print(f"correct agent used")
                success_count += 1
            else:
                print(f"expected {test_case['expected_agent']}, got {active_agent}")
            
        except Exception as e:
            print(f"test failed with error: {e}")
    
    print(f"\n" + "=" * 60)
    print(f"test results: {success_count}/{len(test_cases)} tests passed")
    
    if success_count == len(test_cases):
        print("all tests passed! multi-agent system is working correctly.")
        return True
    else:
        print("some tests failed. check the implementation.")
        return False

def test_intent_classification():
    """Test intent classification specifically"""
    print("\ntesting intent classification")
    print("-" * 40)
    
    try:
        orchestrator = MultiAgentOrchestrator()
        classifier = orchestrator.intent_classifier
        
        test_queries = [
            ("is doctor available", "check_availability"),
            ("book appointment", "book_appointment"),
            ("cancel my booking", "cancel_appointment"),
            ("reschedule appointment", "reschedule_appointment"),
            ("what services do you offer", "general_inquiry"),
            ("hello there", "greeting")
        ]
        
        for query, expected in test_queries:
            result = classifier.classify_intent(query, [])
            actual = result.get('intent', 'unknown')
            status = "pass" if actual == expected else "fail"
            print(f"{status} '{query}' -> {actual} (expected: {expected})")
        
    except Exception as e:
        print(f"intent classification test failed: {e}")

def main():
    """Run all tests"""
    try:
        # Test intent classification
        test_intent_classification()
        
        # Test full multi-agent system
        success = test_multi_agent_system()
        
        if success:
            print("\nmulti-agent system is ready for deployment!")
        else:
            print("\nmulti-agent system needs fixes before deployment.")
            
    except Exception as e:
        print(f"\ntesting failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()