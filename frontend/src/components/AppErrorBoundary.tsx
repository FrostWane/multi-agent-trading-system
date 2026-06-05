import React from "react";

interface AppErrorBoundaryState {
  error: Error | null;
}

const SESSION_STORAGE_KEY = "multi-agent-trading-system:last-session";

export class AppErrorBoundary extends React.Component<React.PropsWithChildren, AppErrorBoundaryState> {
  state: AppErrorBoundaryState = {
    error: null
  };

  static getDerivedStateFromError(error: Error): AppErrorBoundaryState {
    return { error };
  }

  clearSessionAndReload = () => {
    window.localStorage.removeItem(SESSION_STORAGE_KEY);
    window.location.reload();
  };

  render() {
    if (!this.state.error) {
      return this.props.children;
    }

    return (
      <main className="app-shell">
        <section className="fatal-panel" role="alert">
          <h1>页面渲染异常</h1>
          <p>报告或图表数据里有无法直接渲染的字段，页面已拦截错误，没有继续白屏。</p>
          <small>{this.state.error.message}</small>
          <div className="actions">
            <button type="button" onClick={() => window.location.reload()}>
              重新加载
            </button>
            <button type="button" onClick={this.clearSessionAndReload}>
              清除缓存
            </button>
          </div>
        </section>
      </main>
    );
  }
}
