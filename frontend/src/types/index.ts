import { SVGProps } from "react";

export type IconSvgProps = SVGProps<SVGSVGElement> & {
  size?: number;
};

export type ImageProps = {
  className?: string;
  width: string;
  height: string;
}
