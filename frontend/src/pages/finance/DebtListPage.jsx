import { CalculatorOutlined } from "@ant-design/icons";
import { Button, Form, InputNumber, Modal, Space, message } from "antd";
import { useCallback, useState } from "react";
import PageHeader from "../../components/common/PageHeader";
import ResponsiveTable from "../../components/common/ResponsiveTable";
import StatusTag from "../../components/common/StatusTag";
import { debtService } from "../../services/debtService";
import { showApiError } from "../../services/apiClient";
import { useCrudList } from "../../hooks/useCrudList";
import { pick, pickId, formatMoney } from "../../utils/data";
export default function DebtListPage(){
 const [open,setOpen]=useState(false); const [form]=Form.useForm(); const fetcher=useCallback((p)=>debtService.list(p),[]); const {items,loading,reload}=useCrudList(fetcher,{page:1,page_size:20});
 const calculate=async()=>{try{await debtService.calculate(form.getFieldsValue(true)); message.success("Đã tính công nợ"); setOpen(false); form.resetFields(); reload();}catch(e){showApiError(e)}};
 const columns=[{title:"Mã CN",render:(_,r)=>pick(r,["ma_cong_no","ma_cn","MACN"])},{title:"Hợp đồng",render:(_,r)=>pick(r,["ma_hop_dong","MAHD"])},{title:"Kỳ",render:(_,r)=>`${pick(r,["thang","THANG"])} / ${pick(r,["nam","NAM"])}`},{title:"Tổng tiền",render:(_,r)=>formatMoney(pick(r,["tong_tien","TONGTIEN"]))},{title:"Hạn thanh toán",render:(_,r)=>pick(r,["han_thanh_toan","HAN_THANHTOAN"],"-")},{title:"Trạng thái",render:(_,r)=><StatusTag value={pick(r,["trang_thai","TRANGTHAI"])}/>}];
 return <><PageHeader title="Công nợ" breadcrumb={["Tài chính","Công nợ"]} actionText="Tính công nợ" actionIcon={<CalculatorOutlined/>} onAction={()=>setOpen(true)}/><ResponsiveTable rowKey={(r)=>pickId(r,["ma_cong_no","ma_cn","MACN"])} columns={columns} dataSource={items} loading={loading}/><Modal title="Tính công nợ từ dữ liệu import" open={open} onCancel={()=>setOpen(false)} onOk={calculate} okText="Tính công nợ"><Form form={form} layout="vertical"><Space style={{width:"100%"}}><Form.Item name="thang" label="Tháng" rules={[{required:true}]}><InputNumber min={1} max={12}/></Form.Item><Form.Item name="nam" label="Năm" rules={[{required:true}]}><InputNumber min={2000} max={2100}/></Form.Item></Space></Form></Modal></>;
}
