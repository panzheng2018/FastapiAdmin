/**
 * 确认弹窗 —— 封装 ElMessageBox.confirm 常用配置
 */

import { ElMessageBox, type ElMessageBoxOptions } from "element-plus";
import type { VNode } from "vue";

/** 处理换行与 HTML 支持 */
function resolveMessage(message: string | VNode | (() => VNode)): {
  content: string | VNode | (() => VNode);
  isHtml: boolean;
} {
  if (typeof message !== "string") {
    return { content: message, isHtml: false };
  }
  if (/<[a-z][\s\S]*>/i.test(message)) {
    return { content: message, isHtml: true };
  }
  if (message.includes("\n")) {
    const formatted = message
      .split("\n")
      .map((line) => line.trim())
      .filter((line) => line.length > 0)
      .join("<br/>");
    return { content: formatted, isHtml: true };
  }
  return { content: message, isHtml: false };
}

/** 删除确认 */
export async function confirmDelete(
  message: string | VNode | (() => VNode) = "确认删除该项数据?",
  options?: ElMessageBoxOptions
): Promise<void> {
  const { content, isHtml } = resolveMessage(message);
  await ElMessageBox.confirm(content as any, "警告", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning",
    dangerouslyUseHTMLString: isHtml,
    ...options,
  });
}

/** 批量删除确认 */
export async function confirmBatchDelete(
  count: number,
  names?: string[],
  options?: ElMessageBoxOptions
): Promise<void> {
  const detail = names?.length
    ? `（${names.slice(0, 5).join("、")}${names.length > 5 ? `…等${count}条` : ""}）`
    : "";
  await ElMessageBox.confirm(`确定删除选中的 ${count} 条数据吗？${detail}`, "批量删除", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning",
    ...options,
  });
}

/** 状态切换确认 */
export async function confirmToggleStatus(
  value: "enable" | "disable",
  options?: ElMessageBoxOptions
): Promise<void> {
  await ElMessageBox.confirm(`确认${value === "enable" ? "启用" : "停用"}该项数据?`, "警告", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning",
    ...options,
  });
}

/** 通用确认 */
export async function confirmAction(
  message: string | VNode | (() => VNode),
  title = "警告",
  options?: ElMessageBoxOptions
): Promise<void> {
  const { content, isHtml } = resolveMessage(message);
  await ElMessageBox.confirm(content as any, title, {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning",
    dangerouslyUseHTMLString: isHtml,
    ...options,
  });
}

