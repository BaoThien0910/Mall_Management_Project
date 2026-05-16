import { configureStore } from '@reduxjs/toolkit';
import authReducer from './authSlice';
import permissionReducer from './permissionSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    permissions: permissionReducer,
  },
});
