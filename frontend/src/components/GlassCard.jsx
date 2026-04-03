import React from 'react';
import { cn } from '../lib/utils';

export function GlassCard({ children, className, interactive = true, ...props }) {
  // If interactive is false, we use glass-panel which has no hover effect
  return (
    <div 
      className={cn(
        interactive ? 'glass-card' : 'glass-panel', 
        'p-6 w-full',
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}
