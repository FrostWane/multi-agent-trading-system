import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { App } from "../src/App";

describe("App", () => {
  it("renders the trading workspace", () => {
    render(<App />);
    expect(screen.getByText("多智能体量化分析系统")).toBeInTheDocument();
    expect(screen.getByText("智能体流程")).toBeInTheDocument();
    expect(screen.getByText("智能体详情")).toBeInTheDocument();
    expect(screen.getByText("RAG 导入")).toBeInTheDocument();
    expect(screen.getByLabelText("股票搜索")).toBeInTheDocument();
    expect(screen.getByTitle("开始分析")).toBeInTheDocument();
  });
});
