import { expect, test } from "@playwright/test";

test("shows core workbench panels", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "多智能体量化分析系统" })).toBeVisible();
  await expect(page.getByRole("button", { name: /行情回测/ })).toBeVisible();
  await expect(page.getByRole("button", { name: /智能体协作/ })).toBeVisible();
  await expect(page.getByRole("button", { name: /报告证据/ })).toBeVisible();
  await expect(page.getByLabel("策略回测对比")).toBeVisible();
  await expect(page.getByLabel("分析指标")).toBeVisible();
  await page.getByRole("button", { name: /智能体协作/ }).click();
  await expect(page.getByLabel("智能体详情")).toBeVisible();
  await page.getByRole("button", { name: /报告证据/ }).click();
  await expect(page.getByLabel("RAG 文档导入")).toBeVisible();
});
