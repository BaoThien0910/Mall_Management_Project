import { PlusOutlined } from "@ant-design/icons";
import { Form, Input, Modal, Select, message } from "antd";
import { useCallback, useState } from "react";
import PageHeader from "../../components/common/PageHeader";
import ResponsiveTable from "../../components/common/ResponsiveTable";
import StatusTag from "../../components/common/StatusTag";
import { ROLE } from "../../constants/roles";
import { useAuth } from "../../hooks/useAuth";
import { MAT_BANG_STATUS } from "../../constants/statuses";
import { maintenanceReportService } from "../../services/maintenanceService";
import { showApiError } from "../../services/apiClient";
import { useCrudList } from "../../hooks/useCrudList";
import { pick, pickId, formatDate } from "../../utils/data";
export default function MaintenanceReportPage(){
 const {role}=useAuth(); const canCreate=role===ROLE.TP_VHBT; const [open,setOpen]=useState(false); const [form]=Form.useForm(); const fetcher=useCallback((p)=>maintenanceReportService.list(p),[]); const {items,loading,reload}=useCrudList(fetcher,{page:1,page_size:20});
 const create=async()=>{try{await maintenanceReportService.createPremiseStatusReport(form.getFieldsValue(true)); message.success("Đã lập báo cáo bảo trì"); setOpen(false); form.resetFields(); reload();}catch(e){showApiError(e)}};
 const columns=[{title:"Mã báo cáo",render:(_,r)=>pick(r,["ma_bao_cao_bao_tri","ma_bc_bt","MABC_BT"])},{title:"Mặt bằng",render:(_,r)=>pick(r,["ma_mat_bang","MAMB"])},{title:"Ngày lập",render:(_,r)=>formatDate(pick(r,["ngay_lap","NGAYLAP"]))},{title:"Trạng thái thực tế",render:(_,r)=><StatusTag value={pick(r,["trang_thai_thuc_te","TRANGTHAI_THUCTE"])}/>},{title:"Nội dung",render:(_,r)=>pick(r,["noi_dung","NOIDUNG"])},{title:"Kết luận",render:(_,r)=>pick(r,["ket_luan","KETLUAN"])}];
 return <><PageHeader title="Báo cáo bảo trì" breadcrumb={["Báo cáo","Bảo trì"]} actionText={canCreate?"Lập báo cáo":null} actionIcon={<PlusOutlined/>} onAction={()=>setOpen(true)}/><ResponsiveTable rowKey={(r)=>pickId(r,["ma_bao_cao_bao_tri","ma_bc_bt","MABC_BT"])} columns={columns} dataSource={items} loading={loading}/><Modal title="Lập báo cáo trạng thái mặt bằng" open={open} onCancel={()=>setOpen(false)} onOk={create}><Form form={form} layout="vertical"><Form.Item name="ma_mat_bang" label="Mã mặt bằng" rules={[{required:true}]}><Input/></Form.Item><Form.Item name="trang_thai_thuc_te" label="Trạng thái thực tế" rules={[{required:true}]}><Select options={MAT_BANG_STATUS.map(v=>({value:v,label:v}))}/></Form.Item><Form.Item name="noi_dung" label="Nội dung" rules={[{required:true}]}><Input.TextArea rows={4}/></Form.Item><Form.Item name="ket_luan" label="Kết luận"><Input.TextArea rows={3}/></Form.Item></Form></Modal></>;
}
