import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PriceChart } from "../src/components/PriceChart";

describe("PriceChart", () => {
  it("renders non-empty K-line data without crashing", () => {
    render(
      <PriceChart
        data={[
          { date: "2026-01-01", open: 10, high: 11, low: 9.8, close: 10.5, volume: 100000 },
          { date: "2026-01-02", open: 10.5, high: 10.8, low: 10.1, close: 10.2, volume: 120000 },
          { date: "2026-01-05", open: 10.2, high: 11.2, low: 10, close: 11, volume: 160000 },
          { date: "2026-01-06", open: 11, high: 11.4, low: 10.7, close: 10.9, volume: 130000 },
          { date: "2026-01-07", open: 10.9, high: 11.5, low: 10.8, close: 11.3, volume: 150000 }
        ]}
      />
    );

    expect(screen.getByText("K 线走势")).toBeInTheDocument();
    expect(screen.getByText("2026-01-07 收盘 11.30")).toBeInTheDocument();
  });
});
