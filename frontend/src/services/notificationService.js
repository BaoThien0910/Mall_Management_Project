import axiosClient from './axiosClient';

export async function listAnnouncements(params = {}) {
  const { data } = await axiosClient.get('/notifications/announcements', { params });
  return data;
}

export async function getAnnouncementById(id) {
  const { data } = await axiosClient.get(`/notifications/announcements/${id}`);
  return data;
}

export async function createAnnouncement(announcementData) {
  const { data } = await axiosClient.post('/notifications/announcements', announcementData);
  return data;
}

export async function getInbox(params = {}) {
  const { data } = await axiosClient.get('/notifications/inbox', { params });
  return data;
}

export async function markAsRead(messageId) {
  const { data } = await axiosClient.put(`/notifications/inbox/${messageId}/read`);
  return data;
}

export async function markAllAsRead() {
  const { data } = await axiosClient.put('/notifications/inbox/read-all');
  return data;
}

export async function getNotificationStats() {
  const { data } = await axiosClient.get('/notifications/stats');
  return data;
}
