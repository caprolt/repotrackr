import { HTMLAttributes, forwardRef } from 'react';
import { cn } from '@/lib/utils';

export interface StatusBadgeProps extends HTMLAttributes<HTMLSpanElement> {
  status: 'green' | 'yellow' | 'red' | 'gray';
  children: React.ReactNode;
}

const StatusBadge = forwardRef<HTMLSpanElement, StatusBadgeProps>(
  ({ className, status, children, ...props }, ref) => {
    return (
      <span
        ref={ref}
        className={cn(
          'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
          {
            'bg-success-100 text-success-800': status === 'green',
            'bg-warning-100 text-warning-800': status === 'yellow',
            'bg-danger-100 text-danger-800': status === 'red',
            'bg-gray-100 text-gray-800': status === 'gray',
          },
          className
        )}
        {...props}
      >
        {children}
      </span>
    );
  }
);

StatusBadge.displayName = 'StatusBadge';

export { StatusBadge };
