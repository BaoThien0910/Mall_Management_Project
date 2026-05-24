import { UploadOutlined } from "@ant-design/icons";
import { Button, Card, Upload, message } from "antd";
import { useCallback, useState } from "react";
import PageHeader from "../../components/common/PageHeader";
import ResponsiveTable from "../../components/common/ResponsiveTable";
import { financialImportService } from "../../services/financialImportService";
import { showApiError } from "../../services/apiClient";
import { useCrudList } from "../../hooks/useCrudList";
import { pick, pickId, formatMoney } from "../../utils/data";
export default function FinancialImportPage(){
 const [file,setFile]=useState(null); const fetcher=useCallback((p)=>financialImportService.list(p),[]); const {items,loading,reload}=useCrudList(fetcher,{page:1,page_size:20});
 const upload=async()=>{if(!file) return message.warning("Chọn file .xlsx trước"); try{const res=await financialImportService.upload(file); message.success(`Import thành công: ${res?.so_dong_hop_le ?? ""} dòng hợp lệ`); setFile(null); reload();}catch(e){showApiError(e)}};
 const columns=[{title:"Mã import",render:(_,r)=>pick(r,["ma_import","MAIMPORT"])},{title:"Hợp đồng",render:(_,r)=>pick(r,["ma_hop_dong","MAHD"])},{title:"Kỳ",render:(_,r)=>`${pick(r,["thang","THANG"])} / ${pick(r,["nam","NAM"])}`},{title:"Loại khoản",render:(_,r)=>pick(r,["loai_khoan","LOAIKHOAN"])},{title:"Số tiền",render:(_,r)=>formatMoney(pick(r,["so_tien","SOTIEN"]))},{title:"Trạng thái",render:(_,r)=>pick(r,["trang_thai","TRANGTHAI"])}];
 return <><PageHeader title="Import tài chính" breadcrumb={["Tài chính","Import Excel"]}/><Card className="section-card"><Upload beforeUpload={(f)=>{setFile(f); return false;}} maxCount={1} accept=".xlsx"><Button icon={<UploadOutlined/>}>Chọn file .xlsx</Button></Upload><Button type="primary" onClick={upload} style={{marginTop:16}}>Tải lên và xử lý</Button></Card><ResponsiveTable rowKey={(r)=>pickId(r,["ma_import","MAIMPORT"])} columns={columns} dataSource={items} loading={loading}/></>;
}
