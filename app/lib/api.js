const apiUrl = process.env.NEXT_PUBLIC_PET_SAUDE_API_URL || "";

export async function analyzeWithBackend(payload) {
  if (!apiUrl) return null;
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), 20000);
  try {
    const response = await fetch(`${apiUrl.replace(/\/$/, "")}/v1/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      signal: controller.signal
    });
    if (!response.ok) throw new Error(`API ${response.status}`);
    return await response.json();
  } finally {
    window.clearTimeout(timeout);
  }
}

export async function checkBackend() {
  if (!apiUrl) return { connected: false, mode: "local" };
  try {
    const response = await fetch(`${apiUrl.replace(/\/$/, "")}/health`);
    if (!response.ok) return { connected: false, mode: "local" };
    const data = await response.json();
    return { connected: true, mode: data.mode || "api" };
  } catch {
    return { connected: false, mode: "local" };
  }
}
