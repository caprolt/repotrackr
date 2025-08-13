import { HTMLAttributes, forwardRef } from 'react';
import { cn } from '@/lib/utils';

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  title?: string;
}

const Card = forwardRef<HTMLDivElement, CardProps>(
  ({ className, title, children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          'bg-white rounded-lg shadow-md border border-gray-200 p-6',
          className
        )}
        {...props}
      >
        {title && (
          <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>
        )}
        {children}
      </div>
    );
  }
);

Card.displayName = 'Card';

export { Card };
