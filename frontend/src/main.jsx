import React from "react";
import ReactDOM from "react-dom/client";
import { Provider } from "react-redux";
import { ConfigProvider } from "antd";
import viVN from "antd/locale/vi_VN";
import App from "./App.jsx";
import { store } from "./store";
import "antd/dist/reset.css";
import "./styles/global.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <Provider store={store}>
      <ConfigProvider locale={viVN} theme={{ token: { colorPrimary: "#1677ff", borderRadius: 8 } }}>
        <App />
      </ConfigProvider>
    </Provider>
  </React.StrictMode>
);
