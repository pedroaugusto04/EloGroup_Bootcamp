import React from 'react';

const inventoryCopilotIcon = new URL('../../assets/inventory-copilot.png', import.meta.url).href;

interface InventoryCopilotIconProps {
  className?: string;
}

export const InventoryCopilotIcon: React.FC<InventoryCopilotIconProps> = ({
  className = 'w-4 h-4',
}) => (
  <img
    aria-hidden="true"
    alt=""
    className={`object-contain ${className}`}
    draggable={false}
    src={inventoryCopilotIcon}
  />
);
