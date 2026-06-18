import { useState, useEffect } from 'react';

export function useSwarmStatus(projectId: string | null) {
  const [status, setStatus] = useState<{ currentStage: string, logs: string[] }>({ 
    currentStage: 'Initializing', 
    logs: [] 
  });

  useEffect(() => {
    if (!projectId) {
      setStatus({ currentStage: 'Initializing', logs: [] });
      return;
    }

    const fetchStatus = async () => {
      try {
        const response = await fetch(`/api/swarm-status?projectId=${projectId}`);
        if (!response.ok) return;
        
        const data = await response.json();
        setStatus(data);
      } catch (e) {
        console.error("Failed to poll swarm status", e);
      }
    };

    fetchStatus();
    const interval = setInterval(fetchStatus, 3000); // Poll every 3 seconds
    
    return () => clearInterval(interval);
  }, [projectId]);

  return { status };
}