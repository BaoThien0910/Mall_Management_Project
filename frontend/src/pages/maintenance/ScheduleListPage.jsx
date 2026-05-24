import { PlusOutlined } from "@ant-design/icons";
import { Form, Input, Modal, message } from "antd";
import { useCallback, useState } from "react";
import PageHeader from "../../components/common/PageHeader";
import ResponsiveTable from "../../components/common/ResponsiveTable";
import StatusTag from "../../components/common/StatusTag";
import { ROLE } from "../../constants/roles";
import { useAuth } from "../../hooks/useAuth";
import { scheduleService } from "../../services/maintenanceService";
import { showApiError } from "../../services/apiClient";
import { useCrudList } from "../../hooks/useCrudList";
import { pick, pickId, formatDate } from "../../utils/data";
export default function ScheduleListPage(){
 const {role}=useAuth(); const canCreate=role===ROLE.TP_VHBT; const [open,setOpen]=useState(false); const [form]=Form.useForm(); const fetcher=useCallback((p)=>scheduleService.list(p),[]); const {items,loading,reload}=useCrudList(fetcher,{page:1,page_size:20});
 const create=async()=>{try{await scheduleService.create(form.getFieldsValue(true)); message.success("Đã lập lịch bảo trì"); setOpen(false); form.resetFields(); reload();}catch(e){showApiError(e)}};
 const columns=[{title:"Mã lịch",render:(_,r)=>pick(r,["ma_lich_bao_tri","ma_lich_bt","MALICHBT"])},{title:"Mặt bằng",render:(_,r)=>pick(r,["ma_mat_bang","MAMB"])},{title:"Nhân viên",render:(_,r)=>pick(r,["ma_nhan_vien_thuc_hien","MANV_THUCHIEN"])},{title:"Ngày dự kiến",render:(_,r)=>formatDate(pick(r,["ngay_thuc_hien_du_kien","NGAYTHUCHIEN_DUKIEN"]))},{title:"Nội dung",render:(_,r)=>pick(r,["noi_dung","NOIDUNG"])},{title:"Trạng thái",render:(_,r)=><StatusTag value={pick(r,["trang_thai","TRANGTHAI"])}/>}];
 return <><PageHeader title="Lịch bảo trì" breadcrumb={["Bảo trì","Lịch bảo trì"]} actionText={canCreate?"Lập lịch":null} actionIcon={<PlusOutlined/>} onAction={()=>setOpen(true)}/><ResponsiveTable rowKey={(r)=>pickId(r,["ma_lich_bao_tri","ma_lich_bt","MALICHBT"])} columns={columns} dataSource={items} loading={loading}/><Modal title="Lập lịch bảo trì" open={open} onCancel={()=>setOpen(false)} onOk={create}><Form form={form} layout="vertical"><Form.Item name="ma_mat_bang" label="Mã mặt bằng" rules={[{required:true}]}><Input/></Form.Item><Form.Item name="ma_nhan_vien_thuc_hien" label="Mã nhân viên thực hiện" rules={[{required:true}]}><Input/></Form.Item><Form.Item name="ngay_thuc_hien_du_kien" label="Ngày thực hiện dự kiến" rules={[{required:true}]}><Input type="datetime-local"/></Form.Item><Form.Item name="noi_dung" label="Nội dung" rules={[{required:true}]}><Input.TextArea rows={4}/></Form.Item></Form></Modal></>;
}
