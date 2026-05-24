import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import { authService } from "../services/authService";
import { clearAccessToken, getAccessToken, setAccessToken } from "../utils/storage";

export const login = createAsyncThunk("auth/login", async (payload) => {
  const tokenData = await authService.login(payload);
  const token = tokenData?.access_token || tokenData?.token || tokenData?.accessToken;
  setAccessToken(token);
  const user = await authService.getCurrentUser();
  return { token, user };
});

export const bootstrapAuth = createAsyncThunk("auth/bootstrap", async (_, { rejectWithValue }) => {
  const token = getAccessToken();
  if (!token) return rejectWithValue("NO_TOKEN");
  const user = await authService.getCurrentUser();
  return { token, user };
});

const authSlice = createSlice({
  name: "auth",
  initialState: {
    token: getAccessToken(),
    user: null,
    loading: false,
    bootstrapped: false,
  },
  reducers: {
    logoutLocal(state) {
      state.token = null;
      state.user = null;
      clearAccessToken();
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(login.pending, (state) => { state.loading = true; })
      .addCase(login.fulfilled, (state, action) => {
        state.loading = false;
        state.token = action.payload.token;
        state.user = action.payload.user;
        state.bootstrapped = true;
      })
      .addCase(login.rejected, (state) => { state.loading = false; })
      .addCase(bootstrapAuth.pending, (state) => { state.loading = true; })
      .addCase(bootstrapAuth.fulfilled, (state, action) => {
        state.loading = false;
        state.bootstrapped = true;
        state.token = action.payload.token;
        state.user = action.payload.user;
      })
      .addCase(bootstrapAuth.rejected, (state) => {
        state.loading = false;
        state.bootstrapped = true;
        state.token = null;
        state.user = null;
        clearAccessToken();
      });
  },
});

export const { logoutLocal } = authSlice.actions;
export default authSlice.reducer;
