import { useCallback, useState } from "react";
import PageHeader from "../../components/common/PageHeader";
import ResponsiveTable from "../../components/common/ResponsiveTable";
import Toolbar from "../../components/common/Toolbar";
import { auditService } from "../../services/auditService";
import { pick, pickId } from "../../utils/data";
import { useCrudList } from "../../hooks/useCrudList";

export default function AuditLogPage(){
 const [keyword,setKeyword]=useState(""); const fetcher=useCallback((p)=>auditService.list(p),[]); const {items,loading,reload,setParams}=useCrudList(fetcher,{page:1,page_size:20});
 const columns=[{title:"Thời gian",render:(_,r)=>pick(r,["thoi_gian","THOIGIAN"])},{title:"Tài khoản",render:(_,r)=>pick(r,["ma_tai_khoan","ma_tk","MATK"])},{title:"Hành động",render:(_,r)=>pick(r,["hanh_dong","HANHDONG"])},{title:"Đối tượng",render:(_,r)=>pick(r,["doi_tuong","DOITUONG"])},{title:"Chi tiết",render:(_,r)=>pick(r,["chi_tiet","CHITIET"])}];
 return <><PageHeader title="Nhật ký thao tác" breadcrumb={["Quản trị","Nhật ký"]}/><Toolbar keyword={keyword} onKeywordChange={setKeyword} onSearch={()=>setParams({doi_tuong:keyword,page:1,page_size:20})} onReload={reload}/><ResponsiveTable rowKey={(r)=>pickId(r,["ma_nhat_ky","MANHATKY"])} columns={columns} dataSource={items} loading={loading}/></>;
}
