import type { ReactNode } from "react";

interface Props {
  children: ReactNode;
}

export default function MolduraDeTerminal({ children }: Props) {
  return (
    <>
      <rect className="ilustracao__traco" x="8" y="10" width="304" height="170" rx="4" />
      <line className="ilustracao__traco" x1="8" y1="34" x2="312" y2="34" />
      <circle className="ilustracao__traco" cx="22" cy="22" r="4" />
      <circle className="ilustracao__traco" cx="34" cy="22" r="4" />
      <circle className="ilustracao__traco" cx="46" cy="22" r="4" />
      {children}
    </>
  );
}
