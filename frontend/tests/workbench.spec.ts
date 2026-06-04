import { expect, test } from "@playwright/test";

test("shows core workbench panels", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "多智能体量化分析系统" })).toBeVisible();
  await expect(page.getByLabel("智能体执行流程")).toBeVisible();
  await expect(page.getByLabel("分析指标")).toBeVisible();
});
