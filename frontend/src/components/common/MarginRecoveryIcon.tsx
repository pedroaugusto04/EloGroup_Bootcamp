import React from 'react';

const marginRecoveryIcon = new URL('../../assets/margin-recovery-advisor.png', import.meta.url).href;

interface MarginRecoveryIconProps {
  className?: string;
}

export const MarginRecoveryIcon: React.FC<MarginRecoveryIconProps> = ({
  className = 'w-4 h-4',
}) => (
  <img
    aria-hidden="true"
    alt=""
    className={`object-contain ${className}`}
    draggable={false}
    src={marginRecoveryIcon}
  />
);
