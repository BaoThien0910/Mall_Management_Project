import { createSlice } from '@reduxjs/toolkit';

function readCodes() {
  try {
    return JSON.parse(sessionStorage.getItem('permissions') || '[]');
  } catch {
    return [];
  }
}

const permissionSlice = createSlice({
  name: 'permissions',
  initialState: { codes: readCodes() },
  reducers: {
    setCodes(state, action) {
      state.codes = Array.isArray(action.payload) ? action.payload : [];
      sessionStorage.setItem('permissions', JSON.stringify(state.codes));
    },
    clearCodes(state) {
      state.codes = [];
      sessionStorage.removeItem('permissions');
    },
  },
});

export const { setCodes, clearCodes } = permissionSlice.actions;
export default permissionSlice.reducer;
