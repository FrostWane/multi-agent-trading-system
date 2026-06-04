import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { App } from "../src/App";

function today() {
  const value = new Date();
  const year = value.getFullYear();
  const month = String(value.getMonth() + 1).padStart(2, "0");
  const day = String(value.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

describe("App", () => {
  it("renders the trading workspace", () => {
    render(<App />);
    expect(screen.getByText("多智能体量化分析系统")).toBeInTheDocument();
    expect(screen.getByText("智能体流程")).toBeInTheDocument();
    expect(screen.getByText("智能体详情")).toBeInTheDocument();
    expect(screen.getByText("RAG 导入")).toBeInTheDocument();
    expect(screen.getByText("回测参数")).toBeInTheDocument();
    expect(screen.getByText("策略回测对比")).toBeInTheDocument();
    expect(screen.getByText("暂无报告。")).toBeInTheDocument();
    expect(screen.getByLabelText("策略范围")).toBeInTheDocument();
    expect(screen.getByLabelText("股票搜索")).toBeInTheDocument();
    expect(screen.getByLabelText("开始日期")).toHaveValue("2026-01-01");
    expect(screen.getByLabelText("结束日期")).toHaveValue(today());
    expect(screen.getByTitle("开始分析")).toBeInTheDocument();
  });
});
