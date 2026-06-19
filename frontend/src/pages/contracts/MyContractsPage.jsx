import { useCallback } from "react";
import PageHeader from "../../components/common/PageHeader";
import ResponsiveTable from "../../components/common/ResponsiveTable";
import StatusTag from "../../components/common/StatusTag";
import { contractService } from "../../services/contractService";
import { pick, pickId, formatMoney, formatDate } from "../../utils/data";
import { useCrudList } from "../../hooks/useCrudList";
export default function MyContractsPage(){
 const fetcher=useCallback((p)=>contractService.myContracts(p),[]); const {items,loading,reload}=useCrudList(fetcher,{page:1,page_size:20});
 const columns=[{title:"Mã HĐ",render:(_,r)=>pick(r,["ma_hop_dong","MAHD"])},{title:"Mặt bằng",render:(_,r)=>pick(r,["ma_mat_bang","MAMB"])},{title:"Bắt đầu",render:(_,r)=>formatDate(pick(r,["ngay_bat_dau","NGAYBATDAU"]))},{title:"Kết thúc",render:(_,r)=>formatDate(pick(r,["ngay_ket_thuc","NGAYKETTHUC"]))},{title:"Giá thuê",render:(_,r)=>formatMoney(pick(r,["gia_thue_thang","GIATHUETHANG"]))},{title:"Trạng thái",render:(_,r)=><StatusTag value={pick(r,["trang_thai","TRANGTHAI"])}/>}];
 return <><PageHeader title="Hợp đồng của tôi" breadcrumb={["Khách thuê","Hợp đồng"]}/><ResponsiveTable rowKey={(r)=>pickId(r,["ma_hop_dong","MAHD"])} columns={columns} dataSource={items} loading={loading}/></>;
}
