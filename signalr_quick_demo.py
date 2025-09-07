#!/usr/bin/env python3
"""
AI Swarm Intelligence - SignalR Quick Demo
Rapid demonstration of real-time communication capabilities
"""

import asyncio
import json
import random
from datetime import datetime
from integrate_signalr import AISwarmSignalRIntegration

async def quick_signalr_demo():
    """Quick demo of SignalR integration capabilities"""
    print("=" * 60)
    print("AI SWARM INTELLIGENCE - SIGNALR QUICK DEMO")
    print("=" * 60)
    
    # Initialize integration
    integration = AISwarmSignalRIntegration()
    await integration.initialize_swarm()
    
    # Run short coordination simulation
    print("[OK] Running 15-second coordination simulation...")
    await integration.simulate_real_time_coordination(15)
    
    # Generate quick analytics
    analytics = await integration.generate_coordination_analytics()
    
    # Display key metrics
    print("\n" + "=" * 60)
    print("QUICK DEMO RESULTS")
    print("=" * 60)
    print(f"Hub Status: {'ACTIVE' if analytics['hub_status']['is_running'] else 'INACTIVE'}")
    print(f"Connected Agents: {analytics['hub_status']['connected_agents']}/5")
    print(f"Messages Processed: {analytics['hub_status']['total_messages']}")
    print(f"Active Groups: {analytics['hub_status']['active_groups']}")
    print(f"Coordination Efficiency: {analytics['performance_metrics']['coordination_efficiency']*100:.1f}%")
    print(f"Connection Stability: {analytics['performance_metrics']['connection_stability']*100:.1f}%")
    
    # Shutdown
    await integration.shutdown_swarm()
    print("\n[OK] SignalR integration demo completed successfully!")

if __name__ == "__main__":
    asyncio.run(quick_signalr_demo())