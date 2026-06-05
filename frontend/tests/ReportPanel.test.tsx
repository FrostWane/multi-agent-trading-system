import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ReportPanel } from "../src/components/ReportPanel";
import type { AnalysisResult } from "../src/types/analysis";

describe("ReportPanel", () => {
  it("renders unexpected report field shapes without crashing", () => {
    const result = {
      engine: "test-engine",
      report: {
        summary: { text: "对象格式摘要" },
        recommendation: "cautious",
        key_points: [{ point: "对象格式要点" }],
        risk_notes: "单条风险提示",
        llm_commentary: { text: "对象格式评论" },
        disclaimer: "仅用于测试"
      },
      critic: {
        passed: false,
        confidence: "medium",
        issues: { data: "字段格式异常" },
        suggestions: [{ action: "继续观察" }]
      }
    } as unknown as AnalysisResult;

    render(<ReportPanel result={result} />);

    expect(screen.getByText(/对象格式摘要/)).toBeInTheDocument();
    expect(screen.getByText("谨慎观察")).toBeInTheDocument();
    expect(screen.getByText(/字段格式异常/)).toBeInTheDocument();
    expect(screen.getByText("仅用于测试")).toBeInTheDocument();
  });
});
