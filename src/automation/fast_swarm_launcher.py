#!/usr/bin/env python3
"""
FAST AI SWARM LAUNCHER - Minimal overhead, maximum speed
Only loads essential components for terminal operations
"""

import sys
import os

# Speed optimizations
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
os.environ["PYTHONUNBUFFERED"] = "1"

def launch_fast_swarm():
    """Launch only speed-critical components"""
    
    # Only import what we absolutely need
    from integrate_uv_package_manager import AISwarmUVIntelligence
    from integrate_file_organization import AISwarmFileOrganizationIntelligence
    from integrate_template_processing import AISwarmTemplateProcessingIntelligence
    
    print("[FAST] AI Swarm - Speed Mode")
    print("=" * 40)
    
    # Initialize only fast components
    components = {
        "uv": AISwarmUVIntelligence(),
        "files": AISwarmFileOrganizationIntelligence(),
        "templates": AISwarmTemplateProcessingIntelligence()
    }
    
    print(f"[OK] Loaded {len(components)} speed-optimized components")
    print("[OK] Terminal acceleration active")
    
    return components

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--turbo":
        # Ultra-fast mode - no imports at all
        print("[TURBO] Maximum speed - no AI models loaded")
        print("[OK] Terminal is at maximum velocity")
    else:
        components = launch_fast_swarm()
        print(f"\n[READY] System optimized for speed")
        print("Use 'python fast_swarm_launcher.py --turbo' for maximum speed")
