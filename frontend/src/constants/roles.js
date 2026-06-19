export const ROLE = {
  QTV: "QTV",
  BQL: "BQL",
  TP_KDTC: "TP_KDTC",
  NV_KDTC: "NV_KDTC",
  TP_VHBT: "TP_VHBT",
  NV_VHBT: "NV_VHBT",
  KHACH_THUE: "KHACH_THUE",
};

export const ROLE_LABEL = {
  [ROLE.QTV]: "Quản trị viên",
  [ROLE.BQL]: "Ban Quản Lý",
  [ROLE.TP_KDTC]: "Trưởng phòng Kinh doanh - Tài chính",
  [ROLE.NV_KDTC]: "Nhân viên Kinh doanh - Tài chính",
  [ROLE.TP_VHBT]: "Trưởng phòng Vận hành - Bảo trì",
  [ROLE.NV_VHBT]: "Nhân viên Vận hành - Bảo trì",
  [ROLE.KHACH_THUE]: "Khách thuê",
};

export const INTERNAL_ROLES = [
  ROLE.QTV,
  ROLE.BQL,
  ROLE.TP_KDTC,
  ROLE.NV_KDTC,
  ROLE.TP_VHBT,
  ROLE.NV_VHBT,
];

export const KDTC_ROLES = [ROLE.TP_KDTC, ROLE.NV_KDTC];
export const VHBT_ROLES = [ROLE.TP_VHBT, ROLE.NV_VHBT];
export const MANAGER_ROLES = [ROLE.BQL, ROLE.TP_KDTC, ROLE.TP_VHBT];
