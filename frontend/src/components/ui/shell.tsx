import { ReactNode } from "react";

interface ShellProps {
  children: ReactNode;
}

export function Shell({ children }: ShellProps) {
  return <div className="container-shell py-8 md:py-10">{children}</div>;
}
