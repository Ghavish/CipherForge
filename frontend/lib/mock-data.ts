// frontend/lib/mock_data.ts

// We now export BOTH IDs to fully simulate the architecture
export const MOCK_PROJECT_ID = "PROJ-MOCK-999";
export const MOCK_ROOM_ID = "local_sim_room_999";

export const mockLogs = [
  `[System] Mock session initialized. Bypassing Band.ai network...`,
  `[System] Allocated Workspace: [${MOCK_PROJECT_ID}]`,
  `[Conductor] Connecting to local virtual room...`,
  `[Conductor] Received task. Analyzing requirements for ${MOCK_PROJECT_ID}...`,
  `[Conductor] Handing off blueprint generation to Architect.`,
  `[Architect] Drafting system architecture...`,
  `[Architect] Blueprint complete. Delegating to UI and API Coders.`,
  `[UI Coder] Scaffolding React components in /${MOCK_PROJECT_ID}/frontend...`,
  `[API Coder] Setting up database schemas in /${MOCK_PROJECT_ID}/backend...`,
  `[Reviewer] QA check passed. No critical vulnerabilities detected.`,
  `[Mergemaster] Committing to local mock repository. Deployment ready!`
];

// Helper to simulate network latency
export const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

// Simulated agent progression states for your UI progress bar
export const getMockSwarmHealth = (step: number) => {
  const states = [
    // Step 0: Initializing
    { conductor: 'active', architect: 'pending', ui: 'pending', api: 'pending', reviewer: 'pending', merge: 'pending' },
    // Step 1: Architecting
    { conductor: 'complete', architect: 'active', ui: 'pending', api: 'pending', reviewer: 'pending', merge: 'pending' },
    // Step 2: Coding (Notice both coders activate at once for concurrency!)
    { conductor: 'complete', architect: 'complete', ui: 'active', api: 'active', reviewer: 'pending', merge: 'pending' },
    // Step 3: Review
    { conductor: 'complete', architect: 'complete', ui: 'complete', api: 'complete', reviewer: 'active', merge: 'pending' },
    // Step 4: Merge
    { conductor: 'complete', architect: 'complete', ui: 'complete', api: 'complete', reviewer: 'complete', merge: 'active' },
    // Step 5: Done
    { conductor: 'complete', architect: 'complete', ui: 'complete', api: 'complete', reviewer: 'complete', merge: 'complete' }
  ];
  
  return states[Math.min(step, states.length - 1)];
};