import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { App } from "../src/App";

describe("App", () => {
  it("renders the trading workspace", () => {
    render(<App />);
    expect(screen.getByText("Multi-Agent Trading System")).toBeInTheDocument();
    expect(screen.getByText("Agent Flow")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /run/i })).toBeInTheDocument();
  });
});
