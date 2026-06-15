import { useState, useEffect } from 'react';

export function useSwarmStatus(projectId: string | null) {
  // Initialize with a default empty structure
  const [status, setStatus] = useState<{ currentStage: string, logs: string[] }>({ 
    currentStage: 'Initializing', 
    logs: [] 
  });

  useEffect(() => {
    if (!projectId) {
      // Reset if the project ID is cleared
      setStatus({ currentStage: 'Initializing', logs: [] });
      return;
    }

    const fetchStatus = async () => {
      try {
        // Ensure this route matches your actual Next.js API folder name!
        const response = await fetch(`/api/swarm-status?projectId=${projectId}`);
        if (!response.ok) return;
        
        const data = await response.json();
        setStatus(data);
      } catch (e) {
        console.error("Failed to poll swarm status", e);
      }
    };

    // Fetch immediately, then poll every 3 seconds
    fetchStatus();
    const interval = setInterval(fetchStatus, 3000);
    
    return () => clearInterval(interval);
  }, [projectId]);

  return { status };
}