#!/usr/bin/env python3
"""
AutoGen Multi-Agent Examples using Local Ollama Models
"""

from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
import autogen

# Configure Ollama connection
config_list = [
    {
        "model": "deepseek-r1:8b",
        "base_url": "http://localhost:11434/v1",
        "api_key": "ollama",
        "api_type": "openai"
    }
]

llm_config = {
    "config_list": config_list,
    "temperature": 0.7,
    "timeout": 120
}

# Example 1: Simple Two-Agent Conversation
def simple_chat_example():
    """Basic assistant and user proxy interaction"""
    
    # Create assistant
    assistant = AssistantAgent(
        name="Assistant",
        llm_config=llm_config,
        system_message="You are a helpful AI assistant. Provide clear and concise answers."
    )
    
    # Create user proxy (can execute code)
    user_proxy = UserProxyAgent(
        name="User",
        human_input_mode="NEVER",  # Change to "ALWAYS" for interactive
        max_consecutive_auto_reply=3,
        code_execution_config={
            "use_docker": False,
            "work_dir": "coding",
        }
    )
    
    # Start conversation
    user_proxy.initiate_chat(
        assistant,
        message="Write and execute a Python function to calculate fibonacci numbers"
    )

# Example 2: Software Development Team
def dev_team_example():
    """Multi-agent software development team"""
    
    # Product Manager
    pm = AssistantAgent(
        name="ProductManager",
        llm_config=llm_config,
        system_message="""You are a product manager. You:
        - Define requirements clearly
        - Prioritize features
        - Ensure the solution meets user needs
        - Ask clarifying questions"""
    )
    
    # Software Architect
    architect = AssistantAgent(
        name="Architect",
        llm_config=llm_config,
        system_message="""You are a software architect. You:
        - Design system architecture
        - Choose appropriate technologies
        - Define APIs and interfaces
        - Consider scalability and performance"""
    )
    
    # Developer
    developer = AssistantAgent(
        name="Developer",
        llm_config=llm_config,
        system_message="""You are a senior developer. You:
        - Write clean, efficient code
        - Implement features according to specifications
        - Follow best practices
        - Create unit tests"""
    )
    
    # QA Engineer
    qa = AssistantAgent(
        name="QAEngineer",
        llm_config=llm_config,
        system_message="""You are a QA engineer. You:
        - Review code for bugs
        - Suggest test cases
        - Verify requirements are met
        - Check for edge cases"""
    )
    
    # User proxy to execute code
    executor = UserProxyAgent(
        name="Executor",
        human_input_mode="NEVER",
        code_execution_config={
            "use_docker": False,
            "work_dir": "team_coding",
        }
    )
    
    # Create group chat
    group_chat = GroupChat(
        agents=[pm, architect, developer, qa, executor],
        messages=[],
        max_round=10
    )
    
    manager = GroupChatManager(groupchat=group_chat, llm_config=llm_config)
    
    # Start project
    executor.initiate_chat(
        manager,
        message="""Create a REST API for a todo list application with:
        - User authentication
        - CRUD operations for todos
        - Due date reminders
        - Priority levels"""
    )

# Example 3: Research Team
def research_team_example():
    """Multi-agent research and analysis team"""
    
    # Researcher
    researcher = AssistantAgent(
        name="Researcher",
        llm_config=llm_config,
        system_message="""You are a researcher who:
        - Gathers relevant information
        - Identifies key facts and trends
        - Provides citations and sources
        - Summarizes findings clearly"""
    )
    
    # Analyst
    analyst = AssistantAgent(
        name="Analyst",
        llm_config=llm_config,
        system_message="""You are a data analyst who:
        - Analyzes information critically
        - Identifies patterns and insights
        - Creates data visualizations
        - Makes data-driven recommendations"""
    )
    
    # Writer
    writer = AssistantAgent(
        name="Writer",
        llm_config=llm_config,
        system_message="""You are a technical writer who:
        - Creates clear, structured documents
        - Writes for the target audience
        - Ensures accuracy and completeness
        - Formats content professionally"""
    )
    
    # Coordinator
    coordinator = UserProxyAgent(
        name="Coordinator",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=10
    )
    
    # Create group chat
    group_chat = GroupChat(
        agents=[researcher, analyst, writer, coordinator],
        messages=[],
        max_round=8
    )
    
    manager = GroupChatManager(groupchat=group_chat, llm_config=llm_config)
    
    # Start research
    coordinator.initiate_chat(
        manager,
        message="Research and create a report on the current state of quantum computing and its potential applications in cryptography"
    )

