import {
  createContext,
  type InputHTMLAttributes,
  type PointerEvent as ReactPointerEvent,
  type PropsWithChildren,
  type Ref,
  type TextareaHTMLAttributes,
  useContext,
  useMemo,
  useRef,
  useState,
} from "react";
import { motion } from "motion/react";
import { mobileAssets } from "./assets";
import { useMobileDevice } from "./Device";

type KeyboardContextValue = {
  visible: boolean;
  height: number;
  fullHeight: number;
  progress: number;
  dragOffset: number;
  isDragging: boolean;
  focusedElement: HTMLElement | null;
  setDragOffset: (offset: number) => void;
  setDragging: (dragging: boolean) => void;
  show: (element?: HTMLElement | null) => void;
  hide: () => void;
};

type KeyboardInputProps = InputHTMLAttributes<HTMLInputElement> & {
  ref?: Ref<HTMLInputElement>;
};

const KeyboardContext = createContext<KeyboardContextValue | null>(null);

export function KeyboardProvider({ children }: PropsWithChildren) {
  const { device } = useMobileDevice();
  const [visible, setVisible] = useState(false);
  const [dragOffset, setRawDragOffset] = useState(0);
  const [isDragging, setDragging] = useState(false);
  const [focusedElement, setFocusedElement] = useState<HTMLElement | null>(null);
  const fullHeight = device.geometry.keyboard.height;
  const setDragOffset = (offset: number) => {
    setRawDragOffset(Math.max(0, Math.min(fullHeight, offset)));
  };

  const value = useMemo<KeyboardContextValue>(
    () => ({
      visible,
      height: visible ? Math.max(0, fullHeight - dragOffset) : 0,
      fullHeight,
      dragOffset,
      isDragging,
      progress: visible ? 1 : 0,
      focusedElement,
      setDragOffset,
      setDragging,
      show: (element) => {
        setRawDragOffset(0);
        setDragging(false);
        setFocusedElement(element ?? null);
        setVisible(true);
      },
      hide: () => {
        focusedElement?.blur();
        setDragging(false);
        setFocusedElement(null);
        setVisible(false);
      },
    }),
    [dragOffset, focusedElement, fullHeight, isDragging, visible],
  );

  return <KeyboardContext.Provider value={value}>{children}</KeyboardContext.Provider>;
}

export function useKeyboard() {
  const context = useContext(KeyboardContext);

  if (!context) {
    throw new Error("useKeyboard must be used inside KeyboardProvider");
  }

  return context;
}

export function useKeyboardInsets() {
  const keyboard = useKeyboard();
  const { device } = useMobileDevice();
  const reservesAndroidNavigation = device.platform === "android" && !keyboard.visible;

  return {
    keyboardHeight: keyboard.height,
    keyboardFullHeight: keyboard.fullHeight,
    keyboardDragging: keyboard.isDragging,
    bottomInset: reservesAndroidNavigation
      ? 0
      : device.platform === "android"
        ? keyboard.height
        : Math.max(device.geometry.safeArea.bottom, keyboard.height),
    availableHeight:
      device.geometry.screen.height -
      keyboard.height -
      (reservesAndroidNavigation ? device.geometry.safeArea.bottom : 0),
    isKeyboardVisible: keyboard.visible,
  };
}

export function useKeyboardDismissDrag() {
  const keyboard = useKeyboard();
  const dragRef = useRef({
    pointerId: null as number | null,
    startY: 0,
    lastY: 0,
    lastTime: 0,
    velocityY: 0,
  });

  const endDismissDrag = (event: ReactPointerEvent<HTMLElement>) => {
    const drag = dragRef.current;
    if (drag.pointerId !== event.pointerId) return;

    try {
      event.currentTarget.releasePointerCapture(event.pointerId);
    } catch {
      // Capture may already be gone after pointer cancel.
    }

    const nextY = Math.max(0, event.clientY - drag.startY);
    const shouldDismiss = nextY > 76 || drag.velocityY > 0.45;
    drag.pointerId = null;

    if (shouldDismiss) {
      keyboard.setDragOffset(nextY);
      keyboard.hide();
      return;
    }

    keyboard.setDragging(false);
    keyboard.setDragOffset(0);
  };

  return {
    onPointerDown: (event: ReactPointerEvent<HTMLElement>) => {
      if (!keyboard.visible) return;
      if (event.pointerType === "mouse" && event.button !== 0) return;
      if (
        event.target instanceof Element &&
        event.target.closest('button, input, textarea, select, a, [role="button"], [contenteditable="true"]')
      ) {
        return;
      }

      keyboard.setDragging(true);
      dragRef.current = {
        pointerId: event.pointerId,
        startY: event.clientY,
        lastY: event.clientY,
        lastTime: performance.now(),
        velocityY: 0,
      };
      event.currentTarget.setPointerCapture(event.pointerId);
    },
    onPointerMove: (event: ReactPointerEvent<HTMLElement>) => {
      const drag = dragRef.current;
      if (drag.pointerId !== event.pointerId) return;

      const now = performance.now();
      const elapsed = Math.max(1, now - drag.lastTime);
      drag.velocityY = (event.clientY - drag.lastY) / elapsed;
      drag.lastY = event.clientY;
      drag.lastTime = now;
      keyboard.setDragOffset(Math.max(0, event.clientY - drag.startY));
    },
    onPointerUp: endDismissDrag,
    onPointerCancel: endDismissDrag,
  };
}

export function KeyboardInput(props: KeyboardInputProps) {
  const keyboard = useKeyboard();
  const { ref, ...inputProps } = props;

  return (
    <input
      {...inputProps}
      ref={ref}
      onFocus={(event) => {
        keyboard.show(event.currentTarget);
        inputProps.onFocus?.(event);
      }}
    />
  );
}

export function KeyboardTextarea(props: TextareaHTMLAttributes<HTMLTextAreaElement>) {
  const keyboard = useKeyboard();

  return (
    <textarea
      {...props}
      onFocus={(event) => {
        keyboard.show(event.currentTarget);
        props.onFocus?.(event);
      }}
    />
  );
}

export function KeyboardDock() {
  const keyboard = useKeyboard();
  const { device } = useMobileDevice();
  const dismissDrag = useKeyboardDismissDrag();
  const keyboardTransition = keyboard.isDragging
    ? { duration: 0 }
    : { duration: 0.26, ease: [0.2, 0.8, 0.2, 1] as [number, number, number, number] };

  return (
    <motion.div
      className="keyboard-dock"
      data-platform={device.platform}
      data-testid="keyboard-dock"
      data-visible={keyboard.visible ? "true" : "false"}
      initial={{ y: keyboard.fullHeight }}
      animate={{ y: keyboard.visible ? keyboard.dragOffset : keyboard.fullHeight }}
      aria-hidden={keyboard.visible ? undefined : "true"}
      style={{ height: keyboard.fullHeight }}
      transition={keyboardTransition}
      {...dismissDrag}
    >
      <img
        className="keyboard-asset"
        src={device.platform === "android" ? mobileAssets.androidKeyboard : mobileAssets.iphoneKeyboard}
        alt=""
        aria-hidden="true"
        draggable={false}
      />
    </motion.div>
  );
}
