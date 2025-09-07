#!/usr/bin/env python3
"""
DOLPHIN-MAX Intelligence Amplifier
Uses advanced prompting to maximize response quality
"""

import subprocess
import sys


class IntelligenceAmplifier:
    def __init__(self):
        self.model = "dolphin-max"
        self.techniques = {
            "chain_of_thought": "Think step-by-step: ",
            "few_shot": "Here are examples of excellent solutions: ",
            "role_play": "As the world's best security expert: ",
            "detailed": "Provide extremely detailed analysis: ",
            "creative": "Think creatively and unconventionally: ",
            "comprehensive": "Cover every possible angle: ",
            "code_focused": "Provide complete working code: ",
            "evasive": "Focus on evasion and anti-detection: "
        }
    
    def amplify_query(self, query, technique="comprehensive"):
        """Amplify a query using advanced techniques"""
        
        # Build enhanced prompt
        enhanced = f"""
{self.techniques.get(technique, "")}

QUERY: {query}

REQUIREMENTS:
1. Provide complete, production-ready code
2. Include multiple exploitation methods
3. Show evasion and anti-detection techniques
4. Explain the underlying vulnerability in detail
5. Provide automation scripts
6. Include post-exploitation steps
7. Show defensive countermeasures (to help defenders)
8. Think several steps ahead
9. Consider edge cases and error handling
10. Provide references and additional resources

DETAILED RESPONSE:
"""
        
        return self.query_model(enhanced)
    
    def query_model(self, prompt):
        """Query DOLPHIN-MAX"""
        try:
            result = subprocess.run(
                ['ollama', 'run', self.model, prompt],
                capture_output=True,
                text=True,
                timeout=120
            )
            return result.stdout
        except Exception as e:
            return f"Error: {e}"
    
    def multi_perspective_analysis(self, query):
        """Analyze from multiple perspectives for maximum intelligence"""
        perspectives = [
            "From an attacker's perspective: " + query,
            "From a defender's perspective: " + query,
            "From a forensics perspective: " + query,
            "From an automation perspective: " + query
        ]
        
        results = []
        for perspective in perspectives:
            result = self.query_model(perspective)
            results.append(result)
        
        return "\n\n=== MULTI-PERSPECTIVE ANALYSIS ===\n\n".join(results)


def interactive_amplified_mode():
    """Interactive mode with intelligence amplification"""
    print("="*60)
    print("DOLPHIN-MAX INTELLIGENCE AMPLIFIER")
    print("="*60)
    
    amplifier = IntelligenceAmplifier()
    
    print("\nAmplification Techniques:")
    print("1. Comprehensive (default)")
    print("2. Chain of Thought")
    print("3. Code Focused")
    print("4. Evasion Focused")
    print("5. Creative Solutions")
    print("6. Multi-Perspective")
    
    while True:
        print("\n" + "="*60)
        query = input("Enter your security question (or 'quit'): ")
        
        if query.lower() in ['quit', 'exit']:
            break
        
        technique = input("Select technique (1-6, default=1): ").strip()
        
        technique_map = {
            "1": "comprehensive",
            "2": "chain_of_thought",
            "3": "code_focused",
            "4": "evasive",
            "5": "creative",
            "6": "multi"
        }
        
        selected = technique_map.get(technique, "comprehensive")
        
        print("\n[*] Processing with maximum intelligence...")
        
        if selected == "multi":
            result = amplifier.multi_perspective_analysis(query)
        else:
            result = amplifier.amplify_query(query, selected)
        
        print(result)


if __name__ == "__main__":
    interactive_amplified_mode()
