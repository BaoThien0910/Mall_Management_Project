import axiosClient from './axiosClient';

export const loginAPI = async (credentials) => {
  const response = await axiosClient.post("/login", credentials);
  return response.data; 
};