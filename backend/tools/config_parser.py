import os
import yaml

def get_target_agent_id(role_name: str) -> str:
    """
    Dynamically fetches the UUID of a target agent from the config file.
    """
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), 
        'config', 
        'agent_config.yaml'
    )
    
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
        
    try:
        return config[role_name]['agent_id']
    except KeyError:
        raise ValueError(f"Agent role '{role_name}' not found in agent_config.yaml")