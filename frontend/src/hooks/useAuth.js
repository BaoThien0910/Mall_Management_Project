import { useDispatch, useSelector } from "react-redux";
import { useNavigate } from "react-router-dom";
import { logoutLocal } from "../store/authSlice";

export function useAuth() {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const auth = useSelector((state) => state.auth);
  const user = auth.user;
  const role = user?.ma_vai_tro || user?.maVaiTro || user?.role;

  const logout = () => {
    dispatch(logoutLocal());
    navigate("/login", { replace: true });
  };

  return { ...auth, user, role, logout };
}
