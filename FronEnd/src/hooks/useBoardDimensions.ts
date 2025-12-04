import { useEffect, useState } from 'react';

export interface BoardDimensions {
  containerWidth: number;
  containerHeight: number;
  imageWidth: number;
  imageHeight: number;
  imageX: number;
  imageY: number;
  containerLeft: number;
  containerTop: number;
  imageScreenX: number;
  imageScreenY: number;
}

export const useBoardDimensions = (containerRef: React.RefObject<HTMLDivElement>, imageSrc: string) => {
  const [boardDimensions, setBoardDimensions] = useState<BoardDimensions>({
    containerWidth: 0,
    containerHeight: 0,
    imageWidth: 0,
    imageHeight: 0,
    imageX: 0,
    imageY: 0,
    containerLeft: 0,
    containerTop: 0,
    imageScreenX: 0,
    imageScreenY: 0,
  });

  useEffect((): (() => void) => {
    let ro: ResizeObserver | null = null;

    const updateDimensions = () => {
      if (!containerRef.current) return;

      const container = containerRef.current;
      const containerRect = container.getBoundingClientRect();

      const img = new Image();
      img.src = imageSrc;

      img.onload = () => {
        const containerWidth = containerRect.width;
        const containerHeight = containerRect.height;
        const containerLeft = containerRect.left + window.scrollX;
        const containerTop = containerRect.top + window.scrollY;

        const imageAspectRatio = img.naturalWidth / img.naturalHeight;
        const containerAspectRatio = containerWidth / containerHeight;

        let imageWidth = 0,
          imageHeight = 0,
          imageX = 0,
          imageY = 0;

        if (containerAspectRatio > imageAspectRatio) {
          imageHeight = containerHeight;
          imageWidth = imageHeight * imageAspectRatio;
          imageX = (containerWidth - imageWidth) / 2;
          imageY = 0;
        } else {
          imageWidth = containerWidth;
          imageHeight = imageWidth / imageAspectRatio;
          imageX = 0;
          imageY = (containerHeight - imageHeight) / 2;
        }

        const imageScreenX = containerLeft + imageX;
        const imageScreenY = containerTop + imageY;

        setBoardDimensions({
          containerWidth,
          containerHeight,
          imageWidth,
          imageHeight,
          imageX,
          imageY,
          containerLeft,
          containerTop,
          imageScreenX,
          imageScreenY,
        });
      };
    };

    updateDimensions();

    if (window.ResizeObserver) {
      ro = new ResizeObserver(updateDimensions);
      if (containerRef.current) ro.observe(containerRef.current);
    }

    window.addEventListener('resize', updateDimensions);
    window.addEventListener('scroll', updateDimensions, { passive: true });

    return () => {
      if (ro) ro.disconnect();
      window.removeEventListener('resize', updateDimensions);
      window.removeEventListener('scroll', updateDimensions);
    };
  }, [containerRef, imageSrc]);

  return boardDimensions;
};