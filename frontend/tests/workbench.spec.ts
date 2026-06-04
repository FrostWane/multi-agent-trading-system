import { expect, test } from "@playwright/test";

test("shows core workbench panels", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Multi-Agent Trading System" })).toBeVisible();
  await expect(page.getByLabel("Agent execution timeline")).toBeVisible();
  await expect(page.getByLabel("Analysis metrics")).toBeVisible();
});
