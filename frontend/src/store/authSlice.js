import { createSlice } from '@reduxjs/toolkit';

function sessionAuth() {
  return {
    token: sessionStorage.getItem('token'),
    role: sessionStorage.getItem('role'),
    email: sessionStorage.getItem('email'),
  };
}

const initialState = sessionAuth();

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    setCredentials(state, action) {
      const { token, role, email } = action.payload;
      state.token = token;
      state.role = role ?? null;
      state.email = email ?? null;
      if (token) sessionStorage.setItem('token', token);
      else sessionStorage.removeItem('token');
      if (role != null) sessionStorage.setItem('role', role);
      else sessionStorage.removeItem('role');
      if (email) sessionStorage.setItem('email', email);
      else sessionStorage.removeItem('email');
    },
    logout(state) {
      state.token = null;
      state.role = null;
      state.email = null;
      sessionStorage.removeItem('token');
      sessionStorage.removeItem('role');
      sessionStorage.removeItem('email');
      sessionStorage.removeItem('permissions');
    },
  },
});

export const { setCredentials, logout } = authSlice.actions;
export default authSlice.reducer;
