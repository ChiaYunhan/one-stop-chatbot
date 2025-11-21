import React from "react";

interface State {
  hasError: boolean;
}

export class ErrorBoundary extends React.Component<any, State> {
  constructor(props: any) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error: any, errorInfo: any) {
    console.error("ErrorBoundary caught:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: "0.5rem", color: "red" }}>
          Failed to render page.
        </div>
      );
    }
    return this.props.children;
  }
}
