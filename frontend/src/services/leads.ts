export async function fetchLeads() {
  const res = await fetch("http://localhost:8000/api/leads");
  if (!res.ok) throw new Error("Failed to fetch leads");
  return res.json();
}

export async function getLead(id: number) {
  const res = await fetch(`http://localhost:8000/api/leads/${id}`);
  if (!res.ok) throw new Error("Failed to fetch lead");
  return res.json();
}

export async function createLead(data: any) {
  const res = await fetch("http://localhost:8000/api/leads", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to create lead");
  return res.json();
}

export async function updateLead(id: number, data: any) {
  const res = await fetch(`http://localhost:8000/api/leads/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to update lead");
  return res.json();
}

export async function deleteLead(id: number) {
  const res = await fetch(`http://localhost:8000/api/leads/${id}`, {
    method: "DELETE"
  });
  if (!res.ok) throw new Error("Failed to delete lead");
  return res.json();
} 