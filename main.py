
from __future__ import annotations

import asyncio
import json
import re
import ssl
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any

from astrbot.api import AstrBotConfig, logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star


PANEL_TEMPLATE = r"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<title>Sub2API 面板</title>
<style>
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: "Segoe UI", "Microsoft YaHei", Arial, sans-serif;
  background:
    radial-gradient(circle at top left, rgba(108,92,231,0.28), transparent 32%),
    radial-gradient(circle at top right, rgba(0,206,201,0.22), transparent 28%),
    linear-gradient(180deg, #0b1020 0%, #11172b 45%, #171d35 100%);
  color: #eef2ff;
}
.wrapper {
  width: 1240px;
  margin: 0 auto;
  padding: 34px;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}
.brand {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.brand .badge {
  display: inline-flex;
  align-items: center;
  width: fit-content;
  padding: 8px 14px;
  border-radius: 999px;
  background: rgba(255,255,255,0.08);
  color: #c7d2fe;
  font-size: 14px;
  letter-spacing: .4px;
  border: 1px solid rgba(255,255,255,.08);
}
.brand h1 {
  margin: 0;
  font-size: 40px;
  line-height: 1.15;
  letter-spacing: 0.5px;
}
.brand .sub {
  color: #cbd5e1;
  font-size: 15px;
}
.top-meta {
  text-align: right;
  color: #dbe4ff;
  font-size: 14px;
}
.top-meta .time {
  font-size: 22px;
  font-weight: 700;
  color: #ffffff;
}
.grid4 {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 18px;
  margin-bottom: 20px;
}
.card {
  position: relative;
  overflow: hidden;
  border-radius: 24px;
  padding: 22px;
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.10);
  box-shadow: 0 14px 34px rgba(0,0,0,0.22);
  backdrop-filter: blur(12px);
}
.card::before {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(145deg, rgba(255,255,255,0.08), transparent 46%);
  pointer-events: none;
}
.metric-label {
  color: #c7d2fe;
  font-size: 15px;
  margin-bottom: 10px;
}
.metric-value {
  font-size: 34px;
  font-weight: 800;
  line-height: 1.1;
  color: #ffffff;
}
.metric-sub {
  margin-top: 10px;
  color: #b8c4ea;
  font-size: 13px;
}
.layout {
  display: grid;
  grid-template-columns: 1.28fr 1fr;
  gap: 18px;
  margin-bottom: 18px;
}
.section-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}
.section-title h2 {
  margin: 0;
  font-size: 22px;
}
.section-title .hint {
  font-size: 13px;
  color: #b9c5e7;
}
.account-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.account-item {
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 14px;
  align-items: center;
  padding: 14px 16px;
  border-radius: 18px;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.06);
}
.status-dot {
  width: 13px;
  height: 13px;
  border-radius: 50%;
  box-shadow: 0 0 0 5px rgba(255,255,255,0.03);
}
.status-active { background: #22c55e; }
.status-error { background: #ef4444; }
.status-paused { background: #f59e0b; }
.status-other { background: #94a3b8; }
.account-main {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.account-name {
  font-size: 18px;
  font-weight: 700;
  color: #ffffff;
}
.account-meta {
  font-size: 13px;
  color: #cbd5e1;
}
.account-badges {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.pill {
  display: inline-flex;
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(255,255,255,0.08);
  color: #dbeafe;
  font-size: 12px;
  border: 1px solid rgba(255,255,255,0.08);
}
.right-col-grid {
  display: grid;
  grid-template-rows: auto auto;
  align-content: start;
  gap: 18px;
}
.kv-list {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
.kv {
  border-radius: 18px;
  background: rgba(255,255,255,0.05);
  padding: 14px 16px;
  border: 1px solid rgba(255,255,255,0.06);
}
.kv .k {
  font-size: 13px;
  color: #b9c5e7;
  margin-bottom: 8px;
}
.kv .v {
  font-size: 22px;
  font-weight: 700;
  color: #ffffff;
  word-break: break-word;
}
.bottom {
  display: grid;
  grid-template-columns: 1fr 1fr;
  align-items: start;
  gap: 18px;
}
.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
.tag {
  border-radius: 14px;
  padding: 10px 12px;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.06);
  font-size: 13px;
  color: #dbeafe;
}
.state {
  display: inline-flex;
  align-items: center;
  padding: 6px 12px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 700;
  white-space: nowrap;
  border: 1px solid transparent;
}
.lv-ok { color: #86efac; background: rgba(34,197,94,0.14); border-color: rgba(34,197,94,0.35); }
.lv-warn { color: #fcd34d; background: rgba(245,158,11,0.14); border-color: rgba(245,158,11,0.35); }
.lv-bad { color: #fca5a5; background: rgba(239,68,68,0.14); border-color: rgba(239,68,68,0.35); }
.lv-muted { color: #cbd5e1; background: rgba(148,163,184,0.14); border-color: rgba(148,163,184,0.30); }
.bar {
  height: 8px;
  border-radius: 999px;
  background: rgba(255,255,255,0.08);
  overflow: hidden;
}
.bar > span {
  display: block;
  height: 100%;
  border-radius: 999px;
}
.fill-ok { background: linear-gradient(90deg, #16a34a, #4ade80); }
.fill-warn { background: linear-gradient(90deg, #d97706, #fbbf24); }
.fill-bad { background: linear-gradient(90deg, #dc2626, #f87171); }
.pct-ok { color: #86efac; }
.pct-warn { color: #fcd34d; }
.pct-bad { color: #fca5a5; }
.mini-usage {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 10px;
  align-items: center;
  margin-top: 2px;
}
.mini-text {
  min-width: 130px;
  text-align: right;
  font-size: 12px;
  color: #cbd5e1;
  white-space: nowrap;
}
.attention-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.attention-item {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 12px;
  align-items: center;
  padding: 12px 14px;
  border-radius: 16px;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.06);
}
.attention-name {
  font-size: 15px;
  font-weight: 700;
  color: #ffffff;
}
.attention-reasons {
  margin-top: 4px;
  font-size: 12px;
  color: #cbd5e1;
  word-break: break-word;
}
.footer {
  margin-top: 18px;
  color: #9fb0db;
  font-size: 12px;
  text-align: center;
}
.small-muted {
  color: #9fb0db;
  font-size: 12px;
}
.empty {
  padding: 18px;
  border-radius: 16px;
  color: #d4def9;
  background: rgba(255,255,255,0.04);
}
</style>
</head>
<body>
  <div class="wrapper">
    <div class="header">
      <div class="brand">
        <div class="badge">AstrBot · Sub2API 精美状态面板</div>
        <h1>{{ panel_title }}</h1>
        <div class="sub">{{ subtitle }}</div>
      </div>
      <div class="top-meta">
        <div class="small-muted">面板生成时间</div>
        <div class="time">{{ generated_at }}</div>
        {% if base_url %}
        <div class="small-muted">数据来源：{{ base_url }}</div>
        {% endif %}
      </div>
    </div>

    <div class="grid4">
      {% for metric in metrics %}
      <div class="card">
        <div class="metric-label">{{ metric.label }}</div>
        <div class="metric-value">{{ metric.value }}</div>
        <div class="metric-sub">{{ metric.sub }}</div>
      </div>
      {% endfor %}
    </div>

    <div class="layout">
      <div class="card">
        <div class="section-title">
          <h2>账号概览</h2>
          <div class="hint">展示前 {{ accounts|length }} 个账号</div>
        </div>

        {% if accounts %}
        <div class="account-list">
          {% for acc in accounts %}
          <div class="account-item">
            <div class="status-dot {{ acc.dot_class }}"></div>
            <div class="account-main">
              <div class="account-name">#{{ acc.id }} {{ acc.name }}</div>
              <div class="account-meta">{{ acc.platform }} / {{ acc.type }} · 分组：{{ acc.groups }}</div>
              <div class="account-badges">
                <span class="pill">套餐：{{ acc.plan }}</span>
                <span class="pill">到期：{{ acc.expiry }}</span>
                <span class="pill">并发：{{ acc.concurrency }}</span>
                {% if acc.extra_badge %}
                <span class="pill">{{ acc.extra_badge }}</span>
                {% endif %}
              </div>
              {% if acc.usage %}
              <div class="mini-usage">
                <div class="bar"><span class="fill-{{ acc.usage.level }}" style="width: {{ acc.usage.width }}%"></span></div>
                <span class="mini-text">{{ acc.usage.name }} <b class="pct-{{ acc.usage.level }}">{{ acc.usage.percent }}%</b></span>
              </div>
              {% endif %}
            </div>
            <div class="account-badges">
              <span class="state lv-{{ acc.status_level }}">{{ acc.status_label }}</span>
            </div>
          </div>
          {% endfor %}
        </div>
        {% else %}
        <div class="empty">暂无账号数据</div>
        {% endif %}
      </div>

      <div class="right-col-grid">
        <div class="card">
          <div class="section-title">
            <h2>全局状态</h2>
            <div class="hint">实时摘要</div>
          </div>
          <div class="kv-list">
            {% for item in realtime %}
            <div class="kv">
              <div class="k">{{ item.key }}</div>
              <div class="v">{{ item.value }}</div>
            </div>
            {% endfor %}
          </div>
        </div>

        <div class="card">
          <div class="section-title">
            <h2>全局统计</h2>
            <div class="hint">业务摘要</div>
          </div>
          <div class="kv-list">
            {% for item in stats %}
            <div class="kv">
              <div class="k">{{ item.key }}</div>
              <div class="v">{{ item.value }}</div>
            </div>
            {% endfor %}
          </div>
        </div>
      </div>
    </div>

    <div class="bottom">
      <div class="card">
        <div class="section-title">
          <h2>需要关注</h2>
          <div class="hint">{{ attention_hint }}</div>
        </div>
        {% if attention %}
        <div class="attention-list">
          {% for item in attention %}
          <div class="attention-item">
            <span class="state lv-{{ item.level }}">{{ item.label }}</span>
            <div>
              <div class="attention-name">#{{ item.id }} {{ item.name }}</div>
              <div class="attention-reasons">{{ item.reasons|join(" · ") }}</div>
            </div>
          </div>
          {% endfor %}
        </div>
        {% else %}
        <div class="empty">所有账号状态正常，暂无需要处理的账号</div>
        {% endif %}
      </div>

      <div class="card">
        <div class="section-title">
          <h2>可用模型预览</h2>
          <div class="hint">从前几项账号里汇总</div>
        </div>
        {% if model_tags %}
        <div class="tag-list">
          {% for item in model_tags %}
          <span class="tag">{{ item }}</span>
          {% endfor %}
        </div>
        {% else %}
        <div class="empty">暂无模型数据</div>
        {% endif %}
      </div>
    </div>

    <div class="footer">
      Powered by AstrBot HTML 渲染 · Sub2API 管理接口只读查询
    </div>
  </div>
</body>
</html>
"""

DETAIL_TEMPLATE = r"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<title>Sub2API 账号卡片</title>
<style>
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: "Segoe UI", "Microsoft YaHei", Arial, sans-serif;
  background:
    radial-gradient(circle at top left, rgba(14,165,233,0.22), transparent 32%),
    radial-gradient(circle at top right, rgba(168,85,247,0.25), transparent 26%),
    linear-gradient(180deg, #08111d 0%, #10192c 100%);
  color: #eef2ff;
}
.wrap {
  width: 1120px;
  margin: 0 auto;
  padding: 36px;
}
.big-card {
  border-radius: 28px;
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.1);
  box-shadow: 0 16px 40px rgba(0,0,0,0.24);
  padding: 28px;
  backdrop-filter: blur(16px);
}
.top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 22px;
}
.badge {
  display: inline-flex;
  width: fit-content;
  padding: 8px 14px;
  border-radius: 999px;
  background: rgba(255,255,255,0.08);
  font-size: 14px;
  color: #d7e3ff;
  border: 1px solid rgba(255,255,255,.08);
}
.title {
  margin-top: 14px;
  font-size: 36px;
  font-weight: 800;
  color: #fff;
}
.sub {
  margin-top: 6px;
  color: #c9d7f6;
  font-size: 15px;
}
.grid {
  display: grid;
  grid-template-columns: 1.05fr 1fr;
  gap: 18px;
}
.card {
  border-radius: 22px;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.08);
  padding: 20px;
}
.section-title {
  margin: 0 0 16px 0;
  font-size: 22px;
}
.kv-list {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
.kv {
  background: rgba(255,255,255,0.045);
  border-radius: 16px;
  padding: 14px;
}
.k {
  color: #b9caef;
  font-size: 13px;
  margin-bottom: 8px;
}
.v {
  color: white;
  font-size: 22px;
  font-weight: 700;
  line-height: 1.15;
  word-break: break-word;
}
.usage-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.usage-item {
  background: rgba(255,255,255,0.045);
  border-radius: 16px;
  padding: 14px 16px;
}
.usage-item .u-k {
  color: #b9caef;
  font-size: 13px;
  margin-bottom: 6px;
}
.usage-item .u-v {
  color: white;
  font-size: 18px;
  font-weight: 700;
  word-break: break-word;
}
.models {
  margin-top: 18px;
}
.grid > .card {
  align-self: start;
}
.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
.tag {
  padding: 8px 11px;
  border-radius: 14px;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.08);
  color: #dbeafe;
  font-size: 13px;
}
.state {
  display: inline-flex;
  align-items: center;
  padding: 6px 12px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 700;
  white-space: nowrap;
  border: 1px solid transparent;
}
.lv-ok { color: #86efac; background: rgba(34,197,94,0.14); border-color: rgba(34,197,94,0.35); }
.lv-warn { color: #fcd34d; background: rgba(245,158,11,0.14); border-color: rgba(245,158,11,0.35); }
.lv-bad { color: #fca5a5; background: rgba(239,68,68,0.14); border-color: rgba(239,68,68,0.35); }
.lv-muted { color: #cbd5e1; background: rgba(148,163,184,0.14); border-color: rgba(148,163,184,0.30); }
.bar {
  height: 8px;
  border-radius: 999px;
  background: rgba(255,255,255,0.08);
  overflow: hidden;
}
.bar > span {
  display: block;
  height: 100%;
  border-radius: 999px;
}
.fill-ok { background: linear-gradient(90deg, #16a34a, #4ade80); }
.fill-warn { background: linear-gradient(90deg, #d97706, #fbbf24); }
.fill-bad { background: linear-gradient(90deg, #dc2626, #f87171); }
.pct-ok { color: #86efac; }
.pct-warn { color: #fcd34d; }
.pct-bad { color: #fca5a5; }
.state-lg {
  padding: 10px 18px;
  font-size: 18px;
}
.window-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 12px;
}
.window {
  background: rgba(255,255,255,0.045);
  border-radius: 16px;
  padding: 14px 16px;
}
.window-head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 10px;
}
.w-name {
  color: #dbe4ff;
  font-size: 15px;
  font-weight: 600;
}
.w-pct {
  font-size: 22px;
  font-weight: 800;
}
.w-reset {
  margin-top: 8px;
  color: #b9caef;
  font-size: 12px;
}
.footer {
  margin-top: 18px;
  font-size: 12px;
  color: #9ab0df;
  text-align: center;
}
</style>
</head>
<body>
<div class="wrap">
  <div class="big-card">
    <div class="top">
      <div>
        <div class="badge">AstrBot · Sub2API 账号卡片</div>
        <div class="title">#{{ account.id }} {{ account.name }}</div>
        <div class="sub">{{ account.platform }} / {{ account.type }} · 分组：{{ account.groups }}</div>
      </div>
      <div class="state state-lg lv-{{ account.status_level }}">{{ account.status_label }}</div>
    </div>

    <div class="grid">
      <div class="card">
        <h3 class="section-title">基础信息</h3>
        <div class="kv-list">
          {% for item in base_info %}
          <div class="kv">
            <div class="k">{{ item.key }}</div>
            <div class="v">{{ item.value }}</div>
          </div>
          {% endfor %}
        </div>

        <div class="models">
          <h3 class="section-title">可用模型（前 {{ models|length }} 个）</h3>
          <div class="tags">
            {% if models %}
              {% for item in models %}
              <span class="tag">{{ item }}</span>
              {% endfor %}
            {% else %}
              <span class="tag">暂无模型数据</span>
            {% endif %}
          </div>
        </div>
      </div>

      <div class="card">
        <h3 class="section-title">额度 / 用量</h3>
        {% if windows %}
        <div class="window-list">
          {% for w in windows %}
          <div class="window">
            <div class="window-head">
              <span class="w-name">{{ w.name }}</span>
              <span class="w-pct pct-{{ w.level }}">{{ w.percent }}%</span>
            </div>
            <div class="bar"><span class="fill-{{ w.level }}" style="width: {{ w.width }}%"></span></div>
            {% if w.reset %}
            <div class="w-reset">{{ w.reset }}</div>
            {% endif %}
          </div>
          {% endfor %}
        </div>
        {% endif %}
        <div class="usage-list">
          {% for item in usage %}
          <div class="usage-item">
            <div class="u-k">{{ item.key }}</div>
            <div class="u-v">{{ item.value }}</div>
          </div>
          {% endfor %}
        </div>
      </div>
    </div>

    <div class="footer">面板生成时间：{{ generated_at }}{% if base_url %} · 数据来源：{{ base_url }}{% endif %}</div>
  </div>
</div>
</body>
</html>
"""


class Sub2APIRequestError(RuntimeError):
    pass


class Sub2APIStatusPlugin(Star):
    """Sub2API 账号查询 + 精美图形面板"""

    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config

    def _base_url(self) -> str:
        return str(self.config.get("base_url", "http://127.0.0.1:9999")).strip().rstrip("/")

    def _display_base_url(self) -> str:
        return self._base_url() if bool(self.config.get("show_base_url", False)) else ""

    def _timeout(self) -> int:
        try:
            return max(3, min(int(self.config.get("timeout", 12)), 60))
        except Exception:
            return 12

    def _page_size(self) -> int:
        try:
            return max(1, min(int(self.config.get("page_size", 50)), 200))
        except Exception:
            return 50

    def _max_display(self) -> int:
        try:
            return max(1, min(int(self.config.get("max_display_accounts", 8)), 50))
        except Exception:
            return 8

    @staticmethod
    def _render_options() -> dict[str, Any]:
        # AstrBot 会把这里的选项合并进默认的 {"type": "jpeg", "quality": 40}，
        # 若改用 png，残留的 quality 会让 Playwright 截图直接报错，所以保持 jpeg 并提高画质。
        return {"type": "jpeg", "quality": 92, "full_page": True, "scale": "device", "animations": "disabled"}

    def _auth_headers(self) -> dict[str, str]:
        admin_key = str(self.config.get("admin_api_key", "") or "").strip()
        admin_jwt = str(self.config.get("admin_jwt", "") or "").strip()
        if admin_key:
            return {"x-api-key": admin_key}
        if admin_jwt:
            return {"Authorization": f"Bearer {admin_jwt}"}
        raise Sub2APIRequestError("插件还没有配置 Sub2API 管理员凭证。请填写 admin_api_key（推荐）或 admin_jwt。")

    def _unwrap(self, value: Any) -> Any:
        if isinstance(value, dict) and "data" in value:
            if "code" in value or "message" in value or "success" in value:
                return value["data"]
        return value

    def _request_sync(self, method: str, path: str, params: dict[str, Any] | None = None, body: dict[str, Any] | None = None) -> Any:
        url = f"{self._base_url()}{path}"
        if params:
            clean = {k: v for k, v in params.items() if v is not None and v != ""}
            if clean:
                url += "?" + urllib.parse.urlencode(clean)

        headers = {"Accept": "application/json", "User-Agent": "AstrBot-Sub2API-Panel/1.1", **self._auth_headers()}
        data = None
        if body is not None:
            data = json.dumps(body, ensure_ascii=False).encode("utf-8")
            headers["Content-Type"] = "application/json"

        req = urllib.request.Request(url=url, data=data, headers=headers, method=method.upper())

        verify_ssl = bool(self.config.get("verify_ssl", True))
        bypass_proxy = bool(self.config.get("bypass_system_proxy", True))
        handlers: list[Any] = []
        context = None
        if url.lower().startswith("https://") and not verify_ssl:
            context = ssl._create_unverified_context()
        if bypass_proxy:
            handlers.append(urllib.request.ProxyHandler({}))
        if context is not None:
            handlers.append(urllib.request.HTTPSHandler(context=context))
        opener = urllib.request.build_opener(*handlers)

        try:
            with opener.open(req, timeout=self._timeout()) as resp:
                raw = resp.read().decode("utf-8", errors="replace")
                if not raw.strip():
                    return None
                try:
                    parsed = json.loads(raw)
                except json.JSONDecodeError:
                    return raw
                return self._unwrap(parsed)
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            msg = raw
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, dict):
                    msg = parsed.get("message") or parsed.get("detail") or parsed.get("error") or raw
            except Exception:
                pass
            raise Sub2APIRequestError(f"HTTP {exc.code}: {msg}") from exc
        except urllib.error.URLError as exc:
            raise Sub2APIRequestError(f"连接 Sub2API 失败：{exc.reason}") from exc
        except TimeoutError as exc:
            raise Sub2APIRequestError("连接 Sub2API 超时。") from exc

    async def _request(self, method: str, path: str, params: dict[str, Any] | None = None, body: dict[str, Any] | None = None) -> Any:
        return await asyncio.to_thread(self._request_sync, method, path, params, body)

    @staticmethod
    def _pick(obj: dict[str, Any], *keys: str, default: Any = None) -> Any:
        for key in keys:
            if key in obj and obj[key] not in (None, ""):
                return obj[key]
        return default

    @staticmethod
    def _extra(account: dict[str, Any]) -> dict[str, Any]:
        extra = account.get("extra")
        return extra if isinstance(extra, dict) else {}

    @staticmethod
    def _fmt_datetime(value: Any) -> str:
        if value in (None, "", 0):
            return "-"
        if isinstance(value, (int, float)):
            try:
                ts = float(value)
                if ts > 10_000_000_000:
                    ts /= 1000
                return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")
            except Exception:
                return str(value)
        return str(value).replace("T", " ").replace("Z", "")[:19]

    @staticmethod
    def _fmt_number(value: Any, digits: int = 2) -> str:
        try:
            n = float(value)
            if n.is_integer():
                return str(int(n))
            return f"{n:.{digits}f}".rstrip("0").rstrip(".")
        except Exception:
            return str(value)

    def _groups_text(self, account: dict[str, Any]) -> str:
        value = self._pick(account, "group_names", "groups", "group", default=None)
        if value is None:
            return "-"
        if isinstance(value, str):
            return value
        if isinstance(value, list):
            names: list[str] = []
            for item in value:
                if isinstance(item, str):
                    names.append(item)
                elif isinstance(item, dict):
                    names.append(str(item.get("name") or item.get("group_name") or item.get("id") or "?"))
            return ", ".join(names) if names else "-"
        if isinstance(value, dict):
            return str(value.get("name") or value.get("group_name") or value.get("id") or "-")
        return str(value)

    def _plan_text(self, account: dict[str, Any]) -> str:
        extra = self._extra(account)
        value = self._pick(account, "plan_type", "subscription_tier", "subscription_type", "tier", default=None) \
            or self._pick(extra, "plan_type", "subscription_tier", "subscription_type", "tier", default=None)
        return str(value) if value not in (None, "") else "-"

    def _expiry_raw(self, account: dict[str, Any]) -> Any:
        extra = self._extra(account)
        return self._pick(account, "expires_at", "expired_at", "subscription_expires_at", "subscription_expire_at", default=None) \
            or self._pick(extra, "expires_at", "expired_at", "subscription_expires_at", "subscription_expire_at", default=None)

    def _expiry_text(self, account: dict[str, Any]) -> str:
        return self._fmt_datetime(self._expiry_raw(account))

    def _status_icon(self, status: str) -> str:
        s = status.lower().strip()
        if s in {"active", "normal", "ok", "healthy", "enabled"}:
            return "✅"
        if s in {"inactive", "disabled", "stopped"}:
            return "⏸️"
        if s in {"error", "failed", "invalid", "expired"}:
            return "❌"
        return "⚪"

    @staticmethod
    def _parse_dt(value: Any) -> datetime | None:
        if value in (None, "", 0):
            return None
        try:
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                ts = float(value)
                if ts > 10_000_000_000:
                    ts /= 1000
                return datetime.fromtimestamp(ts, timezone.utc)
            text = str(value).strip().replace(" ", "T", 1).replace("Z", "+00:00")
            # Go 的 RFC3339Nano 可能带 9 位小数，fromisoformat 最多接受 6 位
            text = re.sub(r"(\.\d{6})\d+", r"\1", text)
            dt = datetime.fromisoformat(text)
        except Exception:
            return None
        return dt if dt.tzinfo else dt.astimezone()

    def _in_future(self, account: dict[str, Any], *keys: str) -> bool:
        value = self._pick(account, *keys, default=None) or self._pick(self._extra(account), *keys, default=None)
        dt = self._parse_dt(value)
        return dt is not None and dt > datetime.now(timezone.utc)

    def _status_badge(self, account: dict[str, Any]) -> tuple[str, str]:
        """返回 (中文状态, 等级)，等级用于 CSS：ok / warn / bad / muted。"""
        status = str(self._pick(account, "status", default="")).lower().strip()
        if status in {"error", "failed", "invalid", "expired", "banned"}:
            return "异常", "bad"
        if status in {"inactive", "disabled", "stopped", "paused"}:
            return "已停用", "muted"
        if self._in_future(account, "rate_limit_reset_at", "rate_limited_until"):
            return "限流中", "warn"
        if self._in_future(account, "overload_until"):
            return "过载", "warn"
        if self._in_future(account, "temp_unschedulable_until"):
            return "暂停调度", "warn"
        if status in {"active", "normal", "ok", "healthy", "enabled"}:
            return "正常", "ok"
        return (status or "未知"), "muted"

    _PERCENT_KEYS = ("utilization", "used_percent", "usage_percent", "percent_used")
    _RESET_KEYS = ("resets_at", "reset_at", "reset_time")

    @staticmethod
    def _usage_level(percent: float) -> str:
        if percent >= 85:
            return "bad"
        if percent >= 60:
            return "warn"
        return "ok"

    def _reset_text(self, node: dict[str, Any]) -> str:
        now = datetime.now(timezone.utc)
        dt = self._parse_dt(self._pick(node, *self._RESET_KEYS, default=None))
        if dt is None:
            seconds = self._pick(node, "reset_after_seconds", default=None)
            try:
                dt = datetime.fromtimestamp(now.timestamp() + float(seconds), timezone.utc)
            except Exception:
                return ""
        left = int((dt - now).total_seconds())
        when = dt.astimezone().strftime("%m-%d %H:%M")
        if left <= 0:
            return f"重置：{when}"
        if left >= 86400:
            rel = f"{left // 86400}天{left % 86400 // 3600}小时后"
        elif left >= 3600:
            rel = f"{left // 3600}小时{left % 3600 // 60}分后"
        else:
            rel = f"{max(1, left // 60)}分钟后"
        return f"重置：{when}（{rel}）"

    def _usage_windows(self, payload: Any, prefix: str = "", depth: int = 0, out: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
        """从用量数据里找出所有带百分比的额度窗口（如 5 小时 / 7 天窗口）。"""
        if out is None:
            out = []
            payload = self._unwrap(payload)
        if depth > 3:
            return out
        if isinstance(payload, list):
            for idx, child in enumerate(payload[:8]):
                self._usage_windows(child, f"{prefix}[{idx}]", depth + 1, out)
            return out
        if not isinstance(payload, dict):
            return out
        pct = next((payload[k] for k in self._PERCENT_KEYS
                    if isinstance(payload.get(k), (int, float)) and not isinstance(payload.get(k), bool)), None)
        if pct is not None:
            percent = float(pct)
            out.append({
                "path": prefix,
                "name": self._friendly_key(prefix) if prefix else "额度",
                "percent": self._fmt_number(percent, 1),
                "value": percent,
                "width": max(0.0, min(percent, 100.0)),
                "level": self._usage_level(percent),
                "reset": self._reset_text(payload),
            })
            return out
        for key, child in payload.items():
            if isinstance(child, (dict, list)):
                self._usage_windows(child, f"{prefix}.{key}" if prefix else str(key), depth + 1, out)
        return out

    def _display_name(self, account: dict[str, Any]) -> str:
        return str(self._pick(account, "name", "display_name", "username", "email", default=f"账号#{account.get('id', '?')}"))

    def _extract_items(self, payload: Any) -> tuple[list[dict[str, Any]], int | None]:
        payload = self._unwrap(payload)
        if isinstance(payload, list):
            return [x for x in payload if isinstance(x, dict)], len(payload)
        if isinstance(payload, dict):
            for key in ("items", "accounts", "list", "rows"):
                value = payload.get(key)
                if isinstance(value, list):
                    items = [x for x in value if isinstance(x, dict)]
                    total = payload.get("total")
                    try:
                        total = int(total) if total is not None else len(items)
                    except Exception:
                        total = len(items)
                    return items, total
            nested = payload.get("data")
            if nested is not None and nested is not payload:
                return self._extract_items(nested)
        return [], None

    async def _list_accounts(self, search: str = "") -> tuple[list[dict[str, Any]], int | None]:
        params = {"page": 1, "page_size": self._page_size()}
        if search:
            params["search"] = search
        payload = await self._request("GET", "/api/v1/admin/accounts", params=params)
        return self._extract_items(payload)

    async def _find_account(self, selector: str) -> dict[str, Any]:
        selector = str(selector or "").strip()
        if not selector:
            raise Sub2APIRequestError("请提供账号 ID 或账号名称。")
        if selector.isdigit():
            payload = await self._request("GET", f"/api/v1/admin/accounts/{int(selector)}")
            payload = self._unwrap(payload)
            if isinstance(payload, dict):
                return payload
            raise Sub2APIRequestError(f"未找到账号 #{selector}")
        items, _ = await self._list_accounts(selector)
        if not items:
            raise Sub2APIRequestError(f"没有找到包含“{selector}”的账号。")
        lower = selector.lower()
        for item in items:
            candidates = [item.get("name"), item.get("display_name"), item.get("username"), item.get("email")]
            if any(str(v).lower() == lower for v in candidates if v not in (None, "")):
                return item
        if len(items) > 1:
            choices = "\n".join(f"#{i.get('id', '?')} {self._display_name(i)}" for i in items[:8])
            raise Sub2APIRequestError(f"找到多个匹配账号，请改用 ID：\n{choices}")
        return items[0]

    _SENSITIVE_WORDS = ("token", "secret", "password", "credential", "cookie", "authorization", "api_key", "apikey", "access_key", "refresh_token")
    _INTERESTING_WORDS = ("plan", "tier", "usage", "used", "limit", "remain", "quota", "balance", "credit", "reset", "request", "token_count", "input_tokens", "output_tokens", "total_tokens", "cost", "window", "expires", "fetched", "allowed", "reached", "utilization", "percent", "account", "user", "rpm", "tpm", "rate", "duration", "response_time", "uptime")

    def _flatten_interesting(self, value: Any, prefix: str = "", depth: int = 0, out: list[tuple[str, Any]] | None = None) -> list[tuple[str, Any]]:
        if out is None:
            out = []
        if depth > 4 or len(out) >= 30:
            return out
        if isinstance(value, dict):
            for key, child in value.items():
                key_s = str(key)
                key_lower = key_s.lower()
                if any(word in key_lower for word in self._SENSITIVE_WORDS):
                    continue
                path = f"{prefix}.{key_s}" if prefix else key_s
                if isinstance(child, (dict, list)):
                    self._flatten_interesting(child, path, depth + 1, out)
                else:
                    if any(word in key_lower for word in self._INTERESTING_WORDS):
                        out.append((path, child))
        elif isinstance(value, list):
            for idx, child in enumerate(value[:8]):
                self._flatten_interesting(child, f"{prefix}[{idx}]", depth + 1, out)
        return out

    _KEY_LABELS = {
        "used_percent": "已使用%",
        "utilization": "已使用%",
        "reset_after_seconds": "距重置(秒)",
        "reset_at": "重置时间",
        "resets_at": "重置时间",
        "balance": "余额",
        "plan_type": "套餐",
        "subscription_tier": "订阅等级",
        "requests": "请求数",
        "request_count": "请求数",
        "tokens": "Tokens",
        "input_tokens": "输入Tokens",
        "output_tokens": "输出Tokens",
        "total_tokens": "总Tokens",
        "cost": "费用",
        "actual_cost": "实际费用",
        "standard_cost": "标准费用",
        "user_cost": "用户费用",
        "allowed": "允许",
        "limit_reached": "触发限额",
        "fetched_at": "获取时间",
        "expires_at": "到期时间",
        "five_hour": "5小时窗口",
        "seven_day": "7天窗口",
        "seven_day_opus": "7天Opus",
        "seven_day_sonnet": "7天Sonnet",
        "total_accounts": "账号总数",
        "normal_accounts": "正常账号",
        "active_accounts": "活跃账号",
        "error_accounts": "异常账号",
        "ratelimit_accounts": "限流账号",
        "overload_accounts": "过载账号",
        "total_users": "用户总数",
        "active_users": "活跃用户",
        "today_new_users": "今日新用户",
        "total_api_keys": "API Key 总数",
        "active_api_keys": "活跃 API Key",
        "total_requests": "累计请求",
        "today_requests": "今日请求",
        "today_tokens": "今日Tokens",
        "today_input_tokens": "今日输入Tokens",
        "today_output_tokens": "今日输出Tokens",
        "total_cost": "累计费用",
        "total_actual_cost": "累计实际费用",
        "today_cost": "今日费用",
        "today_actual_cost": "今日实际费用",
        "active_requests": "进行中请求",
        "requests_per_minute": "每分钟请求",
        "average_response_time": "平均响应",
        "average_duration_ms": "平均耗时",
        "hourly_active_users": "近1小时活跃用户",
        "today_total_tokens": "今日Tokens",
        "error_rate": "错误率",
        "rpm": "RPM",
        "tpm": "TPM",
        "uptime": "运行时长(秒)",
    }

    def _friendly_key(self, key: str) -> str:
        parts = [p for p in key.replace("[", ".[").split(".") if p]
        return " · ".join(self._KEY_LABELS.get(p, p) for p in parts)

    def _skip_path(self, path: str, skip_paths: list[str]) -> bool:
        for p in skip_paths:
            if p == "":
                if path in self._PERCENT_KEYS + self._RESET_KEYS + ("reset_after_seconds",):
                    return True
            elif path == p or path.startswith(p + ".") or path.startswith(p + "["):
                return True
        return False

    # 值的单位是毫秒的字段，显示时换算成 ms / 秒
    _MS_KEYS = ("average_response_time", "average_duration_ms")
    # 面板“全局统计”优先展示的字段；账号计数已在顶部卡片展示，不再占位
    _STATS_PREFER = (
        "today_requests", "today_tokens", "today_total_tokens", "today_cost",
        "total_requests", "total_cost", "active_users", "rpm", "average_duration_ms",
        "today_actual_cost", "tpm",
    )

    def _fmt_ms(self, value: Any) -> str:
        try:
            ms = float(value)
        except Exception:
            return str(value)
        if ms >= 1000:
            return f"{self._fmt_number(ms / 1000, 1)} 秒"
        return f"{self._fmt_number(ms, 0)} ms"

    def _pairs_for_display(self, payload: Any, limit: int = 12, skip_paths: list[str] | None = None,
                           prefer: tuple[str, ...] = ()) -> list[dict[str, str]]:
        payload = self._unwrap(payload)
        if payload is None:
            return []
        pairs = self._flatten_interesting(payload)
        if prefer and isinstance(payload, dict):
            head = [(k, payload[k]) for k in prefer
                    if isinstance(payload.get(k), (int, float, str)) and not isinstance(payload.get(k), bool)]
            seen = {k for k, _ in head}
            pairs = head + [(k, v) for k, v in pairs if k not in seen]
        if not pairs and isinstance(payload, dict):
            for key, value in payload.items():
                kl = str(key).lower()
                if any(word in kl for word in self._SENSITIVE_WORDS):
                    continue
                if isinstance(value, (str, int, float, bool)) and len(pairs) < limit:
                    pairs.append((str(key), value))
        if skip_paths:
            pairs = [(k, v) for k, v in pairs if not self._skip_path(k, skip_paths)]
        result = []
        for key, value in pairs[:limit]:
            if isinstance(value, bool):
                value_text = "是" if value else "否"
            elif key.split(".")[-1] in self._MS_KEYS:
                value_text = self._fmt_ms(value)
            elif isinstance(value, float):
                value_text = self._fmt_number(value, 4)
            elif isinstance(value, str) and len(value) >= 19 and value[4] == "-" and value[10] == "T":
                value_text = self._fmt_datetime(value)
            else:
                value_text = str(value)
            if len(value_text) > 100:
                value_text = value_text[:97] + "..."
            result.append({"key": self._friendly_key(key), "value": value_text})
        return result

    async def _models_for_account(self, account_id: Any) -> list[str]:
        if account_id is None:
            return []
        try:
            payload = await self._request("GET", f"/api/v1/admin/accounts/{account_id}/models")
            payload = self._unwrap(payload)
            models: list[str] = []
            if isinstance(payload, list):
                for item in payload:
                    if isinstance(item, str):
                        models.append(item)
                    elif isinstance(item, dict):
                        model_id = item.get("id") or item.get("name") or item.get("model")
                        if model_id:
                            models.append(str(model_id))
            elif isinstance(payload, dict):
                maybe = payload.get("models") or payload.get("items") or payload.get("data")
                if isinstance(maybe, list):
                    for item in maybe:
                        if isinstance(item, str):
                            models.append(item)
                        elif isinstance(item, dict):
                            model_id = item.get("id") or item.get("name") or item.get("model")
                            if model_id:
                                models.append(str(model_id))
            seen = set()
            uniq = []
            for m in models:
                if m not in seen:
                    uniq.append(m)
                    seen.add(m)
            return uniq
        except Exception:
            return []

    async def _passive_usage_windows(self, account_id: Any, sem: asyncio.Semaphore) -> list[dict[str, Any]]:
        if account_id is None:
            return []
        async with sem:
            try:
                payload = await self._request("GET", f"/api/v1/admin/accounts/{account_id}/usage", params={"source": "passive"})
            except Exception:
                return []
        return self._usage_windows(payload)

    def _attention_items(self, accounts: list[dict[str, Any]], top_usage: dict[Any, dict[str, Any]]) -> list[dict[str, Any]]:
        now = datetime.now(timezone.utc)
        rank = {"bad": 0, "warn": 1, "muted": 2}
        items = []
        for acc in accounts:
            label, level = self._status_badge(acc)
            reasons: list[str] = []
            if level in {"bad", "warn"}:
                reasons.append(label)
                err = str(self._pick(acc, "error_message", "last_error", default="") or "").strip()
                if err:
                    reasons.append(err[:60] + ("…" if len(err) > 60 else ""))
            expiry = self._parse_dt(self._expiry_raw(acc))
            if expiry is not None:
                days = (expiry - now).total_seconds() / 86400
                if days < 0:
                    reasons.append("订阅已到期")
                    level = "bad"
                elif days <= 7:
                    reasons.append(f"{max(1, int(days + 0.999))} 天内到期")
                    if level not in {"bad"}:
                        level = "warn"
            usage = top_usage.get(acc.get("id"))
            if usage and usage["value"] >= 85:
                reasons.append(f"{usage['name']} 已用 {usage['percent']}%")
                if level != "bad":
                    level = "warn"
            if not reasons:
                continue
            if level == "bad" and label == "正常":
                label = "到期"
            elif level == "warn" and label == "正常":
                label = "额度紧张" if usage and usage["value"] >= 85 else "即将到期"
            items.append({
                "id": acc.get("id", "?"),
                "name": self._display_name(acc),
                "label": label,
                "level": level,
                "reasons": reasons,
            })
        items.sort(key=lambda x: rank.get(x["level"], 3))
        return items

    async def _render_panel_image(self, keyword: str = "") -> str:
        accounts, total = await self._list_accounts(keyword)
        stats_task = self._request("GET", "/api/v1/admin/dashboard/stats")
        realtime_task = self._request("GET", "/api/v1/admin/dashboard/realtime")
        stats_payload, realtime_payload = await asyncio.gather(stats_task, realtime_task, return_exceptions=True)

        display_accounts = accounts[:min(len(accounts), self._max_display())]

        sem = asyncio.Semaphore(5)
        model_lists, usage_lists = await asyncio.gather(
            asyncio.gather(*(self._models_for_account(acc.get("id")) for acc in display_accounts[:4])),
            asyncio.gather(*(self._passive_usage_windows(acc.get("id"), sem) for acc in display_accounts)),
        )
        model_tags: list[str] = []
        for models in model_lists:
            for m in models[:6]:
                if m not in model_tags:
                    model_tags.append(m)
            if len(model_tags) >= 18:
                break

        top_usage: dict[Any, dict[str, Any]] = {}
        for acc, windows in zip(display_accounts, usage_lists):
            if windows:
                top_usage[acc.get("id")] = max(windows, key=lambda w: w["value"])

        acc_rows = []
        for acc in display_accounts:
            label, level = self._status_badge(acc)
            sched = self._pick(acc, "schedulable", "is_schedulable", default=None)
            extra_badge = ""
            if sched is False:
                extra_badge = "不可调度"
            elif sched is True:
                extra_badge = "可调度"
            acc_rows.append({
                "id": acc.get("id", "?"),
                "name": self._display_name(acc),
                "platform": str(self._pick(acc, "platform", default="-")),
                "type": str(self._pick(acc, "type", "account_type", default="-")),
                "status_label": label,
                "status_level": level,
                "dot_class": {"ok": "status-active", "bad": "status-error", "warn": "status-paused"}.get(level, "status-other"),
                "groups": self._groups_text(acc),
                "plan": self._plan_text(acc),
                "expiry": self._expiry_text(acc),
                "concurrency": str(self._pick(acc, "concurrency", "max_concurrency", default="-")),
                "extra_badge": extra_badge,
                "usage": top_usage.get(acc.get("id")),
            })

        # 账号数量优先取全局统计（覆盖全部账号）；带关键词筛选或统计不可用时，退回统计本页数据
        stats_dict = self._unwrap(stats_payload) if isinstance(stats_payload, dict) else {}
        stats_dict = stats_dict if isinstance(stats_dict, dict) else {}
        if not keyword and isinstance(stats_dict.get("normal_accounts"), (int, float)):
            normal = int(stats_dict.get("normal_accounts") or 0)
            errors = int(stats_dict.get("error_accounts") or 0)
            limited = int(stats_dict.get("ratelimit_accounts") or 0) + int(stats_dict.get("overload_accounts") or 0)
            normal_sub = f"异常 {errors} · 限流/过载 {limited} · 全局统计"
        else:
            levels = [self._status_badge(acc)[1] for acc in accounts]
            normal = levels.count("ok")
            normal_sub = f"异常 {levels.count('bad')} · 限流/停用 {levels.count('warn') + levels.count('muted')} · 本页 {len(accounts)} 个"

        metrics = [
            {"label": "账号总数", "value": str(total if total is not None else len(accounts)), "sub": f"筛选条件：{keyword or '全部账号'}"},
            {"label": "正常账号", "value": str(normal), "sub": normal_sub},
            {"label": "展示账号", "value": str(len(display_accounts)), "sub": f"最多显示 {self._max_display()} 个"},
            {"label": "模型样本", "value": str(len(model_tags)), "sub": "从前几项账号汇总"},
        ]

        if isinstance(realtime_payload, Exception):
            realtime = [{"key": "实时状态", "value": "获取失败"}]
        else:
            realtime = self._pairs_for_display(realtime_payload, 6) or [{"key": "实时状态", "value": "暂无数据"}]

        if isinstance(stats_payload, Exception):
            stats = [{"key": "全局统计", "value": "获取失败"}]
        else:
            stats = self._pairs_for_display(stats_payload, 8, prefer=self._STATS_PREFER) or [{"key": "全局统计", "value": "暂无数据"}]

        attention = self._attention_items(accounts, top_usage)
        attention_hint = f"{len(attention)} 个账号" if attention else "异常 / 限流 / 到期 / 额度"
        if len(attention) > 6:
            attention_hint = f"共 {len(attention)} 个，显示前 6 个"

        data = {
            "panel_title": "Sub2API 账号总览",
            "subtitle": "用于快速查看当前账号、状态、模型和整体运行情况",
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "base_url": self._display_base_url(),
            "metrics": metrics,
            "accounts": acc_rows,
            "realtime": realtime,
            "stats": stats,
            "model_tags": model_tags,
            "attention": attention[:6],
            "attention_hint": attention_hint,
        }
        return await self.html_render(PANEL_TEMPLATE, data, options=self._render_options())

    async def _render_detail_image(self, selector: str) -> str:
        account = await self._find_account(selector)
        account_id = account.get("id")
        if account_id is not None:
            try:
                full = await self._request("GET", f"/api/v1/admin/accounts/{account_id}")
                full = self._unwrap(full)
                if isinstance(full, dict):
                    account = full
            except Exception:
                pass

        usage_task = self._request("GET", f"/api/v1/admin/accounts/{account_id}/usage", params={"source": "passive"})
        today_task = self._request("GET", f"/api/v1/admin/accounts/{account_id}/today-stats")
        models_task = self._models_for_account(account_id)
        usage_payload, today_payload, models = await asyncio.gather(usage_task, today_task, models_task, return_exceptions=True)

        windows: list[dict[str, Any]] = []
        usage_rows = []
        if not isinstance(usage_payload, Exception):
            windows = self._usage_windows(usage_payload)
            usage_rows.extend(self._pairs_for_display(usage_payload, 8, skip_paths=[w["path"] for w in windows]))
        if not isinstance(today_payload, Exception):
            today_pairs = self._pairs_for_display(today_payload, 6)
            usage_rows.extend(today_pairs)
        if not usage_rows and not windows:
            usage_rows = [{"key": "用量信息", "value": "暂无数据"}]

        base_info = [
            {"key": "平台", "value": str(self._pick(account, "platform", default="-"))},
            {"key": "类型", "value": str(self._pick(account, "type", "account_type", default="-"))},
            {"key": "套餐", "value": self._plan_text(account)},
            {"key": "到期", "value": self._expiry_text(account)},
            {"key": "分组", "value": self._groups_text(account)},
            {"key": "并发", "value": str(self._pick(account, "concurrency", "max_concurrency", default="-"))},
            {"key": "优先级", "value": str(self._pick(account, "priority", default="-"))},
            {"key": "可调度", "value": "是" if self._pick(account, "schedulable", "is_schedulable", default=None) is True else ("否" if self._pick(account, "schedulable", "is_schedulable", default=None) is False else "-")},
        ]

        data = {
            "account": {
                "id": account.get("id", "?"),
                "name": self._display_name(account),
                "platform": str(self._pick(account, "platform", default="-")),
                "type": str(self._pick(account, "type", "account_type", default="-")),
                "groups": self._groups_text(account),
                "status_label": self._status_badge(account)[0],
                "status_level": self._status_badge(account)[1],
            },
            "base_info": base_info,
            "windows": windows[:6],
            "usage": usage_rows[:14],
            "models": models[:18] if isinstance(models, list) else [],
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "base_url": self._display_base_url(),
        }
        options = self._render_options()
        return await self.html_render(DETAIL_TEMPLATE, data, options=options)

    # ---- commands ----
    @filter.command_group("s2", alias={"sub2api"})
    def s2(self):
        pass

    @filter.permission_type(filter.PermissionType.ADMIN)
    @s2.command("帮助", alias={"help"})
    async def s2_help(self, event: AstrMessageEvent):
        text = (
            "📘 Sub2API 查询插件\n"
            "/s2 测试 - 检查连接和管理员凭证\n"
            "/s2 账号 [关键词] - 查看账号列表（文本）\n"
            "/s2 详情 <ID/名称> - 查看账号详情（文本）\n"
            "/s2 用量 <ID/名称> [刷新] - 查看额度与今日统计（文本）\n"
            "/s2 模型 <ID/名称> - 查看账号可用模型（文本）\n"
            "/s2 状态 - 查看全局状态（文本）\n"
            "/s2 面板 [关键词] - 生成精美总览图片\n"
            "/s2 卡片 <ID/名称> - 生成单账号精美卡片\n"
        )
        yield event.plain_result(text)

    @filter.permission_type(filter.PermissionType.ADMIN)
    @s2.command("测试", alias={"ping", "test"})
    async def s2_test(self, event: AstrMessageEvent):
        try:
            items, total = await self._list_accounts()
            yield event.plain_result(f"✅ Sub2API 连接正常\n地址：{self._base_url()}\n账号：{total if total is not None else len(items)}")
        except Exception as exc:
            yield event.plain_result(f"❌ Sub2API 连接失败\n{exc}")

    @filter.permission_type(filter.PermissionType.ADMIN)
    @s2.command("账号", alias={"accounts", "acc"})
    async def s2_accounts(self, event: AstrMessageEvent, keyword: str = ""):
        try:
            items, total = await self._list_accounts(keyword.strip())
            if not items:
                yield event.plain_result("没有找到账号。")
                return
            active = 0
            errors = 0
            for item in items:
                status = str(self._pick(item, "status", default="")).lower()
                if status in {"active", "normal", "ok", "healthy", "enabled"}:
                    active += 1
                if status in {"error", "failed", "invalid", "expired"}:
                    errors += 1
            display = items[: self._max_display()]
            lines = ["📋 Sub2API 账号", f"共 {total if total is not None else len(items)} 个｜本页正常 {active}｜异常 {errors}"]
            if keyword:
                lines.append(f"筛选：{keyword}")
            lines.append("")
            for item in display:
                status = str(self._pick(item, "status", default="unknown"))
                lines.append(
                    f"{self._status_icon(status)} #{item.get('id', '?')} {self._display_name(item)}\n"
                    f"   {self._pick(item, 'platform', default='?')}/{self._pick(item, 'type', 'account_type', default='?')} ｜ {status} ｜ {self._groups_text(item)}"
                )
            if len(items) > len(display):
                lines.append(f"\n…还有 {len(items) - len(display)} 个未显示，可用关键词筛选。")
            yield event.plain_result("\n".join(lines))
        except Exception as exc:
            yield event.plain_result(f"❌ 查询账号失败\n{exc}")

    @filter.permission_type(filter.PermissionType.ADMIN)
    @s2.command("详情", alias={"detail", "info"})
    async def s2_detail(self, event: AstrMessageEvent, selector: str):
        try:
            account = await self._find_account(selector)
            aid = account.get("id")
            if aid is not None:
                try:
                    full = await self._request("GET", f"/api/v1/admin/accounts/{aid}")
                    full = self._unwrap(full)
                    if isinstance(full, dict):
                        account = full
                except Exception:
                    pass
            text = "\n".join([
                f"📦 Sub2API 账号 #{account.get('id', '?')}",
                f"名称：{self._display_name(account)}",
                f"平台：{self._pick(account, 'platform', default='-')}",
                f"类型：{self._pick(account, 'type', 'account_type', default='-')}",
                f"状态：{self._status_icon(str(self._pick(account, 'status', default='unknown')))} {self._pick(account, 'status', default='unknown')}",
                f"套餐：{self._plan_text(account)}",
                f"到期：{self._expiry_text(account)}",
                f"分组：{self._groups_text(account)}",
                f"并发：{self._pick(account, 'concurrency', 'max_concurrency', default='-')}",
                f"优先级：{self._pick(account, 'priority', default='-')}",
            ])
            yield event.plain_result(text)
        except Exception as exc:
            yield event.plain_result(f"❌ 查询详情失败\n{exc}")

    @filter.permission_type(filter.PermissionType.ADMIN)
    @s2.command("用量", alias={"usage", "quota"})
    async def s2_usage(self, event: AstrMessageEvent, selector: str, mode: str = ""):
        try:
            account = await self._find_account(selector)
            aid = account.get("id")
            force = str(mode).strip().lower() in {"刷新", "refresh", "force", "1", "true"}
            params = {"source": "active" if force else "passive", "force": "true" if force else None}
            usage_task = self._request("GET", f"/api/v1/admin/accounts/{aid}/usage", params=params)
            today_task = self._request("GET", f"/api/v1/admin/accounts/{aid}/today-stats")
            usage, today = await asyncio.gather(usage_task, today_task, return_exceptions=True)
            lines = [f"📊 {self._display_name(account)}（#{aid}）", f"模式：{'主动刷新' if force else '缓存/被动'}"]
            if isinstance(usage, Exception):
                lines.append(f"\n额度/窗口：获取失败：{usage}")
            else:
                pairs = self._pairs_for_display(usage, 10)
                lines.append("\n额度/窗口")
                lines.extend([f"• {x['key']}：{x['value']}" for x in pairs] or ["• 暂无数据"])
            if isinstance(today, Exception):
                lines.append(f"\n今日统计：获取失败：{today}")
            else:
                pairs = self._pairs_for_display(today, 10)
                lines.append("\n今日统计")
                lines.extend([f"• {x['key']}：{x['value']}" for x in pairs] or ["• 暂无数据"])
            yield event.plain_result("\n".join(lines))
        except Exception as exc:
            yield event.plain_result(f"❌ 查询用量失败\n{exc}")

    @filter.permission_type(filter.PermissionType.ADMIN)
    @s2.command("模型", alias={"models"})
    async def s2_models(self, event: AstrMessageEvent, selector: str):
        try:
            account = await self._find_account(selector)
            aid = account.get("id")
            models = await self._models_for_account(aid)
            if not models:
                yield event.plain_result(f"📚 {self._display_name(account)}（#{aid}）\n没有获取到可展示的模型。")
                return
            shown = models[:30]
            text = f"📚 {self._display_name(account)}（#{aid}）\n可用模型：{len(models)} 个\n\n" + "\n".join(f"• {m}" for m in shown)
            if len(models) > 30:
                text += f"\n…还有 {len(models) - 30} 个"
            yield event.plain_result(text)
        except Exception as exc:
            yield event.plain_result(f"❌ 查询模型失败\n{exc}")

    @filter.permission_type(filter.PermissionType.ADMIN)
    @s2.command("状态", alias={"status"})
    async def s2_status(self, event: AstrMessageEvent):
        try:
            stats_task = self._request("GET", "/api/v1/admin/dashboard/stats")
            realtime_task = self._request("GET", "/api/v1/admin/dashboard/realtime")
            stats, realtime = await asyncio.gather(stats_task, realtime_task, return_exceptions=True)
            lines = ["🖥️ Sub2API 状态"]
            if isinstance(realtime, Exception):
                lines.append(f"\n实时状态：获取失败：{realtime}")
            else:
                lines.append("\n实时状态")
                lines.extend([f"• {x['key']}：{x['value']}" for x in self._pairs_for_display(realtime, 10)] or ["• 暂无数据"])
            if isinstance(stats, Exception):
                lines.append(f"\n全局统计：获取失败：{stats}")
            else:
                lines.append("\n全局统计")
                lines.extend([f"• {x['key']}：{x['value']}" for x in self._pairs_for_display(stats, 10)] or ["• 暂无数据"])
            yield event.plain_result("\n".join(lines))
        except Exception as exc:
            yield event.plain_result(f"❌ 查询状态失败\n{exc}")

    @filter.permission_type(filter.PermissionType.ADMIN)
    @s2.command("面板", alias={"panel", "dashboard"})
    async def s2_panel(self, event: AstrMessageEvent, keyword: str = ""):
        try:
            url = await self._render_panel_image(keyword.strip())
            yield event.image_result(url)
        except Exception as exc:
            logger.warning(f"[sub2api_status] panel failed: {exc}")
            yield event.plain_result(f"❌ 生成精美面板失败\n{exc}")

    @filter.permission_type(filter.PermissionType.ADMIN)
    @s2.command("卡片", alias={"card"})
    async def s2_card(self, event: AstrMessageEvent, selector: str):
        try:
            url = await self._render_detail_image(selector)
            yield event.image_result(url)
        except Exception as exc:
            logger.warning(f"[sub2api_status] card failed: {exc}")
            yield event.plain_result(f"❌ 生成账号卡片失败\n{exc}")

    async def terminate(self):
        return