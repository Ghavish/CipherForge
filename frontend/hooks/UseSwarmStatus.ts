import {useState, useEffect} from 'react';

export function useSwarmStatus(projectId: string | null) {
  // Initialize with a default empty structure
  const [status, setStatus] = useState({ currentStage: 'Initializing', logs: [] });

  useEffect(() => {
    if (!projectId) return;

    const fetchStatus = async () => {
      try {
        const response = await fetch(`/api/swarm-status?projectId=${projectId}`);
        if (!response.ok) return;
        const data = await response.json();
        // Update the state with the actual data
        setStatus(data);
      } catch (e) {
        console.error("Failed to poll swarm status", e);
      }
    };

    fetchStatus();
    const interval = setInterval(fetchStatus, 3000);
    return () => clearInterval(interval);
  }, [projectId]);

  // Always return an object
  return { status };
}