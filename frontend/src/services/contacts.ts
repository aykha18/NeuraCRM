export async function fetchContacts() {
  const res = await fetch("http://localhost:8000/api/contacts");
  if (!res.ok) throw new Error("Failed to fetch contacts");
  return res.json();
}

export async function getContact(id: number) {
  const res = await fetch(`http://localhost:8000/api/contacts/${id}`);
  if (!res.ok) throw new Error("Failed to fetch contact");
  return res.json();
}

export async function updateContact(id: number, data: any) {
  const res = await fetch(`http://localhost:8000/api/contacts/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to update contact");
  return res.json();
}

export async function deleteContact(id: number) {
  const res = await fetch(`http://localhost:8000/api/contacts/${id}`, {
    method: "DELETE"
  });
  if (!res.ok) throw new Error("Failed to delete contact");
  return res.json();
}