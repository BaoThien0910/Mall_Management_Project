import { PlusOutlined } from "@ant-design/icons";
import { Button, Form, Input, InputNumber, Modal, Select, Space, message } from "antd";
import { useCallback, useState } from "react";
import PageHeader from "../../components/common/PageHeader";
import ResponsiveTable from "../../components/common/ResponsiveTable";
import StatusTag from "../../components/common/StatusTag";
import { ROLE } from "../../constants/roles";
import { useAuth } from "../../hooks/useAuth";
import { financialReportService } from "../../services/financialReportService";
import { showApiError } from "../../services/apiClient";
import { useCrudList } from "../../hooks/useCrudList";
import { pick, pickId, formatMoney } from "../../utils/data";
export default function FinancialReportPage(){
 const {role}=useAuth(); const canCreate=role===ROLE.TP_KDTC; const [open,setOpen]=useState(false); const [form]=Form.useForm(); const fetcher=useCallback((p)=>financialReportService.list(p),[]); const {items,loading,reload}=useCrudList(fetcher,{page:1,page_size:20});
 const create=async()=>{try{const v=form.getFieldsValue(true); if(v.loai_bao_cao==="Báo cáo doanh số") await financialReportService.createRevenueReport(v); else await financialReportService.createDebtReport(v); message.success("Đã tạo báo cáo bản nháp"); setOpen(false); form.resetFields(); reload();}catch(e){showApiError(e)}};
 const publish=async(r)=>{try{await financialReportService.publish(pickId(r,["ma_bao_cao_tai_chinh","ma_bctc","MABCTC"])); message.success("Đã ban hành báo cáo"); reload();}catch(e){showApiError(e)}};
 const columns=[{title:"Mã BC",render:(_,r)=>pick(r,["ma_bao_cao_tai_chinh","ma_bctc","MABCTC"])},{title:"Loại",render:(_,r)=>pick(r,["loai_bao_cao","LOAIBAOCAO"])},{title:"Kỳ",render:(_,r)=>`${pick(r,["thang","THANG"])} / ${pick(r,["nam","NAM"])}`},{title:"Tổng tiền",render:(_,r)=>formatMoney(pick(r,["tong_tien","TONGTIEN"]))},{title:"Trạng thái",render:(_,r)=><StatusTag value={pick(r,["trang_thai","TRANGTHAI"])}/>},{title:"Thao tác",align:"right",render:(_,r)=>canCreate&&pick(r,["trang_thai","TRANGTHAI"])==="Bản nháp"?<Button onClick={()=>publish(r)}>Ban hành</Button>:null}];
 return <><PageHeader title="Báo cáo tài chính" breadcrumb={["Báo cáo","Tài chính"]} actionText={canCreate?"Lập báo cáo":null} actionIcon={<PlusOutlined/>} onAction={()=>setOpen(true)}/><ResponsiveTable rowKey={(r)=>pickId(r,["ma_bao_cao_tai_chinh","ma_bctc","MABCTC"])} columns={columns} dataSource={items} loading={loading}/><Modal title="Lập báo cáo tài chính" open={open} onCancel={()=>setOpen(false)} onOk={create}><Form form={form} layout="vertical"><Form.Item name="loai_bao_cao" label="Loại báo cáo" rules={[{required:true}]}><Select options={["Báo cáo công nợ","Báo cáo doanh số"].map(v=>({value:v,label:v}))}/></Form.Item><Space><Form.Item name="thang" label="Tháng" rules={[{required:true}]}><InputNumber min={1} max={12}/></Form.Item><Form.Item name="nam" label="Năm" rules={[{required:true}]}><InputNumber min={2000} max={2100}/></Form.Item></Space><Form.Item name="noi_dung" label="Nội dung" rules={[{required:true}]}><Input.TextArea rows={4}/></Form.Item></Form></Modal></>;
}
