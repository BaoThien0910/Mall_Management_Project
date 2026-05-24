import { Button } from "antd";
import { useCallback } from "react";
import { useNavigate } from "react-router-dom";
import PageHeader from "../../components/common/PageHeader";
import ResponsiveTable from "../../components/common/ResponsiveTable";
import StatusTag from "../../components/common/StatusTag";
import StatCard from "../../components/common/StatCard";
import { ROUTES } from "../../constants/routes";
import { debtService } from "../../services/debtService";
import { useCrudList } from "../../hooks/useCrudList";
import { pick, pickId, formatMoney } from "../../utils/data";
export default function MyDebtListPage(){
 const navigate=useNavigate(); const fetcher=useCallback((p)=>debtService.myDebts(p),[]); const {items,loading}=useCrudList(fetcher,{page:1,page_size:20});
 const unpaid=items.filter((r)=>pick(r,["trang_thai","TRANGTHAI"])!=="Đã thanh toán"); const total=unpaid.reduce((s,r)=>s+Number(pick(r,["tong_tien","TONGTIEN"],0)),0);
 const columns=[{title:"Mã công nợ",render:(_,r)=>pick(r,["ma_cong_no","ma_cn","MACN"])},{title:"Kỳ",render:(_,r)=>`${pick(r,["thang","THANG"])} / ${pick(r,["nam","NAM"])}`},{title:"Tổng phải trả",render:(_,r)=>formatMoney(pick(r,["tong_tien","TONGTIEN"]))},{title:"Trạng thái",render:(_,r)=><StatusTag value={pick(r,["trang_thai","TRANGTHAI"])}/>},{title:"Thao tác",align:"right",render:(_,r)=>pick(r,["trang_thai","TRANGTHAI"])!=="Đã thanh toán"?<Button type="link" onClick={()=>navigate(`${ROUTES.PAYMENT}?ma_cong_no=${pickId(r,["ma_cong_no","ma_cn","MACN"])}`)}>Thanh toán</Button>:<Button type="link">Chi tiết</Button>}];
 return <><PageHeader title="Công nợ & Thanh toán" breadcrumb={["Trang chủ","Công nợ & thanh toán"]}/><div className="stats-grid"><StatCard label="Số kỳ công nợ" value={items.length}/><StatCard label="Tổng còn phải trả" value={formatMoney(total)} danger/><StatCard label="Kỳ quá hạn" value={items.filter((r)=>pick(r,["trang_thai","TRANGTHAI"])==="Quá hạn").length}/></div><ResponsiveTable rowKey={(r)=>pickId(r,["ma_cong_no","ma_cn","MACN"])} columns={columns} dataSource={items} loading={loading}/></>;
}
