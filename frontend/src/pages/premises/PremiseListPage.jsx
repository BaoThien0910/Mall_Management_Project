import { DeleteOutlined, PlusOutlined } from "@ant-design/icons";
import { Button, Form, Input, InputNumber, Modal, Popconfirm, Select, Space, message } from "antd";
import { useCallback, useState } from "react";
import PageHeader from "../../components/common/PageHeader";
import ResponsiveTable from "../../components/common/ResponsiveTable";
import StatusTag from "../../components/common/StatusTag";
import Toolbar from "../../components/common/Toolbar";
import { MAT_BANG_STATUS } from "../../constants/statuses";
import { ROLE } from "../../constants/roles";
import { useAuth } from "../../hooks/useAuth";
import { useCrudList } from "../../hooks/useCrudList";
import { premiseService } from "../../services/premiseService";
import { showApiError } from "../../services/apiClient";
import { pick, pickId } from "../../utils/data";

export default function PremiseListPage(){
 const {role}=useAuth(); const canWrite=[ROLE.TP_VHBT,ROLE.NV_VHBT].includes(role); const [status,setStatus]=useState(); const [open,setOpen]=useState(false); const [form]=Form.useForm(); const fetcher=useCallback((p)=>premiseService.list(p),[]); const {items,loading,reload,setParams}=useCrudList(fetcher,{page:1,page_size:20});
 const create=async()=>{try{await premiseService.create(form.getFieldsValue(true)); message.success("Tạo mặt bằng thành công"); setOpen(false); form.resetFields(); reload();}catch(e){showApiError(e)}};
 const remove=async(row)=>{try{await premiseService.remove(pickId(row,["ma_mat_bang","ma_mb","MAMB"])); message.success("Đã xóa mặt bằng"); reload();}catch(e){showApiError(e)}};
 const columns=[{title:"Mã",render:(_,r)=>pick(r,["ma_mat_bang","ma_mb","MAMB"])},{title:"Vị trí",render:(_,r)=>pick(r,["vi_tri","VITRI"])},{title:"Tầng",render:(_,r)=>pick(r,["tang","TANG"])},{title:"Diện tích",render:(_,r)=>pick(r,["dien_tich","DIENTICH"])},{title:"Loại",render:(_,r)=>pick(r,["loai_mat_bang","loai_mb","LOAIMB"])},{title:"Trạng thái",render:(_,r)=><StatusTag value={pick(r,["trang_thai","TRANGTHAI"])}/>},{title:"Thao tác",align:"right",render:(_,r)=>canWrite?<Space><Popconfirm title="Xóa mặt bằng?" onConfirm={()=>remove(r)}><Button danger type="text" icon={<DeleteOutlined/>}/></Popconfirm></Space>:null}];
 return <><PageHeader title="Mặt bằng" subtitle={role===ROLE.KHACH_THUE?"Danh sách mặt bằng còn trống để gửi yêu cầu thuê thêm.":"Quản lý trạng thái và thông tin mặt bằng."} breadcrumb={["Mặt bằng"]} actionText={canWrite?"Thêm mặt bằng":null} actionIcon={<PlusOutlined/>} onAction={()=>setOpen(true)}/><Toolbar status={status} onStatusChange={setStatus} statusOptions={MAT_BANG_STATUS} onSearch={()=>setParams({trang_thai:status,page:1,page_size:20})} onReload={reload}/><ResponsiveTable rowKey={(r)=>pickId(r,["ma_mat_bang","ma_mb","MAMB"])} columns={columns} dataSource={items} loading={loading}/>
 <Modal title="Thêm mặt bằng" open={open} onCancel={()=>setOpen(false)} onOk={create} okText="Tạo"><Form form={form} layout="vertical"><Form.Item name="ma_mat_bang" label="Mã mặt bằng" rules={[{required:true}]}><Input/></Form.Item><Form.Item name="vi_tri" label="Vị trí" rules={[{required:true}]}><Input/></Form.Item><Form.Item name="tang" label="Tầng" rules={[{required:true}]}><InputNumber style={{width:"100%"}}/></Form.Item><Form.Item name="dien_tich" label="Diện tích" rules={[{required:true}]}><InputNumber style={{width:"100%"}} min={1}/></Form.Item><Form.Item name="loai_mat_bang" label="Loại mặt bằng" rules={[{required:true}]}><Input/></Form.Item><Form.Item name="trang_thai" label="Trạng thái" rules={[{required:true}]}><Select options={MAT_BANG_STATUS.map(v=>({value:v,label:v}))}/></Form.Item><Form.Item name="ghi_chu" label="Ghi chú"><Input.TextArea/></Form.Item></Form></Modal></>;
}
