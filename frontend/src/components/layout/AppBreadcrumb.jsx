import React from 'react';
import { Breadcrumb } from 'antd';
import { useLocation, Link } from 'react-router-dom';
import { HomeOutlined } from '@ant-design/icons';
import { breadcrumbsFor } from '../../constants/routeMeta';

function dashboardFor(pathname) {
  if (pathname.startsWith('/admin')) return '/admin';
  if (pathname.startsWith('/tenant')) return '/tenant';
  if (pathname.startsWith('/staff')) return '/staff';
  if (pathname.startsWith('/management')) return '/management';
  return '/login';
}

export default function AppBreadcrumb() {
  const { pathname } = useLocation();
  const crumbs = breadcrumbsFor(pathname);
  const root = dashboardFor(pathname);

  const items = [
    {
      title: (
        <Link to={root}>
          <HomeOutlined /> Trang chủ
        </Link>
      ),
    },
    ...crumbs.map((c, idx) =>
      idx < crumbs.length - 1 ? { title: <span>{c.title}</span> } : { title: c.title }
    ),
  ];

  return <Breadcrumb style={{ marginBottom: 16 }} items={items} />;
}
