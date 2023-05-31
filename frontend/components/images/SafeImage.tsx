import { CSSProperties, DetailedHTMLProps, ImgHTMLAttributes, ReactElement, useCallback, useMemo, useState } from "react";
import Image, { ImageProps } from "next/image";
import imageURL from "image-url.config";


/**
 * @description
 * to prevent image src is false value or error value;
 */

export interface SafeImageProps {
  isNextImage?: boolean,
  nextImageProps?: Omit<ImageProps, "src" | "alt" | "height" | "onError" | "className" | "id" | "style" | "width" | "height">;
  htmlImageProps?: Omit<DetailedHTMLProps<ImgHTMLAttributes<HTMLImageElement>, HTMLImageElement>, "src" | "alt" | "height" | "onError" | "className" | "id" | "style" | "width" | "height">;
  src: string | null | undefined,
  alt: string
  fallbackSrc?: string,
  className?: string,
  id?: string,
  style?: CSSProperties,
  width?: number,
  height?: number,
  hasPlaceholder?: boolean,
}

export default function SafeImage(props: SafeImageProps): JSX.Element {
  const { isNextImage = false } = props;
  const fallbackSrc = useMemo(() => props.fallbackSrc ?? imageURL.default.global, [props.fallbackSrc]);
  const [isError, setIsError] = useState(false);

  if (isNextImage && props.htmlImageProps) throw "you set isNextImage = true, go use nextImageProps";
  if (!isNextImage && props.nextImageProps) throw "you set isNextImage = false, go use htmlImageProps";

  const onError = useCallback(() => {
    setIsError(true);
    console.warn({
      message: "Safe image switch image src to fallback src",
      errorSrc: props.src,
      fallbackSrc: fallbackSrc,
    });
  }, [fallbackSrc, props.src]);

  const genericProps = useMemo(() => ({
    src: ((isError || !props.src) ? fallbackSrc : props.src) as string,
    onError,
    className: props.className,
    id: props.id,
    style: props.style,
    width: props.width,
    height: props.height,
  }), [fallbackSrc, isError, onError, props.className, props.height, props.id, props.src, props.style, props.width]);


  return isNextImage 
    ? (
      <Image 
        {...props.nextImageProps} 
        {...genericProps} 
        {...props.hasPlaceholder && { 
          blurDataURL: fallbackSrc,  
          placeholder: "blur",
        }}
        loading="lazy" 
        quality={50} 
        alt={props.alt}
      />
    ) 
    : (
      <img 
        {...props.htmlImageProps} 
        {...genericProps}
        {...props.hasPlaceholder && { placeholder: fallbackSrc }} 
        loading="lazy"
        alt={props.alt}
      />
    );
}