import { HTMLAttributes, forwardRef } from 'react';
import { cn } from '@/lib/utils';

export interface ProgressProps extends HTMLAttributes<HTMLDivElement> {
  percentage: number;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'circular' | 'linear';
  color?: string;
}

const Progress = forwardRef<HTMLDivElement, ProgressProps>(
  ({ className, percentage, size = 'md', variant = 'linear', color, ...props }, ref) => {
    const clampedPercentage = Math.min(Math.max(percentage, 0), 100);

    if (variant === 'circular') {
      const sizeMap = {
        sm: 32,
        md: 48,
        lg: 64,
      };
      
      const radius = sizeMap[size];
      const strokeWidth = size === 'sm' ? 3 : size === 'md' ? 4 : 6;
      const normalizedRadius = radius - strokeWidth * 2;
      const circumference = normalizedRadius * 2 * Math.PI;
      const strokeDasharray = `${circumference} ${circumference}`;
      const strokeDashoffset = circumference - (clampedPercentage / 100) * circumference;

      return (
        <div
          ref={ref}
          className={cn('relative inline-flex items-center justify-center', className)}
          {...props}
        >
          <svg
            height={radius * 2}
            width={radius * 2}
            className="transform -rotate-90"
          >
            <circle
              stroke="currentColor"
              fill="transparent"
              strokeWidth={strokeWidth}
              strokeDasharray={strokeDasharray}
              strokeDashoffset={strokeDashoffset}
              r={normalizedRadius}
              cx={radius}
              cy={radius}
              className={cn(
                'transition-all duration-300 ease-in-out',
                color || 'text-blue-600'
              )}
            />
            <circle
              stroke="currentColor"
              fill="transparent"
              strokeWidth={strokeWidth}
              r={normalizedRadius}
              cx={radius}
              cy={radius}
              className="text-gray-200"
            />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <span className={cn(
              'font-medium',
              size === 'sm' ? 'text-xs' : size === 'md' ? 'text-sm' : 'text-base'
            )}>
              {Math.round(clampedPercentage)}%
            </span>
          </div>
        </div>
      );
    }

    // Linear progress
    return (
      <div
        ref={ref}
        className={cn('w-full', className)}
        {...props}
      >
        <div className={cn(
          'bg-gray-200 rounded-full overflow-hidden',
          size === 'sm' ? 'h-2' : size === 'md' ? 'h-3' : 'h-4'
        )}>
          <div
            className={cn(
              'h-full transition-all duration-300 ease-in-out rounded-full',
              color || 'bg-blue-600'
            )}
            style={{ width: `${clampedPercentage}%` }}
          />
        </div>
        {size !== 'sm' && (
          <div className="mt-1 text-right">
            <span className={cn(
              'text-sm font-medium',
              size === 'md' ? 'text-sm' : 'text-base'
            )}>
              {Math.round(clampedPercentage)}%
            </span>
          </div>
        )}
      </div>
    );
  }
);

Progress.displayName = 'Progress';

export { Progress };
