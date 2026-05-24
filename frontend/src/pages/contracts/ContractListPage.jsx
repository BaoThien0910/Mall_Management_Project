import { PlusOutlined } from "@ant-design/icons";
import { Button, Form, Input, InputNumber, Modal, Space, message } from "antd";
import { useCallback, useState } from "react";
import PageHeader from "../../components/common/PageHeader";
import ResponsiveTable from "../../components/common/ResponsiveTable";
import StatusTag from "../../components/common/StatusTag";
import Toolbar from "../../components/common/Toolbar";
import { HOP_DONG_STATUS } from "../../constants/statuses";
import { contractService } from "../../services/contractService";
import { showApiError } from "../../services/apiClient";
import { pick, pickId, formatMoney, formatDate } from "../../utils/data";
import { useCrudList } from "../../hooks/useCrudList";

export default function ContractListPage(){
 const [status,setStatus]=useState(); const [open,setOpen]=useState(false); const [form]=Form.useForm(); const fetcher=useCallback((p)=>contractService.list(p),[]); const {items,loading,reload,setParams}=useCrudList(fetcher,{page:1,page_size:20});
 const create=async()=>{try{await contractService.create(form.getFieldsValue(true)); message.success("Số hóa hợp đồng thành công"); setOpen(false); form.resetFields(); reload();}catch(e){showApiError(e)}};
 const columns=[{title:"Mã HĐ",render:(_,r)=>pick(r,["ma_hop_dong","ma_hd","MAHD"])},{title:"Khách thuê",render:(_,r)=>pick(r,["ma_khach_thue","ma_kh","MAKH"])},{title:"Mặt bằng",render:(_,r)=>pick(r,["ma_mat_bang","ma_mb","MAMB"])},{title:"Bắt đầu",render:(_,r)=>formatDate(pick(r,["ngay_bat_dau","NGAYBATDAU"]))},{title:"Kết thúc",render:(_,r)=>formatDate(pick(r,["ngay_ket_thuc","NGAYKETTHUC"]))},{title:"Giá thuê",render:(_,r)=>formatMoney(pick(r,["gia_thue_thang","GIATHUETHANG"]))},{title:"Trạng thái",render:(_,r)=><StatusTag value={pick(r,["trang_thai","TRANGTHAI"])}/>}];
 return <><PageHeader title="Số hóa & Quản lý hợp đồng" breadcrumb={["Hợp đồng"]} actionText="Số hóa hợp đồng" actionIcon={<PlusOutlined/>} onAction={()=>setOpen(true)}/><Toolbar status={status} onStatusChange={setStatus} statusOptions={HOP_DONG_STATUS} onSearch={()=>setParams({trang_thai:status,page:1,page_size:20})} onReload={reload}/><ResponsiveTable rowKey={(r)=>pickId(r,["ma_hop_dong","ma_hd","MAHD"])} columns={columns} dataSource={items} loading={loading}/>
 <Modal width={720} title="Số hóa hợp đồng" open={open} onCancel={()=>setOpen(false)} onOk={create} okText="Tạo hợp đồng"><Form form={form} layout="vertical"><Space direction="vertical" style={{width:"100%"}}><Form.Item name="ma_hop_dong" label="Mã hợp đồng" rules={[{required:true}]}><Input/></Form.Item><Form.Item name="ma_khach_thue" label="Mã khách thuê" rules={[{required:true}]}><Input/></Form.Item><Form.Item name="ma_mat_bang" label="Mã mặt bằng" rules={[{required:true}]}><Input/></Form.Item><Form.Item name="ma_yeu_cau" label="Mã yêu cầu thuê thêm nếu có"><Input/></Form.Item><Form.Item name="ngay_bat_dau" label="Ngày bắt đầu" rules={[{required:true}]}><Input type="date"/></Form.Item><Form.Item name="ngay_ket_thuc" label="Ngày kết thúc" rules={[{required:true}]}><Input type="date"/></Form.Item><Form.Item name="gia_thue_thang" label="Giá thuê tháng" rules={[{required:true}]}><InputNumber style={{width:"100%"}} min={1}/></Form.Item></Space></Form></Modal></>;
}
