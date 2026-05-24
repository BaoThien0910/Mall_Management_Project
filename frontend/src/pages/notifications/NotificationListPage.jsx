import { PlusOutlined } from "@ant-design/icons";
import { Button, Form, Input, Modal, Select, Space, message } from "antd";
import { useCallback, useState } from "react";
import PageHeader from "../../components/common/PageHeader";
import ResponsiveTable from "../../components/common/ResponsiveTable";
import StatusTag from "../../components/common/StatusTag";
import { DOI_TUONG_NHAN, LOAI_THONG_BAO } from "../../constants/statuses";
import { ROLE } from "../../constants/roles";
import { useAuth } from "../../hooks/useAuth";
import { notificationService } from "../../services/notificationService";
import { showApiError } from "../../services/apiClient";
import { useCrudList } from "../../hooks/useCrudList";
import { pick, pickId, formatDate } from "../../utils/data";
export default function NotificationListPage(){
 const {role}=useAuth(); const canCreate=role===ROLE.BQL; const [open,setOpen]=useState(false); const [form]=Form.useForm(); const fetcher=useCallback((p)=>notificationService.list(p),[]); const {items,loading,reload}=useCrudList(fetcher,{page:1,page_size:20});
 const create=async()=>{try{await notificationService.create(form.getFieldsValue(true)); message.success("Đã ban hành thông báo"); setOpen(false); form.resetFields(); reload();}catch(e){showApiError(e)}};
 const revoke=async(row)=>{try{await notificationService.revoke(pickId(row,["ma_thong_bao","ma_tb","MATB"]),{ly_do:"Thu hồi từ giao diện quản lý"}); message.success("Đã thu hồi thông báo"); reload();}catch(e){showApiError(e)}};
 const columns=[{title:"Tiêu đề",render:(_,r)=>pick(r,["tieu_de","TIEUDE"])},{title:"Loại",render:(_,r)=>pick(r,["loai_thong_bao","LOAITHONGBAO"])},{title:"Đối tượng",render:(_,r)=>pick(r,["doi_tuong_nhan","DOITUONGNHAN"])},{title:"Ngày ban hành",render:(_,r)=>formatDate(pick(r,["ngay_ban_hanh","NGAYBANHANH"]))},{title:"Trạng thái",render:(_,r)=><StatusTag value={pick(r,["trang_thai","TRANGTHAI"])}/>},{title:"Thao tác",align:"right",render:(_,r)=>canCreate&&pick(r,["trang_thai","TRANGTHAI"])==="Đã ban hành"?<Button danger onClick={()=>revoke(r)}>Thu hồi</Button>:null}];
 return <><PageHeader title="Thông báo" breadcrumb={["Thông báo"]} actionText={canCreate?"Ban hành":null} actionIcon={<PlusOutlined/>} onAction={()=>setOpen(true)}/><ResponsiveTable rowKey={(r)=>pickId(r,["ma_thong_bao","ma_tb","MATB"])} columns={columns} dataSource={items} loading={loading}/><Modal title="Ban hành thông báo" open={open} onCancel={()=>setOpen(false)} onOk={create}><Form form={form} layout="vertical"><Form.Item name="tieu_de" label="Tiêu đề" rules={[{required:true}]}><Input/></Form.Item><Form.Item name="loai_thong_bao" label="Loại" rules={[{required:true}]}><Select options={LOAI_THONG_BAO.map(v=>({value:v,label:v}))}/></Form.Item><Form.Item name="doi_tuong_nhan" label="Đối tượng nhận" rules={[{required:true}]}><Select options={DOI_TUONG_NHAN.map(v=>({value:v,label:v}))}/></Form.Item><Form.Item name="noi_dung" label="Nội dung" rules={[{required:true}]}><Input.TextArea rows={5}/></Form.Item></Form></Modal></>;
}
