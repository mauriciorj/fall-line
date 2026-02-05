import Link from 'next/link'
import { forwardRef, ReactNode } from 'react'

interface NavLinkCompatProps {
  className?: string // These are unused in implementation if not destructured, but interface has them.
  activeClassName?: string
  pendingClassName?: string
  to: string
  children?: ReactNode
}

const NavLink = forwardRef<HTMLAnchorElement, NavLinkCompatProps>(
  ({ to, children, ...props }, ref) => {
    return (
      <Link ref={ref} href={to} {...props}>
        {children}
      </Link>
    )
  }
)

NavLink.displayName = 'NavLink'

export { NavLink }