# Example 4: Code Review Process
def code_review_example():
    """Automated code review with multiple perspectives"""
    
    code_to_review = '''
    def calculate_discount(price, discount_percent):
        return price * discount_percent / 100
    
    def process_order(items, customer_type):
        total = 0
        for item in items:
            total += item['price']
        
        if customer_type == 'premium':
            total = calculate_discount(total, 20)
        elif customer_type == 'regular':
            total = calculate_discount(total, 10)
        
        return total
    '''
    
    # Security Reviewer
    security = AssistantAgent(
        name="SecurityReviewer",
        llm_config=llm_config,
        system_message="Review code for security vulnerabilities, input validation, and potential exploits."
    )
    
    # Performance Reviewer
    performance = AssistantAgent(
        name="PerformanceReviewer",
        llm_config=llm_config,
        system_message="Review code for performance issues, optimization opportunities, and scalability concerns."
    )
    
    # Clean Code Reviewer
    clean_code = AssistantAgent(
        name="CleanCodeReviewer",
        llm_config=llm_config,
        system_message="Review code for readability, maintainability, naming conventions, and design patterns."
    )
    
    # Lead Developer (coordinator)
    lead = UserProxyAgent(
        name="LeadDeveloper",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=1
    )
    
    # Create group chat
    group_chat = GroupChat(
        agents=[security, performance, clean_code, lead],
        messages=[],
        max_round=6
    )
    
    manager = GroupChatManager(groupchat=group_chat, llm_config=llm_config)
    
    # Start review
    lead.initiate_chat(
        manager,
        message=f"Please review this code:\n```python\n{code_to_review}\n```"
    )

# Example 5: Custom Workflow Automation
def custom_workflow_example(task_description):
    """Create a custom workflow based on task"""
    
    # Planner
    planner = AssistantAgent(
        name="Planner",
        llm_config=llm_config,
        system_message="Break down tasks into clear, actionable steps. Create a detailed plan."
    )
    
    # Implementer
    implementer = AssistantAgent(
        name="Implementer",
        llm_config=llm_config,
        system_message="Execute the plan step by step. Write code, create documents, or perform tasks as needed."
    )
    
    # Validator
    validator = AssistantAgent(
        name="Validator",
        llm_config=llm_config,
        system_message="Verify that all requirements are met. Check for errors and suggest improvements."
    )
    
    # Executor
    executor = UserProxyAgent(
        name="Executor",
        human_input_mode="NEVER",
        code_execution_config={
            "use_docker": False,
            "work_dir": "workflow",
        }
    )
    
    # Create workflow
    group_chat = GroupChat(
        agents=[planner, implementer, validator, executor],
        messages=[],
        max_round=8
    )
    
    manager = GroupChatManager(groupchat=group_chat, llm_config=llm_config)
    
    # Execute workflow
    executor.initiate_chat(manager, message=task_description)

if __name__ == "__main__":
    print("AutoGen Multi-Agent Examples")
    print("=" * 50)
    print("\nChoose an example:")
    print("1. Simple Chat")
    print("2. Development Team")
    print("3. Research Team")
    print("4. Code Review")
    print("5. Custom Workflow")
    
    choice = input("\nEnter choice (1-5): ")
    
    if choice == "1":
        simple_chat_example()
    elif choice == "2":
        dev_team_example()
    elif choice == "3":
        research_team_example()
    elif choice == "4":
        code_review_example()
    elif choice == "5":
        task = input("Enter your task description: ")
        custom_workflow_example(task)
    else:
        print("Invalid choice")