import { useState, type PointerEvent as ReactPointerEvent } from "react";

type CursorState = {
  visible: boolean;
  active: boolean;
  x: number;
  y: number;
};

export function useMobileCursor() {
  const debug =
    typeof window !== "undefined" && new URLSearchParams(window.location.search).has("cursorDebug");
  const [cursor, setCursor] = useState<CursorState>({
    visible: false,
    active: false,
    x: 0,
    y: 0,
  });

  const updatePosition = (event: ReactPointerEvent<HTMLElement>) => {
    const bounds = event.currentTarget.getBoundingClientRect();
    const localX = bounds.width === 0 ? 0 : ((event.clientX - bounds.left) / bounds.width) * event.currentTarget.offsetWidth;
    const localY =
      bounds.height === 0 ? 0 : ((event.clientY - bounds.top) / bounds.height) * event.currentTarget.offsetHeight;

    setCursor((current) => ({
      ...current,
      visible: true,
      x: localX,
      y: localY,
    }));
  };

  return {
    cursorHandlers: {
      onPointerEnter: updatePosition,
      onPointerMove: updatePosition,
      onPointerDown: (event: ReactPointerEvent<HTMLElement>) => {
        updatePosition(event);
        setCursor((current) => ({ ...current, active: true }));
      },
      onPointerUp: (event: ReactPointerEvent<HTMLElement>) => {
        updatePosition(event);
        setCursor((current) => ({ ...current, active: false }));
      },
      onPointerCancel: () => {
        setCursor((current) => ({ ...current, active: false, visible: false }));
      },
      onPointerLeave: () => {
        setCursor((current) => ({ ...current, active: false, visible: false }));
      },
    },
    cursorDebug: debug,
    cursorElement: (
      <div
        className="mobile-cursor"
        data-active={cursor.active ? "true" : "false"}
        data-debug={debug ? "true" : "false"}
        data-visible={cursor.visible ? "true" : "false"}
        data-testid="mobile-cursor"
        style={{
          transform: `translate3d(${cursor.x}px, ${cursor.y}px, 0) translate(-50%, -50%)`,
        }}
      >
        {debug ? <span className="mobile-cursor-hotspot" aria-hidden="true" /> : null}
      </div>
    ),
  };
}
