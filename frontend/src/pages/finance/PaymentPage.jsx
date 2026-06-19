import { Button, Card, Form, Result, Select, Typography, message } from "antd";
import { useSearchParams } from "react-router-dom";
import { useState } from "react";
import PageHeader from "../../components/common/PageHeader";
import { PAYMENT_METHODS } from "../../constants/statuses";
import { paymentService } from "../../services/paymentService";
import { showApiError } from "../../services/apiClient";
const { Text } = Typography;
export default function PaymentPage(){
 const [params]=useSearchParams(); const maCongNo=params.get("ma_cong_no"); const [invoice,setInvoice]=useState(null); const [loading,setLoading]=useState(false);
 const pay=async(values)=>{setLoading(true); try{const created=await paymentService.createSimulatedPayment({ma_cong_no:maCongNo, phuong_thuc:values.phuong_thuc}); const maHoaDon=created?.ma_hoa_don||created?.maHoaDon||created?.MAHOADON; const done=await paymentService.simulateResult(maHoaDon,{ket_qua:"THANH_CONG"}); setInvoice(done||created); message.success("Thanh toán mô phỏng thành công");}catch(e){showApiError(e)}finally{setLoading(false)}};
 return <><PageHeader title="Thanh toán mô phỏng" breadcrumb={["Công nợ","Thanh toán"]}/><Card className="section-card">{invoice?<Result status="success" title="Thanh toán thành công" subTitle={`Mã hóa đơn: ${invoice?.ma_hoa_don||invoice?.MAHOADON||"-"}`}/>:<><Text>Mã công nợ: <b>{maCongNo || "Chưa có"}</b></Text><Form layout="vertical" onFinish={pay} style={{marginTop:20,maxWidth:420}}><Form.Item name="phuong_thuc" label="Phương thức" rules={[{required:true}]}><Select options={PAYMENT_METHODS.map(v=>({value:v,label:v}))}/></Form.Item><Button type="primary" htmlType="submit" loading={loading} disabled={!maCongNo}>Tạo giao dịch và mô phỏng thành công</Button></Form></>}</Card></>;
}
