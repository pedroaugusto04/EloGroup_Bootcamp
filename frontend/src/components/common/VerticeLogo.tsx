import React from 'react';

interface VerticeLogoProps {
  className?: string;
  size?: number;
}

export const VerticeLogo: React.FC<VerticeLogoProps> = ({
  className = 'w-4 h-4',
  size = 18,
}) => {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      <path
        d="M4.5 5.5L12 20L19.5 5.5"
        stroke="currentColor"
        strokeWidth="3.2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
};
