export function PDFSkeleton() {
  return (
    <div style={{ padding: "1rem" }}>
      <div
        style={{
          background: "#af4343ff",
          height: 20,
          width: "40%",
          borderRadius: 4,
          marginBottom: "1rem",
        }}
      />
      <div
        style={{
          background: "#5a78a0ff",
          height: 400,
          width: "100%",
          borderRadius: 8,
        }}
      />
    </div>
  );
}

export function PageSkeleton() {
  return (
    <div
      style={{
        height: 600,
        background: "#f3f3f3",
        borderRadius: 8,
        marginBottom: "1rem",
      }}
    />
  );
}
