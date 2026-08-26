import {
  useCallback,
  useEffect,
  useRef,
  useState,
  type CSSProperties,
  type PropsWithChildren,
} from "react";
import { useKeyboardInsets } from "./Keyboard";

type MobileScrollProps = PropsWithChildren<{
  className?: string;
}>;

const scrollPhysics = {
  momentumFriction: 2.1,
  momentumVelocityScale: 890,
  momentumTolerance: 18,
  bounceTension: 200,
  bounceFriction: 40,
  bounceTolerance: 0.5,
  overdragScale: 0.5,
  maxOverdrag: 96,
  velocitySampleWindow: 100,
  tapSlop: 8,
} as const;

function shouldIgnoreScrollDrag(target: EventTarget | null) {
  return (
    target instanceof Element &&
    Boolean(target.closest('[data-scroll-drag="ignore"]'))
  );
}

type DragSample = {
  y: number;
  time: number;
};

type DragSession = {
  active: boolean;
  captured: boolean;
  pointerId: number | null;
  startY: number;
  startScrollTop: number;
  hasDragged: boolean;
};

export function MobileScroll({ className, children }: MobileScrollProps) {
  const { isKeyboardVisible, keyboardHeight, keyboardDragging } = useKeyboardInsets();
  const scrollRef = useRef<HTMLDivElement | null>(null);
  const hideTimerRef = useRef<number | null>(null);
  const inertiaFrameRef = useRef<number | null>(null);
  const lastInertiaTimeRef = useRef<number | null>(null);
  const overscrollRef = useRef(0);
  const dragSamplesRef = useRef<DragSample[]>([]);
  const isDraggingRef = useRef(false);
  const suppressNextClickRef = useRef(false);
  const suppressClickTimerRef = useRef<number | null>(null);
  const dragSessionRef = useRef<DragSession>({
    active: false,
    captured: false,
    pointerId: null,
    startY: 0,
    startScrollTop: 0,
    hasDragged: false,
  });
  const [isDragging, setIsDragging] = useState(false);
  const [overscrollY, setOverscrollY] = useState(0);
  const [thumb, setThumb] = useState({
    visible: false,
    top: 0,
    height: 0,
    enabled: false,
  });

  const stopInertia = useCallback(() => {
    if (inertiaFrameRef.current !== null) {
      window.cancelAnimationFrame(inertiaFrameRef.current);
      inertiaFrameRef.current = null;
    }

    lastInertiaTimeRef.current = null;
  }, []);

  const suppressUpcomingClick = useCallback(() => {
    suppressNextClickRef.current = true;

    if (suppressClickTimerRef.current !== null) {
      window.clearTimeout(suppressClickTimerRef.current);
    }

    suppressClickTimerRef.current = window.setTimeout(() => {
      suppressNextClickRef.current = false;
      suppressClickTimerRef.current = null;
    }, 180);
  }, []);

  const setRubberBand = useCallback((value: number) => {
    const clamped = Math.max(-scrollPhysics.maxOverdrag, Math.min(scrollPhysics.maxOverdrag, value));
    overscrollRef.current = clamped;
    setOverscrollY(clamped);
  }, []);

  const maxScrollTop = useCallback((scroll: HTMLDivElement) => {
    return Math.max(0, scroll.scrollHeight - scroll.clientHeight);
  }, []);

  const rubberBand = useCallback((distance: number) => {
    return distance * scrollPhysics.overdragScale;
  }, []);

  const pushDragSample = useCallback((y: number) => {
    const time = performance.now();
    const samples = [...dragSamplesRef.current, { y, time }].filter(
      (sample) => time - sample.time <= scrollPhysics.velocitySampleWindow,
    );

    dragSamplesRef.current = samples;
  }, []);

  const releaseVelocity = useCallback(() => {
    const samples = dragSamplesRef.current;
    if (samples.length < 2) return 0;

    const first = samples[0];
    const last = samples[samples.length - 1];
    const elapsed = Math.max(1, last.time - first.time);
    const pointerVelocity = (last.y - first.y) / elapsed;

    return -pointerVelocity * scrollPhysics.momentumVelocityScale;
  }, []);

  const springBack = useCallback((initialVelocity = 0) => {
    stopInertia();

    let position = overscrollRef.current;
    let velocity = Math.max(-1400, Math.min(1400, initialVelocity));
    let lastTime: number | null = null;

    const step = (time: number) => {
      const deltaTime = Math.min(0.034, ((lastTime === null ? time : time - lastTime) || 16) / 1000);
      lastTime = time;
      const acceleration = -scrollPhysics.bounceTension * position - scrollPhysics.bounceFriction * velocity;
      velocity += acceleration * deltaTime;
      position += velocity * deltaTime;

      if (Math.abs(position) < scrollPhysics.bounceTolerance && Math.abs(velocity) < scrollPhysics.bounceTolerance) {
        setRubberBand(0);
        inertiaFrameRef.current = null;
        return;
      }

      setRubberBand(position);
      inertiaFrameRef.current = window.requestAnimationFrame(step);
    };

    inertiaFrameRef.current = window.requestAnimationFrame(step);
  }, [setRubberBand, stopInertia]);

  const updateThumb = useCallback((visible = true) => {
    const scroll = scrollRef.current;
    if (!scroll) return;

    const { clientHeight, scrollHeight, scrollTop } = scroll;
    const enabled = scrollHeight > clientHeight + 2;
    const height = enabled ? Math.max(36, (clientHeight / scrollHeight) * clientHeight) : 0;
    const maxThumbTop = Math.max(0, clientHeight - height - 8);
    const maxScrollTop = Math.max(1, scrollHeight - clientHeight);
    const top = enabled ? 4 + (scrollTop / maxScrollTop) * maxThumbTop : 0;

    setThumb({ visible: visible && enabled, top, height, enabled });

    if (hideTimerRef.current !== null) {
      window.clearTimeout(hideTimerRef.current);
    }

    if (visible && enabled && !isDraggingRef.current) {
      hideTimerRef.current = window.setTimeout(() => {
        setThumb((current) => ({ ...current, visible: false }));
      }, 650);
    }
  }, []);

  const applyDragPosition = useCallback((startScrollTop: number, movementY: number, scroll: HTMLDivElement) => {
    const desiredScrollTop = startScrollTop - movementY;
    const maxTop = maxScrollTop(scroll);

    if (desiredScrollTop < 0) {
      scroll.scrollTop = 0;
      setRubberBand(rubberBand(-desiredScrollTop));
    } else if (desiredScrollTop > maxTop) {
      scroll.scrollTop = maxTop;
      setRubberBand(-rubberBand(desiredScrollTop - maxTop));
    } else {
      scroll.scrollTop = desiredScrollTop;
      setRubberBand(0);
    }

    updateThumb(true);
  }, [maxScrollTop, rubberBand, setRubberBand, updateThumb]);

  useEffect(() => {
    updateThumb(false);

    const scroll = scrollRef.current;
    if (!scroll) return;

    const handleScroll = () => updateThumb(true);
    const resizeObserver = new ResizeObserver(() => updateThumb(false));

    scroll.addEventListener("scroll", handleScroll, { passive: true });
    resizeObserver.observe(scroll);

    if (scroll.firstElementChild) {
      resizeObserver.observe(scroll.firstElementChild);
    }

    return () => {
      scroll.removeEventListener("scroll", handleScroll);
      resizeObserver.disconnect();

      if (hideTimerRef.current !== null) {
        window.clearTimeout(hideTimerRef.current);
      }

      if (suppressClickTimerRef.current !== null) {
        window.clearTimeout(suppressClickTimerRef.current);
      }

      stopInertia();
    };
  }, [stopInertia, updateThumb]);

  useEffect(() => {
    updateThumb(false);
  }, [keyboardHeight, updateThumb]);

  const startMomentum = useCallback((scroll: HTMLDivElement, initialVelocity: number) => {
    let velocity = initialVelocity;

    const step = (time: number) => {
      const deltaTime =
        lastInertiaTimeRef.current === null ? 16 : Math.min(34, time - lastInertiaTimeRef.current);
      const deltaSeconds = deltaTime / 1000;
      lastInertiaTimeRef.current = time;
      velocity *= Math.exp(-scrollPhysics.momentumFriction * deltaSeconds);

      if (Math.abs(velocity) < scrollPhysics.momentumTolerance) {
        updateThumb(true);
        lastInertiaTimeRef.current = null;
        inertiaFrameRef.current = null;
        return;
      }

      const maxTop = maxScrollTop(scroll);
      const attempted = scroll.scrollTop + velocity * deltaSeconds;
      const before = scroll.scrollTop;

      if (attempted < 0) {
        scroll.scrollTop = 0;
        setRubberBand(rubberBand(-attempted));
        springBack(velocity * scrollPhysics.overdragScale);
        return;
      }

      if (attempted > maxTop) {
        scroll.scrollTop = maxTop;
        setRubberBand(-rubberBand(attempted - maxTop));
        springBack(velocity * scrollPhysics.overdragScale);
        return;
      }

      scroll.scrollTop = attempted;
      updateThumb(true);

      if (scroll.scrollTop === before) {
        lastInertiaTimeRef.current = null;
        inertiaFrameRef.current = null;
        return;
      }

      inertiaFrameRef.current = window.requestAnimationFrame(step);
    };

    if (Math.abs(velocity) > scrollPhysics.momentumTolerance) {
      lastInertiaTimeRef.current = null;
      inertiaFrameRef.current = window.requestAnimationFrame(step);
    } else {
      updateThumb(true);
    }
  }, [maxScrollTop, rubberBand, setRubberBand, springBack, updateThumb]);

  const endDrag = useCallback((event: React.PointerEvent<HTMLDivElement>) => {
    const scroll = scrollRef.current;
    const session = dragSessionRef.current;

    if (!scroll || !session.active || session.pointerId !== event.pointerId) return;

    // A nested horizontal scroller can let pointer-down bubble, then claim
    // pointer-move. Its pointer-up may still reach this parent. Without a
    // completed parent drag there is no valid release velocity or click to
    // suppress, so discard the pending session without starting motion.
    if (!session.hasDragged) {
      dragSamplesRef.current = [];
      dragSessionRef.current = {
        active: false,
        captured: false,
        pointerId: null,
        startY: 0,
        startScrollTop: 0,
        hasDragged: false,
      };
      setIsDragging(false);
      isDraggingRef.current = false;
      return;
    }

    if (session.captured) {
      try {
        event.currentTarget.releasePointerCapture(event.pointerId);
      } catch {
        // Pointer capture can already be gone after a browser-level cancel.
      }
    }

    if (session.hasDragged) {
      event.preventDefault();
      suppressUpcomingClick();
    }

    pushDragSample(event.clientY);
    const velocity = releaseVelocity();
    dragSessionRef.current = {
      active: false,
      captured: false,
      pointerId: null,
      startY: 0,
      startScrollTop: 0,
      hasDragged: false,
    };
    setIsDragging(false);
    isDraggingRef.current = false;

    if (Math.abs(overscrollRef.current) > 0.1) {
      springBack(velocity * scrollPhysics.overdragScale);
      return;
    }

    startMomentum(scroll, velocity);
  }, [pushDragSample, releaseVelocity, springBack, startMomentum, suppressUpcomingClick]);

  const handlePointerDown = useCallback((event: React.PointerEvent<HTMLDivElement>) => {
    const scroll = scrollRef.current;
    if (!scroll || scroll.scrollHeight <= scroll.clientHeight) return;
    if (event.pointerType === "mouse" && event.button !== 0) return;

    stopInertia();
    if (shouldIgnoreScrollDrag(event.target)) {
      setRubberBand(0);
      return;
    }

    isDraggingRef.current = false;
    dragSamplesRef.current = [];
    pushDragSample(event.clientY);
    setRubberBand(0);
    setThumb((current) => ({ ...current, visible: current.enabled }));

    dragSessionRef.current = {
      active: true,
      captured: false,
      pointerId: event.pointerId,
      startY: event.clientY,
      startScrollTop: scroll.scrollTop,
      hasDragged: false,
    };
  }, [pushDragSample, setRubberBand, stopInertia]);

  const handlePointerMove = useCallback((event: React.PointerEvent<HTMLDivElement>) => {
    const scroll = scrollRef.current;
    const session = dragSessionRef.current;

    if (!scroll || !session.active || session.pointerId !== event.pointerId) return;

    const movementY = event.clientY - session.startY;
    if (!session.hasDragged && Math.abs(movementY) < scrollPhysics.tapSlop) return;

    if (!session.captured) {
      try {
        event.currentTarget.setPointerCapture(event.pointerId);
        session.captured = true;
      } catch {
        // Pointer capture can fail if the browser has already canceled the pointer.
      }
    }

    event.preventDefault();
    session.hasDragged = true;
    suppressUpcomingClick();
    isDraggingRef.current = true;
    setIsDragging(true);
    pushDragSample(event.clientY);
    applyDragPosition(session.startScrollTop, movementY, scroll);
  }, [applyDragPosition, pushDragSample, suppressUpcomingClick]);

  const suppressClickAfterDrag = useCallback((event: React.MouseEvent<HTMLDivElement>) => {
    if (!suppressNextClickRef.current) return;

    suppressNextClickRef.current = false;
    if (suppressClickTimerRef.current !== null) {
      window.clearTimeout(suppressClickTimerRef.current);
      suppressClickTimerRef.current = null;
    }
    event.preventDefault();
    event.stopPropagation();
  }, []);

  const style = {
    "--keyboard-height": `${keyboardHeight}px`,
  } as CSSProperties;

  return (
    <section
      className={`mobile-page ${className ?? ""}`}
      data-keyboard-dragging={keyboardDragging ? "true" : "false"}
      data-keyboard-visible={isKeyboardVisible ? "true" : "false"}
      style={style}
    >
      <div
        ref={scrollRef}
        className="mobile-scroll"
        data-testid="mobile-scroll"
        data-dragging={isDragging ? "true" : "false"}
        data-overscroll={overscrollY.toFixed(2)}
        onPointerDown={handlePointerDown}
        onPointerMove={handlePointerMove}
        onPointerUp={endDrag}
        onPointerCancel={endDrag}
        onClickCapture={suppressClickAfterDrag}
      >
        <div
          className="mobile-scroll-content"
          data-testid="mobile-scroll-content"
          style={{ transform: `translateY(${overscrollY}px)` }}
        >
          {children}
        </div>
      </div>
      <div
        className="mobile-scrollbar"
        data-testid="mobile-scrollbar"
        data-visible={thumb.visible ? "true" : "false"}
        aria-hidden="true"
      >
        <div
          className="mobile-scrollbar-thumb"
          style={{
            height: thumb.height,
            transform: `translateY(${thumb.top}px)`,
          }}
        />
      </div>
    </section>
  );
}
