import { HTMLAttributes, forwardRef, useState, useRef, useEffect } from 'react';
import { ChevronDown, ChevronRight } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface CollapsibleProps extends HTMLAttributes<HTMLDivElement> {
  defaultOpen?: boolean;
  trigger: React.ReactNode;
  children: React.ReactNode;
}

const Collapsible = forwardRef<HTMLDivElement, CollapsibleProps>(
  ({ className, defaultOpen = false, trigger, children, ...props }, ref) => {
    const [isOpen, setIsOpen] = useState(defaultOpen);
    const contentRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
      if (contentRef.current) {
        if (isOpen) {
          contentRef.current.style.maxHeight = `${contentRef.current.scrollHeight}px`;
        } else {
          contentRef.current.style.maxHeight = '0px';
        }
      }
    }, [isOpen, children]);

    return (
      <div ref={ref} className={cn('w-full', className)} {...props}>
        <button
          type="button"
          onClick={() => setIsOpen(!isOpen)}
          className="flex items-center gap-2 w-full text-left hover:bg-gray-50 p-2 rounded-md transition-colors"
        >
          {isOpen ? (
            <ChevronDown className="w-4 h-4 text-gray-500" />
          ) : (
            <ChevronRight className="w-4 h-4 text-gray-500" />
          )}
          {trigger}
        </button>
        <div
          ref={contentRef}
          className="overflow-hidden transition-all duration-200 ease-in-out"
          style={{ maxHeight: isOpen ? 'auto' : '0px' }}
        >
          <div className="p-4 bg-gray-50 border-l-2 border-gray-200 ml-6">
            {children}
          </div>
        </div>
      </div>
    );
  }
);

Collapsible.displayName = 'Collapsible';

export { Collapsible };
