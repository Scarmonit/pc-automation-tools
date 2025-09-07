import logging
import json
import azure.functions as func
from datetime import datetime
import uuid

def main(req: func.HttpRequest, outputSbMsg: func.Out[str]) -> func.HttpResponse:
    """
    Azure Function to trigger swarm agent tasks
    Receives HTTP requests and queues them for processing by the swarm
    """
    logging.info('Agent trigger function processing request')

    try:
        # Parse request body
        req_body = req.get_json()
        task_type = req_body.get('task_type', 'general')
        task_description = req_body.get('description')
        priority = req_body.get('priority', 5)
        agents_required = req_body.get('agents', ['queen'])
        
        if not task_description:
            return func.HttpResponse(
                "Please provide a task description",
                status_code=400
            )
        
        # Create task message
        task_id = str(uuid.uuid4())
        task_message = {
            'task_id': task_id,
            'task_type': task_type,
            'description': task_description,
            'priority': priority,
            'agents_required': agents_required,
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'queued',
            'metadata': {
                'source': 'azure_function',
                'function_name': 'agent-trigger',
                'request_id': req.headers.get('x-ms-request-id')
            }
        }
        
        # Send to Service Bus queue
        outputSbMsg.set(json.dumps(task_message))
        
        logging.info(f'Task {task_id} queued for processing')
        
        # Return response
        response = {
            'task_id': task_id,
            'status': 'queued',
            'message': f'Task queued for processing by {", ".join(agents_required)}',
            'estimated_time': estimate_completion_time(task_type, agents_required)
        }
        
        return func.HttpResponse(
            json.dumps(response),
            status_code=202,
            headers={'Content-Type': 'application/json'}
        )
        
    except ValueError as e:
        logging.error(f'Invalid request: {e}')
        return func.HttpResponse(
            f"Invalid request: {str(e)}",
            status_code=400
        )
    except Exception as e:
        logging.error(f'Error processing request: {e}')
        return func.HttpResponse(
            f"Error processing request: {str(e)}",
            status_code=500
        )

def estimate_completion_time(task_type: str, agents: list) -> str:
    """
    Estimate task completion time based on type and agents involved
    """
    base_times = {
        'simple': 30,
        'coding': 120,
        'analysis': 60,
        'research': 90,
        'testing': 45,
        'general': 60
    }
    
    base_time = base_times.get(task_type, 60)
    
    # Add time for multi-agent coordination
    if len(agents) > 1:
        base_time += len(agents) * 10
    
    # Add time for complex tasks requiring consensus
    if 'queen' in agents and len(agents) > 3:
        base_time += 30
    
    return f"{base_time} seconds"