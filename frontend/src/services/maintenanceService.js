import axiosClient from './axiosClient';

export function normalizeTicketList(data) {
  if (Array.isArray(data)) return data;
  if (data && Array.isArray(data.items)) return data.items;
  return [];
}

export async function listTickets(params = {}) {
  const { data } = await axiosClient.get('/maintenance/tickets', { params });
  return data;
}

export async function getTicketById(id) {
  const { data } = await axiosClient.get(`/maintenance/tickets/${id}`);
  return data;
}

export async function createTicket(ticketData) {
  const { data } = await axiosClient.post('/maintenance/tickets', ticketData);
  return data;
}

export async function updateTicketStatus(ticketId, status) {
  const { data } = await axiosClient.put(`/maintenance/tickets/${ticketId}/status`, {
    status,
  });
  return data;
}

export async function assignTicket(ticketId, assignedTo) {
  const { data } = await axiosClient.put(`/maintenance/tickets/${ticketId}/assign`, {
    assigned_to: assignedTo,
  });
  return data;
}

export async function listSchedule(params = {}) {
  const { data } = await axiosClient.get('/maintenance/schedule', { params });
  return data;
}

export async function getStatistics() {
  const { data } = await axiosClient.get('/maintenance/statistics');
  return data;
}
