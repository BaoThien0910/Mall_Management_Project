import { SaveOutlined } from "@ant-design/icons";
import { Button, Card, Col, List, Row, Select, Space, Typography, message } from "antd";
import { useEffect, useState } from "react";
import PageHeader from "../../components/common/PageHeader";
import { rbacService } from "../../services/rbacService";
import { showApiError } from "../../services/apiClient";
import { pick, toArray } from "../../utils/data";

const { Text } = Typography;
export default function RbacPage() {
  const [roles, setRoles] = useState([]); const [permissions, setPermissions] = useState([]); const [selectedRole, setSelectedRole] = useState(); const [selectedPerms, setSelectedPerms] = useState([]); const [loading, setLoading] = useState(false);
  const load = async () => { try { const [r, p] = await Promise.all([rbacService.listRoles(), rbacService.listPermissions()]); setRoles(toArray(r)); setPermissions(toArray(p)); } catch(e) { showApiError(e); } };
  useEffect(() => { load(); }, []);
  const loadRolePerms = async (role) => { setSelectedRole(role); if (!role) return; try { const data = await rbacService.getPermissionsByRole(role); setSelectedPerms(toArray(data?.danh_sach_quyen || data?.permissions).map((x) => pick(x, ["ma_quyen", "MAQUYEN"]))); } catch(e) { showApiError(e); } };
  const save = async () => { setLoading(true); try { await rbacService.assignPermissions(selectedRole, selectedPerms); message.success("Đã cập nhật quyền cho vai trò"); } catch(e) { showApiError(e); } finally { setLoading(false); } };
  return <><PageHeader title="Vai trò & quyền" breadcrumb={["Quản trị", "RBAC"]} />
    <Row gutter={[16,16]}><Col xs={24} md={8}><Card title="Vai trò"><List dataSource={roles} renderItem={(r) => { const id=pick(r,["ma_vai_tro","MAVAITRO"]); return <List.Item onClick={() => loadRolePerms(id)} className={selectedRole===id?"clickable-list active":"clickable-list"}>{id} — {pick(r,["ten_vai_tro","TENVAITRO"])}</List.Item> }} /></Card></Col><Col xs={24} md={16}><Card title="Gán quyền"><Space direction="vertical" style={{width:"100%"}} size={16}><Text>Vai trò đang chọn: <b>{selectedRole || "Chưa chọn"}</b></Text><Select mode="multiple" allowClear style={{width:"100%"}} placeholder="Chọn quyền" value={selectedPerms} onChange={setSelectedPerms} options={permissions.map((p)=>({value:pick(p,["ma_quyen","MAQUYEN"]), label:`${pick(p,["ma_quyen","MAQUYEN"])} - ${pick(p,["ten_quyen","TENQUYEN"])}`}))} /><Button type="primary" icon={<SaveOutlined />} disabled={!selectedRole} loading={loading} onClick={save}>Lưu phân quyền</Button></Space></Card></Col></Row>
  </>;
}
